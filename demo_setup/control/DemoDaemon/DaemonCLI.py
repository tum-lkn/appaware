#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import argparse
import json
import redis
import sys
import time


redis_con = None
redis_sub = None

def publish(msg):
    data = json.dumps(msg)
    redis_con.publish("daemon_broadcast", data)

def flush_message_buffer():
    while True:
        message = redis_sub.get_message()
        if message:
            print("flushed %s" % (message))
        else:
            break

def cli_list_daemons(args):
    daemons = list_daemons()
    print("Found %s daemons: %s" % (len(daemons), daemons))

def list_daemons():
    flush_message_buffer()
    publish(msg={"type": "PING"})

    daemons = []
    while True:
        msg = redis_sub.get_message(timeout=1)
        if msg:
            try:
                data = json.loads(msg["data"])
                if data["type"] == "PONG":
                    daemons.append(data["daemon_id"])
            except Exception as e:
                print("couldn't encode json string '%s'" % (msg["data"]))
        else:
            break
    return sorted(daemons)

def cli_stop_apps(args):
    print("Stopping Apps")
    stop_apps()

def stop_apps():
    publish({"type": "STOP_APPS"})

def cli_quit_daemons(args):
    print("Stopping Daemons")
    quit_daemons()

def quit_daemons():
    publish({"type": "STOP_DAEMON"})

def register_subcommands(functions, subparsers):
    functions['list'] = cli_list_daemons
    parser = subparsers.add_parser('list')

    functions['stop'] = cli_stop_apps
    parser = subparsers.add_parser('stop')

    functions['quit'] = cli_quit_daemons
    parser = subparsers.add_parser('quit')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="CLI for Daemon interaction")

    parser.add_argument("-r", "--redis", help="Redis host", dest="redis_host", default="10.0.1.0")

    subparsers = parser.add_subparsers(dest='subcommand')

    functions = {}
    register_subcommands(functions, subparsers)

    args = parser.parse_args()

    if args.subcommand is None:
        parser.print_help()
        parser.exit()

    try:
        redis_con = redis.StrictRedis(host=args.redis_host, port=6379, db=0, charset="utf-8", decode_responses=True)
        redis_sub = redis_con.pubsub(ignore_subscribe_messages=True)
        redis_sub.subscribe("daemon_broadcast")
    except Exception as e:
        print("No connection to redis host - exiting")
        sys.exit(1)

    # initial flush and wait for flush
    flush_message_buffer()
    time.sleep(0.5)

    func = functions[args.subcommand]
    r = func(args)
