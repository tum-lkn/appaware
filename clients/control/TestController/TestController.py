#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import argparse
import json
import os
import redis
import signal
import sys
import time


class TestController(object):
    def __init__(self, config, redis_host="localhost", redis_port=6379, redis_db=0, redis_channel="daemon_broadcast"):
        self._config = config
        self._running = False
        self._redis = None
        self._redis_sub = None
        self._redis_config = {
            "redis_host": redis_host,
            "redis_port": redis_port,
            "redis_db": redis_db,
            "redis_channel": redis_channel
        }
        signal.signal(signal.SIGINT, self._signal_handler)

    def prepare(self):
        self._redis = redis.StrictRedis(host=self._redis_config["redis_host"], port=self._redis_config["redis_port"], db=self._redis_config["redis_db"], decode_responses=True)
        self._redis_sub = self._redis.pubsub(ignore_subscribe_messages=True)
        self._redis_sub.subscribe(self._redis_config["redis_channel"])
        self._flush_message_buffer()

        # stop all clients if running
        self._publish(msg={"type": "STOP_APPS"})

        # wait for apps to stop
        # time.sleep(1)

        # clear db?

        # load config
        # overwrite json string with cleaned generated version (no spaces or \n)
        self._json_config = json.dumps(self._config)

        if not self._config.get("experiment", {}).get("study_id", None):
            print("No study_id specified - exiting")
            sys.exit(-1)

        # make sure each client has daemon running
        daemons_present = self._get_running_daemons()
        daemons_required = self._config.get("daemons", None)

        if not daemons_required:
            print("No daemons specified - exiting")
            sys.exit(-1)

        daemons_required = list(daemons_required.keys())

        # Timeout

        if not set(daemons_required).issubset(set(daemons_present)):
            daemons_missing = list(set(daemons_required).difference(set(daemons_present)))
            print("Daemons found %s" % (sorted(daemons_present)))
            print("Daemons required %s" % (sorted(daemons_required)))
            print("Daemons missing %s" % (sorted(daemons_missing)))
            print("Not all required Daemons running - exiting")
            sys.exit(-1)
        else:
            print("All required daemons running")

    def run(self):
        # if collect logs update dict with timestamp time.time()
        if self._config.get("experiment", {}).get("collect_logs", {}):
            self._config["experiment"]["collect_logs"]["timestamp"] = time.time()
            print("Updated timestamp in config")

        self._publish(msg={"type": "CONFIG", "config": self._config})

        self._running = True

        # if time specified wait until time
        duration = self._config.get("experiment", {}).get("duration", 0)
        start_time = time.time()
        if duration > 0:
            print("running test for %s seconds - abort with ctrl+c" % (duration))
            stop_time = start_time + duration
        else:
            print("running test until stopped with ctrl+c")
            stop_time = None

        # schedule initial ping after 30s
        next_ping = 15

        while self._running:
            time_passed = time.time() - start_time
            if duration > 0:
                percent = 100 * time_passed / duration
                print("TestController running %.1fs/%.1fs (%.1f%%)" % (time_passed, duration, percent))
            else:
                print("TestController running for %.1fs" % (time_passed))
            time.sleep(1)
            if stop_time:
                if time.time() >= stop_time:
                    self._running = False

            # send pings every 30s to keep connection up - chekc self._running to avoid ping message flood while stopping clients
            if time_passed >= next_ping and self._running:
                self._publish(msg={"type": "PING"})
                next_ping += 30

        # stop all clients
        self._publish(msg={"type": "STOP_APPS"})

    def stop(self):
        self._running = False

    def clean_up(self):
        pass

    def _publish(self, msg):
        data = json.dumps(msg)
        self._redis.publish(self._redis_config["redis_channel"], data)

    def _get_running_daemons(self):
        self._flush_message_buffer()
        self._publish(msg={"type": "PING"})

        daemons = []
        while True:
            msg = self._redis_sub.get_message(timeout=1)
            if msg:
                try:
                    data = json.loads(msg["data"])
                    if data["type"] == "PONG":
                        daemons.append(data["daemon_id"])
                except Exception as e:
                    self._logger.error("couldn't encode json string '%s'" % (msg["data"]))
            else:
                break
        return daemons

    def _flush_message_buffer(self):
        print("_flush_message_buffer")
        while True:
            message = self._redis_sub.get_message()
            if message:
                print("flushed %s" % (message))
            else:
                break

    def _signal_handler(self, signal, frame):
        self._running = False

if __name__ == '__main__':
    description = ("Start Test on remote hosts")

    parser = argparse.ArgumentParser(description=description)

    parser.add_argument("-c", "--config", help="Config file", dest="config", default="test_config.json")
    parser.add_argument("-r", "--redis", help="Redis host", dest="redis_host", default="127.0.0.1")

    args = vars(parser.parse_args())

    # TODO argparse for redis server

    config_file = open(args["config"], 'r')
    config = json.load(config_file)

    test_controller = TestController(config=config, redis_host=args["redis_host"])
    test_controller.prepare()
    test_controller.run()
    test_controller.clean_up()
