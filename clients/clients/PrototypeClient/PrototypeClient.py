#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import json
import logging
import numpy as np
import os
import requests
import threading
import time
import uuid
import random

from utils.interface_list import interface_list


class PrototypeClient(threading.Thread):
    def __init__(self, client_id=None,
                 host_id=None,
                 client_type=None,
                 app_controller="10.0.0.1",
                 app_controller_port=8080,
                 app_controller_log=None,
                 metric_log=None):
        super(PrototypeClient, self).__init__()

        # setup client specific logger
        self._logger = logging.getLogger("AppAware.Client." + self.__class__.__name__)
        self._logger.debug("PrototypeClient.__init__()")

        self._running = False
        self._default_config = {'request_mode': 'constant',
                                'request_interval': 0.1,
                                'random_wait_time': 0.0}
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

        if app_controller_log:
            if app_controller_log[-1] == '/':
                app_controller_log = os.path.join(self._log_dir, app_controller_log, "%s.app_controller_log" % (self.__class__.__name__))
            self._app_controller_log = open(app_controller_log, 'w')

        self._metric_log = None
        if metric_log:
            if metric_log[-1] == '/':
                metric_log = os.path.join(self._log_dir, metric_log, "%s.metric_log" % (self.__class__.__name__))
            self._metric_log = open(metric_log, 'w')

        self.setName("%s %s" % (self.__class__.__name__, self._client_id))

        self._next_request = time.time()

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
        self._logger.debug("PrototypeClient.set_config()")
        # if no config supplied only overwrite if no self._config already set
        if config or not self._config:
            self._config = self._default_config.copy()
            self._config.update(config)
        self._apply_config()

    # overwritten by individual client
    def _apply_config(self):
        self._logger.debug("PrototypeClient._apply_config()")
        pass

    def _app_controller_call(self, url, method="GET", payload=None, raw=False, ssl=False):
        self._logger.debug("PrototypeClient._app_controller_call()")

        proto = "https" if ssl else "http"

        url = "{}://{}:{}{}".format(proto, self._app_controller, self._app_controller_port, url)

        self._logger.debug("%s %s payload=%s" % (method, url, payload))

        if self._app_controller_log:
            log_msg = {"url": url, "method": method, "payload": payload, "raw": raw, "ssl": ssl}
            self._app_controller_log.write("%s\n" % (json.dumps(log_msg)))
            self._app_controller_log.flush()

        if self._app_controller == "0.0.0.0":
            self._logger.debug("Standalone mode - skipping app-controller call")
            return None

        try:
            if method == "GET":
                response = requests.get(url, params=payload, timeout=self._timeout)
            elif method == "POST":
                response = requests.post(url, json=payload, timeout=self._timeout)
            elif method == "PUT":
                response = requests.put(url, json=payload, timeout=self._timeout)
            else:
                self._logger.error("Unrecognized API call method %s" % (method))
                return None
        except Exception as e:
            self._logger.error("AppController call gone wrong '%s'" % (e))
            return None

        if response.ok:
            if raw:
                self._logger.debug("Call got response \"%s\"" % (response.text))
                return response.text
            else:
                self._logger.debug("Call got response \"%s\"" % (response.json()))
                return response.json()
        else:
            self._logger.error("API call delivered bad response")
            self._logger.debug(response.text)
            return None

    def _create_metric(self, metric):
        self._logger.debug("PrototypeClient._create_metric()")
        self._metric = {"timestamp": time.time(), "metric": metric}

    # used to report metric as json containing all captured data
    def _report_metric(self):
        self._logger.debug("PrototypeClient._report_metric()")

        if self._metric_log:
            self._metric_log.write("%s\n" % (json.dumps(self._metric)))
            self._metric_log.flush()

        msg = self._metric
        self._app_controller_call(url="/application/%s/status" % (self._client_id), method="PUT", payload=msg)

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

        self._logger.debug("PrototypeClient._next_request_ts()")

        # set if not already contained in config
        if self._config.get('inter_request_not_pause', False):
            self._config['inter_request_not_pause'] = True
        else:
            self._config['inter_request_not_pause'] = False

        if self._config['inter_request_not_pause']:
            self._logger.debug("Using old request timestamp as starting point")
            t_ref = self._next_request
            self._logger.debug("Using time.time() as starting point")
        else:
            t_ref = time.time()

        # Constant time between requests
        if self._config['request_mode'] == 'constant':
            req_ts = t_ref + self._config['request_interval']
        # Exponential distributed time between the requests
        elif self._config['request_mode'] == 'exponential':
            req_ts = t_ref + np.random.exponential(self._config['request_interval'])
        else:
            raise Exception("Unknown request mode %s" % self._config['request_mode'])

        self._logger.debug("next_request_ts(): mode: %s, interval: %.1f, rel_ts: %.3fs, inter_request_not_pause %s" %
                           (self._config['request_mode'], self._config['request_interval'], req_ts - time.time(), self._config['inter_request_not_pause']))

        return req_ts

    def register_application(self):
        self._logger.debug("PrototypeClient.register_application()")
        if not self._registered:
            msg = {"host": self._host_id,
                   "id": self._client_id,
                   "type": self._client_type,
                   "ifs": self._client_ifs}
            self._logger.info("register_application() - %s" % (msg))

            response = self._app_controller_call(url="/applications", method="POST", payload=msg)
            if response:
                self._registered = True

    def unregister_application(self):
        self._logger.debug("PrototypeClient.unregister_application()")
        if self._registered:
            msg = {"host": self._host_id, "id": self._client_id, "app_type": self._client_type}
            self._logger.info("unregister_application() - %s" % (msg))

            # Not implemented now by API
            #response = self._app_controller_call(url="/applications", method="POST", payload=msg)
            #if response:
            #    self._registered = False

            self._registered = False
