import re
import subprocess
import time

from .exceptions import InterfaceNotFoundError
from control.utils.iface_statistics.stats_reader import StatsReader


class InterfaceStatisticsTc(StatsReader):
    @staticmethod
    def _call_tc() -> str:
        cmd = ['tc', '-s', 'qdisc']
        completed_process = subprocess.run(cmd, stdout=subprocess.PIPE)
        return completed_process.stdout.decode('UTF-8')

    @staticmethod
    def _split_output_in_interfaces(tc_output: str) -> list:
        # split the output per interfaces
        pattern1 = re.compile(r'qdisc.*\n.*\n.*\n', re.MULTILINE)
        splitted_interfaces = re.findall(pattern1, tc_output)
        return splitted_interfaces

    @staticmethod
    def _extract_interface_name(interface_information: str) -> str:
        pattern = re.compile(r'qdisc .*: dev (\w*) ')
        match = re.search(pattern, interface_information)
        return match.group(1)

    @staticmethod
    def _extract_interface_queuing(interface_information: str) -> str:
        pattern = re.compile(r'qdisc (\w*) [0-9]*: ')
        match = re.search(pattern, interface_information)
        return match.group(1)

    @staticmethod
    def _extract_interface_sent_statistics(interface_information: str) -> dict:
        pattern = re.compile(r'Sent ([0-9]*) bytes ([0-9]*) pkt \(dropped ([0-9]*), '
                             r'overlimits ([0-9]*) requeues ([0-9]*)\)')
        match = re.search(pattern, interface_information)
        statistics = {'bytes': int(match.group(1)),
                      'packets': int(match.group(2)),
                      'dropped': int(match.group(3)),
                      'overlimits': int(match.group(4)),
                      'requeues': int(match.group(5))}
        return statistics

    @staticmethod
    def _extract_interface_backlog(interface_information: str) -> dict:
        pattern = re.compile(r'backlog ([0-9]*)b ([0-9]*)p requeues ([0-9]*)')
        match = re.search(pattern, interface_information)
        backlog = {'bytes': int(match.group(1)),
                   'packets': int(match.group(2)),
                   'requeues': int(match.group(3))}
        return backlog

    @staticmethod
    def _extract_fq_information(interface_information: str) -> dict:
        pattern = re.compile(r'.*\srefcnt\s(\d*)\slimit\s(\d*p)\sflow_limit\s(\d*p)\sbuckets\s(\d*)\sorphan_mask\s'
                             r'(\d*)\squantum\s(\d*)\sinitial_quantum\s(\d*)\smaxrate\s(\d*\w*)\srefill_delay\s'
                             r'(\d*[.]\d*ms)')
        match = re.search(pattern, interface_information)
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
        iface_dict = {'name': cls._extract_interface_name(interface_information),
                      'timestamp': time.time(),
                      'queueing': cls._extract_interface_queuing(interface_information),
                      'sent_statistics': cls._extract_interface_sent_statistics(interface_information),
                      'backlog_statistics': cls._extract_interface_backlog(interface_information)}
        if iface_dict['queueing'] == 'cfq' or iface_dict['queueing'] == 'fq':
            iface_dict['cfq_stats'] = cls._extract_fq_information(interface_information)
        return iface_dict

    @classmethod
    def _extract_interface_information_by_name(cls, interface_name: str, interface_info_list: list) -> str:
        for interface_information in interface_info_list:
            if cls._extract_interface_name(interface_information) == interface_name:
                return interface_information
        raise InterfaceNotFoundError("Interface {} not found".format(interface_name))

    @classmethod
    def get_stats(cls, interface_name: str) -> list:
        ifaces = cls._call_tc()
        ifaces_list = cls._split_output_in_interfaces(ifaces)
        interface_information = cls._extract_interface_information_by_name(interface_name, ifaces_list)
        return [cls._create_interface_dict(interface_information)]

    @staticmethod
    def get_type():
        return "tc"
