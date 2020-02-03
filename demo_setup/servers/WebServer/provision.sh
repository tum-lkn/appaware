#!/usr/bin/env bash

apt-get update
apt-get update

apt-get install -y nginx-light

# make sure nginx is stopped and won't start again
service nginx stop
systemctl disable nginx

# install dependencies for TemplateConverter
pip3 install -r ./TemplateConverter/requirements.txt
