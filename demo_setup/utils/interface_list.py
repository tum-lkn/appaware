#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import platform
import re
import subprocess
from collections import namedtuple

def interface_list(external=False, ip=False):
    """
    Source: https://codereview.stackexchange.com/questions/104504/get-network-interfaces-on-linux

    Get a list of network interfaces on Linux.

    To access the MAC address and/or the IP address, set the relevant keyword
    arguments to True.

    Parameters
    ----------
    external : bool, optional
        Only show external interfaces, and ignore virtual (e.g. loopback)
        devices, and return their MAC addresses.
    ip : bool, optional
        Only show interfaces which are UP and have an IP address, and return
        their IPv4 addresses.

    Returns
    -------
    interfaces
        list of str containing the interface name by default, or list of
        namedtuple containing `name`, `mac`, and `ip` as requested.

    Examples
    --------
    >>> print(get_interfaces())
    ['eth0', 'lo', 'wlan0']
    >>> print(get_interfaces(external=True))
    [Interface(name='eth0', mac='a0:b1:c2:d3:e4:f5'), Interface(name='wlan0', ma
    c='f5:e4:d3:c2:b1:a0')]
    >>> print(get_interfaces(ip=True))
    [Interface(name='lo', ip='127.0.0.1'), Interface(name='wlan0', ip='192.168.1
    1.2')]
    >>> print(get_interfaces(external=True, ip=True))
    [Interface(name='wlan0', mac='f5:e4:d3:c2:b1:a0', ip='192.168.11.2')]

    """

    release = platform.release().upper()

    # fix for arch based distros - assuming all other distros have ubuntu like output
    if "MANJARO" in release or "ARCH" in release:
        name_pattern = "^([\w:-]+):\s.*?"
        ip_pattern = "\n\s+inet[ ]((?:\d+\.){3}\d+).*?" if ip else "\n\s.*?"
        mac_pattern = "\n(?:.*?\n){0,3}\s+ether[ ]([0-9A-Fa-f:]{17})" if external else ""
        pattern = re.compile("".join((name_pattern, ip_pattern, mac_pattern)),
                             flags=re.MULTILINE)
        # namedtuple fields in correct order
        fields = "name {ip} {mac}".format(ip="ip" if ip else "",
                                          mac="mac" if external else "")
    else:
        name_pattern = "^([\w:-]+)\s"
        mac_pattern = ".*?HWaddr[ ]([0-9A-Fa-f:]{17})" if external else ""
        ip_pattern = ".*?\n\s+inet[ ]addr:((?:\d+\.){3}\d+)" if ip else ""
        pattern = re.compile("".join((name_pattern, mac_pattern, ip_pattern)),
                             flags=re.MULTILINE)
        # namedtuple fields in correct order
        fields = "name {mac} {ip}".format(mac="mac" if external else "",
                                          ip="ip" if ip else "")

    ifconfig = subprocess.check_output("ifconfig").decode()
    interfaces = pattern.findall(ifconfig)
    if external or ip:
        Interface = namedtuple("Interface", fields)
        return [Interface(*interface) for interface in interfaces]
    else:
        return interfaces
