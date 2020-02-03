# Application-Aware Demo Set-up

This repository contains everything for the physical and virtual demonstration set-up.

## QUICKSTART (Vagrant)

### Provision Machines

First start the management host and the switch:

	vagrant up mgnt switch

Initiate the first provision step of the PCs by calling up:

	vagrant up pc1 pc5

Once the first provision step is finished, reload the VMs (only required after the very first provision):

	vagrant reload pc1 pc5

### Check the daemons

Enter the PC1:

	vagrant ssh pc1

You can check the output of a daemon with **screen -r** (*sudo* is important):

	sudo screen -r pc1_host1

You can disconnect from screen by *Ctrl + a* and then *Ctrl + b*.

### Check the Demo GUI:

Check if Grafana is reachable at http://10.0.8.0:3000/. 

User and password: admin/admin

## Check connectivity and Grafana statistics:
	
Login to PC1 and run *iperf* as server:

	vagrant ssh pc1
	sudo apt-get install iperf
	iperf -s

Login to PC5 and run iperf as client:

	vagrant ssh pc5
	sudo apt-get install iperf
	iperf -c 192.168.1.0

In Grafana, you should see an increase for *Sent Datarate eth2* under *Switch Stats*.

## Execute the clients

Enter the management PC and execute the daemon:

	vagrant ssh mgnt
	cd /vagrant
	./control/DemoController/DemoController.py -c configs/simple_config.json

## Components

| Component      | Description                                                                         | 
| -------------- | ----------------------------------------------------------------------------------- | 
| DemoDaemon     | Starts applications and monitoring on physical hosts and all network namespaces     | 
| DemoController | Instructs the daemons to start the applications and distributes the configuration.  | 

### DemoDaemon

Tasks:

  - Starts / stops the application when instructed so
  - Applies pacing when instructed so
  - Handles the monitoring
  
### DemoController

The DemoController takes a configuration file and distributes it over redis.

## Required Steps

### Step 1: Create namespaces and start the demo-daemons

  * Use **netns/create_netns.sh** to create the network namespaces.
  * Use **netns/start_daemons** to start a demo daemon in every namespace.

### Step 2: Use the DemoController to execute a configuration file

Example:

    ./control/DemoController/DemoController.py -c configs/demo.json

## Start Daemons manually:

For host0:

```
cd /vagrant && sudo -H -u vagrant python3 -m control.DemoDaemon.Daemon --id pc1_host0 --working-dir /home/vagrant --redis 10.0.8.0
```

For host1:

```
sudo ip netns exec host1 bash -c 'cd /vagrant && python3 -m control.DemoDaemon.Daemon --id pc1_host1 --working-dir /home/vagrant --redis 10.0.8.0'
```
