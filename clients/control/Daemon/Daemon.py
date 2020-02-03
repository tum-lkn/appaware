#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import collections
import importlib
import ipaddress
import json
import logging
import os
import paramiko
import redis
import shutil
import signal
import subprocess
import sys
import time
import copy

from ..utils.TCPDump import TCPDump
from ..utils.InterfaceStats import InterfaceStats
from ..utils.RTTMeasurement import RTTMeasurementStandalone
from utils.interface_list import interface_list, phy_from_bridge


class Daemon(object):
    def __init__(self, daemon_id, redis_host="localhost", redis_port=6379, redis_db=0, redis_channel="daemon_broadcast", working_dir=None):

        if not working_dir:
            working_dir = ""

        # drops getcwd if working dir is absolute path
        working_dir = os.path.join(os.getcwd(), working_dir, daemon_id)

        if os.path.exists(working_dir):
            # TODO move existing dir?
            print("%s already exists" % (working_dir))
            pass
        else:
            os.makedirs(working_dir)

        os.chdir(working_dir)

        self._working_dir = working_dir

        # Setup logger to accept every level
        logger = logging.getLogger("AppAware")
        logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # create file handler
        # TODO use abs path from file
        file_handler = logging.FileHandler("Daemon.log", mode='w')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # get Daemon logger
        self._logger = logging.getLogger("AppAware." + self.__class__.__name__)
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

        # store study_id to see if daemon is involved in test
        self._running_study = None

        # CTRL-C signal
        signal.signal(signal.SIGINT, self._signal_handler)

    def prepare(self):
        self._logger.debug("Daemon.prepare()")
        try:
            self._redis = redis.StrictRedis(host=self._redis_config["redis_host"], port=self._redis_config["redis_port"], db=self._redis_config["redis_db"], charset="utf-8", decode_responses=True)
            self._redis_sub = self._redis.pubsub(ignore_subscribe_messages=True)
            self._redis_sub.subscribe(self._redis_config["redis_channel"])
        except redis.exceptions.ConnectionError:
            self._logger.error("Couldn't connect to redis server (%s:%s) - exiting" % (self._redis_config["redis_host"], self._redis_config["redis_port"]))
            sys.exit(-1)

    def run(self):
        self._logger.debug("Daemon.run()")
        self._running = True

        while self._running:
            #self._logger.debug("checking for messages")
            msg = self._redis_sub.get_message(timeout=1)
            if msg:
                self._logger.debug("received msg: \"%s\"" % (msg))
                self._handle_msg(msg=msg)
            else:
                pass
                #time.sleep(0.01)

        self.stop_apps()

    def _handle_msg(self, msg):
        self._logger.debug("Daemon._handle_msg()")

        try:
            data = json.loads(msg["data"])
        except Exception as e:
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
        else:
            self._logger.debug("Unrecognized command %s" % (data))

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

            # wait some time so all all clients can receive stop message - maybe the amount of scp requests block some redis messages
            time.sleep(2)

            self._send_logs()

        self._running_study = None

    def clean_up(self):
        self._logger.debug("Daemon.clean_up()")
        self._redis_sub.unsubscribe()
        self._redis_sub.close()

    def _send_logs(self):
        self._logger.debug("Daemon._send_logs()")

        collect_settings = self._config.get("experiment", {}).get("collect_logs", {})
        if not collect_settings:
            self._logger.error("No log collection settings - aborting")
            return

        remote_path = collect_settings.get("remote_path", None)
        if not remote_path:
            self._logger.error("No remote_path specified - aborting")
            return

        timestamp = collect_settings.get("timestamp", None)
        if not timestamp:
            self._logger.error("No timestamp specified - aborting")
            return

        ssh_args = collect_settings.get("ssh_args", {})
        if not ssh_args:
            self._logger.error("No settings for log collection set - aborting")
            return

        self._logger.debug("Connecting using args %s" % (ssh_args))
        ssh_client = paramiko.SSHClient()
        ssh_client.load_system_host_keys()
        ssh_client.set_missing_host_key_policy(paramiko.WarningPolicy())
        num_connects = 0
        while True:
            try:
                num_connects += 1
                ssh_client.connect(**ssh_args)
                break
            except Exception as e:
                if num_connects < 20:
                    self._logger.error("Couldn't connect (%s) - retrying" % (e))
                    time.sleep(0.25)
                else:
                    self._logger.error("Couldn't connect (%s) - aborting" % (e))
                    return
        sftp_client = ssh_client.open_sftp()

        local_path = os.path.abspath(os.getcwd())

        # complete remote path to split correct
        timestamp_str = time.strftime("%Y_%m_%d-%H_%M_%S", time.localtime(timestamp))
        remote_path = os.path.join(remote_path, timestamp_str + '-' + self._running_study , self._daemon_id)
        if not os.path.isabs(remote_path):
            remote_path = "./" + remote_path
        if not os.path.isfile(local_path) and not remote_path.endswith('/'):
            # append '/'' if local_path is file to create all folders via os.path.split()
            remote_path += '/'

        # test if parent dirs exist:
        remote_dir = os.path.dirname(remote_path)
        folders = []
        while True:
            if remote_path == "":
                # reached end of path - should never happen
                break
            try:
                sftp_client.listdir(remote_dir)
                # dir exists
                break
            except FileNotFoundError:
                remote_dir, folder = os.path.split(remote_dir)
                # folder not existing - add to mkdir list
                folders.insert(0, folder)
        for folder in folders:
            # append folder to last existing path and create
            remote_dir = os.path.join(remote_dir, folder)
            # ignore exception because other client might have created folder during check and creation
            try:
                sftp_client.mkdir(remote_dir)
            except Exception as e:
                pass

        # file / dir handling
        if os.path.isfile(local_path):
            # if remote_path is folder append filename
            if remote_path.endswith('/'):
                filename = os.path.basename(local_path)
                remote_path = os.path.join(remote_path, filename)
            sftp_client.put(local_path, remote_path)
        else:
            for root, folders, files in os.walk(local_path):
                # make root relative to localpath
                rel_root = os.path.relpath(root, local_path)
                try:
                    sftp_client.mkdir(os.path.join(remote_path,rel_root))
                except:
                    pass
                for file in files:
                    sftp_client.put(os.path.join(root,file),os.path.join(remote_path,rel_root,file))

        sftp_client.close()
        ssh_client.close()

        if collect_settings.get("delete", False):
            study_dir = os.getcwd()
            os.chdir(self._working_dir)
            shutil.rmtree(study_dir)

        self._logger.debug("Logs sent")

    def _publish(self, msg):
        msg["daemon_id"] = self._daemon_id
        data = json.dumps(msg)
        self._redis.publish(self._redis_config["redis_channel"], data)

    def _signal_handler(self, signal, frame):
        self._logger.debug("Daemon._signal_handler()")
        self._running = False

    def _apply_config(self):
        self._logger.debug("Daemon._apply_config()")

        # make sure no old apps are running
        self.stop_apps()

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

            # check if found interface is bridge
            if iface and "br" in iface:
                iface = phy_from_bridge(br=iface)[0]
                self._logger.info("Interface was bridge - physical interface is %s" % (iface))

            # apply pacing
            # value in kbits - 0 to delete - null to leave settings
            pacing = daemon_config.get("pacing", 0)
            if pacing is not None:
                self._logger.debug("setting pacing to %s kbit/s" % (pacing))
                fq_set = False
                output = subprocess.check_output("sudo tc qdisc show", shell=True).decode("utf-8")
                for line in output.splitlines():
                    # searching "fq " because "fq" matches on arch which uses "fq_codel" per default - ubuntu "pfifo_fast"
                    if iface in line and "cfq" in line:
                        fq_set = True

                if fq_set:
                    if pacing > 0:
                        cmd = "sudo tc qdisc change dev %s root cfq maxrate %skbit" % (iface, pacing)
                    else:
                        cmd = "sudo tc qdisc del dev %s root" % (iface)
                else:
                    if pacing > 0:
                        cmd = "sudo tc qdisc add dev %s root cfq maxrate %skbit" % (iface, pacing)
                    else:
                        cmd = None

                if cmd:
                    self._logger.debug("Executing %s" % (cmd))
                    # ToDo echo stdout and stderr
                    process = subprocess.call(cmd, shell=True)

            # start tcpdump if specified in config
            tcpdump_settings = logging_settings.get("tcpdump", None)
            if tcpdump_settings:
                if type(tcpdump_settings) is dict:
                    # tcpdump can be called without an interface so iface None is ok
                    truncate = tcpdump_settings.get("truncate", None)
                    self._logger.debug("Starting TCPDump on %s" % (iface))
                    self._tcpdump = TCPDump(iface=iface, truncate=truncate)
                    self._tcpdump.start()
                else:
                    self._logger.error("tcpdump settings not in dict format")

            # start interface stats
            interface_stats_settings = logging_settings.get("interface_stats", None)
            if interface_stats_settings:
                if type(interface_stats_settings) is dict:
                    # interface stats need an interface
                    if iface:
                        interval = interface_stats_settings.get("interval", 1)
                        self._logger.debug("Starting InterfaceStats on %s" % (iface))
                        self._interface_stats = InterfaceStats(iface=iface, interval=interval)
                        self._interface_stats.start()
                    else:
                        self._logger.error("Could not start InterfaceStats because no interface was found")
                else:
                    self._logger.error("interface_stats settings not in dict format")

            # start rtt measurement
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
                    self._rtt_measurement = RTTMeasurementStandalone(host_list=host_list, bind_ip=bind_ip, interval=interval, max_id=max_id, payload_size=payload_size, nice=nice)
                    self._rtt_measurement.start()
                else:
                    self._logger.error("rtt settings not in dict format")

            app_controller = daemon_settings["applications"].get("app_controller", "0.0.0.0")
            app_controller_log = daemon_settings["applications"].get("app_controller_log", None)
            metric_log = daemon_settings["applications"].get("metric_log", None)

            # parse server applications
            for server_application in daemon_config.get("server_applications", []):
                application = server_application["application"]
                module = importlib.import_module("servers.%s.%s" % (application, application))

                # extract used args from application settings
                arg_list = []
                args = daemon_settings.get("applications", {})
                server_args = {k:args[k] for k in arg_list if k in args}

                self._logger.debug("Starting %s using args %s" % (application, server_args))
                server = getattr(module, application)(**server_args)
                server.prepare()
                config = copy.deepcopy(daemon_settings["applications"])
                config.update(server_application.get("config", {}))
                server.set_config(config=config)
                self._apps.append(server)

            # parse client_applications
            for client_application in daemon_config.get("client_applications", []):
                application = client_application["application"]
                module = importlib.import_module("clients.%s.%s" % (application, application))

                # extract used args from application settings
                arg_list = ["app_controller", "app_controller_port", "app_controller_log", "metric_log"]
                args = daemon_settings.get("applications", {})
                client_args = {k:args[k] for k in arg_list if k in args}

                self._logger.debug("Starting %s using args %s" % (application, client_args))
                client = getattr(module, application)(**client_args)
                client.prepare()
                config = copy.deepcopy(daemon_settings["applications"])
                config.update(client_application.get("config", {}))
                client.set_config(config=config)
                self._apps.append(client)

            # start apps
            for app in self._apps:
                app.start()
        else:
            # not involved in last sent config - redundant
            self._running_study = None
            self._logger.debug("No config for this daemon id contained")

    @staticmethod
    def _dict_update(d, u):
        # https://stackoverflow.com/a/3233356
        for k, v in u.items():
            if isinstance(v, collections.Mapping):
                d[k] = Daemon._dict_update(d.get(k, {}), v)
            else:
                d[k] = v
        return d

if __name__ == '__main__':
    # TODO add argparse like Standalone client
    # --host-id
    # -v
    # -log
    # --redis_settings
    daemon = Daemon(daemon_id="client_a", redis_host="10.0.0.1")
    daemon.prepare()
    daemon.run()
    daemon.clean_up()
