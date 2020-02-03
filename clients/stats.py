import argparse
import time
import logging

from control.utils.iface_statistics.ip import InterfaceStatisticsIp
from control.utils.iface_statistics.tc import InterfaceStatisticsTc
from control.utils.iface_statistics.ss import SSStats
from control.utils.iface_statistics.queue_limits import QueueLimits

from control.utils.iface_statistics.json_writer import JsonWriter

from control.utils.iface_statistics.redis_pusher import RedisPusher

log = logging.getLogger(__name__)


def run(host_name: str, write: bool, file_name: bool, redis: bool, ip: bool, queue_limits: bool, ss: bool, tc: bool, frequency: int,
        interface_name: str, redis_ip: str, redis_port: int) -> None:
    readers = []
    writer = None
    pusher = None

    if ip:
        readers.append(InterfaceStatisticsIp)
    if queue_limits:
        readers.append(QueueLimits)
    if ss:
        readers.append(SSStats)
    if tc:
        readers.append(InterfaceStatisticsTc)

    if len(readers) < 1:
        log.error("No statistics to parse.")
        return

    if redis:
        pusher = RedisPusher(redis_ip, redis_port)

    if write:
        writer = JsonWriter(file_name)
        writer.open()

    try:
        while True:

            time_stamp = time.perf_counter()
            for reader in readers:
                stats = reader.get_stats(interface_name)
                stat_type = reader.get_type()
                for stat in stats:
                    if write:
                        writer.write({'stats': stat,
                                      'type': stat_type})
                    stat['host_name'] = host_name
                    if redis:
                        pusher.publish(stat, stat_type)
            sleep_time = 1 / frequency - (time.perf_counter() - time_stamp)
            if sleep_time > 0:
                time.sleep(sleep_time)
    except KeyboardInterrupt:
        if write:
            writer.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="StatusPusher")
    parser.add_argument('host_name', help="Name of the host stats.py is running on")

    parser.add_argument('-v', '--verbose', help="Enable debug log.", dest='verbose', action='store_true')

    parser.add_argument('iface', help='Interface to monitor')
    parser.add_argument('-f', '--frequency', help='Number of samples per second. (default %(default)s)', default=1,
                        type=float, dest='frequency')
    parser.add_argument('--write', help='Write statistics to file', action='store_true'),
    parser.add_argument('--redis', help='Enable redis', action='store_true'),
    parser.add_argument('--ip', help='Parse ip output', action='store_true'),
    parser.add_argument('--tc', help='Parse tc output', action='store_true'),
    parser.add_argument('--ss', help='Parse ss output', action='store_true'),
    parser.add_argument('--queue-limits', help='Parse queue limits', action='store_true'),
    parser.add_argument('--file-name', help='Name of output file. (default \'%(default)s\')', default='stats.txt'),
    parser.add_argument('--redis-ip', help="IP of the redis instance. (default %(default)s)",
                        default="192.168.10.11")
    parser.add_argument('--redis-port', help="Port of the redis instance. (default %(default)d)",
                        default=6379, type=int)

    args = parser.parse_args()

    logconf = {'format': '[%(asctime)s.%(msecs)-3d: %(name)-16s - %(levelname)-5s] %(message)s', 'datefmt': "%H:%M:%S"}

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG, **logconf)
    else:
        logging.basicConfig(level=logging.INFO, **logconf)

    run(args.host_name, args.write, args.file_name, args.redis, args.ip, args.queue_limits, args.ss, args.tc, args.frequency,
        args.iface, args.redis_ip, args.redis_port)
