#!/usr/bin/env bash

apt-get update
apt-get update

apt-get install -y nginx-light

# make sure nginx is stopped and won't start again
# service nginx stop
# systemctl disable nginx

# install dependencies for TemplateConverter
pip3 install -r ./TemplateConverter/requirements.txt

cd /var/www/html

wget http://pages.lkn.ei.tum.de/~appaware/bbb_60s.tar.gz

tar xf bbb_60s.tar.gz
rm bbb_60s.tar.gz

wget http://pages.lkn.ei.tum.de/~appaware/bbb_1s.tar.gz

tar xf bbb_1s.tar.gz
rm bbb_1s.tar.gz

