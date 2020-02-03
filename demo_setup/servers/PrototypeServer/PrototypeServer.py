#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import logging
import threading
import time
import numpy as np
import random


class PrototypeServer(threading.Thread):
    def __init__(self):
        super(PrototypeServer, self).__init__()

        # setup client specific logger
        self._logger = logging.getLogger("AppAware.Server." + self.__class__.__name__)
        self._logger.debug("PrototypeServer.__init__()")

        self._running = False
        self._default_config = {'request_mode': 'constant',
                                'request_interval': 0.1,
                                'random_wait_time': 0.0}
        self._config = None

        self.setName("%s" % (self.__class__.__name__))

        self._next_request = time.time()

    def prepare(self):
        self._logger.debug("PrototypeServer.prepare()")
        pass

    def run(self):
        self._logger.debug("PrototypeServer.run()")
        self._running = True
        while self._running:
            self._logger.info("PrototypeServer running")
            time.sleep(1)

    def stop(self):
        self._logger.debug("PrototypeServer.stop()")
        self._running = False

    def clean_up(self):
        self._logger.debug("PrototypeServer.clean_up()")
        pass

    def is_running(self):
        return self._running

    def set_config(self, config={}):
        self._logger.debug("PrototypeServer.set_config()")
        self._config = self._default_config.copy()
        self._config.update(config)
        self._apply_config()

    # overwritten by individual client
    def _apply_config(self):
        self._logger.debug("PrototypeServer._apply_config()")
        pass

    def _random_wait_start(self):
        """
        If configured, randomly wait up to one minute. Is called before the first request.

        :return:
        """

        # wait random amount of time to break synchron client behavior
        wait_until = time.time() + random.randint(0, self._config['random_wait_time'])
        while time.time() < wait_until and self._running:
            self._logger.debug("Waiting %.1fs to start first request" % (wait_until - time.time()))
            time.sleep(1)

    def _do_request(self):
        """
        Returns true of the client should do a new request.

        :return:
        """

        if time.time() < self._next_request:
            return False
        else:
            return True

    def _request_finished(self):
        """
        Call when client request is finished.

        :return:
        """

        self._next_request = self._next_request_ts()

        self._logger.debug("next call at %s" % (time.strftime("%H:%M:%S", time.localtime(self._next_request))))

    def _next_request_ts(self):
        """
        Returns the timestamp when to schedule the next request.
        :return:
        """

        self._logger.debug("PrototypeServer._next_request_ts()")

        # Constant time between requests
        if self._config['request_mode'] == 'constant':
            self._logger.debug("next_request_ts(): using constant method")
            req_ts = time.time() + self._config['request_interval']
        # Exponential distributed time between the requests
        elif self._config['request_mode'] == 'exponential':
            self._logger.debug("next_request_ts(): using exponential method")
            req_ts = time.time() + np.random.exponential(self._config['request_interval'])
        else:
            raise Exception("Unknown request mode %s" % self._config['request_mode'])

        self._logger.debug("next_request_ts(): mode: %s, interval: %.1f, rel_ts: %.3fs" %
                           (self._config['request_mode'], self._config['request_interval'], req_ts - time.time()))

        return req_ts