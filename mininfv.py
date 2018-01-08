#!/usr/bin/python

# Author: Jose Castillo Lema <josecastillolema@gmail.com>
# Author: Alberico Castro <>

"Main module of the mini-nfv framework"

#import json
#import logging
#import re
import yaml
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
#from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.node import OVSController
#from mininet.node import RemoteController
from mininet.cli import CLI

MAX_VDUS = 100

def parse_vnfd(path):
    "Parses the yaml file corresponding to the vnfd"
    yaml_file = open(path, 'r')
    content = yaml_file.read()
    parsed_file = yaml.load(content)
    return parsed_file['topology_template']['node_templates']

def parse_vnffgd(path):
    "Parses the yaml file corresponding to the vnffgd"
    return path

class MyTopo(Topo):
    "Creates the mininet topology"
    def __init__(self, **opts):
        Topo.__init__(self, **opts)
        # Add hosts and switches
        hosts = []
        i = 1
        while VNFD.has_key('VDU%s' % i):
            num_cpus = 1
            try:
                num_cpus = VNFD['VDU%s'%i]['capabilities']['nfv_compute2']['properties']['num_cpus']
                if num_cpus >= 16:
                    num_cpus = 16
            except KeyError:
                pass
            hosts.append(self.addHost('h%s' % i, cpu=1./(16-num_cpus)))
            i += 1
        #host1 = self.addHost('h1')
        #host2 = self.addHost('h2', ip='10.0.0.2/24', cpu=.5/k)
        #host3 = self.addHost('h3', ip='10.0.5.2/24')
        switchs = []
        i = 1

        while VNFD.has_key('VL%s' % i):
            switchs.append(self.addSwitch('s%s' % i))
            i += 1
        #switch1 = self.addSwitch('s1')
        #switch2 = self.addSwitch('s2')

        # links Add
        for switch in switchs:
            for host in hosts:
                self.addLink(switch, host)

        #self.addLink(switch1, host1)
        #self.addLink(switch1, host2)
        #self.addLink(switch2, host1)
        #self.addLink(switch2, host3)

        # self.addLink(switch1, host2, 2, 1)
        # self.addLink(switch1, host2, 3, 2)
        #self.addLink(switch1, host2, 2, 1, intfName1='h2-eth1')
        # self.addLink(s2, s3, 2, 3, bw=10, delay='200ms', jitter='2ms', loss=10,
        #              max_queue_size=1000, use_htb=True)

def configure_network(net):
    "Configures the networks."
    host1 = net.getNodeByName('h1')
    i = 1
    while VNFD.has_key('VL%s' % i):
        if VNFD['VL%s' % i]['properties']['network_name'] == 'net_mgmt':
            host1.setIP('192.168.120.1/24', intf='h1-eth%s' % (i-1))
        elif VNFD['VL%s' % i]['properties']['network_name'] == 'net0':
            host1.setIP('10.10.0.1/24', intf='h1-eth%s' % (i-1))
        elif VNFD['VL%s' % i]['properties']['network_name'] == 'net1':
            host1.setIP('10.10.1.1/24', intf='h1-eth%s' % (i-1))
        else:
            host1.setIP('10.0.%s.1/24', intf='h1-eth%s' % (i-1))
        i += 1
    # host1.setIP('10.0.1.10', intf='h1-eth0')
    # host1.setMAC('00:00:00:00:00:10', intf='h1-eth0')
    # host1.setIP('10.0.5.11', intf='h1-eth1')
    # host1.setIP('10.0.6.11', intf='h1-eth2')
    # host1.setMAC('00:00:00:00:00:11', intf='h1-eth1')

def inicializa_red():
    "Create network and run simple performance test"
    topo = MyTopo()
    #net = Mininet(topo=topo, link=TCLink, controller=RemoteController)
    #net = Mininet(topo=topo, link=TCLink)
    net = Mininet(topo=topo, link=TCLink, controller=OVSController)
    configure_network(net)

    net.start()
    host1 = net.getNodeByName('h1')

    print '*** Initializing VDUs ...'
    host1.cmdPrint('ls')

    CLI(net)
    net.stop()

if __name__ == '__main__':
    print 'main'
    VNFD = parse_vnfd('samples/vnfd/tosca-vnfd-hello-world.yaml')
    setLogLevel('info')
    inicializa_red()
