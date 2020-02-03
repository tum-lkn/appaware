#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import os
import shlex
import subprocess


class Process(object):
    def __init__(self, cmd):
        self._process = None
        self._cmd = cmd

    def start(self, silent=False):
        cmd = shlex.split(self._cmd)
        # Python 3.6
        # cmd = list(shlex.shlex(cmd, punctuation_chars=True))

        # to kill all nginx children
        # https://stackoverflow.com/questions/2638909/killing-a-subprocess-including-its-children-from-python

        args = {
            "preexec_fn": os.setsid
        }

        if silent:
            args["stdout"] = subprocess.PIPE
            args["stderr"] = subprocess.PIPE

        self._process = subprocess.Popen(cmd, **args)

    def stop(self):
        cmd = "sudo kill -SIGINT %s" % (self._process.pid)
        cmd = shlex.split(cmd)
        kill_process = subprocess.Popen(cmd)
        kill_process.wait()
