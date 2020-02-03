import re
import subprocess
import time

from .exceptions import InterfaceNotFoundError
from .abstract_readers import TcIpQueueLimitsStatsReader


class TcStatsReader(TcIpQueueLimitsStatsReader):
    _split_pattern = None
    _base_patterns = None
    _sent_pattern = None
    _backlog_pattern = None
    _fq_pattern = None

    @staticmethod
    def _call_tc() -> str:
        cmd = ['tc', '-s', 'qdisc']
        completed_process = subprocess.run(cmd, stdout=subprocess.PIPE)
        return completed_process.stdout.decode('UTF-8')

    @classmethod
    def _split_output_in_interfaces(cls, tc_output: str) -> list:
        # split the output per interfaces
        splitted_interfaces = re.findall(cls._split_pattern, tc_output)
        return splitted_interfaces

    @classmethod
    def _extract_base_information(cls, interface_information: str, pattern):
        match = re.search(pattern, interface_information)
        return match.group(1)

    @classmethod
    def _extract_interface_sent_statistics(cls, interface_information: str) -> dict:
        match = re.search(cls._sent_pattern, interface_information)
        statistics = {'bytes': int(match.group(1)),
                      'packets': int(match.group(2)),
                      'dropped': int(match.group(3)),
                      'overlimits': int(match.group(4)),
                      'requeues': int(match.group(5))}
        return statistics

    @classmethod
    def _extract_interface_backlog(cls, interface_information: str) -> dict:
        match = re.search(cls._backlog_pattern, interface_information)
        backlog = {'bytes': int(match.group(1)),
                   'packets': int(match.group(2)),
                   'requeues': int(match.group(3))}
        return backlog

    @classmethod
    def _extract_fq_information(cls, interface_information: str) -> dict:
        match = re.search(cls._fq_pattern, interface_information)
        cfq = {'refcnt': match.group(1),
               'limit': match.group(2),
               'flow_limit': match.group(3),
               'buckets': match.group(4),
               'orphan_mask': match.group(5),
               'quantum': match.group(6),
               'initial_quantum': match.group(7),
               'maxrate': match.group(8),
               'refill_delay': match.group(9)}
        return cfq

    @classmethod
    def _create_interface_dict(cls, interface_information: str) -> dict:
        iface_dict = {'name': cls._extract_base_information(interface_information, cls._base_patterns['name']),
                      'timestamp': time.time(),
                      'queueing': cls._extract_base_information(interface_information, cls._base_patterns['queueing']),
                      'sent_statistics': cls._extract_interface_sent_statistics(interface_information),
                      'backlog_statistics': cls._extract_interface_backlog(interface_information)}
        if iface_dict['queueing'] == 'cfq' or iface_dict['queueing'] == 'fq':
            iface_dict['cfq_stats'] = cls._extract_fq_information(interface_information)
        return iface_dict

    @classmethod
    def _extract_interface_information_by_name(cls, interface_name: str, interface_info_list: list) -> str:
        for interface_information in interface_info_list:
            if cls._extract_base_information(interface_information, cls._base_patterns['name']) == interface_name:
                return interface_information
        raise InterfaceNotFoundError("Interface {} not found".format(interface_name))

    @classmethod
    def compile_patterns(cls):
        if cls._base_patterns is not None:
            return
        cls._split_pattern = re.compile(r'qdisc.*\n.*\n.*\n', re.MULTILINE)
        cls._base_patterns = {'name': re.compile(r'qdisc .*: dev (\w*) '),
                              'queueing': re.compile(r'qdisc (\w*) [0-9]*: ')}
        cls._sent_pattern = re.compile(r'Sent ([0-9]*) bytes ([0-9]*) pkt \(dropped ([0-9]*), '
                                       r'overlimits ([0-9]*) requeues ([0-9]*)\)')
        cls._backlog_pattern = re.compile(r'backlog ([0-9]*)b ([0-9]*)p requeues ([0-9]*)')
        cls._fq_pattern = re.compile(r'.*\srefcnt\s(\d*)\slimit\s(\d*p)\sflow_limit\s(\d*p)\sbuckets\s(\d*)\s'
                                     r'orphan_mask\s(\d*)\squantum\s(\d*)\sinitial_quantum\s(\d*)\smaxrate\s(\d*\w*)\s'
                                     r'refill_delay\s(\d*[.]\d*ms)')

    @classmethod
    def get_interface_stats(cls, interface_name: str) -> dict:
        if cls._base_patterns is None:
            cls.compile_patterns()
        ifaces = cls._call_tc()
        ifaces_list = cls._split_output_in_interfaces(ifaces)
        interface_information = cls._extract_interface_information_by_name(interface_name, ifaces_list)
        return cls._create_interface_dict(interface_information)

    @classmethod
    def get_all_stats(cls) -> list:
        if cls._base_patterns is None:
            cls.compile_patterns()
        tc_output = cls._call_tc()
        ifaces_list = cls._split_output_in_interfaces(tc_output)
        all_stats = []
        for iface in ifaces_list:
            all_stats.append(cls._create_interface_dict(iface))
        return all_stats

    @staticmethod
    def get_type():
        return "tc"
