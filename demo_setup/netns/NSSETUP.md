# Namespace Setup

## Overview

### Before

```
 Host                                  
 +-------------+
 |             |
 |     NIC     |
 |    +-----------------+      +-----------+
 |    |  192.168.100.11 o <--> o  NETWORK  |
 |    +-----------------+      +-----------+
 |             |                                   
 |             |
 +-------------+
```

### After

```
 Host
+--------------------------------------------+
|                                            |
|     container: web1                +--------------------+
|    +--------------+                | bridge: br_clients |
|    |              |                |                    |
|    |  veth: web1_p1                |  192.168.100.11    |
|    |  +-----------------+          |                    |
|    |  | 192.168.100.201 o <-+      |       NIC          |
|    |  +-----------------+   |      |  +-------------+   |
|    |              |         |      |  |  <no ip>    |   |
|    +--------------+         |      |  +-------------+   |       +---------+
|                             |      |                    o <---> o NETWORK |
|                             |      |  veth: web1_p0     |       +---------+
|     container: ssh1         |      |  +-------------+   |
|    +--------------+         +-------> o  <no ip>    |   |
|    |              |                |  +---------- --+   |
|    |   veth: ssh1_p1               |  veth: ssh1_p0     |
|    |   +----------------+          |  +-------------+   |
|    |   |192.168.100.202 o <---------> o  <no ip>    |   |
|    |   +----------------+          |  +-------------+   |
|    |              |                |                    |
|    +--------------+                +--------------------+
|                                            |
+--------------------------------------------+
```

## QUICKSTART

Create a bridge for the clients and add the testbed interface to the bridge:

```
./nssetup.py create_bridge 192.168.100.11
```

Create a namespace for a client container:

```
./nssetup.py create_ns --ns-name web1 --ns-ip 192.168.100.201
```

Destroy the namespace again:

```
./nssetup.py destroy_ns --ns-name web1
```

Destroy the bridge again, restore the IP of the testbed interface:

```
./nssetup.py destroy_bridge
```

## Parameters

### create_bridge

```
phy_ip                IP address of the physical interface to bind the
                      virtual interfaces to.

-n BR_NAME, --br-name BR_NAME
                      Name of the bridge to create.
```

### destroy_bridge

```
  -n BR_NAME, --br-name BR_NAME
                        Name of the bridge to create.
```

### create_ns

```
-n BR_NAME, --br-name BR_NAME
                      Name of the bridge to connect the namespace to.
-s NS_NAME, --ns-name NS_NAME
                      Name of the namespace to create.
-i NS_IP, --ns-ip NS_IP
                      IP of the interface in the namespace.
-m NS_NETMASK, --ns-netmask NS_NETMASK
                      Netmask (in bits) of the interface in the namespace.
```

### Start application in namespace

```
ip netns exec python3 ....
```

### destroy_ns

```
-s NS_NAME, --ns-name NS_NAME
                      Name of the namespace to destroy.
```