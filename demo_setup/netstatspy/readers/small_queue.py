import time

from .abstract_readers import StatsReader


class SmallQueueStatsReader(StatsReader):
    @staticmethod
    def _read_small_queue_value():
        with open('/proc/sys/net/ipv4/tcp_limit_output_bytes', 'r') as f:
            value = int(f.read()[:-1])
        return value

    @classmethod
    def get_all_stats(cls):
        return [{'value': cls._read_small_queue_value(),
                 'timestamp': time.time()}]

    @staticmethod
    def get_type():
        return "small_queue"
