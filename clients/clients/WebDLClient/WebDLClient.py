#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import random
import requests
import time

from clients.PrototypeClient import PrototypeClient


class WebDLClient(PrototypeClient.PrototypeClient):
    def __init__(self, **kwargs):
        super(WebDLClient, self).__init__(**kwargs)
        self._logger.debug("WebDLClient.__init__()")

        self._default_config.update({
            "url_pool": [
                "http://ipv4.download.thinkbroadband.com/5MB.zip",
                "http://ipv4.download.thinkbroadband.com/10MB.zip"
            ]
        })

        self._next_call = time.time()

    def prepare(self):
        self._logger.debug("WebDLClient.prepare()")
        self.register_application()

    def run(self):
        self._logger.debug("WebDLClient.run()")
        self._running = True

        if not self._config:
            # no browser opened yet - load default config
            self._logger.info("No config applied yet - using default config")
            self.set_config(config={})

        self._random_wait_start()

        while self._running:
            if not self._do_request():
                time.sleep(0.1)
            else:
                self._logger.debug("WebDLClient running")

                # get next url
                url_pool = self._config["url_pool"]
                url = url_pool[random.randint(0, len(url_pool) - 1)]

                # check url http/https otherwise add
                if not (url.startswith("http://") or url.startswith("https://")):
                    url = "http://" + url

                self.download_url(url=url)
                self._report_metric()

                self._request_finished()

    def clean_up(self):
        self._logger.debug("WebDLClient.clean_up()")
        self.unregister_application()

    def download_url(self, url):
        self._logger.debug("WebDLClient.download_url()")

        try:
            start = time.time()
            response = requests.get(url)
            stop = time.time()

            if response.ok:
                content_length = int(response.headers.get("Content-length", -1))
                timing = stop - start
            else:
                content_length = -1
                timing = -1

            metric = {"timing": timing, "url": url, "content_length" : content_length}
            self._create_metric(metric=metric)
        except Exception as e:
            content_length = -1
            timing = -1

            metric = {"timing": timing, "url": url, "content_length" : content_length}
            self._create_metric(metric=metric)

            self._logger.error(e)

            # if server refuses connection wait a bit and don't spam with requests
            if type(e) is requests.exceptions.ConnectionError:
                self._logger.debug("Connection refused - sleeping")
                time.sleep(0.5)


if __name__ == '__main__':

    from clients.StandaloneClient import StandaloneClient

    # start client
    client = StandaloneClient.StandaloneClient(client_class=WebDLClient)
    client.run()
