import redis
import json
import subprocess


class SimpleRTT(object):
    def __init__(self, duration, frequency, host, port):
        self._running = False

    def run(self):
        self._running = True

        while self._running:
            pass

    def end(self):
        pass
