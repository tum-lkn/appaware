#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import json
import logging
import numpy as np
import os
import threading
import time
import uuid
import redis

from utils.interface_list import interface_list


class PrototypeClient(threading.Thread):
    def __init__(self, client_id=None,
                 host_id=None,
                 client_type=None,
                 app_controller="10.0.0.1",
                 app_controller_port=8080,
                 app_controller_log=None,
                 redis_ip="10.0.8.0",
                 redis_port=6379,
                 redis_channel='statistics.client',
                 metric_log=None):
        super(PrototypeClient, self).__init__()

        # setup client specific logger
        self._logger = logging.getLogger("AppAware.Client." + self.__class__.__name__)
        self._logger.debug("PrototypeClient.__init__()")

        self._running = False
        self._default_config = {}
        self._config = None

        self._registered = False

        self._metric = "{}"

        self._timeout = 2

        if client_id:
            self._client_id = client_id
        else:
            self._client_id = str(uuid.uuid4())[:8]

        self._client_ifs = [dict(i._asdict()) for i in interface_list(external=True, ip=True)]

        if host_id:
            self._host_id = host_id
        else:
            self._host_id = self._client_ifs[0]['ip']

        if client_type:
            self._client_type = client_type
        else:
            self._client_type = self.__class__.__name__

        # create and change working dir
        folder = "%s_%s" % (self.__class__.__name__, self._client_id)
        self._log_dir = os.path.join(os.getcwd(), folder)

        # create dir if not exists
        if not os.path.exists(self._log_dir):
            os.makedirs(self._log_dir)

        self._app_controller = app_controller
        self._app_controller_port = app_controller_port
        self._app_controller_log = None

        self._redis_channel = redis_channel

        self._redis = redis.StrictRedis(redis_ip, redis_port)

        if app_controller_log:
            if app_controller_log[-1] == '/':
                app_controller_log = os.path.join(self._log_dir, app_controller_log, "%s.app_controller_log" %
                                                  self.__class__.__name__)
            self._app_controller_log = open(app_controller_log, 'w')

        self._metric_log = None
        if metric_log:
            if metric_log[-1] == '/':
                metric_log = os.path.join(self._log_dir, metric_log, "%s.metric_log" % self.__class__.__name__)
            self._metric_log = open(metric_log, 'w')

        self.setName("%s %s" % (self.__class__.__name__, self._client_id))

    def prepare(self):
        self._logger.debug("PrototypeClient.prepare()")
        pass

    def run(self):
        self._logger.debug("PrototypeClient.run()")
        self._running = True
        while self._running:
            self._logger.info("PrototypeClient running")
            time.sleep(1)

    def stop(self):
        self._logger.debug("PrototypeClient.stop()")
        self._running = False

    def clean_up(self):
        self._logger.debug("PrototypeClient.clean_up()")
        pass

    def is_running(self):
        return self._running

    def set_config(self, config):
        self._logger.debug("PrototypeClient.set_config(): %s" % config)
        # if no config supplied only overwrite if no self._config already set
        if config or not self._config:
            self._config = self._default_config.copy()
            self._config.update(config)
        self._apply_config()

    # overwritten by individual client
    def _apply_config(self):
        self._logger.debug("PrototypeClient._apply_config()")
        pass

    def _create_metric(self, metric):
        self._logger.debug("PrototypeClient._create_metric()")
        self._metric = {"timestamp": time.time(), "metric": metric, 'client_id': self._client_id,
                        'host_id': self._host_id, 'client_type': self._client_type}

    # used to report metric as json containing all captured data
    def _report_metric(self):
        self._logger.debug("PrototypeClient._report_metric()")

        if self._metric_log:
            self._metric_log.write("%s\n" % (json.dumps(self._metric)))
            self._metric_log.flush()

        msg = json.dumps(self._metric)
        self._logger.debug("Publishing data '{}' to redis channel '{}'".format(msg, self._redis_channel))
        self._redis.publish(self._redis_channel, msg)

    def _time_step(self, time_constant):
        self._logger.debug("PrototypeClient._time_step()")
        increment = np.random.exponential(time_constant)
        return increment

    def register_application(self):
        self._logger.debug("PrototypeClient.register_application()")
        if not self._registered:
            self._registered = True

    def unregister_application(self):
        self._logger.debug("PrototypeClient.unregister_application()")
        if self._registered:
            msg = {"host": self._host_id, "id": self._client_id, "app_type": self._client_type}
            self._logger.info("unregister_application() - %s" % msg)

            self._registered = False
