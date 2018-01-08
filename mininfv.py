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
    # print parsed_file
    # print yaml.dump(parsed_file)
    # print parsed_file['description']
    # print parsed_file['topology_template']['node_templates']['VDU1']
    return parsed_file['topology_template']['node_templates']
    # i = 1
    # while parsed_file['topology_template']['node_templates'].has_key('VDU'+str(i)):
    #     print 'yes'
    #     i += 1

def parse_vnffgd(path):
    "Parses the yaml file corresponding to the vnffgd"
    return path

class MyTopo(Topo):
    "Creates the mininet topology"
    def __init__(self, k=2, **opts):
        Topo.__init__(self, **opts)
        # Add hosts and switches
        hosts = []
        i = 1
        #while VNFD.has_key('VDU'+str(i)):
        #    hosts.append(self.addHost('h'+str(i), ip='10.0.0.'+str(i)+'/24'))
        #    i += 1
        host1 = self.addHost('h1')
        host2 = self.addHost('h2', ip='10.0.0.2/24', cpu=.5/k)
        host3 = self.addHost('h3', ip='10.0.5.2/24')
        switch1 = self.addSwitch('s1')
        switch2 = self.addSwitch('s2')

        # links Add
        #for host in hosts:
        #    self.addLink(switch1, host, 1, 1)
        self.addLink(switch1, host1)
        self.addLink(switch1, host2)
        self.addLink(switch2, host1)
        self.addLink(switch2, host3)
        #host2 = net.getNodeByName('h2')
        #host2.cmd('ifconfig h2-eth1 5.5.5.5 netmask 255.255.255.0')
        # self.addLink(switch1, host2, 2, 1)
        # self.addLink(switch1, host2, 3, 2)
        #self.addLink(switch1, host2, 2, 1, intfName1='h2-eth1')
        # self.addLink(s2, s3, 2, 3, bw=10, delay='200ms', jitter='2ms', loss=10,
        #              max_queue_size=1000, use_htb=True)

def configure_network(net):
    host1 = net.getNodeByName('h1')
    host1.setIP('10.0.0.10', intf='h1-eth0')
    #host1.setMAC('00:00:00:00:00:10', intf='h1-eth0')
    host1.setIP('10.0.5.11', intf='h1-eth1')
    #host1.setMAC('00:00:00:00:00:11', intf='h1-eth1')

def inicializa_red():
    "Create network and run simple performance test"
    topo = MyTopo(k=4)
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
