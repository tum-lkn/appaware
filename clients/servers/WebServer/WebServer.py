#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import json
import os
import tempfile
import time

from servers.PrototypeServer import PrototypeServer
from servers.utils import Nginx
from servers.WebServer.TemplateConverter import TemplateConverter


class WebServer(PrototypeServer.PrototypeServer):
    def __init__(self, **kwargs):
        super(WebServer, self).__init__(**kwargs)
        self._logger.debug("WebServer.__init__()")

        self._nginx = None
        self._tempdir = None

        self._default_config.update({
            "servers": [
                {"port": 80, "document_root": "/var/www/", "ssl": False, "websocket": None}
            ],
            "websockets": [],
            "convert": None
        })

    def prepare(self):
        self._logger.debug("WebServer.prepare()")

    def run(self):
        self._logger.debug("WebServer.run()")
        self._running = True

        if not self._nginx:
            # no nginx running yet - load default config
            self._logger.info("No config applied yet - using default config")
            self.set_config(config={})

        self._logger.debug("Starting nginx")
        self._nginx.start()

        self._next_call = time.time()
        while self._running:
            if time.time() < self._next_call:
                time.sleep(0.1)
            else:
                self._next_call += 5
                self._logger.debug("WebServer running")

        self._nginx.stop()

    def clean_up(self):
        self._logger.debug("WebServer.clean_up()")
        self._nginx.clean_up()
        if self._tempdir:
            self._tempdir.cleanup()

    def _apply_config(self):
        self._logger.debug("WebServer._apply_config()")

        if not self._nginx:
            self._nginx = Nginx.Nginx()

        servers = self._config["servers"]
        websockets = self._config["websockets"]

        # convert template to temp path if convert is set
        if self._config["convert"]:
            self._logger.debug("converting document root")

            # create tempdir
            self._tempdir = tempfile.TemporaryDirectory()
            os.chmod(self._tempdir.name, 0o777)

            # save converter config
            config_file_path = os.path.join(self._tempdir.name, "convert.json")
            config_file = open(config_file_path, 'w')
            json.dump(self._config["convert"], config_file)
            config_file.close()

            # convert
            document_root = servers[0]["document_root"]
            template_converter = TemplateConverter.TemplateConverter(input_dir=document_root, output_dir=self._tempdir.name, config_file=config_file_path, force=True)
            template_converter.run()

            # replace document root in every server
            for server in servers:
                server["document_root"] = self._tempdir.name

        self._nginx.generate_config(servers=servers, websockets=websockets)

if __name__ == '__main__':

    from servers.StandaloneServer import StandaloneServer

    # start server
    server = StandaloneServer(server_class=WebServer)
    server.run()
