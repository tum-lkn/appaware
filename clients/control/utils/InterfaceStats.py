#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import json
import logging
import os
import threading
import time


class InterfaceStats(threading.Thread):
    def __init__(self, iface, out_path=None, interval=1):
        super(InterfaceStats, self).__init__()

        self._logger = logging.getLogger("AppAware." + self.__class__.__name__)

        self._iface = iface
        self._out_path = out_path
        self._interval = interval

        self._running = False

    def run(self):
        self._logger.debug("InterfaceStats.run()")
        self._running = True

        if not self._out_path:
            self._out_path = "%s.iface_stats" % (self._iface)

        if os.path.exists(self._out_path):
            self._logger.debug("out_file already exists - generating new name")
            name, suffix = self._out_path.rsplit('.', 1)
            i = 1
            while True:
                self._out_path = "%s_%s.%s" % (name, i, suffix)
                if not os.path.exists(self._out_path):
                    break
                i += 1

        # open statistics files
        statistics_path = "/sys/class/net/%s/statistics" % (self._iface)
        stat_files = []
        if not os.path.isdir(statistics_path):
            self._logger.error("no interface named '%s' or no statistics directory '%s' found" % (self._iface, statistics_path))
            return
        for file_name in os.listdir(statistics_path):
            file_path = os.path.join(statistics_path, file_name)
            if os.path.isfile(file_path):
                fd = open(file_path, 'r')
                stat_files.append((file_name, fd))

        out_file = open(self._out_path, 'w')

        next_call = time.time()
        while self._running:
            data = {"timestamp": time.time()}
            for file_name, fd in stat_files:
                fd.seek(0)
                value = int(fd.read().strip())
                data[file_name] = value

            out_file.write(json.dumps(data) + '\n')
            out_file.flush()
            self._logger.debug("wrote interface stats")

            next_call += self._interval
            time_diff = next_call - time.time()
            if time_diff >= 0:
                time.sleep(time_diff)

        out_file.close()
        for file_name, fd in stat_files:
            fd.close()

    def stop(self):
        self._logger.debug("InterfaceStats.stop()")
        self._running = False
        self.join()
