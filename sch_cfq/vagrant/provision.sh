#!/usr/bin/env bash

apt-get update
apt-get update

apt-get install -y build-essential linux-headers-$(uname -r) devscripts

sudo apt-get build-dep iproute2

mkdir /root/iproute2-src
cd /root/iproute2-src

apt-get source iproute2

#cd iproute2
# apply changes
# - add q_cfq file
#   - cp ... ...
# - Use new makefile
#   - patch Makefile.orig /vagrant/tc/Makefile.patch
# debuild -b -uc -us
