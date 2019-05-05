#!/usr/bin/python

# Author: Jose Castillo Lema <josecastillolema@gmail.com>

"Main module of the mini-nfv framework"

import sys
import netaddr
import yaml
import subprocess
from collections import defaultdict
from jinja2 import Template
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
# from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.node import OVSController
from mininet.node import RemoteController
from mininet.cli import CLI, output
from mn_wifi.node import UserAP
from mn_wifi.cli import CLI_wifi
from mn_wifi.net import Mininet_wifi

MAX_VDUS = 100
VNFD = {}
VNFS = []
VNFFGS = []
VNFFGD = {}
HOSTS = []
SWITCH = {}
PORTS = defaultdict(list)
INC = 10

def parse_tosca(path):
    "Parses the yaml file corresponding to the TOSCA vnfd ou vnnffgg template."
    try:
        yaml_file = open(path, 'r')
    except IOError:
        print 'File does not exist'
        return None
    content = yaml_file.read()
    parsed_file = yaml.load(content)
    return parsed_file

def configure_network(net, vnfd, host):
    "Configures the networks."
    if MULTSWITCHES:
        i = 1
        switchs = []
        topo = vnfd['topology_template']['node_templates']
        while topo.has_key('VL%s' % i):
            if topo['CP%s' % i]['properties'].has_key('ip_address'):
                ip_address = topo['CP%s' % i]['properties']['ip_address']
                switch_name = 's' + ip_address
                switchs.append(switch_name)
                if not SWITCH.has_key(switch_name):
                    SWITCH[switch_name] = net.addSwitch(switch_name[:10])
            else:
                if topo['VL%s' % i]['properties']['network_name'] == 'net_mgmt':
                    switch_name = 's' + '192.168.120.0'
                    switchs.append(switch_name[:10])
                    if not SWITCH.has_key(switch_name):
                        SWITCH[switch_name] = net.addSwitch(switch_name[:10])
                elif topo['VL%s' % i]['properties']['network_name'] == 'net0':
                    switch_name = 's' + '10.10.0.0'
                    switchs.append(switch_name[:10])
                    if not SWITCH.has_key(switch_name):
                        SWITCH[switch_name] = net.addSwitch(switch_name[:10])
                elif topo['VL%s' % i]['properties']['network_name'] == 'net1':
                    switch_name = 's' + '10.10.1.0'
                    switchs.append(switch_name[:10])
                    if not SWITCH.has_key(switch_name):
                        SWITCH[switch_name] = net.addSwitch(switch_name[:10])
                elif topo['VL%s' % i]['properties'].has_key('cidr'):
                    cidr = netaddr.IPNetwork(topo['VL%s' % i]['properties']['cidr'])
                    if topo['node_templates']['VL%s' % i]['properties'].has_key('start_ip'):
                        start_ip = netaddr.IPNetwork(topo['VL%s' % i]['properties']['start_ip'])
                        switch_name = 's%s' % start_ip.network
                        switchs.append(switch_name[:10])
                        if not SWITCH.has_key(switch_name):
                            SWITCH[switch_name] = net.addSwitch(switch_name[:10])
                    else:
                        switch_name = 's%s' % cidr.ip
                        switchs.append(switch_name[:10])
                        if not SWITCH.has_key(switch_name):
                            SWITCH[switch_name] = net.addSwitch(switch_name[:10])
            i += 1

        host1 = net.getNodeByName(host)
        for i in switchs:
            net.addLink(i, host1)
            PORTS[i].append(host1)
    else:
        host1 = net.getNodeByName(host)
        net.addLink('s1', host1)
        PORTS['s1'].append(host1)

