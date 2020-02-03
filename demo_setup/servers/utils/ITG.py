#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import os
import shlex
import subprocess


class ITG(object):
    def __init__(self, cmd):
        self._process = None
        self._cmd = cmd

    def start(self, silent=False):

        cmd = shlex.split(self._cmd)

        args = {}

        if silent:
            args["stdout"] = subprocess.PIPE
            args["stderr"] = subprocess.PIPE

        self._process = subprocess.Popen(cmd, **args)

    def stop(self):

        self._process.terminate()
        self._process.wait()

    def wait(self):
        self._process.wait()

        #cmd = "sudo kill -SIGINT %s" % (self._process.pid)
        #cmd = shlex.split(cmd)
        #kill_process = subprocess.Popen(cmd)
        #kill_process.wait()
