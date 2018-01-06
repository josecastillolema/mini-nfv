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
#from mininet.node import RemoteController
from mininet.cli import CLI

MAX_VDUS = 100

def parse_file(path):
    "Parses the yaml file"
    yaml_file = open(path, 'r')
    content = yaml_file.read()
    parsed_file = yaml.load(content)
    # print parsed_file
    # print yaml.dump(parsed_file)
    # print parsed_file['description']
    # print parsed_file['topology_template']['node_templates']['VDU1']
    i = 1
    while parsed_file['topology_template']['node_templates'].has_key('VDU'+str(i)):
        print 'yes'
        i += 1

class MyTopo(Topo):
    "Creates the mininet topology"
    def __init__(self, n=2, **opts):
        Topo.__init__(self, **opts)

	# Add hosts and switches
    host1 = self.addHost('h1')
    s1 = self.addSwitch('s1', dpid='00:00:00:00:00:01')

	# links Add
    self.addLink(s1, host1, 1, 1)
    # self.addLink(s2, s3, 2, 3, bw=10, delay='200ms', jitter='2ms', loss=10,
    #              max_queue_size=1000, use_htb=True)

def inicializa_red():
    "Create network and run simple performance test"
    topo = MyTopo()
    #net = Mininet(topo=topo, link=TCLink, controller=RemoteController)
    net = Mininet(topo=topo, link=TCLink)
    net.start()
    host1 = net.getNodeByName('h1')

    print '*** cleaning ...'
    host1.cmdPrint('ls')

    print '*** initializing VDUs ...'
    # host1.cmdPrint('ls')

    CLI(net)
    net.stop()

if __name__ == '__main__':
    print 'main'
    parse_file('samples/tosca-vnfd-hello-world.yaml')
    setLogLevel('info')
    inicializa_red()
