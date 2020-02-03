#!/usr/bin/env bash

if [ -z $1 ]; then
	echo "no interface ip supplied! $0 <ip>"
	exit 1
fi

iface_ip=$1

echo "searching interfaces with ip $iface_ip"

ifaces=$(ifconfig | sed -n "/addr:$iface_ip/{g;H;p};H;x" | awk '{print $1}')

if [ $ifaces ]; then
	echo "found $ifaces"
	# Disable all offloading features for 
	for eth in "$ifaces"
	do
		for feature in "gso" "gro" "tso"
		do
			cmd="sudo ethtool -K ${eth} ${feature} off"
			echo "running $cmd"
			eval $cmd
		done
	done
else
	echo "no interface found"
fi
