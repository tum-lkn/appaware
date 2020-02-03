#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import logging
import threading
import time
import queue
import socket

from netstatspy.readers.ip import IpStatsReader

IFACE_STATS_MESSAGE_TYPE = 'iface_stats'


class InterfaceStats(threading.Thread):
    def __init__(self, iface, comm_queue=None, interval=1):
        super(InterfaceStats, self).__init__()

        self._logger = logging.getLogger("AppAware." + self.__class__.__name__)

        self._iface = iface
        self._interval = interval

        self._comm_queue = comm_queue

        self._running = False

        # precompile regex
        IpStatsReader.compile_regex()

    def run(self):
        self._logger.debug("InterfaceStats.run()")
        self._running = True

        next_call = time.perf_counter()
        while self._running:
            self._logger.debug("wrote interface stats")
            data = IpStatsReader.get_interface_stats(self._iface)
            data['host_name'] = socket.gethostname()

            msg = {'type': IFACE_STATS_MESSAGE_TYPE,
                   'data': data}

            if self._comm_queue is None:
                self._logger.error("No target msg queue available! Msg was: %s" )
            else:
                self._comm_queue.put(msg)

            next_call += self._interval
            time_diff = next_call - time.perf_counter()
            if time_diff >= 0:
                time.sleep(time_diff)

    def stop(self):
        self._logger.debug("InterfaceStats.stop()")
        self._running = False
        self.join()
