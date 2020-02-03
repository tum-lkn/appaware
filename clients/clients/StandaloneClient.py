#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import argparse
import json
import logging
import signal
import time


class StandaloneClient(object):
    def __init__(self, client_class):
        # parse args
        description = ("%s parameter" % (client_class.__name__))

        parser = argparse.ArgumentParser(description=description, add_help=False)

        parser.add_argument("--help", action="help", help="show this help message and exit")
        parser.add_argument("-a", "--app-controller", help="IP of app controller", dest="app_controller")
        parser.add_argument("-c", "--config", help="Client config file", dest="config")
        parser.add_argument("-d", "--debug-log", help="Log verbose output to file", nargs='?', dest="debug_log", action="store", const="./")
        parser.add_argument("-h", "--host", help="Host identifier (e.g. IP)", dest="host_id")
        parser.add_argument("-i", "--id", help="Client identifier", dest="client_id")
        parser.add_argument("-l", "--log", help="Log app cotroller calls to file", nargs='?', dest="app_controller_log", action="store", const="./")
        parser.add_argument("-m", "--metric-log", help="Log app metric to file", nargs='?', dest="metric_log", action="store", const="./")
        parser.add_argument("-p", "--port", help="App controller port", dest="app_controller_port")
        parser.add_argument("-s", "--standalone", help="Standalone without app-controller", dest="standalone", action="store_true")
        parser.add_argument("-v", "--verbose", help="Verbose", dest="verbose", action="store_true")

        args = vars(parser.parse_args())

        # setting up CTRL+C handler
        signal.signal(signal.SIGINT, self._signal_handler)

        if args["verbose"]:
            loglevel = logging.DEBUG
        else:
            loglevel = logging.INFO

        # setting up logger
        self._logger = logging.getLogger("AppAware")
        self._logger.setLevel(loglevel)

        # TODO format based on verbose level
        # maybe use verbose formatter all the time for logfile
        # use DEBUG level all the time for logfile
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(threadName)s - %(levelname)s - %(message)s')

        # create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(loglevel)
        console_handler.setFormatter(formatter)
        self._logger.addHandler(console_handler)

        if args["debug_log"]:
            path = args["debug_log"]
            # assume a path is given if last char is /
            if path[-1] == '/':
                path = path + "%s.debug_log" % (client_class.__name__)
            file_handler = logging.FileHandler(path, mode='w')
            file_handler.setLevel(loglevel)
            file_handler.setFormatter(formatter)
            self._logger.addHandler(file_handler)

        if args["standalone"]:
            args["app_controller"] = "0.0.0.0"

        # filter all recognized args and drop all None args
        arg_list = ["client_id", "host_id", "client_type", "app_controller", "app_controller_port", "app_controller_log", "metric_log"]
        client_args = {k:args[k] for k in arg_list if k in args and args[k]}

        self._logger.debug("Starting %s with args %s" % (client_class.__name__, client_args))
        self._client = client_class(**client_args)

        if args["config"]:
            config_file = open(args["config"], 'r')
            config = json.load(config_file)
            self._logger.debug("Loading config %s" % config)
            self._client.set_config(config=config)

    def run(self):
        self._client.prepare()
        self._client.start()
        # wait for client to start up
        for i in range(10):
            if self._client.is_running():
                break
            time.sleep(1)
        # wait for client to stop running
        while self._client.is_running():
            time.sleep(1)
        self._client.join()
        self._client.clean_up()

    def _signal_handler(self, signal, frame):
        self._client.stop()