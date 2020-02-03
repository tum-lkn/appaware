import re
import subprocess
import time

from .exceptions import InterfaceNotFoundError
from control.utils.iface_statistics.stats_reader import StatsReader


class InterfaceStatisticsIp(StatsReader):
    @staticmethod
    def _call_ip() -> str:
        cmd = ['ip', '-s', 'link']
        completed_process = subprocess.run(cmd, stdout=subprocess.PIPE)
        return completed_process.stdout.decode('UTF-8')

    @staticmethod
    def _split_output_in_interfaces(tc_output: str) -> list:
        # split the output per interfaces
        pattern1 = re.compile(r'[0-9]*: \w*: .*\n.*\n.*\n.*\n.*\n.*\n', re.MULTILINE)
        splitted_interfaces = re.findall(pattern1, tc_output)
        return splitted_interfaces

    @staticmethod
    def _extract_interface_name(interface_information: str) -> str:
        pattern = re.compile(r'[0-9]+: (\w+):')
        match = re.search(pattern, interface_information)
        return match.group(1)

    @staticmethod
    def _extract_interface_mtu(interface_information: str) -> str:
        pattern = re.compile(r' mtu (\w+) ')
        match = re.search(pattern, interface_information)
        return match.group(1)

    @staticmethod
    def _extract_interface_queueing(interface_information: str) -> str:
        pattern = re.compile(r' qdisc (\w+) ')
        match = re.search(pattern, interface_information)
        return match.group(1)

    @staticmethod
    def _extract_interface_state(interface_information: str) -> str:
        pattern = re.compile(r' state (\w+) ')
        match = re.search(pattern, interface_information)
        return match.group(1)

    @staticmethod
    def _extract_interface_mode(interface_information: str) -> str:
        pattern = re.compile(r' mode (\w+) ')
        match = re.search(pattern, interface_information)
        return match.group(1)

    @staticmethod
    def _extract_interface_group(interface_information: str) -> str:
        pattern = re.compile(r' group (\w+) ')
        match = re.search(pattern, interface_information)
        return match.group(1)

    @staticmethod
    def _extract_interface_qlen(interface_information: str) -> str:
        pattern = re.compile(r' qlen (\w+)')
        match = re.search(pattern, interface_information)
        return match.group(1)

    @staticmethod
    def _extract_interface_rx(interface_information: str) -> dict:
        pattern = re.compile(r'RX:\sbytes\s+packets\s+errors\s+dropped\s+overrun\s+mcast\s+'
                             r'([0-9]+)\s+([0-9]+)\s+([0-9]+)\s+([0-9]+)\s+([0-9]+)\s+([0-9]+)')
        match = re.search(pattern, interface_information)
        rx = {'bytes': int(match.group(1)),
              'packets': int(match.group(2)),
              'errors': int(match.group(3)),
              'dropped': int(match.group(4)),
              'overrun': int(match.group(5)),
              'mcast': int(match.group(6))}
        return rx

    @staticmethod
    def _extract_interface_tx(interface_information: str) -> dict:
        pattern = re.compile(r'TX:\sbytes\s+packets\s+errors\s+dropped\s+carrier\s+collsns\s+'
                             r'([0-9]+)\s+([0-9]+)\s+([0-9]+)\s+([0-9]+)\s+([0-9]+)\s+([0-9]+)')
        match = re.search(pattern, interface_information)
        rx = {'bytes': int(match.group(1)),
              'packets': int(match.group(2)),
              'errors': int(match.group(3)),
              'dropped': int(match.group(4)),
              'carrier': int(match.group(5)),
              'collisions': int(match.group(6))}
        return rx

    @staticmethod
    def _create_interface_dict(interface_information: str) -> dict:
        iface_dict = {'name': InterfaceStatisticsIp._extract_interface_name(interface_information),
                      'timestamp': time.time(),
                      'mtu': InterfaceStatisticsIp._extract_interface_mtu(interface_information),
                      'queueing': InterfaceStatisticsIp._extract_interface_queueing(interface_information),
                      'state': InterfaceStatisticsIp._extract_interface_state(interface_information),
                      'mode': InterfaceStatisticsIp._extract_interface_mode(interface_information),
                      'group': InterfaceStatisticsIp._extract_interface_group(interface_information),
                      'qlen': InterfaceStatisticsIp._extract_interface_qlen(interface_information),
                      'rx_statistics': InterfaceStatisticsIp._extract_interface_rx(interface_information),
                      'tx_statistics': InterfaceStatisticsIp._extract_interface_tx(interface_information)}
        return iface_dict

    @staticmethod
    def _extract_interface_information_by_name(interface_name: str, interface_info_list: list) -> str:
        for interface_information in interface_info_list:
            if InterfaceStatisticsIp._extract_interface_name(interface_information) == interface_name:
                return interface_information
        raise InterfaceNotFoundError("Interface {} not found".format(interface_name))

    @staticmethod
    def get_stats(interface_name: str) -> list:
        ifaces = InterfaceStatisticsIp._call_ip()
        ifaces_list = InterfaceStatisticsIp._split_output_in_interfaces(ifaces)
        interface_information = InterfaceStatisticsIp._extract_interface_information_by_name(interface_name,
                                                                                             ifaces_list)
        return [InterfaceStatisticsIp._create_interface_dict(interface_information)]

    @staticmethod
    def get_type():
        return "ip"
