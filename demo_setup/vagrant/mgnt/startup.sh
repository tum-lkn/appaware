#!/usr/bin/env bash

DOCKER_PS=$(docker ps -a -q)

if [[ ! -z $DOCKER_PS ]]
then
	echo "Removing containers: $DOCKER_PS"
	docker rm -f $DOCKER_PS
fi

# influxDB
docker run -d -p 8086:8086 --name=influxdb influxdb:1.4.3-alpine

# Grafana
docker run -d --link influxdb --name=grafana -p 3000:3000 grafana/grafana:5.1.5

# Redis
docker run -d -p 6379:6379 --name=redis redis:4.0.7-alpine

sleep 1
cd /vagrant/vagrant/mgnt/grafana/
bash setup.sh

# start statspusher
nohup python3 /vagrant/stats/stats_pusher.py -v > /home/vagrant/stats_pusher.out 2>&1 &
