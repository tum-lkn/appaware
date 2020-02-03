#!/usr/bin/env python3
import logging
import argparse
import os
import sys
import subprocess
from nsenter import Namespace


log = logging.getLogger(__name__)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Start a client in a network namespace.")
    parser.add_argument("-u", "--user", help="User to execute command as.", default="vagrant")
    parser.add_argument("ns_name", help="Namespace to enter", type=str)
    parser.add_argument("command", help="Command to execute in namespace", type=str, nargs=argparse.REMAINDER)

    parser.add_argument('-v', '--verbose', help="Enable debug log.", dest='verbose', action='store_true')

    cmdargs = parser.parse_args()

    logconf = {'format': '[%(asctime)s.%(msecs)-3d: %(name)-16s - %(levelname)-5s] %(message)s',
               'datefmt': "%H:%M:%S"}

    if cmdargs.verbose:
        logging.basicConfig(level=logging.DEBUG, **logconf)
    else:
        logging.basicConfig(level=logging.INFO, **logconf)

    if os.geteuid() != 0:
        log.fatal("You need to be root!")
        sys.exit(-1)

    ns_name = "/var/run/netns/%s" % cmdargs.ns_name

    if not os.path.exists(ns_name):
        log.fatal("Namespace %s does not exist!" % ns_name)
        sys.exit(-1)

    cmd = "sudo -H -u %s " % cmdargs.user
    cmd += " ".join(cmdargs.command)

    log.debug("Command: %s" % cmd)

    with Namespace(ns_name, 'net'):
        p = subprocess.Popen(cmd, shell=True)
        sys.exit(p.wait())
