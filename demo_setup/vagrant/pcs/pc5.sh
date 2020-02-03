#!/usr/bin/env bash

nohup python3 /vagrant/utils/RTTMeasurement.py > /home/vagrant/rtt.out 2>&1 &
