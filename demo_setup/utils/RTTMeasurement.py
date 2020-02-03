#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import argparse
import json
import logging
import os
import random
import shlex
import signal
import socket
import subprocess
import threading
import time
import queue
import redis


class RTTMeasurement(object):
    def __init__(self, host_list=[], port=6666, bind_ip = "0.0.0.0", out_file=None, interval=1, max_id=256,
                 payload_size=0, redis_host="10.0.8.0", redis_port=6379, channel='statistics.rtt'):
        self._logger = logging.getLogger("AppAware." + self.__class__.__name__)

        self._host_list = host_list
        self._port = port
        self._bind_ip = bind_ip
        self._out_file = out_file
        self._interval = interval
        self._max_id = max_id
        self._payload_size = payload_size

        self._running = False

        self._server_thread = None
        self._client_thread = None

        self._recv_queue = queue.Queue()
        self._requests = {}

        # create/calculate once to save performance
        if self._payload_size > 0:
            # safety overhead
            self._recv_size = self._payload_size + 50
        else:
            self._recv_size = 1024
        self._max_id_len = len(str(self._max_id))
        self._msg_frame = "{{}} {{:0{}}} {{}}".format(self._max_id_len)
        # note ' ' at beginning to strip msg_id correct
        self._pad_str = ' ' + ''.join([chr(random.randint(65,90)) for i in range(self._payload_size)])

        # redis
        self._redis = redis.StrictRedis(redis_host, redis_port)
        self._redis_channel = channel

    def start(self):
        self._logger.debug("RTTMeasurement.start()")
        self._running = True
        self._server_thread = threading.Thread(target=self.server)
        self._client_thread = threading.Thread(target=self.client)
        self._logging_thread = threading.Thread(target=self.logging)
        self._server_thread.start()
        self._client_thread.start()
        self._logging_thread.start()

    def stop(self):
        self._logger.debug("RTTMeasurement.stop()")
        self._running = False
        if self._server_thread:
            self._server_thread.join()
            self._logger.debug("server joined")
        if self._client_thread:
            self._client_thread.join()
            self._logger.debug("client joined")
        if self._logging_thread:
            self._logging_thread.join()
            self._logger.debug("logging joined")

    def server(self):
        self._logger.debug("RTTMeasurement.server()")
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((self._bind_ip, self._port))
        sock.settimeout(1)

        while self._running:
            self._logger.debug("server running")
            try:
                data, addr = sock.recvfrom(self._recv_size)
                timestamp = time.time()
            except socket.timeout:
                self._logger.debug("socket timeout")
                continue
            if not data:
                self._logger.debug("no data")
                continue
            data = data.decode("utf-8")
            self._logger.debug("received {} from {}".format(data, addr))

            host = addr[0]
            try:
                msg_id = int(data.split()[1])
            except Exception as e:
                self._logger.warn("couldn't extraxt message id from {}".format(data))

            if data.startswith("PING"):
                answer_addr = (host, self._port)
                answer_msg = self._create_msg(msg="PONG", msg_id=msg_id)
                try:
                    sock.sendto(answer_msg.encode("utf-8"), answer_addr)
                except Exception as e:
                    self._logger.error(e.errno, e.strerror)
                    self._logger.error("msg: %s, addr: %s" % (answer_msg, answer_addr))
            elif data.startswith("PONG"):
                entry = {"timestamp": timestamp, "msg_id": msg_id, "host": host}
                self._recv_queue.put(entry)
            else:
                self._logger.warn("ignoring message %s")

    def client(self):
        self._logger.debug("RTTMeasurement.client()")
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        msg_id = 0
        next_call = time.time()
        while self._running:
            self._logger.debug("client running")
            for host in self._host_list:
                # first time host is added
                if host not in self._requests:
                    self._requests[host] = {}
                msg = self._create_msg(msg="PING", msg_id=msg_id)
                self._requests[host][msg_id] = time.time()
                try:
                    sock.sendto(msg.encode("utf-8"), (host, self._port))
                except Exception as e:
                    self._logger.error(e.errno, e.strerror)
                    self._logger.error("msg: %s, addr: %s" % (msg, (host, self._port)))
            msg_id = (msg_id + 1) % self._max_id
            next_call += self._interval

            if time.time() < next_call:
                time.sleep(next_call - time.time())
            else:
                self._logger.warn("sending took longer than interval")

    def logging(self):
        self._logger.debug("RTTMeasurement.logging()")

        if not self._out_file:
            self._out_file = "rtt.log"

        if os.path.exists(self._out_file):
            self._logger.debug("out_file already exists - generating new name")
            name, suffix = self._out_file.rsplit('.', 1)
            i = 1
            while True:
                self._out_file = "%s_%s.%s" % (name, i, suffix)
                if not os.path.exists(self._out_file):
                    break
                i += 1

        logfile = open(self._out_file, 'w')

        # get queue and search in requests
        while self._running or not self._recv_queue.empty():
            self._logger.debug("logging running")
            try:
                entry = self._recv_queue.get(timeout=1)
            except queue.Empty:
                self._logger.debug("nothing in queue")
                continue
            host = entry["host"]
            msg_id = entry["msg_id"]
            request_timestamp = self._requests[host][msg_id]
            response_timestamp = entry["timestamp"]
            rtt = response_timestamp - request_timestamp

            log_msg = {"timestamp": request_timestamp, "host": host, "rtt": rtt}

            logfile.write(json.dumps(log_msg) + '\n')
            logfile.flush()

            self._redis.publish(self._redis_channel, json.dumps(log_msg))

            self._logger.debug("wrote log message {}".format(log_msg))

            # clear message timestamp
            del self._requests[entry["host"]][entry["msg_id"]]

    def _create_msg(self, msg, msg_id):
        msg = self._msg_frame.format(msg, msg_id, time.time() * 1000)
        if len(msg) < self._payload_size:
            pad_len = self._payload_size - len(msg)
            msg += self._pad_str[0:pad_len]
        return msg