def configure_host(net, vnfd, host):
    "Configures the host."
    host1 = net.getNodeByName(host)
    i = 1
    global INC
    topo = vnfd['topology_template']['node_templates']
    while topo.has_key('VL%s' % i):
        if topo['CP%s' % i]['properties'].has_key('ip_address'):
            ip_address = topo['CP%s' % i]['properties']['ip_address']
        else:
            if topo['VL%s' % i]['properties']['network_name'] == 'net_mgmt':
                ip_address = '192.168.120.%s/24' % INC
                INC += 1
            elif topo['VL%s' % i]['properties']['network_name'] == 'net0':
                ip_address = '10.10.0.%s/24' % INC
                INC += 1
            elif topo['VL%s' % i]['properties']['network_name'] == 'net1':
                ip_address = '10.10.1.%s/24' % INC
                INC += 1
            elif topo['VL%s' % i]['properties'].has_key('cidr'):
                cidr = netaddr.IPNetwork(topo['VL%s' % i]['properties']['cidr'])
                if topo['VL%s' % i]['properties'].has_key('start_ip'):
                    start_ip = topo['VL%s' % i]['properties']['start_ip']
                    ip_address = '%s/%s' % (start_ip, cidr.prefixlen)
                else:
                    ip_address = str(cidr.ip+INC)+'/%s' % cidr.prefixlen
                    INC += 1
            else:
                ip_address = '10.0.%s.%s/24' %(i, INC)
                INC += 1
        host1.setIP(ip_address, intf=host+'-eth%s' % (i-1))
        c =  netaddr.IPNetwork(ip_address)
        host1.cmd('ip route add default via %s' % netaddr.IPAddress(c.first+1))
        PORTS[host].append(ip_address)
        if topo['CP%s' % i]['properties'].has_key('mac_address'):
            mac_address = topo['CP%s' % i]['properties']['mac_address']
            host1.setMAC(mac_address, intf=host+'-eth%s' % (i-1))
        i += 1

def configure_host2(net, ips, host):
    "Configures the host."
    host1 = net.getNodeByName(host)
    for i in range(len(ips)):
        ip_address = netaddr.IPNetwork(ips[i])
        ip_address_final = '%s/%s' % (ip_address.ip, ip_address.prefixlen)
        host1.setIP(ip_address_final, intf=host+'-eth%s' % i)
        host1.cmd('ip route add default via %s' % netaddr.IPAddress(ip_address.first+1))
        PORTS[host].append(ip_address)
        PORTS[host].append(ip_address_final)

def list_ports(self, line):
    "List all ports."
    if len(line.split()) != 0:
        output('Use: list_ports\n')
        return None
    for i in PORTS:
        if i[0] == 's':
            output('%s ' % i)
            for j in PORTS[i]:
                output ('%s ' % j.IP())
        else:
            output(i, PORTS[i])
        output('\n')
    return None

def find_port(ip_address):
    "Returns the host of the port if the port exists."
    for i in PORTS:
        if ip_address in PORTS[i]:
            return i
    return None

def find_port2(ip_address):
    "Returns the number of the port in the switch if the port exists."
    for i in PORTS:
        if i[0] == 's':
            port_number=1
            for j in PORTS[i]:
                if j.IP() == str(ip_address):
                    return port_number
                port_number += 1
    return None

def find_port3(host, ip_src, ip_dst):
    "Returns the IP of the host if the host exists."
    if host in PORTS:
        for i in PORTS[host]:
            i2 = netaddr.IPNetwork(i)
            if i2.cidr == ip_src.cidr or i2.cidr == ip_dst.cidr:
                return i2.ip
    return None

def add_host(self, line):
    "Adds a host to the mininet topology."
    net = self.mn
    if len(line.split()) < 1:
        output('Use: add_host <HOST-NAME> [<IP1/masc> <IP2/masc> ...]\n')
        return None
    host_name = line.split()[0]
    if host_name in HOSTS:
        output('<HOST-NAME> already in use\n')
        return None
    ips = line.split()[1:]
    if MULTSWITCHES:
        i = 1
        switchs = []
        for i in ips:
            try:
                ip_address = netaddr.IPNetwork(i)
            except netaddr.core.AddrFormatError:
                output('IP format not valid: ' + i + '\n')
                output('Use: add_host <HOST-NAME> [<IP1/masc> <IP2/masc> ...]\n')
                return None
            switch_name = 's%s' % ip_address.network
            if not SWITCH.has_key(switch_name):
                SWITCH[switch_name] = net.addSwitch(switch_name[:10])
            switchs.append(switch_name)
        host = net.addHost(host_name)
        HOSTS.append(host_name)
        for i in switchs:
            net.addLink(i[:10], host)
            PORTS[i[:10]].append(host)
    else:
        host = net.addHost(host_name)
        HOSTS.append(host_name)
        net.addLink('s1', host)
        PORTS['s1'].append(host)

    configure_host2(net, ips, host_name)
    return None

