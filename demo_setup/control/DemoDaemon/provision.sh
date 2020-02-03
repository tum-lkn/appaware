#!/usr/bin/env bash

apt-get update
apt-get update

apt-get install -y python3-pip

cd $(dirname $0)

pip3 install -r requirements.txt
