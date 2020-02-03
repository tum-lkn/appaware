import re
import subprocess
import time

from .exceptions import InterfaceNotFoundError
from .abstract_readers import TcIpQueueLimitsStatsReader


class IpStatsReader(TcIpQueueLimitsStatsReader):
    _base_patterns = None
    _split_pattern = None
    _rx_pattern = None
    _tx_pattern = None

    @staticmethod
    def _call_ip() -> str:
        cmd = ['ip', '-s', 'link']
        completed_process = subprocess.run(cmd, stdout=subprocess.PIPE)
        return completed_process.stdout.decode('UTF-8')

    @classmethod
    def _split_output_in_interfaces(cls, tc_output: str) -> list:
        # split the output per interfaces
        splitted_interfaces = re.findall(cls._split_pattern, tc_output)
        return splitted_interfaces

    @classmethod
    def _extract_interface_rx(cls, interface_information: str) -> dict:
        match = re.search(cls._rx_pattern, interface_information)
        rx = {'bytes': int(match.group(1)),
              'packets': int(match.group(2)),
              'errors': int(match.group(3)),
              'dropped': int(match.group(4)),
              'overrun': int(match.group(5)),
              'mcast': int(match.group(6))}
        return rx

    @classmethod
    def _extract_interface_tx(cls, interface_information: str) -> dict:
        match = re.search(cls._tx_pattern, interface_information)
        rx = {'bytes': int(match.group(1)),
              'packets': int(match.group(2)),
              'errors': int(match.group(3)),
              'dropped': int(match.group(4)),
              'carrier': int(match.group(5)),
              'collisions': int(match.group(6))}
        return rx

    @staticmethod
    def _extract_base_information(interface_information: str, pattern):
        match = re.search(pattern, interface_information)
        return match.group(1)

    @classmethod
    def _create_interface_dict(cls, interface_information: str) -> dict:
        iface_dict = {'timestamp': time.time(),
                      'rx_statistics': IpStatsReader._extract_interface_rx(interface_information),
                      'tx_statistics': IpStatsReader._extract_interface_tx(interface_information)}
        for key, pattern in cls._base_patterns.items():
            iface_dict[key] = cls._extract_base_information(interface_information, pattern)
        return iface_dict

    @classmethod
    def _extract_interface_information_by_name(cls, interface_name: str, interface_info_list: list) -> str:
        for interface_information in interface_info_list:
            if cls._extract_base_information(interface_information, cls._base_patterns['name']) == interface_name:
                return interface_information
        raise InterfaceNotFoundError("Interface {} not found".format(interface_name))

    @classmethod
    def compile_regex(cls):
        """
        compile patterns for later use
        """
        if cls._base_patterns is not None:
            return
        cls._base_patterns = {'name': re.compile(r'[0-9]+: ([\w]+)@?\w*:'),
                              'mtu': re.compile(r' mtu (\w+) '),
                              'queueing': re.compile(r' qdisc (\w+) '),
                              'state': re.compile(r' state (\w+) '),
                              'mode': re.compile(r' mode (\w+) '),
                              'group': re.compile(r' group (\w+) '),
                              'qlen': re.compile(r' qlen (\w+)')}
        cls._split_pattern = re.compile(r'[0-9]*: \w+@?\w*: .*\n.*\n.*\n.*\n.*\n.*\n', re.MULTILINE)
        cls._rx_pattern = re.compile(r'RX:\sbytes\s+packets\s+errors\s+dropped\s+overrun\s+mcast\s+'
                                     r'([0-9]+)\s+([0-9]+)\s+([0-9]+)\s+([0-9]+)\s+([0-9]+)\s+([0-9]+)')
        cls._tx_pattern = re.compile(r'TX:\sbytes\s+packets\s+errors\s+dropped\s+carrier\s+collsns\s+'
                                     r'([0-9]+)\s+([0-9]+)\s+([0-9]+)\s+([0-9]+)\s+([0-9]+)\s+([0-9]+)')

    @classmethod
    def get_interface_stats(cls, interface_name: str) -> dict:
        if cls._base_patterns is None:
            cls.compile_regex()
        ifaces = IpStatsReader._call_ip()
        ifaces_list = IpStatsReader._split_output_in_interfaces(ifaces)
        interface_information = IpStatsReader._extract_interface_information_by_name(interface_name,
                                                                                     ifaces_list)
        return IpStatsReader._create_interface_dict(interface_information)

    @classmethod
    def get_all_stats(cls) -> list:
        if cls._base_patterns is None:
            cls.compile_regex()
        print(type(cls._base_patterns))
        ip_output = IpStatsReader._call_ip()
        ifaces_list = IpStatsReader._split_output_in_interfaces(ip_output)
        all_stats = []
        for iface in ifaces_list:
            all_stats.append(cls._create_interface_dict(iface))
        return all_stats

    @staticmethod
    def get_type():
        return "ip"
