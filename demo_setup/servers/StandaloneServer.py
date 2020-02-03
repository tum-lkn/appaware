#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import argparse
import json
import logging
import signal
import time


class StandaloneServer(object):
    def __init__(self, server_class):
        # parse args
        description = ("%s parameter" % (server_class.__name__))

        parser = argparse.ArgumentParser(description=description)

        parser.add_argument("-c", "--config", help="Client config file", dest="config")
        parser.add_argument("-d", "--debug-log", help="Log verbose output to file", nargs='?', dest="debug_log", action="store", const="./")
        parser.add_argument("-v", "--verbose", help="Verbose", dest="verbose", action="store_true")

        args = vars(parser.parse_args())

        # setting up CTRL+C handler
        signal.signal(signal.SIGINT, self._signal_handler)

        if args["verbose"]:
            loglevel = logging.DEBUG
        else:
            loglevel = logging.INFO

        # setting up logger
        self._logger = logging.getLogger("AppAware.Server")
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
                path = path + "%s.debug_log" % (server_class.__name__)
            file_handler = logging.FileHandler(path, mode='w')
            file_handler.setLevel(loglevel)
            file_handler.setFormatter(formatter)
            self._logger.addHandler(file_handler)

        # filter all recognized args and drop all None args
        arg_list = []
        server_args = {k:args[k] for k in arg_list if k in args and args[k]}

        self._logger.debug("Starting %s with args %s" % (server_class.__name__, server_args))
        self._server = server_class(**server_args)

        if args["config"]:
            config_file = open(args["config"], 'r')
            config = json.load(config_file)
            self._logger.debug("Loading config %s" % config)
            self._server.set_config(config=config)

    def run(self):
        self._server.prepare()
        self._server.start()
        # wait for server to start up
        for i in range(10):
            if self._server.is_running():
                break
            time.sleep(1)
        # wait for server to stop running
        while self._server.is_running():
            time.sleep(1)
        self._server.join()
        self._server.clean_up()

    def _signal_handler(self, signal, frame):
        self._server.stop()