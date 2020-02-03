#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import http.client
import os
import random
import shutil
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
import time

from clients.PrototypeClient import PrototypeClient


class WebClient(PrototypeClient.PrototypeClient):
    def __init__(self, **kwargs):
        super(WebClient, self).__init__(**kwargs)
        self._logger.debug("WebClient.__init__()")

        self._browser = None

        self._default_config.update({
            "webdriver": "Firefox",
            "url_pool": [
                "https://google.de",
                "https://de.wikipedia.org/wiki/Wikipedia:Hauptseite",
                "https://heise.de"
            ]
        })

    def prepare(self):
        self._logger.debug("WebClient.prepare()")
        self.register_application()

    def run(self):
        self._logger.debug("WebClient.run()")
        self._running = True

        if not self._browser:
            # no browser opened yet - load default config
            self._logger.info("No config applied yet - using default config")
            self.set_config(config={})

        self._random_wait_start()

        while self._running:
            if not self._do_request():
                time.sleep(0.1)
            else:
                self._logger.debug("WebClient running")

                # get next url
                url_pool = self._config["url_pool"]
                url = url_pool[random.randint(0, len(url_pool) - 1)]

                # check url http/https otherwise add
                if not (url.startswith("http://") or url.startswith("https://")):
                    url = "http://" + url

                # try except because ctrl+c in the right moment raises this exception - make sure it isn't raised unter other conditions
                try:
                    # call a new site or do some interaction
                    self.load_url(url=url)
                    self._report_metric()
                except http.client.RemoteDisconnected as e:
                    self._logger.warn("Caught Exception http.client.RemoteDisconnected: %s" % (e))
                except Exception as e:
                    self._logger.error("Browser get() exception %s" % (e))

                self._request_finished()

    def clean_up(self):
        self._logger.debug("WebClient.clean_up()")
        self.unregister_application()
        if self._browser:
            # TODO investigate difference between close() and quit() when dealing with multiple browser windows
            self._browser.quit()

    def _apply_config(self):
        self._logger.debug("WebClient._apply_config()")

        if not self._browser:
            if self._config["webdriver"] == "Chrome":
                chrome_options = webdriver.ChromeOptions()
                # chrome_options.add_argument("--incognito")
                self._browser = webdriver.Chrome(chrome_options=chrome_options)
            elif self._config["webdriver"] == "Firefox":
                firefox_options = webdriver.firefox.options.Options()
                firefox_options.add_argument("--private-window")
                firefox_options.add_argument("--headless")

                firefox_profile = webdriver.FirefoxProfile()
                firefox_profile.set_preference("browser.cache.disk.enable", False)
                firefox_profile.set_preference("browser.cache.memory.enable", False)
                firefox_profile.set_preference("browser.cache.offline.enable", False)
                firefox_profile.set_preference("network.http.use-cache", False)
                firefox_profile.set_preference("media.gmp-provider.enabled", False)  # Disable Cisco OpenH264 codec download

                # add extension manually because selenium can't handle the new extension format
                xpi_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "extensions/firefox/cache_cleanup/cache_cleanup-1.0-an+fx.xpi")
                addon_id = "{27cf6b57-3c62-4ce1-89bd-2ea90d9d7457}"
                extensions_path = os.path.join(firefox_profile.profile_dir, "extensions")
                addon_path = os.path.join(extensions_path, addon_id + ".xpi")
                if not os.path.exists(extensions_path):
                    os.makedirs(extensions_path)
                shutil.copy(xpi_path, addon_path)

                log_path = os.path.join(self._log_dir, "geckodriver.log")

                self._browser = webdriver.Firefox(firefox_profile=firefox_profile, firefox_options=firefox_options, log_path=log_path)
            elif self._config["webdriver"] == "PhantomJS":
                self._browser = webdriver.PhantomJS()
            else:
                self._logger.error("Unrecognized webdriver %s" % (self._config["webdriver"]))
                pass

        # TODO
        # check if config specifies a other browser and change to specified

    def load_url(self, url):
        self._logger.debug("WebClient.load_url()")
        if self._browser:
            self._logger.debug("getting %s" % (url))

            # if CTRL+C was pressed get() raises "BadStatusLine: ''" exception while kill -SIGINT is ok
            try:
                self._browser.get(url)
            except Exception as e:
                raise e

            self.calculate_web_metric()

    def calculate_web_metric(self):
        self._logger.debug("WebClient.calculate_web_metric()")
        metric = {"timing": self.get_timing(), "url": self._browser.current_url}
        self._create_metric(metric=metric)

    def get_timing(self):
        self._logger.debug("WebClient.get_timing()")
        timing = self._browser.execute_script("return performance.timing;")
        # delete method
        if "toJSON" in timing:
            del(timing["toJSON"])
        # convert timings
        # TODO fallback if navigationStart key isn't there
        ref = timing["navigationStart"]
        for key in timing:
            if timing[key] != 0:
                timing[key] -= ref

        try:
            navigation_timing = self._browser.execute_script("return performance.getEntriesByType('navigation');")
            resource_timing = self._browser.execute_script("return performance.getEntriesByType('resource');")
        except WebDriverException as e:
            navigation_timing = []
            resource_timing = []

        for entry in navigation_timing + resource_timing:
            if "toJSON" in entry:
                del(entry["toJSON"])

        return {"timing": timing, "navigation_timing": navigation_timing, "resource_timing": resource_timing}

    # TODO
    # add interaction methods like clicking and text entering


if __name__ == '__main__':

    from clients.StandaloneClient import StandaloneClient

    # start client
    client = StandaloneClient.StandaloneClient(client_class=WebClient)
    client.run()
