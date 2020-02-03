#!/usr/bin/env python3
import sys
import time
import os
import logging
import argparse
from pyroute2 import netns, NetNS, IPDB, IPRoute

log = logging.getLogger(__name__)


def cli_create_ns(args):
    return create_ns(args.br_name, args.ns_name, args.ns_ip, args.ns_netmask, args.if_description, args.add_if)


def create_ns(br_name, ns_name, ns_ip, ns_netmask, if_description, add_if):
    """
    :param br_name:
    :param ns_name:
    :param ns_ip:
    :param ns_netmask:
    :param if_description:
    :param add_if:
    :return:
    """

    # start the main network settings database:
    ipdb = IPDB()

    # Check if the bridge exists
    if br_name not in ipdb.interfaces.keys():
        log.fatal("Could not find bridge %s!" % br_name)
        sys.exit(-1)

    # veth naming
    ifname = "%s_%s_p%%d" % (ns_name, if_description)

    if (ifname % 0) in ipdb.interfaces.keys():
        log.fatal("%s already exists as interface!" % (ifname % 0))
        return False

    log.debug("Creating veth pair %s - %s for namespace %s." % (ifname % 0, ifname % 1, ns_name))

    if ns_name in netns.listnetns() and not add_if:
        log.warning("Namespace %s already exists!" % ns_name)

    # Create/configure a network namespace
    ipdb_ns = IPDB(nl=NetNS(ns_name))

    # Make sure lo is up in the namespace
    ipdb_ns.interfaces["lo"].up().commit()

    # Create veth pair
    ipdb.create(kind='veth', ifname=(ifname % 0), peer=(ifname % 1)).commit()

    # Move peer veth into the netns
    with ipdb.interfaces[(ifname % 1)] as veth:
        veth.net_ns_fd = ns_name

    with ipdb.interfaces[(ifname % 0)] as veth:
        veth.up()

    # wait for iface to be moved to ns
    time.sleep(0.1)

    ns_ip = '%s/%s' % (ns_ip, ns_netmask)

    log.debug("Assigning IP %s to %s." % (ns_ip, (ifname % 1)))

    with ipdb_ns.interfaces[(ifname % 1)] as veth:
        veth.add_ip(ns_ip)
        veth.up()

    log.debug("Adding port %s to bridge %s." % ((ifname % 0), br_name))

    ipdb.interfaces[br_name].add_port((ifname % 0))

    ipdb.commit()

    return True


def cli_destroy_ns(args):
    destroy_ns(args.ns_name)


def destroy_ns(ns_name):
    """
    Deletes a network namespace

    :param ns_name: The name of the network
    :return: Returns True of the namespace was deleted or did not exist.
    """

    if ns_name not in netns.listnetns():
        log.warning("Namespace %s not found! Doing nothing." % ns_name)
        return True

    netns.remove(ns_name)

    return True


def cli_destroy_bridge(args):
    destroy_bridge(args.br_name)


def destroy_bridge(br_name):

    log.info("Deleting bridge %s." % br_name)

    ipdb = IPDB()

    if br_name not in ipdb.interfaces.keys():
        log.fatal("A bridge/interface with the name %s does not exist!" % br_name)
        return False

    # Guess what the original physical interface could be

    ifnames = [ipdb.interfaces[p].ifname for p in ipdb.interfaces['br-clients'].ports]
    ifnames = [i for i in ifnames if i.startswith("enp")]

    phy_eth = None

    if len(ifnames) != 1:
        log.warning("Could not determine which interface is the physical one in the bridge!")
    else:
        phy_eth = ifnames[0]
        log.debug("Assuming %s is the physical interface on the bridge." % phy_eth)

    # Guess what the original physical IP could be
    phy_ip = None

    if phy_eth is not None:
        for ip, netmask in ipdb.interfaces[br_name].ipaddr:
            if ip.startswith('10.') or ip.startswith('192.'):
                phy_ip = (ip, netmask)

        if phy_ip is None:
            log.warning("Could not find a valid IP on the bridge. The physical interface will be without IP!")
        else:
            log.debug("Found IP %s on the bridge." % str(phy_ip))

    #FIXME: Not sure if this is still needed or not
    # Using IPRoute and IPDB at the same time feels very ugly anyway..
    #ipdb.commit()
    #ipdb.release()

    ip = IPRoute()

    ip.link('del', index=ip.link_lookup(ifname=br_name)[0])

    if phy_eth is not None and phy_ip is not None:

        log.info("Setting %s on %s." % ('%s/%s' % (phy_ip[0], phy_ip[1]), phy_eth))

        with IPDB() as ipdb:
            with ipdb.interfaces[phy_eth] as eth:
                eth.add_ip('%s/%s' % (phy_ip[0], phy_ip[1]))

    ip.close()

    return True


