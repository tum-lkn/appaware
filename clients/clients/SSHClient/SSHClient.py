#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import os
import random
import time
import paramiko

from clients.PrototypeClient import PrototypeClient


class SSHClient(PrototypeClient.PrototypeClient):
    def __init__(self, **kwargs):
        super(SSHClient, self).__init__(**kwargs)
        self._logger.debug("SSHClient.__init__()")

        self._default_config.update({
            "ssh_args": {
                "hostname": "localhost",
                "port": 22,
                "username": "vagrant",
                "password": "vagrant"
            },
            "cmd_pool": [
                "ls -la",
                "date",
                "uptime"
            ]
        })

        self._connected = False
        self._connection = None

    def prepare(self):
        self._logger.debug("SSHClient.prepare()")
        self.register_application()
        pass

    def run(self):
        self._logger.debug("SSHClient.run()")
        self._running = True

        if not self._connection:
            # not connected yet - load default config
            self._logger.info("No config applied yet - using default config")
            self.set_config(config={})

        self._random_wait_start()

        while self._running:
            if not self._do_request():
                time.sleep(0.1)
            else:
                self._logger.debug("SSHClient running")

                cmd_pool = self._config["cmd_pool"]
                cmd = cmd_pool[random.randint(0, len(cmd_pool) - 1)]
                stdout, stderr = self.run_command(cmd=cmd)
                self._logger.debug("stdout: %s" % (stdout))
                self._logger.debug("stderr: %s" % (stderr))
                self._report_metric()

                self._request_finished()

    def clean_up(self):
        self._logger.debug("SSHClient.clean_up()")
        self.unregister_application()
        self._disconnect()

    def run_command(self, cmd):
        self._logger.debug("SSHClient.run_command()")
        if self._connected:
            # assign cmd_stop also because a connection to e.g. localhost is too fast so stdout.channel.exit_status_ready() is already True for fast commands
            self._logger.debug("Running command \"%s\"" % (cmd))
            cmd_start = time.time()
            stdin, stdout, stderr = self._connection.exec_command(cmd)
            # blocking wait method stdout.channel.recv_exit_status() and stderr.channel.recv_exit_status() would be a shorter solution but not recommendet
            # http://docs.paramiko.org/en/2.2/api/channel.html#paramiko.channel.Channel.recv_exit_status
            if stdout.channel.exit_status_ready() and stderr.channel.exit_status_ready():
                # exec_command was somehow blocking and cmd already finished
                cmd_stop = time.time()
            else:
                # wait until cmd finished
                while not (stdout.channel.exit_status_ready() and stderr.channel.exit_status_ready()):
                    time.sleep(0.01)
                cmd_stop = time.time()
            self._create_metric(metric={"cmd": cmd, "cmd_time": cmd_stop - cmd_start})
            return stdout.read(), stderr.read()
        else:
            self._logger.warn("Not connected - returning None, None")
            self._create_metric(metric={"cmd": cmd, "cmd_time": -1})
            return None, None

    def _apply_config(self):
        self._logger.debug("SSHClient._apply_config()")
        self._connect()

    # TODO catch exceptions from connect()
    # unknown host
    # timeout
    # etc
    def _connect(self):
        self._logger.debug("SSHClient._connect()")
        if self._connection is not None:
            self._disconnect()
        # only try to connect if client is running to avoid blocking daemons application statup
        while self._running:
            try:
                args = self._config["ssh_args"]
                self._connection = paramiko.SSHClient()
                self._connection.load_system_host_keys()
                self._connection.set_missing_host_key_policy(paramiko.WarningPolicy())
                self._connection.connect(**args)
                self._connected = True
                self._logger.debug("Connected")
                break
            except paramiko.ssh_exception.AuthenticationException:
                self._logger.error("Auth error")
            except Exception as e:
                self._logger.error("Error: %s, %s" % (e.errno, e.strerror))
            self._connection = None
            self._connected = False

    def _disconnect(self):
        self._logger.debug("SSHClient._disconnect()")
        self._connected = False
        if self._connection:
            self._connection.close()
            self._connection = None


# use StandaloneClient to keep argparsing stuff central for every client
if __name__ == '__main__':

    from clients.StandaloneClient import StandaloneClient

    # start client
    client = StandaloneClient.StandaloneClient(client_class=SSHClient)
    client.run()
