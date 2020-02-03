#!/usr/bin/env bash

nohup python3 /vagrant/utils/RTTMeasurement.py -h 192.168.5.0 > /home/vagrant/rtt.out 2>&1 &
