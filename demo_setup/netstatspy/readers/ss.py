import re
import subprocess
import time

from .abstract_readers import StatsReader


class SSStatsReader(StatsReader):
    _compiled = False
    _split_pattern = None
    _base_pattern = None
    _more_pattern = None

    @staticmethod
    def _call_ss() -> str:
        cmd = ['ss', '-inm', '--tcp', '--udp', '-o', 'state', 'established']
        completed_process = subprocess.run(cmd, stdout=subprocess.PIPE)
        return completed_process.stdout.decode('UTF-8')

    @classmethod
    def _split_output_in_connections(cls, ss_output: str) -> list:
        return re.findall(cls._split_pattern, ss_output)

    @classmethod
    def _compile_patterns(cls):
        if cls._compiled:
            return
        cls._compiled = True

        cls._split_pattern = re.compile(r'udp.+\n.+|tcp.+\n.+', re.MULTILINE)
        cls._base_pattern = re.compile(r'(?P<protocol>tcp|udp)\s+(?P<recv_q>\d+)\s+(?P<send_q>\d+)\s+'
                                       r'(?P<local_addr>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+|[\w:]+)\s+'
                                       r'(?P<peer_addr>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+|[\w:]+)'),
        cls._more_pattern = re.compile(r'(?<=\s)(?P<name>([^:\s.]+|(?P<pacing_rate>pacing_rate)|(?P<send>send)))'
                                       r'(?(send) |(?(pacing_rate) |:))(?!Port)(?P<value>[^:\s]+)(?=\s|$)')

    @classmethod
    def _extract_more(cls, ss_iface_stats: str) -> dict:
        more = re.finditer(cls._more_pattern, ss_iface_stats)
        more_information = {}
        try:
            while True:
                match = next(more)
                more_information[match.group('name')] = match.group('value')
        except StopIteration:
            return more_information

    @classmethod
    def _extract_basics(cls, ss_iface_stats: str) -> dict:
        basics = re.search(cls._base_pattern, ss_iface_stats)
        basics_information = {'protocol':   basics.group('protocol'),
                              'recv_q':     basics.group('recv_q'),
                              'send_q':     basics.group('send_q'),
                              'local_addr': basics.group('local_addr'),
                              'peer_addr':  basics.group('peer_addr')}
        return basics_information

    @staticmethod
    def _extract_ts_sack_cubic(ss_iface_stats: str) -> dict:
        return {'ts': ' ts ' in ss_iface_stats,
                'sack': ' sack ' in ss_iface_stats,
                'cubic': ' cubic ' in ss_iface_stats}

    @classmethod
    def get_all_stats(cls) -> list:
        if not cls._compiled:
            cls._compile_patterns()
        connections = cls._split_output_in_connections(cls._call_ss())
        parsed_connections = []
        time_stamp = time.time()
        for connection in connections:
            parsed_connection = {'timestamp': time_stamp}
            parsed_connection.update(cls._extract_basics(connection))
            parsed_connection.update(cls._extract_more(connection))
            parsed_connection.update(cls._extract_ts_sack_cubic(connection))
            parsed_connections.append(parsed_connection)
        return parsed_connections

    @staticmethod
    def get_type():
        return "ss"
