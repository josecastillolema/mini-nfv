#!/usr/bin/python

# Author: Jose Castillo Lema <josecastillolema@gmail.com>
# Author: Alberico Castro <>

"Main module of the mini-nfv framework"

# import json
# import logging
# import re
import netaddr
import yaml
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
# from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.node import OVSController
# from mininet.node import RemoteController
from mininet.cli import CLI, output

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

def configure_network(net, vnfd, host):
    "Configures the networks."
    switch = {}
    i = 1
    while vnfd.has_key('VL%s' % i):
        if vnfd['CP%s' % i]['properties'].has_key('ip_address'):
            ip_address = vnfd['CP%s' % i]['properties']['ip_address']
            switch_name = 's' + ip_address
            if not switch.has_key(switch_name):
                switch[switch_name] = net.addSwitch(switch_name[:10])
        else:
            if vnfd['VL%s' % i]['properties']['network_name'] == 'net_mgmt':
                switch_name = 's' + '192.168.120.0'
                if not switch.has_key(switch_name):
                    switch[switch_name] = net.addSwitch(switch_name[:10])
            elif vnfd['VL%s' % i]['properties']['network_name'] == 'net0':
                switch_name = 's' + '10.10.0.0'
                if not switch.has_key(switch_name):
                    switch[switch_name] = net.addSwitch(switch_name[:10])
            elif vnfd['VL%s' % i]['properties']['network_name'] == 'net1':
                switch_name = 's' + '10.10.1.0'
                if not switch.has_key(switch_name):
                    switch[switch_name] = net.addSwitch(switch_name[:10])
            elif vnfd['VL%s' % i]['properties'].has_key('cidr'):
                cidr = netaddr.IPNetwork(vnfd['VL%s' % i]['properties']['cidr'])
                if vnfd['VL%s' % i]['properties'].has_key('start_ip'):
                    start_ip = netaddr.IPNetwork(vnfd['VL%s' % i]['properties']['start_ip'])
                    switch_name = 's%s' % start_ip.network
                    if not switch.has_key(switch_name):
                        switch[switch_name] = net.addSwitch(switch_name[:10])
                else:
                    switch_name = 's%s' % cidr.ip
                    if not switch.has_key(switch_name):
                        switch[switch_name] = net.addSwitch(switch_name[:10])
        i += 1

    host1 = net.getNodeByName(host)
    for i in switch:
        net.addLink(switch[i], host1)

def configure_host(net, vnfd, host):
    "Configures the host."
    host1 = net.getNodeByName(host)
    i = 1
    while vnfd.has_key('VL%s' % i):
        if vnfd['CP%s' % i]['properties'].has_key('ip_address'):
            ip_address = vnfd['CP%s' % i]['properties']['ip_address']
            host1.setIP(ip_address, intf=host+'-eth%s' % (i-1))
        else:
            if vnfd['VL%s' % i]['properties']['network_name'] == 'net_mgmt':
                host1.setIP('192.168.120.10/24', intf=host+'-eth%s' % (i-1))
            elif vnfd['VL%s' % i]['properties']['network_name'] == 'net0':
                host1.setIP('10.10.0.10/24', intf=host+'-eth%s' % (i-1))
            elif vnfd['VL%s' % i]['properties']['network_name'] == 'net1':
                host1.setIP('10.10.1.10/24', intf=host+'-eth%s' % (i-1))
            elif vnfd['VL%s' % i]['properties'].has_key('cidr'):
                cidr = netaddr.IPNetwork(vnfd['VL%s' % i]['properties']['cidr'])
                if vnfd['VL%s' % i]['properties'].has_key('start_ip'):
                    start_ip = vnfd['VL%s' % i]['properties']['start_ip']
                    host1.setIP(start_ip+'/%s' % cidr.prefixlen, intf=host+'-eth%s' % (i-1))
                else:
                    host1.setIP(str(cidr.ip+10)+'/%s' % cidr.prefixlen, intf=host+'-eth%s' % (i-1))
            else:
                host1.setIP('10.0.%s.10/24' %i, intf=host+'-eth%s' % (i-1))
        if vnfd['CP%s' % i]['properties'].has_key('mac_address'):
            mac_address = vnfd['CP%s' % i]['properties']['mac_address']
            host1.setMAC(mac_address, intf=host+'-eth%s' % (i-1))
        i += 1

def cloud_init(net, vnfd, host_name):
    "Configures the networks."
    host = net.getNodeByName(host_name)
    cloudinit = vnfd['VDU1']['properties']['user_data']
    output('*** Initializing VDU ' + host_name + ' ...\n')
    host.cmdPrint(cloudinit)

def add_host(self, line):
    "add_host <HOST-NAME> [<IP1> <IP2s> ...]"
    net = self.mn
    if len(line.split()) >= 1:
        output('Wrong number or arguments\n')
        output('Use: add_host <HOST-NAME> [<IP1> <IP2s> ...]\n')
        return None
    host_name = line.split()[0]
    output('creating host ' + host_name + '\n')
    net.addHost(host_name)
    return None

def vnfd_create(self, line):
    "vnfd-create --vnfd-file <yaml file path> <VNFD-NAME>"
    net = self.mn
    if len(line.split()) != 3:
        output('Wrong number or arguments\n')
        output('Use: vnfd-create --vnfd-file <yaml file path> <VNFD-NAME>\n')
        return None
    if line.split()[0] != '--vnfd-file':
        output('Use: vnfd-create --vnfd-file <yaml file path> <VNFD-NAME>\n')
        return None
    file_path = line.split()[1]
    vnf_name = line.split()[2]
    output('parsing ' + file_path + '\n')
    vnfd = parse_vnfd(file_path)
    net.addHost(vnf_name)
    configure_network(net, vnfd, vnf_name)
    configure_host(net, vnfd, vnf_name)
    if vnfd['VDU1']['properties'].has_key('user_data'):
        cloud_init(net, vnfd, vnf_name)
    return None

def vnf_create(self, line):
    "vnf-create --vnfd-name <VNFD-FILE-NAME> <VNF-NAME>"
    net = self.mn
    if len(line.split()) != 3:
        output('Wrong number or arguments\n')
        output('Use: vnfd-create --vnfd-file <yaml file path> <VNFD-NAME>\n')
        return None
    if line.split()[0] != '--vnfd-file':
        output('Use: vnfd-create --vnfd-file <yaml file path> <VNFD-NAME>\n')
        return None
    file_path = line.split()[1]
    vnf_name = line.split()[2]
    output('parsing ' + file_path + '\n')
    vnfd = parse_vnfd(file_path)
    net.addHost(vnf_name)
    configure_network(net, vnfd, vnf_name)
    configure_host(net, vnfd, vnf_name)
    if vnfd['VDU1']['properties'].has_key('user_data'):
        cloud_init(net, vnfd, vnf_name)
    return None

def vnfd_list(self, line):
    "vnfd-list"
    print line

if __name__ == '__main__':
    setLogLevel('info')
    # TOPO = MyTopo()
    # NET = Mininet(topo=topo, link=TCLink, controller=RemoteController)
    # NET = Mininet(topo=topo, link=TCLink)
    # NET = Mininet(topo=TOPO, link=TCLink, controller=OVSController)
    NET = Mininet(link=TCLink, controller=OVSController)
    NET.start()

    #print '*** Initializing VDUs ...'
    # host1.cmdPrint('ls')

    CLI.do_add_host = add_host
    CLI.do_vnfd_create = vnfd_create
    CLI.do_vnf_create = vnf_create
    CLI.do_vnfd_list = vnfd_list
    CLI(NET)
    NET.stop()