def cloud_init(net, vnfd, host_name):
    "Configures the networks."
    host = net.getNodeByName(host_name)
    cloudinit = vnfd['topology_template']['node_templates']['VDU1']['properties']['user_data']
    output('*** Initializing VDU ' + host_name + ' ...\n')
    host.cmdPrint(cloudinit)

# VNFD

def vnfd_create(self, line, jinja=False):
    "Creates vnfd from template."
    if len(line.split()) != 3 or line.split()[0] != '--vnfd-file':
        output('Use: vnfd_create --vnfd-file <yaml file path> <VNFD-NAME>\n')
        return None
    file_path = line.split()[1]
    vnfd = parse_tosca(file_path)
    if vnfd:
        vnfd_name = line.split()[2]
        if not VNFD.has_key(vnfd_name):
            VNFD[vnfd_name] = vnfd
        else:
            output('<VNFD-NAME> already in use\n')
    return None

def vnfd_create_jinja(self, line):
    "Creates vnfd using jinja template."
    vnfd_create(self, line, jinja=True)
    return None

def vnfd_list(self, line):
    "Lists all VNFD uploaded."
    if line:
        output('Use: vnfd_list\n')
        return None
    for i in VNFD:
        output('%s: %s\n' % (i, VNFD[i]['description']))
    #output('%s' % VNFD.keys() + '\n')
    return None

def vnfd_delete(self, line):
    "Deletes a given vnfd."
    if len(line.split()) != 1:
        output('Use: vnfd_delete <VNFD-NAME>\n')
        return None
    vnfd_name = line.split()[0]
    if VNFD.has_key(vnfd_name):
        del VNFD[vnfd_name]
    else:
        output('<VNFD-NAME> does not exist\n')
    return None

def vnfd_template_show(self, line):
    "Shows the template of a given vnfd."
    if len(line.split()) != 1:
        output('Wrong number or arguments\n')
        output('Use: vnfd_template_show <VNFD-NAME>\n')
        return None
    vnfd_name = line.split()[0]
    output(('%s' % VNFD[vnfd_name])+'\n')
    return None

# VNF

def vnf_create(self, line, jinja=False):
    "Creates vnf from vnfd previously created or directly from template."
    net = self.mn
    if len(line.split()) != 3 or line.split()[0] not in ['--vnfd-name', '--vnfd-file', '--vnfd-template']:
        output('Use: vnf_create --vnfd-name <VNFD-NAME> <VNF-NAME>\n')
        output('     vnf_create --vnfd-file <yaml file path> <VNFD-NAME>\n')
        output('     vnf_create --vnfd-template <yaml file path> <VNFD-NAME>\n')
        return None
    if line.split()[0] in ['--vnfd-file', '--vnfd-template']:
        file_path = line.split()[1]
        vnfd = parse_tosca(file_path)
        if jinja:
            template=Template(str(vnfd))
            print 'template jinja',
            print "{}".format(template.render(net.values))
    else:  # --vnfd-name
        vnfd_name = line.split()[1]
        vnfd = VNFD[vnfd_name]
    if vnfd:
        vnf_name = line.split()[2]
        if vnf_name in VNFS:
            output('<VNF-NAME> already in use\n')
            return None
        VNFS.append(vnf_name)
        net.addHost(vnf_name)
        configure_network(net, vnfd, vnf_name)

        configure_host(net, vnfd, vnf_name)
        if vnfd['topology_template']['node_templates']['VDU1']['properties'].has_key('user_data'):
            cloud_init(net, vnfd, vnf_name)
        return None
    return None

