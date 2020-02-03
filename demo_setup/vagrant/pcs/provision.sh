#!/usr/bin/env bash

export LC_ALL=C

if [ $(uname -r) != "4.15.4-041504-generic" ]; then
    exit
fi

if [ -a ~/provisioned ]; then
    echo cfq already installed
    exit
fi

apt-get -y update
#apt-get -y upgrade

apt-get -y install bridge-utils

if [ $(basename $0) = "provision.sh" ]; then
    # We can use relative PATH
    REPO_PATH=$(dirname $0)"/../"
else
    # Called from e.g. /tmp/vagrant-shell so we assume repo can be found in /vagrant
    REPO_PATH="/vagrant/"
fi

# Control
bash ${REPO_PATH}/control/DemoDaemon/provision.sh
bash ${REPO_PATH}/control/DemoController/provision.sh

# Clients
bash ${REPO_PATH}/clients/SSHClient/provision.sh
bash ${REPO_PATH}/clients/WebDLClient/provision.sh


# installation of sch_cfq (see: https://gitlab.lrz.de/DFG_SDN_APPAWARE/sch_cfq)

## install dependencies

apt-get -y install build-essential devscripts libelf-dev

## Compile
cp -R ${REPO_PATH}/sch_cfq/sched_cfq/ ~/sched_cfq/
cd ~/sched_cfq/
make

# tc modifications
## There are minor modifications for the tc tool necessary to add the cfq qdisc.


## add xenial packet to sources
touch /etc/apt/sources.list.d/xenial.list
sh -c 'echo "deb-src http://us.archive.ubuntu.com/ubuntu/ xenial main restricted" >> /etc/apt/sources.list'
sh -c 'echo "deb-src http://us.archive.ubuntu.com/ubuntu/ xenial-updates main restricted" >> /etc/apt/sources.list'
apt-get -y update

## Install all build dependencies for iproute2

apt-get -y build-dep iproute2

## Create a folder for the iproute2 source code:

cd ~
mkdir iproute2-src
cd iproute2-src

## Get the iproute2 source code:

apt-get -y source iproute2

## Enter the unpacked source folder:

cd iproute2-*/

## Check if it compiles and installs successfully (without any modifications):

sudo debuild -b -uc -us
cd ..
dpkg -i iproute2_*_amd64.deb

## Add the cfq scheduler to the tc source code:

cd iproute2-*/
cp ${REPO_PATH}/sch_cfq/tc/q_cfq.c tc/
patch tc/Makefile ${REPO_PATH}/sch_cfq/tc/Makefile.patch

## Create a new iproute2 package and install it:

debuild -b -uc -us
cd ..
dpkg -i iproute2_*_amd64.deb

# install python requirements
pip3 install -r ${REPO_PATH}vagrant/pcs/requirements.txt

touch ~/provisioned




#############################
##   stuff for webserver   ##
#############################

apt-get install -y nginx-light

# make sure nginx is stopped and won't start again
# service nginx stop
# systemctl disable nginx

cd /var/www

wget http://pages.lkn.ei.tum.de/~appaware/bbb_60s.tar.gz

tar xf bbb_60s.tar.gz
rm bbb_60s.tar.gz

wget http://pages.lkn.ei.tum.de/~appaware/bbb_1s.tar.gz

tar xf bbb_1s.tar.gz
rm bbb_1s.tar.gz

dd if=/dev/zero of=10M.bin bs=1 count=0 seek=10M

mkdir science_lab
cd science_lab
wget http://pages.lkn.ei.tum.de/~appaware/templates/science_lab/science_lab.json
wget http://pages.lkn.ei.tum.de/~appaware/templates/science_lab/science_lab_template.zip
wget http://pages.lkn.ei.tum.de/~appaware/templates/science_lab/science_lab_template_converted.zip
wget http://pages.lkn.ei.tum.de/~appaware/templates/science_lab/science_lab_template_with_jquery.zip
wget http://pages.lkn.ei.tum.de/~appaware/templates/science_lab/science_lab_template_with_jquery_converted.zip

# dash
sudo sh /vagrant/clients/DASHClient/provision.sh

# voip
sh /vagrant/clients/VoIPClient/provision.sh
sh /vagrant/servers/VoIPServer/provision.sh
