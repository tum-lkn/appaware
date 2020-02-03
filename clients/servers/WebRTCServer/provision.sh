#!/usr/bin/env bash

apt-get update
apt-get update

apt-get install -y nginx-light nodejs node-ws

# make sure nginx is stopped and won't start again
service nginx stop
systemctl disable nginx