class RTTMeasurementStandalone(object):
    def __init__(self, host_list=None, port=None, bind_ip=None, out_file=None, interval=None, max_id=None, payload_size=None, nice=0, verbose=False):
        self._logger = logging.getLogger("AppAware." + self.__class__.__name__)
        print("standalone init")
        self._host_list = host_list
        self._port = port
        self._bind_ip = bind_ip
        self._out_file = out_file
        self._interval = interval
        self._max_id = max_id
        self._payload_size = payload_size
        self._nice = nice
        self._verbose = verbose

        self._process = None

    def start(self):
        self._logger.debug("RTTMeasurementStandalone.start()")
        # create cmd call
        cmd = ['python3', os.path.abspath(__file__)]
        if self._host_list:
            cmd += ["--host-list"]
            cmd += self._host_list
        if self._port:
            cmd += ["--port", str(self._port)]
        if self._bind_ip:
            cmd += ["--bind-ip", self._bind_ip]
        if self._out_file:
            cmd += ["--our-file", self._out_file]
        if self._interval:
            cmd += ["--interval", str(self._interval)]
        if self._max_id:
            cmd += ["--max-id", str(self._max_id)]
        if self._payload_size:
            cmd += ["--payload-size", str(self._payload_size)]
        if self._verbose:
            cmd += ["--verbose"]

        cmd = ' '.join(cmd)
        self._logger.debug("Executing %s" % (cmd))

        # start process and nice
        self._process = subprocess.Popen(shlex.split(cmd))  # , preexec_fn=lambda : os.nice(self._nice))
        # get pid and select nice value
        nice_cmd = "sudo renice %s %s" % (self._nice, self._process.pid)
        self._logger.debug("Executing %s" % (nice_cmd))
        subprocess.call(shlex.split(nice_cmd))

    def stop(self):
        self._logger.debug("RTTMeasurementStandalone.stop()")
        self._process.kill()

def signal_handler(signum, frame):
    global running
    running = False

if __name__ == '__main__':
    running = True
    signal.signal(signal.SIGINT, signal_handler)

    # parse args
    description = ("RTT Measurement")

    parser = argparse.ArgumentParser(description=description, add_help=False)

    parser.add_argument("--help", action="help", help="show this help message and exit")
    parser.add_argument("-b", "--bind-ip", help="IP of interface to bind to", dest="bind_ip")
    parser.add_argument("-h", "--host-list", help="IP of app controller", nargs='+', dest="host_list")
    parser.add_argument("-i", "--interval", help="RTT Measurement interval", dest="interval", type=float)
    parser.add_argument("--max-id", help="Max message id", dest="max_id", type=int)
    parser.add_argument("-o", "--out-file", help="Filepath to store log", dest="out_file")
    parser.add_argument("-p", "--port", help="Port to listen", dest="port", type=int)
    parser.add_argument("--payload-size", help="Min payload size", dest="payload_size", type=int)
    parser.add_argument("-v", "--verbose", help="Enable debug output", dest="verbose", action="store_true")

    args = vars(parser.parse_args())

    if args["verbose"]:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig()

    # delete verbose key because RTTMeasurement won't handle it
    del(args["verbose"])
    # delete all None values to use default values
    args = {key: value for (key, value) in args.items() if value}

    rtt_measurement = RTTMeasurement(**args)
    rtt_measurement.start()

    while running:
        time.sleep(0.5)

    rtt_measurement.stop()
