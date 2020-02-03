#!/usr/bin/env bash

sysctl net.ipv4.ip_forward=1

sudo tc qdisc add dev eth2 root cfq maxrate 100Mbit
sudo tc qdisc add dev eth3 root cfq maxrate 100Mbit

cd /vagrant/

nohup python3 -m switch.switch_stats > /home/vagrant/switch_stats.out 2>&1 &
