import os.path
import subprocess
import time

from .exceptions import InterfaceNotFoundError
from control.utils.iface_statistics.stats_reader import StatsReader


class QueueLimits(StatsReader):
    @staticmethod
    def _interface_exists(interface_name: str) -> bool:
        return os.path.exists('/sys/class/net/{}'.format(interface_name))

    @staticmethod
    def _get_all_tx_queues(interface_name: str) -> list:
        path = '/sys/class/net/{}/queues/'.format(interface_name)
        queues = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d)) and 'tx' in d]
        return queues

    @staticmethod
    def _read_qlimit_file(interface_name: str, queue_name: str, file_name: str) -> int:
        cmd = ['cat', '/sys/class/net/{}/queues/{}/byte_queue_limits/{}'.format(interface_name, queue_name, file_name)]
        completed_process = subprocess.run(cmd, stdout=subprocess.PIPE)
        return int(completed_process.stdout.decode('UTF-8'))

    @staticmethod
    def get_stats(interface_name: str) -> list:
        if not QueueLimits._interface_exists(interface_name):
            raise InterfaceNotFoundError
        queues = QueueLimits._get_all_tx_queues(interface_name)
        queue_limits = {}
        for queue in queues:
            queue_limits[queue] = {'hold_time': QueueLimits._read_qlimit_file(interface_name, queue, 'hold_time'),
                                   'timestamp': time.time(),
                                   'inflight': QueueLimits._read_qlimit_file(interface_name, queue, 'inflight'),
                                   'limit': QueueLimits._read_qlimit_file(interface_name, queue, 'limit'),
                                   'limit_max': QueueLimits._read_qlimit_file(interface_name, queue, 'limit_max'),
                                   'limit_min': QueueLimits._read_qlimit_file(interface_name, queue, 'limit_min')}
        return [queue_limits]

    @staticmethod
    def get_type():
        return "queue"
