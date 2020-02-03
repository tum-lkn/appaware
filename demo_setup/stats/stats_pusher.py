"""
# Init
influx = InfluxDBClient(cmdargs.influxdb_ip, cmdargs.influxdb_port, database="appaware")
influx.create_database('appaware')

# Subscribe and read a message
r = redis.StrictRedis(host=cmdargs.redis, port=cmdargs.port, db=0)
p = r.pubsub(ignore_subscribe_messages=True)
p.subscribe(cmdargs.channels)
message = p.get_message()
measurements = json.loads(message['data'])

# Create data points array and fill it
data = []
for .. in ..:
    data.append({
                 "measurement": 'eth.rx',
                 "tags": {'host': "appaware1",
                           'dev': "eth1",
                 "time": int(time.time() * 1000), # use here the timestamp of the measurement in ms
                 "fields": {'bytes': 1203123,
                          'packets': 5343}
               })

# Write all to database
influx.write_points(data, time_precision="ms")
"""

import redis
import argparse
import logging
import influxdb
import json

from typing import List


log = logging.getLogger(__name__)


class InfluxPusher(object):
    def __init__(self, ip, port, database='appaware'):
        self._influx = influxdb.InfluxDBClient(ip, port, database=database)
        self._influx.create_database(database)

    def push(self, data: list):
        self._influx.write_points(data, time_precision="ms")


class StatsReader(object):
    @classmethod
    def read(cls, stats) -> list:
        raise NotImplementedError


class IPStatsReader(StatsReader):
    """
    sample output:

    {"stats": {"name": "wlo1", "timestamp": 153408.542992316, "mtu": "1500", "queueing": "mq", "state": "UP",
    "mode": "DORMANT", "group": "default", "qlen": "1000",
    "rx_statistics":
    {"bytes": "5157286463", "packets": "4914085", "errors": "0", "dropped:": "0", "overrun": "0", "mcast": "0"},
    "tx_statistics":
    {"bytes": "234914902", "packets": "1260850", "errors": "0", "dropped:": "0", "carrier": "0", "collisions": "0"}},
    "type": "ip"}
    """
    @classmethod
    def read(cls, stats: dict) -> list:
        """
        "rx_statistics": {"bytes": "5157286463", "packets": "4914085", "errors": "0", "dropped:": "0", "overrun": "0",
                          "mcast": "0"}
        """
        data = [cls._read_rx(stats['rx_statistics'], stats['host_name'], stats['timestamp'], stats['name']),
                cls._read_tx(stats['tx_statistics'], stats['host_name'], stats['timestamp'], stats['name'])]

        return data

    @staticmethod
    def _read_rx(rx_stats: dict, host_name: str, time_stamp: float, interface_name: str) -> dict:
        """
        format of rx_stats:

        {"bytes": "5157286463", "packets": "4914085", "errors": "0", "dropped:": "0", "overrun": "0",
         "mcast": "0"}
        """
        return {"measurement": 'ip.rx',
                "tags": {'host': host_name,
                         'dev': interface_name,
                         'host_dev': "{}:{}".format(host_name, interface_name)},
                "time": int(time_stamp * 1000),
                "fields": {'bytes': rx_stats['bytes'],
                           'packets': rx_stats['packets'],
                           'errors': rx_stats['errors'],
                           'dropped': rx_stats['dropped'],
                           'overrun': rx_stats['overrun'],
                           'mcast': rx_stats['mcast']}}

    @staticmethod
    def _read_tx(tx_stats: dict, host_name: str, time_stamp: float, interface_name: str) -> dict:
        return {"measurement": 'ip.tx',
                "tags": {'host': host_name,
                         'dev': interface_name,
                         'host_dev': "{}:{}".format(host_name, interface_name)},
                "time": int(time_stamp * 1000),
                "fields": {'bytes': tx_stats['bytes'],
                           'packets': tx_stats['packets'],
                           'errors': tx_stats['errors'],
                           'dropped': tx_stats['dropped'],
                           'overrun': tx_stats['carrier'],
                           'collisions': tx_stats['collisions']}}


