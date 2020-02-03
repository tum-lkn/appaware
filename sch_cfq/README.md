# sch\_cfq: Custom fair queuing kernel module

Modified version of the fq scheduler in the Kernel. The modified version puts all packets of an interface into one single queue. The original *sch_fg.c* [link](https://github.com/torvalds/linux/blob/master/net/sched/sch_fq.c) is part of the Linux Kernel published under the GPL-2.0 license.

We use it in the AppAware research project to pace all packets originating from a network namespace.

## Dependencies

	apt-get install build-essential devscripts linux-headers-$(uname -r)

## Compile

	cd sch_cfq/
	make

## Load / unload module

Load module:

	insmod sch_cfq.ko

Unload module:

	rmmod sch_cfq
	
You can check if the module is loaded with lsmod:

    lsmod | grep cfq

## Add / delete qdisc

Add:

	tc qdisc add dev eth1 root cfq maxrate 5mbit

Delete:

	tc qdisc del dev eth1 root

# tc modifications

There are minor modifications for the tc tool necessary to add the cfq qdisc.

First install general build dependencies:

	apt-get install build-essential devscripts

Get the source code:

	git clone git@gitlab.lrz.de:DFG_SDN_APPAWARE/sch_cfq.git

Enable deb-src in apt:

	nano /etc/apt/sources.list

Make sure the following lines are uncommented:

	deb-src http://us.archive.ubuntu.com/ubuntu/ xenial main restricted
	deb-src http://us.archive.ubuntu.com/ubuntu/ xenial-updates main restricted

Afterwards run `apt-get update`.

Install all build dependencies for iproute2 with:

	apt-get build-dep iproute2

Create a folder for the iproute2 source code:

	cd ~
	mkdir iproute2-src
	cd iproute2-src

Get the iproute2 source code:

	apt-get source iproute2

Enter the unpacked source folder:

	cd iproute2-4.3.0/

Check if it compiles and installs successfully (without any modifications):

	debuild -b -uc -us
	cd ..
	dpkg -i iproute2_4.3.0-1ubuntu3.16.04.3_all.deb

Add the cfq scheduler to the tc source code:

	cd iproute2-4.3.0/
	cp ~/sch_cfq/tc/q_cfq.c tc/
	patch tc/Makefile ~/sch_cfq/tc/Makefile.patch

Create a new iproute2 package and install it:

	debuild -b -uc -us
	cd ..
	dpkg -i iproute2_4.3.0-1ubuntu3.16.04.3_all.deb

