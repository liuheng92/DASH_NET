"""
author: Michael liu (michaelliubnu@163.com)
Dashnettopo is a class use minievents to introduce an topo for dash test or network speed control.
Using a json document to input two network cards and events.
Events include (bandwidth, loss, delay).
It will launch mininet and perform the events at the specific time of each event.
"""
import re
import json
import argparse
from minievents import Minievents
from mininet.log import setLogLevel, info, error
from mininet.clean import cleanup, sh
from mininet.util import quietRun, errRun
from mininet.link import Intf, TCLink
from mininet.node import Node

class Dashnettopo( object ):

    def __init__(self, minievents, config_json):
        self.net = minievents
        self.cmd = errRun
        self.link1 = None
        self.in_intf = str(config_json['in_intf'])
        self.out_intf = str(config_json['out_intf'])

    #Recommend: use before restart your program
    #Cleanup Mininet and OpenFlow
    def cleanup_mn(self):
        cleanup()

    #Recommend: use after stop your program
    #kill dhcp
    def kill_dhcp(self):
        output = re.findall('\d+', sh("netstat -uap | grep dhcpd | awk '{ print $6 }'"))
        if output:
            sh('kill %s' % output[0])

    #Configure subnet by editing /etc/dhcp/dhcpd.conf
    #and /etc/default/isc-dhcp-server
    def config_dhcp_subnet(self):
        # edit /etc/dhcp/dhcpd.conf
        info('make sure you did not have subnet configure'
             ' in your /etc/dhcp/dhcpd.conf file!\n')

        dhcp_conf = '/etc/dhcp/dhcpd.conf'
        #using special line to determine if the configuration exists
        #TODO(michael):if there is a better idea to do this
        line = '\n#michael special code 012345678\n'
        config = open( dhcp_conf ).read()
        if ( line ) not in config:
            info( '*** Adding subnet config to ' + dhcp_conf + '\n' )
            #TODO(michael):ugly ip address and dns address
            with open( dhcp_conf, 'a' ) as f:
                f.write( line )
                f.write( 'subnet 192.168.1.0 netmask 255.255.255.0\n'
                         '{\n'
                         '\trange 192.168.1.2 192.168.1.10;\n'  #ip range
                         '\toption routers 192.168.1.1;\n'      #gateway
                         '\toption domain-name-servers 10.210.97.123,10.210.97.21,10.210.97.61;\n'  #dns
                         '}\n' )

    # get link node name(link : node <--> switch)
    def get_node_intfname(self):
        if not self.link1:
            error('please build a link first (use TClink())')
            exit(1)
        if type(self.link1.intf1.node) == Node:
            return self.link1.intf1.name
        return self.link1.intf2.name

    #clean last dhcp config(delete line which includes "INTERFACES=")
    def clean_dhcp_inf(self, dhcp_default):
        with open(dhcp_default, 'r') as f:
            lines = f.readlines()
            # print(lines)
        enter_key = ['\n', '\r\n', '\r']
        with open(dhcp_default, 'w') as f_w:
            for line in lines:
                if "INTERFACES=" in line:
                    continue
                #delete line if there are two "enter"
                if (line in enter_key) and (lines[lines.index(line)+1] in enter_key):
                    continue
                f_w.write(line)

    def config_dhcp_intf(self):
        #edit /etc/default/isc-dhcp-server
        info('make sure you did not have interface configure'
             ' in your /etc/default/isc-dhcp-server file!\n')
        dhcp_default = '/etc/default/isc-dhcp-server'
        self.clean_dhcp_inf(dhcp_default)
        #use node's port, not switch's port
        #like: line = '\nINTERFACES="root-eth0"\n'
        node_intfname = self.get_node_intfname()
        line = '\nINTERFACES="%s"\n' % node_intfname
        info( '*** Adding "' + line.strip() + '" to ' + dhcp_default + '\n' )
        with open( dhcp_default, 'a' ) as f:
            f.write( line )

    #test dhcp if it can start(0:yes, 1:no)
    def test_dhcp(self):
        self.kill_dhcp()
        (out, err, returncode) = errRun('dhcpd')
        if returncode:
            error('\n##### dhcpd error! #####\n')
            error(err)
            return 1
        return 0

    #Configure NAT
    def config_nat(self):
        # Cleanup iptables rules
        # TODO(michael): not sure . Is it safe ?
        self.cmd('iptables -X')
        self.cmd('iptables -F')

        # Create default entries for unmatched traffic
        self.cmd( 'iptables -P INPUT ACCEPT' )
        self.cmd( 'iptables -P OUTPUT ACCEPT' )
        self.cmd( 'iptables -P FORWARD DROP' )

        # Configure NAT
        node_intfname = self.get_node_intfname()
        self.cmd('iptables -t nat -A POSTROUTING -o %s -j MASQUERADE' % self.in_intf)
        self.cmd('iptables -A FORWARD -i %s -o %s -m state --state RELATED,ESTABLISHED -j ACCEPT' % (self.in_intf,node_intfname))
        self.cmd('iptables -A FORWARD -i %s -o %s -j ACCEPT' % (node_intfname,self.in_intf))

        # Instruct the kernel to support forwarding
        self.cmd('sysctl net.ipv4.ip_forward=1')

        # Probably need to restart network-manager to be safe -
        # hopefully this won't disconnect you
        self.cmd('service network-manager restart')

    def checkIntf(self, hwintf):
        "Make sure hardware interface exists and is not configured."
        if (' %s:' % hwintf) not in quietRun('ip link show'):
            error('Error:', hwintf, 'does not exist!\n')
            exit(1)
        ips = re.findall(r'\d+\.\d+\.\d+\.\d+', quietRun('ifconfig ' + hwintf))
        if ips:
            error('Error:', hwintf, 'has an IP address,'
                                  'and is probably in use!\n')
            exit(1)

    #define the topo for traffic control
    def define_dashnet_topo(self):
        info('*** Adding controller\n')
        self.net.addController(name='c0')

        info('*** Add switches\n')
        s1 = self.net.addSwitch('s1')

        #no ip address for this interface
        self.checkIntf(self.out_intf)
        s1_inf = Intf(self.out_intf, node=s1)
        # s1_inf.ifconfig('0.0.0.0')

        root = Node('root', inNamespace=False)

        info("*** Creating links\n")
        self.link1 = TCLink(root, s1)
        self.net.add_dict_link('link1', self.link1)

    def start(self):
        #1.clean all the config
        self.cleanup_mn()
        #2.create dashnet topo
        self.define_dashnet_topo()
        #3.configure dhcp for local net IP address
        self.config_dhcp_subnet()
        #4.configure dhcp for virtual interface
        self.config_dhcp_intf()
        node_intfname = self.get_node_intfname()
        # TODO(michael):ugly ip address
        self.cmd('ifconfig %s 192.168.1.1/24' % node_intfname)
        #5.configure NAT
        self.config_nat()
        #6.start dhcpd
        if self.test_dhcp():
            exit(1)
        self.cmd('dhcpd %s' % node_intfname)
        #7.start minievents
        self.net.start()

def load_dash_minievents(json_path=None):
    if json_path:
        json_file = json.load(open(json_path))
        return json_file
    else:
        error('must input dash_minievents.json !')
        exit(1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--events", default="dash_minievents.json", help="json file with event descriptions")
    args = parser.parse_args()
    json_file = load_dash_minievents(args.events)
    net = Minievents(topo=None, build = False, events_json=json_file['events'])
    dnt = Dashnettopo(net, config_json=json_file['config'])
    setLogLevel('info')
    dnt.start()
    dnt.kill_dhcp()