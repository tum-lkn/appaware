#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import os
import time

from servers.PrototypeServer import PrototypeServer
from servers.utils import Nginx
from servers.utils import Process


class WebRTCServer(PrototypeServer.PrototypeServer):
    def __init__(self, **kwargs):
        super(WebRTCServer, self).__init__(**kwargs)
        self._logger.debug("WebRTCServer.__init__()")

        self._nginx = None
        self._node = None

        self._default_config = {
            "servers": [
                {
                    "port": 443,
                    "document_root": "%s" % os.path.join(os.path.dirname(os.path.abspath(__file__)), "www/"),
                    "ssl": True,
                    "websocket": [{"location": "/ws/", "proxy": "node"}]
                }
            ],
            "websockets": [
                {"name": "node", "url": "localhost", "port": 9090}
            ]
        }

    def prepare(self):
        self._logger.debug("WebRTCServer.prepare()")

    def run(self):
        self._logger.debug("WebRTCServer.run()")
        self._running = True

        if not self._nginx or not self._node:
            # no nginx or node running yet - load default config
            self._logger.info("No config applied yet - using default config")
            self.set_config(config={})

        self._logger.debug("Starting nginx")

        self._node.start(silent=False)
        self._nginx.start()

        self._next_call = time.time()
        while self._running:
            if time.time() < self._next_call:
                time.sleep(0.1)
            else:
                self._next_call += 5
                self._logger.debug("WebRTCServer running")

        self._nginx.stop()
        self._node.stop()

    def clean_up(self):
        self._logger.debug("WebRTCServer.clean_up()")
        self._nginx.clean_up()

    def _apply_config(self):
        self._logger.debug("WebServer._apply_config()")

        if not self._node:
            node_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "signaling/chat.js")
            cmd = "sudo nodejs %s" % (node_file)
            self._node = Process.Process(cmd=cmd)

        if not self._nginx:
            self._nginx = Nginx.Nginx()

        servers = self._config["servers"]
        websockets = self._config["websockets"]

        self._nginx.generate_config(servers=servers, websockets=websockets)

if __name__ == '__main__':

    from servers.StandaloneServer import StandaloneServer

    # start server
    server = StandaloneServer(server_class=WebRTCServer)
    server.run()