def vnf_create_jinja(self, line):
    "Creates vnf using jinja templates."
    vnf_create(self, line, jinja=True)
    return None

def vnf_list(self, line):
    "Lists all vnfs created."
    output('%s' % VNFS + '\n')

def vnf_delete(self, line):
    "Deletes a given vnf."
    net = self.mn
    if len(line.split()) != 1:
        output('Use: vnf_delete <VNF-NAME>\n')
        return None
    vnf_name = line.split()[0]
    if vnf_name in VNFS:
        del VNFS[VNFS.index(vnf_name)]
        # net.delNode(vnf_name)
        # AttributeError: 'Mininet' object has no attribute 'delNode'
    else:
        output('<VNF-NAME> does not exist\n')
    return None

# VNFFG

def configure_vnffg(net, vnffg, vnffg_name, binds):
    "NFV Orchestration function."
    criteria = vnffg['topology_template']['node_templates']['Forwarding_path1']['properties']['policy']['criteria']
    path = vnffg['topology_template']['node_templates']['Forwarding_path1']['properties']['path'][0]
    vnfs = vnffg['topology_template']['groups']['VNFFG1']['properties']['constituent_vnfs']
    if vnfs[0] != binds[0]:
        output('vnf-mapping <' + binds[0] + '> not defined in template\n')
        return
    if len(criteria) != 1:
        for i in range(len(criteria)):
            if criteria[i].has_key('network_src_port_id'):
                port_id = criteria[i]['network_src_port_id']
            elif criteria[i].has_key('ip_src_prefix'):
                ip_src = criteria[i]['ip_src_prefix']
                if not find_port(ip_src):
                    output('ip_src_prefix ,' + ip_src + '> not exists in current environment\n')
                    return
                ip_src = netaddr.IPNetwork(ip_src)
                #ip_address_final = '%s/%s' % (ip_address.ip, ip_address.prefixlen)
            elif criteria[i].has_key('ip_dst_prefix'):
                ip_dst = criteria[i]['ip_dst_prefix']
                if not find_port(ip_dst):
                    output('ip_dst_prefix ,' + ip_dst + '> not exists in current environment\n')
                    return
                ip_dst = netaddr.IPNetwork(ip_dst)
            elif criteria[i].has_key('ip_proto'):
                ip_proto = criteria[i]['ip_proto']
            elif criteria[i].has_key('destination_port_range'):
                port_range = criteria[i]['destination_port_range']
    else:
        if criteria[0].has_key('network_src_port_id'):
            port_id = criteria[0]['network_src_port_id']
        if criteria[0].has_key('ip_src_prefix'):
            ip_src = criteria[0]['ip_src_prefix']
            if not find_port(ip_src):
                output('ip_src_prefix ,' + ip_src + '> not exists in current environment\n')
                return
        if criteria[0].has_key('ip_dst_prefix'):
            ip_dst = criteria[0]['ip_dst_prefix']
            if not find_port(ip_dst):
                output('ip_dst_prefix ,' + ip_dst + '> not exists in current environment\n')
                return
        if criteria[0].has_key('ip_proto'):
            ip_proto = criteria[0]['ip_proto']
        if criteria[i].has_key('destination_port_range'):
            port_range = criteria[0]['destination_port_range']

    print 'vnfs0', binds[1], 'ip_src', ip_src, 'ip_dst', ip_dst
    vnf = binds[1]
    vnf = net.getNodeByName(vnf)

    forwarder = path['forwarder']
    port_dst = find_port2(ip_dst.ip)
    port_vnf = find_port2(find_port3(forwarder, ip_src, ip_dst))
    VNFFGS.append(vnffg_name)
    print ip_src.ip, find_port2(ip_src.ip), ip_dst.ip, port_dst, forwarder, port_vnf
    if MULTSWITCHES:
        #command = 'sudo ovs-ofctl mod-flows s192.168.1 ip,nw_src=192.168.120.1,actions=output:2,3'
        command2 = "ovs-ofctl add-flow s192.168.1 priority=1,arp,actions=flood"
        command = 'sudo ovs-ofctl mod-flows s192.168.1 ip,nw_src=%s,actions=output:%s,%s' % (ip_src.ip, port_dst, port_vnf)
        #command = 'sudo ovs-ofctl mod-flows s192.168.1 ip,nw_src=%s,actions=output:%s' % (ip_src.ip, port_vnf)
        #command2 = 'sudo ovs-ofctl mod-flows s192.168.1 in_port=%s,actions=output:%s' % (port_vnf, port_dst)
        #command3 = 'sudo ovs-ofctl mod-flows s192.168.1 arp,in_port="s192.168.1-eth4",vlan_tci=0x0000/0x1fff,dl_src=12:b9:d1:5d:26:5e,dl_dst=1e:29:c2:41:d5:02,arp_spa=192.168.120.2,arp_tpa=192.168.120.1,arp_op=2,actions=output:"s192.168.1-eth3"'
        s2 = subprocess.check_output(command2, shell=True)
        s = subprocess.check_output(command, shell=True)
        #s3 = subprocess.check_output(command2, shell=True)
        print s, s2
    else:
        vnf.cmdPrint('ip addr add %s/24 brd + dev %s-eth0' % (netaddr.IPAddress(netaddr.IPNetwork(ip_src).first+1), binds[1]))
        vnf.cmdPrint('ip addr add %s/24 brd + dev %s-eth0' % (netaddr.IPAddress(netaddr.IPNetwork(ip_dst).first+1), binds[1]))
        vnf.cmdPrint("echo 1 > /proc/sys/net/ipv4/ip_forward")
        #s1 = net.getNodeByName('s1')
        #s1.cmdPrint('ovs-ofctl add-flow s1 priority=1,arp,actions=flood')
        #s1.cmdPrint("ovs-ofctl add-flow s1 priority=65535,ip,dl_dst=00:00:00:00:01:00,actions=output:1")
        #s1.cmdPrint("ovs-ofctl add-flow s1 priority=10,ip,nw_dst=10.0.10.0/24,actions=output:2")
        #s1.cmdPrint("ovs-ofctl add-flow s1 priority=10,ip,nw_dst=10.0.20.0/24,actions=output:3")

