Dash-net:A class use minievents to introduce an topo for dash test or network speed control.
========================================================

depend on Minievents(Mininet) 2.2.0

## What is Mininet?

Mininet emulates a complete network of hosts, links, and switches
on a single machine.  To create a sample two-host, one-switch network,
just run:

  `sudo mn`

Mininet is useful for interactive development, testing, and demos,
especially those using OpenFlow and SDN.  OpenFlow-based network
controllers prototyped in Mininet can usually be transferred to
hardware with minimal changes for full line-rate execution.

## What is Minievents?

Minievents is a Framework build over Mininet to introduce an event generator.
Events are changes in a mininet network at specific times. 

Events in Minievents are defined in an external json document.
Up to now the implemented events are TCP and UDP traffic (iperf) and link 
properties modification (delay, bandwidth).

## How to config and run?
### config
Cause it is related to hardware config, so please see my blog 
https://www.jianshu.com/p/c0cecf819eab


### run

Just run from the project root directory:

  `sudo python dashnettopo.py`

This command will use *dash_minievents.json* as event source file.
The source file have two big part :
one is about two networkcards name, in_intf represents the card which connect to internet
or local net,(you should use ifconfig to checkout your networkcards name and modify the first part)
other part is defining events. 
The events define a network speed limit starting at second 0 (0.5Mbps bandwidth), and  modified at second 5 (50 Mbps bandwidth), at second 30 (3 Mbps bandwidth), second 45 (1Mbps bandwidth) and second 50 (10Mbps and 100ms delay) and second 55 (100% loss) and second 60 (10Mbps bandwidth) and second 70 (2Mbps bandwidth) and second 70 (3Mbps bandwidth). The network is stopped at second 105.

## Json event file format and events
The dash_minievents.json is an example of the json definition of events for minievents 
Framework. The file should be an array of Json objets (the events) with the following members:

* time: time in seconds since launch when the event should happen.
* type: event type. Up to now, the following event types are present
  * editLink: edit Link properties.
  * stop: stop the network
* params: parameters for the event.

The events are:

The *editLink* event modifies the properties of a link and takes the next parameters:
* link: virtual link between node and switch
* loss: percentage of packet loss in the link
* bw: link bandwidth in Mbits/sec
* delay: in milliseconds

## Author

* Michael liu

Sina Weibo

michaelliubnu@163.com

