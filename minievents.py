"""
minievents is a Framework over Mininet to introduce an event generator.
Events are changes in mininet network at a specific time. The events are defined in a json document.
Implemented events are traffic generation (iperf) and link variations
(bandwidth, loss, delay) during a mininet launch.
It will launch mininet and perform the events at the specific time of each event
"""

import time
import json
import argparse
import os
from time import sleep

from mininet.minisched import scheduler
from mininet.cli import CLI
# from mininet.topo import SingleSwitchTopo
# from mininet.log import setLogLevel, info, debug
from mininet.log import info, debug, error
from mininet.net import Mininet
# from mininet.node import OVSController, DefaultController, Host, OVSKernelSwitch
from mininet.node import DefaultController, Host, OVSKernelSwitch
# from mininet.link import TCLink, Intf, Link
from mininet.link import Intf, Link

__author__ = 'Carlos Giraldo'
__copyright__ = "Copyright 2014, AtlantTIC - University of Vigo"
__credits__ = ["Carlos Giraldo"]
__license__ = "GPL"
__version__ = "2.2.0"
__maintainer__ = "Carlos Giraldo"
__email__ = "carlos.giraldo@gti.uvigo.es"
__status__ = "Prototype"

class Minievents(Mininet):
    def __init__(self, topo=None, switch=OVSKernelSwitch, host=Host,
                 controller=DefaultController, link=Link, intf=Intf,
                 build=True, xterms=False, cleanup=False, ipBase='10.0.0.0/8',
                 inNamespace=False,
                 autoSetMacs=False, autoStaticArp=False, autoPinCpus=False,
                 listenPort=None, waitConnected=False, events_json=None):
        super(Minievents, self).__init__(topo=topo, switch=switch, host=host, controller=controller,
                                         link=link, intf=intf, build=build, xterms=xterms, cleanup=cleanup,
                                         ipBase=ipBase, inNamespace=inNamespace, autoSetMacs=autoSetMacs,
                                         autoStaticArp=autoStaticArp, autoPinCpus=autoPinCpus,
                                         listenPort=listenPort,
                                         waitConnected=waitConnected)
        #added by michael
        self.dict_links = {}
        self.scheduler = scheduler(time.time, time.sleep)
        if events_json:
            # json_file = json.load(open(events_file))
            #modified by michael
            self.load_events(events_json)
        else:
            error('events_json should not be none, please checkout your dash_minievents.json!')
            exit(1)

    #added by michael
    def add_dict_link(self, dict_link_key, dict_link_value):
        self.dict_links[dict_link_key] = dict_link_value
        print self.dict_links

    def load_events(self, json_events):
        # event type to function correspondence
        event_type_to_f = {'editLink': self.editLink, 'iperf': self.iperf, 'ping': self.ping, 'stop': self.stop}
        for event in json_events:
            debug("processing event: time {time}, type {type}, params {params}\n".format(**event))
            event_type = event['type']
            self.scheduler.enter(event['time'], 1, event_type_to_f[event_type], kwargs=event['params'])

    # EVENT COMMANDS
    def delLink(self, src, dst):
        # TODO This code should be tested
        info('{time}:deleting link from {src} to {dst}\n'.format(time=time.time(), src=src, dst=dst))
        n1, n2 = self.get(src, dst)
        intf_pairs = n1.connectionsTo(n2)
        for intf_pair in intf_pairs:
            n1_intf, n2_intf = intf_pair
            info('{time}:deleting link from {intf1} and {intf2}\n'.format(time=time.time(), intf1=n1_intf.name,
                                                                          intf2=n2_intf.name))
            n1_intf.link.delete()
            self.links.remove(n1_intf.link)
            del n1.intfs[n1.ports[n1_intf]]
            del n1.ports[n1_intf]
            del n1.nameToIntf[n1_intf.name]

            n2_intf.delete()
            del n2.intfs[n2.ports[n2_intf]]
            del n2.ports[n2_intf]
            del n2.nameToIntf[n2_intf.name]

    # def editLink(self, **kwargs):
    #     """
    #     Command to edit the properties of a link between src and dst.
    #     :param kwargs: named arguments
    #         src: name of the source node.
    #         dst: name of the destination node.
    #         bw: bandwidth in Mbps.
    #         loss: packet loss ratio percentage.
    #         delay: delay in ms.
    #     """
    #     n1, n2 = self.get(kwargs['src'], kwargs['dst'])
    #     intf_pairs = n1.connectionsTo(n2)
    #     info('***editLink event at t={time}: {args}\n'.format(time=time.time(), args=kwargs))
    #     for intf_pair in intf_pairs:
    #         n1_intf, n2_intf = intf_pair
    #         n1_intf.config(**kwargs)
    #         n2_intf.config(**kwargs)

    #modified by michael
    def editLink(self, **kwargs):
        """
        Command to edit the properties of a link between src and dst.
        :param kwargs: named arguments
            link: name of the link.
            bw: bandwidth in Mbps.
            loss: packet loss ratio percentage.
            delay: delay in ms.
        """
        link1 = self.dict_links[kwargs['link']]
        n1_intf, n2_intf = link1.intf1, link1.intf2
        n1_intf.config(**kwargs)
        n2_intf.config(**kwargs)

    def iperf(self, **kwargs):
        """
        Command to start a transfer between src and dst.
        :param kwargs: named arguments
            src: name of the source node.
            dst: name of the destination node.
            protocol: tcp or udp (default tcp).
            duration: duration of the transfert in seconds (default 10s).
            bw: for udp, bandwidth to send at in bits/sec (default 1 Mbit/sec)

        """
        kwargs.setdefault('protocol', 'TCP')
        kwargs.setdefault('duration', 10)
        kwargs.setdefault('bw', 100000)
        info('***iperf event at t={time}: {args}\n'.format(time=time.time(), args=kwargs))
        
        if not os.path.exists("output"):
            os.makedirs("output")
        server_output = "output/iperf-{protocol}-server-{src}-{dst}.txt".format(**kwargs)
        client_output = "output/iperf-{protocol}-client-{src}-{dst}.txt".format(**kwargs)
        info('output filenames: {client} {server}\n'.format(client=client_output, server=server_output))

        client, server = self.get(kwargs['src'], kwargs['dst'])
        iperf_server_cmd = ''
        iperf_client_cmd = ''
        if kwargs['protocol'].upper() == 'UDP':
             iperf_server_cmd = 'iperf -u -s -i 1'
             iperf_client_cmd = 'iperf -u -t {duration} -c {server_ip} -b {bw}'.format(server_ip=server.IP(), **kwargs)


        elif kwargs['protocol'].upper() == 'TCP':
             iperf_server_cmd = 'iperf -s -i 1'
             iperf_client_cmd = 'iperf -t {duration} -c {server_ip}'.format(server_ip=server.IP(), **kwargs)
        else :
            raise Exception( 'Unexpected protocol:{protocol}'.format(**kwargs))

        server.sendCmd('{cmd} &>{output} &'.format(cmd=iperf_server_cmd, output=server_output))
        info('iperf server command: {cmd} -s -i 1 &>{output} &\n'.format(cmd=iperf_server_cmd,
                                                                                output=server_output))
        # This is a patch to allow sendingCmd while iperf is running in background.CONS: we can not know when
        # iperf finishes and get their output
        server.waiting = False

        if kwargs['protocol'].lower() == 'tcp':
            while 'Connected' not in client.cmd(
                            'sh -c "echo A | telnet -e A %s 5001"' % server.IP()):
                info('Waiting for iperf to start up...\n')
                sleep(.5)

        info('iperf client command: {cmd} &>{output} &\n'.format(
            cmd = iperf_client_cmd, output=client_output))
        client.sendCmd('{cmd} &>{output} &'.format(
            cmd = iperf_client_cmd, output=client_output))
        # This is a patch to allow sendingCmd while iperf is running in background.CONS: we can not know when
        # iperf finishes and get their output
        client.waiting = False

    def ping(self, **kwargs):
        """
        Command to send pings between src and dst.\

        :param kwargs: named arguments
            src: name of the source node.
            dst: name of the destination node.
            interval: time between ping packet transmissions.
            count: number of ping packets.
        """
        kwargs.setdefault('count', 3)
        kwargs.setdefault('interval', 1.0)
        info('***ping event at t={time}: {args}\n'.format(time=time.time(), args=kwargs))
        
        if not os.path.exists("output"):
            os.makedirs("output")
        output = "output/ping-{src}-{dst}.txt".format(**kwargs)
        info('output filename: {output}\n'.format(output=output))

        src, dst = self.get(kwargs['src'], kwargs['dst'])
        ping_cmd = 'ping -c {count} -i {interval} {dst_ip}'.format(dst_ip=dst.IP(), **kwargs)

        info('ping command: {cmd} &>{output} &\n'.format(
            cmd = ping_cmd, output=output))
        src.sendCmd('{cmd} &>{output} &'.format(
            cmd = ping_cmd, output=output))
        # This is a patch to allow sendingCmd while ping is running in background.CONS: we can not know when
        # ping finishes and get its output
        src.waiting = False

    # modified by michael
    def start(self):
        super(Minievents, self).start()
        self.scheduler.run()
        # CLI(self) if self.scheduler.empty() else self.scheduler.run()

# if __name__ == '__main__':
#     parser = argparse.ArgumentParser()
#     parser.add_argument("--events",default="minievents.json", help="json file with event descriptions")
#     args = parser.parse_args()
#     setLogLevel('info')
#     net = Minievents(topo=SingleSwitchTopo(k=2), link=TCLink, controller=OVSController, events_file=args.events)
#     net.start()
