import os
import subprocess
import time

from .exceptions import InterfaceNotFoundError
from .abstract_readers import TcIpQueueLimitsStatsReader
from .utils.available_interfaces import AvailableInterfaces


class QueueLimitsStatsReader(TcIpQueueLimitsStatsReader):
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

    @classmethod
    def get_interface_stats(cls, interface_name: str) -> dict:
        if not cls._interface_exists(interface_name):
            raise InterfaceNotFoundError
        queues = cls._get_all_tx_queues(interface_name)
        queue_limits = {'interface_name': interface_name}
        for queue in queues:
            queue_limits[queue] = {'hold_time': cls._read_qlimit_file(interface_name, queue, 'hold_time'),
                                   'timestamp': time.time(),
                                   'inflight': cls._read_qlimit_file(interface_name, queue, 'inflight'),
                                   'limit': cls._read_qlimit_file(interface_name, queue, 'limit'),
                                   'limit_max': cls._read_qlimit_file(interface_name, queue, 'limit_max'),
                                   'limit_min': cls._read_qlimit_file(interface_name, queue, 'limit_min')}
        return queue_limits

    @classmethod
    def get_all_stats(cls) -> list:
        interfaces = AvailableInterfaces.get_interfaces()
        all_stats = []
        for interface in interfaces:
            all_stats.append(cls.get_interface_stats(interface))
        return all_stats

    @staticmethod
    def get_type():
        return "queue"
