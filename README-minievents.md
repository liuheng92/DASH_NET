Minievents: A mininet Framework to define events in mininet networks
========================================================

Minievents 2.2.0

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

## How to use Minievents?
Minievents is a child class of Mininet class. It adds events_file argument
to specify the json event document. There is no Minievent CLI up to now.

### Simple Example

The __main__ of the minievents.py provides a simple example of Minievents framework.
It is a single switch topology with two host.
Just run from the project root directory:

  `sudo python mininet/minievents.py`

This command will use *mininet/minievents.json* as event source file.
The events define a UDP and TCP streams starting at second 2, and the link between h1 and s1
is modified at second 5 (50 Mbps bandwidth), at second 10 (100 Mbps bandwidth and 100 ms delay), 
second 15 (100 % loss) and second 20 (0% loss and 500 Mbps bandwidth). The network is stopped at
second 30.
 
#### Check results
Next Graphs are generated with data extracted from iperf output:
![iperf TCP bandwidth](https://raw.githubusercontent.com/cgiraldo/minievents/master/output/tcp-bw.png)

## Json event file format and events
The minievents.json is an example of the json definition of events for minievents 
Framework. The file should be an array of Json objets (the events) with the following members:

* time: time in seconds since launch when the event should happen.
* type: event type. Up to now, the following event types are present
  * iperf: data traffic generator
  * editLink: edit Link properties.
  * stop: stop the network
* params: parameters for the event.

The events are:

The *editLink* event modifies the properties of a link and takes the next parameters:
* src: name of the source node of the link
* dst: name of the destination node of the link.
* loss: percentage of packet loss in the link
* bw: link bandwidth in Mbits/sec
* delay: in milliseconds
* (...) It should work with any of the config parameters of the Mininet TCIntf class.

The *iperf* event  creates a traffic stream between two hosts (TCP or UDP) and takes the next parameters:
* src: name of the source node
* dst: name of the destination node
* protocol: L4 protocol, should be TCP (default) or UDP.
* duration: duration of the traffic stream in seconds.
* bw (for UDP only): transmission in bits/sec.

The *iperf* client and server process outputs to the files:
`output/iperf-{TCP-UDP}-{client|server}-{src}-{dst}.txt`

## Authoring

* Carlos Giraldo
AtlantTIC Research Center, University of Vigo, Spain
http://atlanttic.uvigo.es/en/

