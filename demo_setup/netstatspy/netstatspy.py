import argparse
import time
import logging

from readers.ip import IpStatsReader
from readers.tc import TcStatsReader
from readers.queue_limits import QueueLimitsStatsReader
from readers.small_queue import SmallQueueStatsReader
from readers.ss import SSStatsReader

from loggers.console_logger import ConsoleLogger
from loggers.json_logger import JsonLogger


log = logging.getLogger(__name__)


def run(console: bool, json: bool, json_filename: str, ip: bool, queue_limits: bool, ss: bool, tc: bool,
        small_queue: bool, frequency: int, interface_name: str, run_time: float) -> None:
    readers = []
    loggers = []
    if ip:
        readers.append(IpStatsReader)
    if queue_limits:
        readers.append(QueueLimitsStatsReader)
    if ss:
        readers.append(SSStatsReader)
    if tc:
        readers.append(TcStatsReader)
    if small_queue:
        readers.append(SmallQueueStatsReader)

    if len(readers) < 1:
        log.error("No statistics to parse.")
        return

    if console:
        loggers.append(ConsoleLogger())
    if json:
        loggers.append(JsonLogger(json_filename))

    for logger in loggers:
        logger.open()

    start_time = time.perf_counter()
    end_time = start_time + run_time
    runs = 0
    try:
        while True:
            if time.perf_counter() >= end_time:
                log.info("Finished after {} secs. And {} runs".format(run_time, runs))
                return
            time_stamp = time.perf_counter()
            for reader in readers:
                stat_type = reader.get_type()
                if interface_name is None:
                    for logger in loggers:
                        logger.log_multiple(reader.get_all_stats(), stat_type)
                else:
                    if (stat_type == 'ss') or (stat_type == 'small_queue'):
                        for logger in loggers:
                            logger.log_multiple(reader.get_all_stats(), stat_type)
                    else:
                        for logger in loggers:
                            logger.log(reader.get_interface_stats(interface_name), stat_type)

            # sleep till next call
            sleep_time = 1 / frequency - (time.perf_counter() - time_stamp)
            if sleep_time > 0:
                time.sleep(sleep_time)

            runs += 1
    except KeyboardInterrupt:
        log.debug("Stopping")
        for logger in loggers:
            logger.close()
        log.info("Stopped after {} secs, with {} runs".format(time.perf_counter()-start_time, runs))


def main():
    parser = argparse.ArgumentParser(description="StatusPusher")

    parser.add_argument('-v', '--verbose', help="Enable debug log.", dest='verbose', action='store_true')

    parser.add_argument('--iface', help='Interface to monitor. If set to None (default value) all available interfaces '
                                        'will be monitored',
                        default=None)

    # frequency and monitor time
    parser.add_argument('-f', '--frequency', help='Number of samples per second. (default %(default)s)', default=1,
                        type=float, dest='frequency')
    parser.add_argument('-t', '--time', help='The duration (in s) netstatspy should run. If None it will run forever',
                        type=float, default=10)

    # logger
    parser.add_argument('-c', '--no-console', help='Do not print statistics to the console', action='store_false')
    parser.add_argument('-j', '--json', help='Write statistics to file', action='store_true')
    parser.add_argument('--file-name', help='Name of output file. (default \'%(default)s\'). Only used if "-j" option'
                                            'is active', default='stats.txt')

    # readers
    parser.add_argument('--no-ip', help='Do not parse ip output', action='store_false')
    parser.add_argument('--tc', help='Parse tc output', action='store_true')
    parser.add_argument('--ss', help='Parse ss output', action='store_true')
    parser.add_argument('--queue-limits', help='Parse queue limits', action='store_true')
    parser.add_argument('--small-queue', help='Parse small queue values', action='store_true')

    args = parser.parse_args()

    logconf = {'format': '[%(asctime)s.%(msecs)-3d: %(name)-16s - %(levelname)-5s] %(message)s', 'datefmt': "%H:%M:%S"}

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG, **logconf)
    else:
        logging.basicConfig(level=logging.INFO, **logconf)

    run(args.no_console, args.json, args.file_name, args.no_ip, args.queue_limits, args.ss, args.tc, args.small_queue,
        args.frequency, args.iface, args.time)


if __name__ == '__main__':
    main()
