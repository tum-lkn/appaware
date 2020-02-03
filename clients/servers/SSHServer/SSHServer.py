#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import time

from servers.PrototypeServer import PrototypeServer
from servers.utils import Process


class SSHServer(PrototypeServer.PrototypeServer):
    def __init__(self, **kwargs):
        super(SSHServer, self).__init__(**kwargs)
        self._logger.debug("SSHServer.__init__()")

        self._sshd = None

        self._default_config.update({
            "port": 22
        })

    def prepare(self):
        self._logger.debug("SSHServer.prepare()")

    def run(self):
        self._logger.debug("SSHServer.run()")
        self._running = True

        if not self._sshd:
            # no nginx running yet - load default config
            self._logger.info("No config applied yet - using default config")
            self.set_config(config={})

        self._logger.debug("Starting sshd")
        self._sshd.start()

        self._next_call = time.time()
        while self._running:
            if time.time() < self._next_call:
                time.sleep(0.1)
            else:
                self._next_call += 5
                self._logger.debug("SSHServer running")

        self._sshd.stop()

    def clean_up(self):
        self._logger.debug("SSHServer.clean_up()")

    def _apply_config(self):
        self._logger.debug("SSHServer._apply_config()")

        # ToDo use config port

        if not self._sshd:
            port = self._config["port"]
            cmd = "sudo /usr/sbin/sshd -D -o UseDNS=no -u0 -p %s" % (port)
            self._sshd = Process.Process(cmd=cmd)


if __name__ == '__main__':

    from servers.StandaloneServer import StandaloneServer

    # start server
    server = StandaloneServer(server_class=SSHServer)
    server.run()
