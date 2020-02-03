#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import argparse
import os
import subprocess

if __name__ == "__main__":
    # parse args
    description = ("NetNS Daemon start parameter")

    parser = argparse.ArgumentParser(description=description)

    parser.add_argument("-k", "--keep-screen", help="Keep screen in bash after Daemon exit", dest="keep_screen", action="store_true")
    parser.add_argument("-r", "--redis", help="Redis host", dest="redis_host", default="10.0.8.0")
    parser.add_argument("-u", "--user", help="User", dest="user", default="vagrant")
    parser.add_argument("-w", "--working-dir", help="Working directory for logs", dest="working_dir", default="/home/vagrant")

    args = vars(parser.parse_args())

    hostname = subprocess.check_output("hostname").decode().strip()

    base_path = os.path.dirname(os.path.abspath(__file__))

    netns_list = subprocess.check_output("ip netns list", shell=True).decode().strip().split('\n')

    if args["keep_screen"]:
        keep_screen = "; /bin/bash"
    else:
        keep_screen = ""

    redis_host = "--redis {}".format(args["redis_host"])
    working_dir = "--working-dir {}".format(args["working_dir"])
    user = args["user"]

    # start daemon on physical host
    daemon_id = "{}_host0".format(hostname)
    cmd = ('screen -dmS {} bash -c "cd /vagrant && sudo -H -u {} python3 -m control.DemoDaemon.Daemon --id {} {} {} '
           '{}"'.format(daemon_id, user, daemon_id, working_dir, redis_host, keep_screen))
    print("running {}".format(cmd))
    subprocess.call(cmd, shell=True)

    # start dameons on virtual hosts
    for netns in netns_list:
        netns_name = netns.split(' ')[0]
        daemon_id = "{}_{}".format(hostname, netns_name)
        cmd = ('screen -dmS {} bash -c "sudo ip netns exec {} bash -c \'cd /vagrant && python3 -m control.DemoDaemon.Daemon '
               '--id {} {} {} {}\'"'.format(daemon_id, netns_name, daemon_id, working_dir, redis_host,
                                          keep_screen))
        print("running {}".format(cmd))
        subprocess.call(cmd, shell=True)
