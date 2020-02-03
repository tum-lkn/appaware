import redis
import time
import json

from typing import List

from netstatspy.readers.tc import TcStatsReader


class SwitchStats(object):
    def __init__(self, host: str, port: int, interval: float, ifaces: List[str], channel="statistics.switch"):
        self._redis = redis.StrictRedis(host, port)
        self._interval = interval
        self._running = False
        self._channel = channel
        self._ifaces = ifaces
        TcStatsReader.compile_patterns()

    def run(self):
        self._running = True
        try:
            self._loop()
        except KeyboardInterrupt:
            print('\nStopping')
            self._running = False

    def _loop(self):
        next_time = time.perf_counter()
        while self._running:
            for iface in self._ifaces:
                data = TcStatsReader.get_interface_stats(iface)
                data['host_name'] = 'switch'
                self._redis.publish(self._channel, json.dumps(data))
            next_time += self._interval
            diff = next_time - time.perf_counter()
            if diff > 0:
                time.sleep(diff)


if __name__ == "__main__":
    stats = SwitchStats("10.0.8.0", 6379, 1, ['eth2', 'eth3'])
    stats.run()
