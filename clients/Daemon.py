#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import argparse
from control.Daemon.Daemon import Daemon

if __name__ == "__main__":
    # parse args
    description = ("Daemon parameter")

    parser = argparse.ArgumentParser(description=description)

    parser.add_argument("-i", "--id", help="Daemon identifier", dest="daemon_id", required=True)
    parser.add_argument("-r", "--redis", help="Redis host", dest="redis_host", default="10.0.0.1")
    parser.add_argument("-w", "--working-dir", help="Working directory for logs", dest="working_dir")

    args = vars(parser.parse_args())

    # start daemon
    daemon = Daemon(daemon_id=args["daemon_id"], redis_host=args["redis_host"], working_dir=args["working_dir"])
    daemon.prepare()
    daemon.run()
    daemon.clean_up()
