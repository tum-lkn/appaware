import re
import subprocess
import time

from control.utils.iface_statistics.stats_reader import StatsReader


class SSStats(StatsReader):
    @staticmethod
    def _call_ss() -> str:
        cmd = ['ss', '-inm', '--tcp', '--udp', '-o', 'state', 'established']
        completed_process = subprocess.run(cmd, stdout=subprocess.PIPE)
        return completed_process.stdout.decode('UTF-8')

    @staticmethod
    def _split_output_in_connections(ss_output: str) -> list:
        pattern = re.compile(r'udp.+\n.+|tcp.+\n.+', re.MULTILINE)
        return re.findall(pattern, ss_output)

    @staticmethod
    def _precompile_patterns():
        return {'basics': re.compile(r'(?P<protocol>tcp|udp)\s+(?P<recv_q>\d+)\s+(?P<send_q>\d+)\s+'
                                     r'(?P<local_addr>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+|[\w:]+)\s+'
                                     r'(?P<peer_addr>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+|[\w:]+)'),
                'more':   re.compile(r'(?<=\s)(?P<name>([^:\s.]+|(?P<pacing_rate>pacing_rate)|(?P<send>send)))'
                                     r'(?(send) |(?(pacing_rate) |:))(?!Port)(?P<value>[^:\s]+)(?=\s|$)')}

    @staticmethod
    def _extract_more(more_pattern, ss_iface_stats: str) -> dict:
        more = re.finditer(more_pattern, ss_iface_stats)
        more_information = {}
        try:
            while True:
                match = next(more)
                more_information[match.group('name')] = match.group('value')
        except StopIteration:
            return more_information

    @staticmethod
    def _extract_basics(basics_pattern, ss_iface_stats: str) -> dict:
        basics = re.search(basics_pattern, ss_iface_stats)
        basics_information = {'protocol':   basics.group('protocol'),
                              'recv_q':     basics.group('recv_q'),
                              'send_q':     basics.group('send_q'),
                              'local_addr': basics.group('local_addr'),
                              'peer_addr':  basics.group('peer_addr'),}
        return basics_information

    @staticmethod
    def _extract_ts_sack_cubic(ss_iface_stats: str) -> dict:
        return {'ts': ' ts ' in ss_iface_stats,
                'sack': ' sack ' in ss_iface_stats,
                'cubic': ' cubic ' in ss_iface_stats}

    @staticmethod
    def get_stats(interface_name) -> list:
        connections = SSStats._split_output_in_connections(SSStats._call_ss())
        patterns = SSStats._precompile_patterns()
        parsed_connections = []
        time_stamp = time.time()
        for connection in connections:
            parsed_connection = {'timestamp': time_stamp}
            parsed_connection.update(SSStats._extract_basics(patterns['basics'], connection))
            parsed_connection.update(SSStats._extract_more(patterns['more'], connection))
            parsed_connection.update(SSStats._extract_ts_sack_cubic(connection))
            parsed_connections.append(parsed_connection)
        return parsed_connections

    @staticmethod
    def get_type():
        return "ss"
