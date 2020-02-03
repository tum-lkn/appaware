#!/usr/bin/env bash

apt-get update

export LC_ALL=C

# Install dependencies
apt-get install -q -y python3-pip ntpdate curl software-properties-common apt-transport-https

pip3 install influxdb
pip3 install redis

# Install docker
curl -fsSL https://download.docker.com/linux/$(. /etc/os-release; echo "$ID")/gpg | sudo apt-key add -

add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/$(. /etc/os-release; echo "$ID") $(lsb_release -cs) stable"
apt-get update
apt-get install -y docker-ce
