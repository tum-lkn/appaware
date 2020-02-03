#!/usr/bin/env bash

export LC_ALL=C

apt-get update
apt-get update

apt-get -y install python3-pip

pip3 install redis
