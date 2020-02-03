import threading
import time
import csv
import queue
from typing import Union

from .ip import InterfaceStatisticsIp
from .queue_limits import QueueLimits
from .ss import SSStats
from .tc import InterfaceStatisticsTc


class CSVWriter(threading.Thread):
    def __init__(self, write_frequency: int, file_name: str, status_queue: Union[queue.Queue, None]):
        threading.Thread.__init__(self)
        self._sleep_time = CSVWriter._calc_sleep_time(write_frequency)
        self._file_name = file_name
        self._running = False
        self._last_sleep_end = 0

        if status_queue is None:
            self._enqueue = False
        else:
            self._enqueue = True
            self._queue = status_queue

    @staticmethod
    def _calc_sleep_time(frequency: int) -> float:
        return 1 / frequency

    def _get_stats(self) -> list:
        raise NotImplementedError

    def _get_field_names(self) -> list:
        raise NotImplementedError

    @staticmethod
    def _information_source_command() -> str:
        """
         Should return the command executed to get the information written to the csv file.
        """
        raise NotImplementedError

    def _sleep(self):
        time_to_sleep = self._sleep_time - (time.perf_counter() - self._last_sleep_end)
        try:
            time.sleep(time_to_sleep)
        except ValueError:
            # maybe some error message?
            pass
        self._last_sleep_end = time.perf_counter()

    def stop(self):
        self._running = False

    def run(self):
        self._running = True
        with open(self._file_name, mode='w', newline='') as csv_file:
            writer = csv.DictWriter(csv_file, self._get_field_names())
            writer.writeheader()
            self._last_sleep_end = time.perf_counter()
            while self._running:
                for stat in self._get_stats():
                    writer.writerow(stat)
                    if self._enqueue:
                        self._queue.put((self._information_source_command(), stat))
                self._sleep()


class IpCSVWriter(CSVWriter):
    def __init__(self, write_frequency: int, file_name: str, interface_name: str,
                 status_queue: Union[queue.Queue, None]):
        CSVWriter.__init__(self, write_frequency, file_name, status_queue)
        self._interface_name = interface_name

    def _get_field_names(self) -> list:
        return list(InterfaceStatisticsIp.get_interface_statistics(self._interface_name).keys())

    def _get_stats(self) -> list:
        return [InterfaceStatisticsIp.get_interface_statistics(self._interface_name)]

    @staticmethod
    def _information_source_command() -> str:
        return 'ip'


class QueueCSVWriter(CSVWriter):
    def __init__(self, write_frequency: int, file_name: str, interface_name: str,
                 status_queue: Union[queue.Queue, None]):
        CSVWriter.__init__(self, write_frequency, file_name, status_queue)
        self._interface_name = interface_name

    def _get_field_names(self) -> list:
        return list(QueueLimits.get_queue_limits(self._interface_name).keys())

    def _get_stats(self) -> list:
        return [QueueLimits.get_queue_limits(self._interface_name)]

    @staticmethod
    def _information_source_command() -> str:
        return 'queue'


class SSCSVWriter(CSVWriter):
    def _get_field_names(self):
        stats = SSStats.get_ss_stats()
        longest = None
        longest_length = 0
        for stat in stats:
            length = len(stat)
            if length > longest_length:
                longest_length = length
                longest = stat
        return list(longest.keys())

    def _get_stats(self):
        return SSStats.get_ss_stats()

    @staticmethod
    def _information_source_command() -> str:
        return 'ss'


class TcCSVWriter(CSVWriter):
    def __init__(self, write_frequency: int, file_name: str, interface_name: str,
                 status_queue: Union[queue.Queue, None]):
        CSVWriter.__init__(self, write_frequency, file_name, status_queue)
        self._interface_name = interface_name

    def _get_field_names(self) -> list:
        return list(InterfaceStatisticsTc.get_interface_statistics(self._interface_name).keys())

    def _get_stats(self) -> list:
        return [InterfaceStatisticsTc.get_interface_statistics(self._interface_name)]

    @staticmethod
    def _information_source_command() -> str:
        return 'tc'