def read_binding(binding):
    "Translates something in the form VNF:'vnf' into ('VNF', 'vnf')"
    return (binding.split(':')[0], binding.split(':')[1].replace("'", ''))

def vnffg_create(self, line, jinja=False):
    "Creates vnffg from previously defined vnffgd or directly from template."
    net = self.mn
    #if len(line.split()) != 7:
    #    print 'problema e tamanho'
    #    print line.split()[0]
    if len(line.split()) != 7 or line.split()[0] not in ['--vnffgd-name', '--vnffgd-template'] or line.split()[2] != '--vnf-mapping' or line.split()[4] != '--symmetrical':
        output('''Use: vnffg-create --vnffgd-name <vnffgd-name> --vnf-mapping <vnf-mapping>
                  --symmetrical <boolean> <vnffg-name>\n''')
        output('''     vnffg-create --vnffgd-template <vnffgd-template> --vnf-mapping <vnf-mapping>
                  --symmetrical <boolean> <vnffg-name>\n''')
        return None
    if line.split()[0] == '--vnffgd-template':
        file_path = line.split()[1]
        vnffg = parse_tosca(file_path)
        #print 'antes: ', vnffg
        if jinja:
            template=Template(str(vnffg))
            #print 'template jinja',
            #print "{}".format(template.render(net.values))
            vnffg = yaml.load("{}".format(template.render(net.values)))
            #print 'despues: ', vnffg
    else:  # --vnffg-name
        vnffg_name = line.split()[1]
        vnffg = VNFFGD[vnffg_name]
    binds = read_binding(line.split()[3])
    if vnffg:
        vnffg_name = line.split()[6]
        if vnffg_name in VNFFGS:
            output('<VNFFG-NAME> already in use\n')
            return None
        #VNFFGS.append(vnffg_name)
        configure_vnffg(net, vnffg, vnffg_name, binds)
        return None
    return None

