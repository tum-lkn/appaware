#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import os
import time

from servers.PrototypeServer import PrototypeServer
from servers.utils.ITG import ITG


class VoIPServer(PrototypeServer.PrototypeServer):

    def __init__(self, **kwargs):
        super(VoIPServer, self).__init__(**kwargs)
        self._logger.debug("VoIPServer.__init__()")

        self._default_config.update({
            "client_ip": "127.0.0.1",
            "call_duration": 30,
            "codec": "G.729.2"
        })

        self._itgsend = None

    def prepare(self):
        self._logger.debug("VoIPServer.prepare()")

    def run(self):
        self._logger.debug("VoIPServer.run()")
        self._running = True

        if not self._config:
            self._logger.info("No config applied yet - using default config")
            self.set_config()

        self._random_wait_start()

        args = {'duration': self._config['call_duration'] * 1000,
                'client_ip': self._config['client_ip'],
                'codec': self._config['codec']}

        call_cnt = 0

        while self._running:
            if not self._do_request():
                time.sleep(0.1)
            else:
                self._logger.debug("VoIPServer running")

                call_cnt += 1

                args['rcv_file'] = "call_%d.bin" % int((time.time() - 1523017559) * 10)

                cmd = "ITGSend -a {client_ip} -t {duration} -m rttm -x {rcv_file} VoIP -x {codec}".format(**args)

                self._itgsend = ITG(cmd)

                self._itgsend.start()
                self._itgsend.wait()

                self._request_finished()

    def clean_up(self):
        self._logger.debug("VoIPServer.clean_up()")
        self._itgsend.stop()

    def _apply_config(self):
        self._logger.debug("VoIPServer._apply_config()")

if __name__ == '__main__':

    from servers.StandaloneServer import StandaloneServer

    # start server
    server = StandaloneServer(server_class=VoIPServer)
    server.run()