class TCStatsReader(StatsReader):
    """
    sample output:

    {"name": "wlo1", "timestamp": 153408.704362032, "queueing": "mq", "sent_statistics":
    {"bytes": "199661964", "packets": "1260861", "dropped": "0", "overlimits": "0", "requeues": "48"},
    "backlog_statistics": {"bytes": "0", "packets": "0", "requeues": "48"}}
    """
    @classmethod
    def read(cls, stats: dict) -> list:
        data = [cls._read_sent(stats['sent_statistics'], stats['host_name'], stats['timestamp'], stats['name']),
                cls._read_backlog(stats['backlog_statistics'], stats['host_name'], stats['timestamp'], stats['name'])]
        return data

    @staticmethod
    def _read_sent(sent_stats: dict, host_name: str, time_stamp: float, interface_name: str) -> dict:
        return {"measurement": 'tc.sent',
                "tags": {'host': host_name,
                         'dev': interface_name},
                "time": int(time_stamp * 1000),
                "fields": {'bytes': sent_stats['bytes'],
                           'packets': sent_stats['packets'],
                           'dropped': sent_stats['dropped'],
                           'overlimits': sent_stats['overlimits'],
                           'requeues': sent_stats['requeues']}}

    @staticmethod
    def _read_backlog(backlog_stats: dict, host_name: str, time_stamp: float, interface_name: str) -> dict:
        return {"measurement": 'tc.backlog',
                "tags": {'host': host_name,
                         'dev': interface_name},
                "time": int(time_stamp * 1000),
                "fields": {'bytes': backlog_stats['bytes'],
                           'packets': backlog_stats['packets'],
                           'requeues': backlog_stats['requeues']}}


class ClientReader(StatsReader):
    """
    example output:
    {'timestamp': 1534285034.5283153, 'host_id': '192.168.1.1', 'client_id': 'fd110be1', 'client_type': 'WebDLClient',
    'metric': {'timing': 0.8974659442901611, 'content_length': 10485760, 'url': 'http://192.168.5.1/10M.bin'}}
    """
    @classmethod
    def read(cls, stats):
        pc_host = 'pc{}host{}'.format(stats["host_id"].split('.')[2], stats["host_id"].split('.')[3])
        return [{"measurement": 'client',
                 "tags": {'pc_host': pc_host},
                 "time": int(stats['timestamp'] * 1000),
                 "fields": {'app_id': stats['client_id'],
                            'app_type': stats['client_type'],
                            'raw_application_metric': float(stats['metric']['raw_application_metric'])}}]

class RTTReader(StatsReader):
    """
    example output:
    {"host": "192.168.5.0", "timestamp": 1536834208.8756206, "rtt": 0.005765438079833984}
    """
    @classmethod
    def read(cls, stats):
        return [{'measurement': 'rtt',
                 'tags': {'host': stats['host']},
                 "time": int(stats['timestamp'] * 1000),
                 "fields": {'rtt': float(stats['rtt'])}}]


class StatsPusher(object):
    def __init__(self, influx_ip: str, influx_port: int, redis_ip: str, redis_port: int,
                 channels: List[str]):
        self._redis = redis.StrictRedis(host=redis_ip, port=redis_port, db=0)
        self._influx = InfluxPusher(influx_ip, influx_port)
        self._channels = channels
        self._running = False

    def run(self):
        self._running = True
        p = self._redis.pubsub(ignore_subscribe_messages=True)
        p.subscribe(self._channels)
        while self._running:
            message = p.get_message(timeout=0.5)
            if message:
                log.debug("Got message from channel {} with length of {} bytes".format(message['channel'].decode(),
                                                                                       len(message['data'])))
                if message['channel'].decode() == 'statistics.switch':
                    self._influx.push(TCStatsReader.read(json.loads(message['data'].decode())))
                elif message['channel'].decode() == 'statistics.iface':
                    self._influx.push(IPStatsReader.read(json.loads(message['data'].decode())))
                elif message['channel'].decode() == 'statistics.client':
                    data = ClientReader.read(json.loads(message['data'].decode()))
                    self._influx.push(data)
                    log.debug("Pushed: {}".format(data))
                elif  message['channel'].decode() == 'statistics.rtt':
                    self._influx.push(RTTReader.read(json.loads(message['data'].decode())))

    def stop(self):
        self._running = False


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="StatusPusher")
    parser.add_argument('-v', '--verbose', help="Enable debug log.", dest='verbose', action='store_true')

    parser.add_argument('--influxdb-ip', help="IP of the InfluxDB instance. (default %(default)s)",
                        default="127.0.0.1")
    parser.add_argument('--influxdb-port', help="Port of the InfluxDB instance. (default %(default)d)",
                        default=8086, type=int)
    parser.add_argument('--redis-ip', help="IP of the redis instance. (default %(default)s)",
                        default="127.0.0.1")
    parser.add_argument('--redis-port', help="Port of the redis instance. (default %(default)d)",
                        default=6379, type=int)

    args = parser.parse_args()

    logconf = {'format': '[%(asctime)s.%(msecs)-3d: %(name)-16s - %(levelname)-5s] %(message)s', 'datefmt': "%H:%M:%S"}

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG, **logconf)
    else:
        logging.basicConfig(level=logging.INFO, **logconf)

    pusher = StatsPusher(args.influxdb_ip, args.influxdb_port, args.redis_ip, args.redis_port, ['statistics.switch',
                                                                                                'statistics.client',
                                                                                                'statistics.iface',
                                                                                                'statistics.rtt'])
    try:
        pusher.run()
    except KeyboardInterrupt:
        pusher.stop()
