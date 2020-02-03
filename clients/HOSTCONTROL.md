# HostControl

HostControl provides an API for configuring the shaping/pacing on a host.

## QUICKSTART

To start the host controller:

`python3 -m control.HostControl`

See the REST API description for examples how to interact with the host controller.

# HostControl REST API

  * [GET /shaping/tc_show](#get-output-of-tc-qdisc-show): Get output of tc qdisc show
  * [PUT /shaping/fq/add](#add-a-fq-pacing-scheduler-to-an-interface): Add a FQ pacing scheduler to an interface
  
**Get output of tc qdisc show**
----
  Returns the raw output of *tc -s disc show*. 
  
* **URL**

    /shaping/tc_show
    
* **METHOD**

    `GET`

* **URL Params**
* **Success Response:**
* **Error Response**
* **Sample Call:**

    `curl http://192.168.10.21:8099/shaping/tc_show`

* **Example Body:**

   ```
   qdisc noqueue 0: dev lo root refcnt 2 
    Sent 0 bytes 0 pkt (dropped 0, overlimits 0 requeues 0) 
    backlog 0b 0p requeues 0 
   qdisc pfifo_fast 0: dev enp0s3 root refcnt 2 bands 3 priomap  1 2 2 2 1 2 0 0 1 1 1 1 1 1 1 1
    Sent 66229 bytes 529 pkt (dropped 0, overlimits 0 requeues 0) 
    backlog 0b 0p requeues 0 
   qdisc fq 8001: dev enp0s8 root refcnt 2 limit 10000p flow_limit 100p buckets 1024 orphan_mask 1023 quantum 3028 initial_quantum 15140 maxrate 15Mbit refill_delay 40.0ms 
    Sent 4914 bytes 19 pkt (dropped 0, overlimits 0 requeues 0) 
    backlog 0b 0p requeues 0 
     7 flows (7 inactive, 0 throttled)
     0 gc, 0 highprio, 0 throttled
 
   ```
   
   
**Add a FQ pacing scheduler to an interface**
----
  Add a FQ pacing scheduler to an interface.
  
* **URL**

    /shaping/fq/add
    
* **METHOD**

    `PUT`

* **URL Params**
* **Success Response:**
* **Error Response**
* **Sample Call:**

    `curl -H "Content-Type:application/json" -X PUT http://192.168.10.21:8099/shaping/fq/add -d '{"eth": "enp0s8", "maxrate": "15Mbit"}'`

* **Example Body:**