def cli_create_bridge(args):
    return create_bridge(args.br_name, args.phy_ip)


def create_bridge(br_name, phy_ip):
    """
    Create a bridge for connecting the container clients to the network.

    :param br_name: Name of the bridge to create.
    :param phy_ip: IP of the physical interface to include in the bridge.
    :return: True if success, False if failure
    """

    log.info("Creating bridge %s." % br_name)

    assert(phy_ip.startswith('10.') or phy_ip.startswith('192.'))

    ipdb = IPDB()

    if br_name in ipdb.interfaces.keys():
        log.fatal("A bridge/interface with the name %s already exists!" % br_name)
        return False

    phy_eth = None

    for eth in ipdb.interfaces.keys():
        if type(eth) is int: continue
        for ip, netmask in ipdb.interfaces[eth]['ipaddr']:
            log.debug("%s: %s" % (eth, ip))
            if ip == phy_ip:
                phy_eth = (eth, ip, netmask)
                break

    if phy_eth is None:
        log.fatal("Could not find an interface with IP '%s'!" % phy_ip)
        return False

    log.info("Using interface %s for the bridge." % str(phy_eth))

    log.debug("Creating bridge with ifname %s." % br_name)

    with ipdb.create(kind='bridge', ifname=br_name) as br:
        br.add_port(ipdb.interfaces[phy_eth[0]])
        br.up()
        br.add_ip('%s/%s' % (phy_eth[1], phy_eth[2]))

    log.debug("Removing IP %s from interface %s." % (phy_eth[1], phy_eth))

    with ipdb.interfaces[phy_eth[0]] as i:
        i.del_ip('%s/%s' % (phy_eth[1], phy_eth[2]))

    ipdb.commit()
    ipdb.release()

    return True


def register_subcommands(functions, subparsers):

    functions['create_bridge'] = cli_create_bridge

    parser = subparsers.add_parser('create_bridge')

    parser.add_argument('-n', '--br-name', help="Name of the bridge to create.", default="br-clients")
    parser.add_argument("phy_ip", help="IP address of the physical interface to bind the virtual interfaces to.",
                        type=str)

    functions['destroy_bridge'] = cli_destroy_bridge

    parser = subparsers.add_parser('destroy_bridge')

    parser.add_argument('-n', '--br-name', help="Name of the bridge to destroy.", default="br-clients")

    functions['create_ns'] = cli_create_ns

    parser = subparsers.add_parser('create_ns')

    parser.add_argument('-n', '--br-name', help="Name of the bridge to connect the namespace to.", default="br-clients")
    parser.add_argument('-s', '--ns-name',
                        help="Name of the namespace to create.",
                        required=True)
    parser.add_argument('-i', '--ns-ip',
                        help="IP of the interface in the namespace.",
                        required=True)
    parser.add_argument('-m', '--ns-netmask',
                        help="Netmask (in bits) of the interface in the namespace.",
                        default=24)
    parser.add_argument('-d', '--if-description',
                        help="Name of the interface to create.",
                        default="clients")
    parser.add_argument('-a', '--add-if',
                        help="Add interface to existing namespace",
                        action='store_true')

    functions['destroy_ns'] = cli_destroy_ns

    parser = subparsers.add_parser('destroy_ns')

    parser.add_argument('-s', '--ns-name',
                        help="Name of the namespace to destroy.",
                        default="test")

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Create bridges and namespaces for the client containers.")
    parser.add_argument('-v', '--verbose', help="Enable debug log.", dest='verbose', action='store_true')

    subparsers = parser.add_subparsers(dest='subcommand')

    functions = {}

    register_subcommands(functions, subparsers)

    args = parser.parse_args()

    logconf = {'format': '[%(asctime)s.%(msecs)-3d: %(name)-16s - %(levelname)-5s] %(message)s', 'datefmt': "%H:%M:%S"}

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG, **logconf)
    else:
        logging.basicConfig(level=logging.INFO, **logconf)

    if os.geteuid() != 0:
        log.fatal("You need to be root!")
        sys.exit(-1)

    if args.subcommand is None:
        parser.print_help()
        parser.exit()

    func = functions[args.subcommand]
    r = func(args)

    if r is False:
        sys.exit(-1)
