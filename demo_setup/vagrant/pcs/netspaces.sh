#!/usr/bin/env bash

if [ $(uname -r) != "4.15.4-041504-generic" ]; then
    exit
fi

if [ $(basename $0) = "provision.sh" ]; then
    # We can use relative PATH
    REPO_PATH=$(dirname $0)"/../"
else
    # Called from e.g. /tmp/vagrant-shell so we assume repo can be found in /vagrant
    REPO_PATH="/vagrant/"
fi

mgmt_ip=$(ip addr | grep 'inet 10.0' | tr -s ' ' | cut -d ' ' -f3 | cut -d '/' -f1)
data_ip=$(ip addr | grep 'inet 192.168' | tr -s ' ' | cut -d ' ' -f3 | cut -d '/' -f1)

sudo ${REPO_PATH}netns/nssetup.py create_bridge $data_ip -n br-data
sudo ${REPO_PATH}netns/nssetup.py create_bridge $mgmt_ip -n br-mgmt

namespace_num=20 # change this number to create more namespaces

sudo ${REPO_PATH}netns/create_netns.sh ${namespace_num}

subnet_identifier=$(ip addr | grep 'inet 192.168' | tr -s ' ' | cut -d ' ' -f3 | cut -d '/' -f1 | cut -d '.' -f3)

if [ ${subnet_identifier} == "1" -o ${subnet_identifier} == "2" ];
then
    route_command="ip route add 192.168.4.0/22 via 192.168.3.100"
else
    route_command="ip route add 192.168.0.0/22 via 192.168.4.100"
fi

${route_command}

for i in `seq 1 $namespace_num`
do
    ip netns exec host${i} ${route_command}
done


python3 /vagrant/netns/start_daemons.py
