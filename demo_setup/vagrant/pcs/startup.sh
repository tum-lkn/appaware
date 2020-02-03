#!/usr/bin/env bash

if [ -a ~/provisioned ]; then
    cd ~/sched_cfq
    insmod sch_cfq.ko
fi

export LC_ALL=C  # get rid of unsupported locale setting

sudo tc qdisc add dev eth2 root cfq maxrate 100Mbit
