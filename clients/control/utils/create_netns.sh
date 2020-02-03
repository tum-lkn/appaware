#!/usr/bin/env bash

if [ -z $1 ]; then
	echo "no number of netns to create supplied! $0 <num>"
	exit 1
fi

num_netns=$(ip netns list | wc -l)

if [ $num_netns -gt 0 ]; then
	# delete existing netns
	sudo ip -all netns delete
	# restart networking because netns deletion causes trouble
	sudo /etc/init.d/networking restart
fi

# collect info
host_identifier=$(hostname)

base_path=$(realpath $(dirname $0))

mgmt_address=$(ip -f inet -o addr show br-mgmt | grep -v mgmt:0 | cut -d ' ' -f 7)
mgmt_base_ip=$(echo $mgmt_address | cut -d '/' -f 1)
mgmt_netmask=$(echo $mgmt_address | cut -d '/' -f 2)

data_address=$(ip -f inet -o addr show br-data | cut -d ' ' -f 7)
data_base_ip=$(echo $data_address | cut -d '/' -f 1)
data_netmask=$(echo $data_address | cut -d '/' -f 2)

for i in $(seq 1 $1); do
	netns_name="host${i}"
	mgmt_ip="$(echo $mgmt_base_ip | cut -d '.' -f 1-3).${i}"
	data_ip="$(echo $data_base_ip | cut -d '.' -f 1-3).${i}"

	cmd_mgmt="sudo ${base_path}/nssetup.py -v create_ns --ns-name ${netns_name} --ns-ip ${mgmt_ip} --ns-netmask ${mgmt_netmask} --br-name br-mgmt -d mgmt"
	cmd_data="sudo ${base_path}/nssetup.py -v create_ns --ns-name ${netns_name} --ns-ip ${data_ip} --ns-netmask ${data_netmask} --br-name br-data -d data -a"

	echo "running $cmd_mgmt"
	eval $cmd_mgmt
	echo "running $cmd_data"
	eval $cmd_data

	# Disable all offloading features for data network
	cmd_data_offload="sudo ip netns exec ${netns_name} ${base_path}/disable_offloading.sh ${data_ip}"
	echo "running $cmd_data_offload"
	eval $cmd_data_offload

done