def vnffg_create_jinja(self, line):
    "Creates vnffg using jinja templates."
    vnffg_create(self, line, jinja=True)
    return None

def vnffg_list(self, line):
    "Lists all vnffgs created."
    output('%s' % VNFFGS + '\n')

def vnffg_delete(self, line):
    "Deletes a given vnffg."
    net = self.mn
    if len(line.split()) != 1:
        output('Use: vnffg_delete <VNFFG-NAME>\n')
        return None
    vnffg_name = line.split()[0]
    if vnffg_name in VNFFGS:
        del VNFFGS[VNFFGS.index(vnffg_name)]
        # net.delNode(vnf_name)
        # AttributeError: 'Mininet' object has no attribute 'delNode'
    else:
        output('<VNFFG-NAME> does not exist\n')
    return None

def do_print(self, line):
    "Prints a given line."
    output(line + '\n')
    return None

if __name__ == '__main__':
    setLogLevel('info')
    usage = """Usage: mininfv [options]

The mininfv utility loads vNFs into Mininet networks from the command line.
It can create parametrized topologies, invoke the mininfv CLI, and run tests.

Options:
  -h, --help            show this help message and exit
  --controller=CONTROLLER
                        remote=RemoteController
  --multipleswitches    creates a individual switch for every L2 topo
  --wifi                integrates and lauchs mininet-wifi instead
    --container         name of the mininet-wifi container. If no present, defaults to mininet-wifi
    --ssh-user          name of the localhost user for mininet-wifi. If no present, defaults to root"""
    if len(sys.argv) > 2:
        sys.exit(usage)
    elif len(sys.argv) == 2:
        if (sys.argv[1] == '-h' or sys.argv[1] == '--help'):
            sys.exit(usage)
        elif sys.argv[1] == '--controller=remote':
            STANDALONE = False
        elif sys.argv[1] == '--multipleswitches':
            STANDALONE = True
            MULTSWITCHES = True
            print 'true'
        elif sys.argv[1] == '--wifi':
            WIFI = True
            STANDALONE = True
            MULTSWITCHES = False
            container = "mininet-wifi"
            ssh_user = "jose"
        else:
            sys.exit(usage)
    else:
        STANDALONE = True
        MULTSWITCHES = False
        WIFI = False

    #TOPO = MyTopo()
    # NET = Mininet(topo=topo, link=TCLink)
    if STANDALONE:
        NET = Mininet(link=TCLink, controller=OVSController)
    elif not WIFI:
        NET = Mininet(link=TCLink, controller=RemoteController)
    elif WIFI:
        NET = Mininet_wifi(container=container, ssh_user=ssh_user, docker=True)
    if not MULTSWITCHES:
        NET.addSwitch('s1')   
    NET.start()
    CLI.do_add_host = add_host
    CLI.do_list_ports = list_ports
    CLI.do_vnfd_create = vnfd_create
    CLI.do_vnfd_create_jinja = vnfd_create_jinja
    CLI.do_vnfd_list = vnfd_list
    CLI.do_vnfd_delete = vnfd_delete
    CLI.do_vnfd_template_show = vnfd_template_show
    CLI.do_vnf_create = vnf_create
    CLI.do_vnf_create_jinja = vnf_create_jinja
    CLI.do_vnf_list = vnf_list
    CLI.do_vnf_delete = vnf_delete
    CLI.do_vnffg_create = vnffg_create
    CLI.do_vnffg_create_jinja = vnffg_create_jinja
    CLI.do_vnffg_list = vnffg_list
    CLI.do_vnffg_delete = vnffg_delete
    CLI.do_print = do_print
    if not WIFI:
        CLI.prompt = 'mininfv> '
        CLI(NET)
    else:
        CLI_wifi(NET)
    NET.stop()
