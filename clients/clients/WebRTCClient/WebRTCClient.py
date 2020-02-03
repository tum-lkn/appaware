#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import os
from selenium import webdriver
import time

from clients.PrototypeClient import PrototypeClient


class WebRTCClient(PrototypeClient.PrototypeClient):
    def __init__(self, **kwargs):
        super(WebRTCClient, self).__init__(**kwargs)
        self._logger.debug("WebRTCClient.__init__()")

        self._browser = None

        self._default_config = {
            "url": "https://192.168.10.21/chat.html",
            "username": "Testuser",
            "callee": None,
            "request_interval": 5
        }

        self._next_call = time.time()

    def prepare(self):
        self._logger.debug("WebRTCClient.prepare()")
        self.register_application()

    def run(self):
        self._logger.debug("WebRTCClient.run()")
        self._running = True

        if not self._browser:
            # no browser opened yet - load default config
            self._logger.info("No config applied yet - using default config")
            self.set_config(config={})

        # request page
        self._browser.get(self._config["url"])

        # wait for socket to become ready
        while self._running:
            appStatus = self._browser.execute_script("return getAppStatus();")
            self._logger.debug(appStatus)
            if appStatus.get("socket", "") == "ready":
                break
            else:
                self._logger.debug("waiting for socket to become ready")
                time.sleep(0.5)

        # enter username and login
        usernameInput = self._browser.find_element_by_id("usernameInput")
        usernameInput.clear()
        usernameInput.send_keys(self._config["username"])

        loginBtn = self._browser.find_element_by_id("loginBtn")
        loginBtn.click()

        # wait till callee is ready or getting called
        callee = self._config.get("callee", None)
        if callee:
            userAvailable = False
            self._logger.debug("waiting for callee %s to get ready" % (callee))
            while self._running:
                # send request
                self._logger.debug("sending request")
                self._browser.execute_script("userAvailableRequest('%s');" % (callee))
                # polling response
                while self._running:
                    userAvailable = self._browser.execute_script("return getUserAvailableResponse();")
                    self._logger.debug("polling response")
                    if userAvailable != None:
                        self._logger.debug("response: %s" %(userAvailable))
                        break
                    elif userAvailable:
                        time.sleep(0.1)

                if userAvailable:
                    break
                else:
                    time.sleep(1)

            # enter callee name
            calleeNameInput = self._browser.find_element_by_id("calleeNameInput")
            calleeNameInput.clear()
            calleeNameInput.send_keys(callee)
            # call
            callBtn = self._browser.find_element_by_id("callBtn")
            callBtn.click()
        else:
            self._logger.debug("no callee set - waiting to get called")
            # polling appStatus until "call active"
            while self._running:
                appStatus = self._browser.execute_script("return getAppStatus();")
                self._logger.debug("current appStatus: %s" % (appStatus))
                if appStatus.get("app", "") == "call active":
                    self._logger.debug("got call from %s" % (appStatus["remoteUsername"]))
                    break
                else:
                    time.sleep(5)

        self._next_call = time.time()
        while self._running:
            if time.time() < self._next_call:
                time.sleep(0.1)
            else:
                self._logger.debug("WebRTCClient running")
                self._next_call += self._config["request_interval"]

                self._logger.debug("requesting RTCStats")
                self._browser.execute_script("requestRTCStats();")

                # we have time to wait for response - if not there collect at next call
                time.sleep(0.5)

                # collect stats
                rtcStats = self._browser.execute_script("return getRTCStats();")
                self._logger.debug("received rtcStats %s" % (rtcStats))

                appStatus = self._browser.execute_script("return getAppStatus();")
                self._logger.debug("received appStatus %s" % (appStatus))

                metric = {"appStatus": appStatus, "rtcStats": rtcStats}
                self._create_metric(metric=metric)
                self._report_metric()

        # hang up
        hangUpBtn = self._browser.find_element_by_id("hangUpBtn")
        hangUpBtn.click()

        # TODO
        # investigate stop call before hangup

    def clean_up(self):
        self._logger.debug("WebRTCClient.clean_up()")
        self.unregister_application()
        if self._browser:
            # TODO investigate difference between close() and quit() when dealing with multiple browser windows
            self._browser.quit()

    def _apply_config(self):
        self._logger.debug("WebRTCClient._apply_config()")

        if not self._browser:
            firefox_options = webdriver.firefox.options.Options()
            firefox_options.add_argument("--private-window")
            firefox_options.add_argument("--headless")

            firefox_profile = webdriver.FirefoxProfile()
            firefox_profile.set_preference("media.navigator.permission.disabled", True)
            firefox_profile.set_preference("media.navigator.streams.fake", True)

            log_path = os.path.join(self._log_dir, "geckodriver.log")

            self._browser = webdriver.Firefox(firefox_profile=firefox_profile, firefox_options=firefox_options, log_path=log_path)


if __name__ == '__main__':

    from clients.StandaloneClient import StandaloneClient

    # start client
    client = StandaloneClient.StandaloneClient(client_class=WebRTCClient)
    client.run()
