#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import logging
import os
import shlex
import subprocess


class TCPDump(object):
    def __init__(self, iface=None, truncate=None, out_path=None):
        self._logger = logging.getLogger("AppAware." + self.__class__.__name__)

        self._iface = iface
        self._truncate = truncate
        self._out_path = out_path

        self._process = None

    def start(self, optional_args=None, silent=True):
        self._logger.debug("TCPDump.start()")
        cmd = ["sudo tcpdump"]
        if self._iface:
            cmd += ["-i", self._iface]
        if self._truncate:
            cmd += ["-s", str(self._truncate)]
        if not self._out_path:
            self._out_path = "capture.pcap"

        if os.path.exists(self._out_path):
            self._logger.debug("out_file already exists - generating new name")
            name, suffix = self._out_path.rsplit('.', 1)
            i = 1
            while True:
                self._out_path = "%s_%s.%s" % (name, i, suffix)
                if not os.path.exists(self._out_path):
                    break
                i += 1

        cmd += ["-w", self._out_path]
        if optional_args != None:
            # convert string to list to handle strings and lists
            if type(optional_args) is str:
                optional_args = optional_args.split(' ')
            cmd += [optional_args]
        cmd = " ".join(cmd)
        cmd = shlex.split(cmd)

        args = {
            "preexec_fn": os.setsid
        }

        if silent:
            args["stdout"] = subprocess.PIPE
            args["stderr"] = subprocess.PIPE

        self._process = subprocess.Popen(cmd, **args)

    def stop(self):
        self._logger.debug("TCPDump.stop()")
        cmd = "sudo kill -SIGINT %s" % (self._process.pid)
        cmd = shlex.split(cmd)
        kill_process = subprocess.Popen(cmd)
        kill_process.wait()

