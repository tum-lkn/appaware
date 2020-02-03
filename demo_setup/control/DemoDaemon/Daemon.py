#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import collections
import importlib
import ipaddress
import json
import logging
import os
import shutil
import signal
import subprocess
import time
import queue
import argparse
import sys

from utils.RTTMeasurement import RTTMeasurementStandalone
from utils.InterfaceStats import InterfaceStats, IFACE_STATS_MESSAGE_TYPE
from utils.interface_list import interface_list
from utils.redis_communicator import RedisCommunicator, REDIS_MESSAGE_TYPE


class Daemon(object):
    def __init__(self, daemon_id, redis_host="localhost", redis_port=6379, redis_db=0,
                 redis_channel="daemon_broadcast", working_dir=None):

        # Add current working dir to Python search path
        sys.path.append(os.getcwd())

        if not working_dir:
            working_dir = ""

        # drops getcwd if working dir is absolute path
        working_dir = os.path.join(os.getcwd(), working_dir, daemon_id)

        if os.path.exists(working_dir):
            # TODO move existing dir?
            print("%s already exists" % working_dir)
            pass
        else:
            os.makedirs(working_dir)

        print("chdir: %s" % working_dir)

        os.chdir(working_dir)

        self._working_dir = working_dir

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s \t %(message)s')

        # create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)

        # create file handler
        # TODO use abs path from file
        file_handler = logging.FileHandler("Daemon.log", mode='w')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)

        logging.basicConfig(level=logging.DEBUG, handlers=[console_handler, file_handler])

        # get Daemon logger
        self._logger = logging.getLogger("Daemon")
        self._logger.debug("Daemon.__init__()")

        self._daemon_id = daemon_id
        self._running = False
        self._redis = None
        self._redis_sub = None
        self._redis_config = {
            "redis_host": redis_host,
            "redis_port": redis_port,
            "redis_db": redis_db,
            "redis_channel": redis_channel
        }
        self._config = None
        self._tcpdump = None
        self._interface_stats = None
        self._rtt_measurement = None
        self._apps = []
        self._pacing = None
        self._iface = None
        self._comm_queue = queue.Queue()

        self._redis_communicator = RedisCommunicator(redis_host, redis_port, redis_channel, self._comm_queue, redis_db)

        # store study_id to see if daemon is involved in test
        self._running_study = None

        # CTRL-C signal
        signal.signal(signal.SIGINT, self._signal_handler)

    def prepare(self):
        self._logger.debug("Daemon.prepare()")
        self._redis_communicator.connect()
        self._redis_communicator.start()

    def run(self):
        self._logger.debug("Daemon.run()")
        self._running = True

        while self._running:
            if self._comm_queue.empty():
                time.sleep(0.1)
            else:
                msg = self._comm_queue.get()
                msg_type = msg.get('type', None)
                if msg_type == REDIS_MESSAGE_TYPE:
                    self._handle_msg(msg=msg['data'])
                elif msg_type == IFACE_STATS_MESSAGE_TYPE:
                    self._publish(msg['data'], 'statistics.iface')
                else:
                    self._logger.error("Received message of type {} from comm_queue. Not implemented".format(msg_type))

        self.stop_apps()

    def _handle_msg(self, msg):
        self._logger.debug("Daemon._handle_msg()")

        try:
            data = json.loads(msg["data"])
        except json.JSONDecodeError:
            self._logger.error("couldn't encode json string '%s'" % (msg["data"]))
            return

        msg_type = data["type"]

        if msg_type == "STOP_DAEMON":
            self.stop()
        elif msg_type == "STOP_APPS":
            self.stop_apps()
        elif msg_type == "CONFIG":
            self._config = data["config"]
            self._apply_config()
        elif msg_type == "PING":
            # TODO add running clients?
            self._publish(msg={"type": "PONG"})
        elif msg_type == "PONG":
            # ignore PING answers
            pass
        elif msg_type == "PACING_ON":
            self._apply_pacing()
        elif msg_type == "PACING_OFF":
            self._reset_pacing()
        else:
            self._logger.debug("Unrecognized command %s" % data)

    def stop(self):
        self._logger.debug("Daemon.stop()")
        self._running = False

    def stop_apps(self):
        self._logger.debug("Daemon.stop_apps()")

        for application in self._apps:
            try:
                application.stop()
                application.join()
                application.clean_up()
            except Exception as e:
                self._logger.error(e)

        self._apps = []

        if self._tcpdump:
            self._tcpdump.stop()
            self._tcpdump = None
        if self._interface_stats:
            self._interface_stats.stop()
            self._interface_stats = None
        if self._rtt_measurement:
            self._rtt_measurement.stop()
            self._rtt_measurement = None

        if self._running_study:
            # Daemon.log should be in parent folder - copy to collect with logs
            if os.path.isfile("./../Daemon.log"):
                shutil.copy("./../Daemon.log", "./Daemon.log")

            # wait some time so all all clients can receive stop message - maybe the amount of scp requests block
            # some redis messages
            time.sleep(2)

        self._running_study = None

    def clean_up(self):
        self._logger.debug("Daemon.clean_up()")
        self._redis_communicator.stop()
        self._redis_communicator.join()

    def _publish(self, msg, channel=None):
        if channel is None:
            channel = self._redis_config["redis_channel"]
        msg["daemon_id"] = self._daemon_id
        data = json.dumps(msg)
        self._redis_communicator.publish(data, channel)

    def _signal_handler(self, signal, frame):
        self._logger.debug("Daemon._signal_handler()")
        self._running = False

    def _apply_config(self):
        self._logger.debug("Daemon._apply_config()")

        # make sure no old apps are running
        self.stop_apps()

        # make sure no pacing is active
        self._reset_pacing()

        # get configs for the daemon
        daemon_config = self._config["daemons"].get(self._daemon_id, None)
        if daemon_config:
            # directory setup
            # get experiment config
            experiment_config = self._config.get("experiment", {})
            self._running_study = experiment_config.get("study_id", "unknown")

            # create new dir for study
            study_dir = os.path.join(self._working_dir, self._running_study)
            if os.path.exists(study_dir):
                self._logger.debug("study_dir already existing - generating new name")
                i = 1
                while True:
                    new_dir = "%s_%s" % (study_dir, i)
                    if not os.path.exists(new_dir):
                        study_dir = new_dir
                        break
                    i += 1

            os.makedirs(study_dir)
            os.chdir(study_dir)

            # save received config for documentation
            json.dump(self._config, open("config.json", 'w'), indent=2)

            daemon_settings = self._config.get("global_settings", {})
            Daemon._dict_update(daemon_settings, daemon_config.get("daemon_settings", {}))

            logging_settings = daemon_settings.get("logging", {})

            # find interface to dump based on iprange
            iface = None
            iface_ip = None

            network = ipaddress.ip_network(logging_settings.get("data_network", "192.168.0.0/21"), strict=False)
            for interface in [dict(i._asdict()) for i in interface_list(external=True, ip=True)]:
                ip = ipaddress.ip_address(interface["ip"])
                if ip in network:
                    iface_ip = interface["ip"]
                    iface = interface["name"]
                    self._logger.info("Found interface %s to be in network %s" % (iface, network))
                    break
            self._iface = iface

            # get pacing
            # value in kbits - 0 to delete - null to leave settings
            self._pacing = daemon_config.get("pacing", 0)

            # start interface stats
            self._start_interface_stats(logging_settings, iface)

            # start rtt measurement
            # self._start_rtt(logging_settings, iface_ip)

            # parse server applications
            self._parse_server_applications(daemon_config, daemon_settings)

            # parse client_applications
            self._parse_client_applications(daemon_config, daemon_settings)

            # start apps
            for app in self._apps:
                app.start()
        else:
            # not involved in last sent config - redundant
            self._running_study = None
            self._logger.debug("No config for this daemon id contained")

    def _start_interface_stats(self, logging_settings, iface):
        interface_stats_settings = logging_settings.get("interface_stats", None)
        if interface_stats_settings:
            if type(interface_stats_settings) is dict:
                # interface stats need an interface
                if iface:
                    interval = interface_stats_settings.get("interval", 1)
                    self._logger.debug("Starting InterfaceStats on %s" % iface)
                    self._interface_stats = InterfaceStats(iface=iface, comm_queue=self._comm_queue, interval=interval)
                    self._interface_stats.start()
                else:
                    self._logger.error("Could not start InterfaceStats because no interface was found")
            else:
                self._logger.error("interface_stats settings not in dict format")

    def _start_rtt(self, logging_settings, iface_ip):
        rtt_settings = logging_settings.get("rtt", None)
        if rtt_settings:
            if type(rtt_settings) is dict:
                # interface stats need an interface
                bind_ip = iface_ip if iface_ip else "0.0.0.0"
                host_list = rtt_settings.get("host_list", [])
                interval = rtt_settings.get("interval", 1)
                max_id = rtt_settings.get("max_id", 256)
                payload_size = rtt_settings.get("payload_size", 0)
                nice = rtt_settings.get("nice", 0)
                self._logger.debug("Starting RTT Measurement for hosts %s on %s" % (host_list, bind_ip))
                self._rtt_measurement = RTTMeasurementStandalone(host_list=host_list, bind_ip=bind_ip,
                                                                 interval=interval, max_id=max_id,
                                                                 payload_size=payload_size, nice=nice)
                self._rtt_measurement.start()
            else:
                self._logger.error("rtt settings not in dict format")

    def _parse_server_applications(self, daemon_config, daemon_settings):
        for server_application in daemon_config.get("server_applications", []):
            application = server_application["application"]
            module = importlib.import_module("servers.%s.%s" % (application, application))

            # extract used args from application settings
            arg_list = []
            args = daemon_settings.get("applications", {})
            server_args = {k: args[k] for k in arg_list if k in args}

            self._logger.debug("Starting %s using args %s" % (application, server_args))
            server = getattr(module, application)(**server_args)
            server.prepare()
            config = server_application.get("config", {})
            server.set_config(config=config)
            self._apps.append(server)

    def _parse_client_applications(self, daemon_config, daemon_settings):
        for client_application in daemon_config.get("client_applications", []):
            application = client_application["application"]

            m = "clients.%s.%s" % (application, application)

            self._logger.debug("Loading module: %s" % m)
            self._logger.debug("Import paths: %s" % sys.path)

            module = importlib.import_module(m)

            # extract used args from application settings
            arg_list = ["app_controller", "app_controller_port", "app_controller_log", "metric_log"]
            args = daemon_settings.get("applications", {})
            client_args = {k: args[k] for k in arg_list if k in args}

            self._logger.debug("Starting %s using args %s" % (application, client_args))
            client = getattr(module, application)(**client_args)
            client.prepare()
            config = client_application.get("config", {})
            client.set_config(config=config)
            self._apps.append(client)

    def _apply_pacing(self):

        self._logger.debug("_apply_pacing()")

        if self._pacing is not None:

            if self._iface is None:
                self._logger.error("self._iface is not set !")
                return

            self._logger.debug("setting pacing to %s kbit/s" % self._pacing)

            fq_set = False
            output = subprocess.check_output("sudo tc qdisc show", shell=True).decode("utf-8")

            for line in output.splitlines():
                # searching "fq " because "fq" matches on arch which uses "fq_codel"
                # per default - ubuntu "pfifo_fast"

               if self._iface in line and "cfq" in line:
                   fq_set = True

            if fq_set:
                if self._pacing > 0:
                    cmd = "sudo tc qdisc change dev %s root cfq maxrate %skbit" % (self._iface, self._pacing)
                else:
                    cmd = "sudo tc qdisc del dev %s root" % self._iface
            else:
                if self._pacing > 0:
                    cmd = "sudo tc qdisc add dev %s root cfq maxrate %skbit" % (self._iface, self._pacing)
                else:
                    cmd = None

            if cmd:
                self._logger.debug("Executing %s" % cmd)
                # ToDo echo stdout and stderr
                subprocess.call(cmd, shell=True)

    def _reset_pacing(self):
        self._logger.debug("_reset_pacing()")
        fq_set = False
        output = subprocess.check_output("sudo tc qdisc show", shell=True).decode("utf-8")

        if self._iface is None:
            self._logger.error("self._iface is not set !")
            return

        for line in output.splitlines():
            # searching "fq " because "fq" matches on arch which uses "fq_codel"
            # per default - ubuntu "pfifo_fast"

            if self._iface in line and "cfq" in line:
                fq_set = True
                break

        if fq_set:
            cmd = "sudo tc qdisc del dev %s root" % self._iface
            self._logger.debug("Executing %s" % cmd)
            subprocess.call(cmd, shell=True)

    @staticmethod
    def _dict_update(d, u):
        # https://stackoverflow.com/a/3233356
        for k, v in u.items():
            if isinstance(v, collections.Mapping):
                d[k] = Daemon._dict_update(d.get(k, {}), v)
            else:
                d[k] = v
        return d


if __name__ == "__main__":
    # parse args
    description = ("Daemon parameter")

    parser = argparse.ArgumentParser(description=description)

    parser.add_argument("-i", "--id", help="Daemon identifier", dest="daemon_id", required=True)
    parser.add_argument("-r", "--redis", help="Redis host", dest="redis_host", default="10.0.8.0")
    parser.add_argument("-w", "--working-dir", help="Working directory for logs", dest="working_dir")

    args = vars(parser.parse_args())

    # start daemon
    daemon = Daemon(daemon_id=args["daemon_id"], redis_host=args["redis_host"], working_dir=args["working_dir"])
    daemon.prepare()
    daemon.run()
    daemon.clean_up()

