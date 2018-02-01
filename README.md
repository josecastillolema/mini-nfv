# mini-nfv
Mini-nfv is a framework for NFV Orchestration with a general purpose VNF Manager to deploy and operate Virtual Network Functions (VNFs) and Network Services on Mininet. It is based on ETSI MANO Architectural Framework.

Mini-nfv manages the life-cycle of a Virtual Network Function (VNF). Mini-nfv takes care of deployment, monitoring, scaling and removal of VNFs on Mininet.

Mini-nfv allows loading [OASIS TOSCA](http://docs.oasis-open.org/tosca/TOSCA/v1.0/TOSCA-v1.0.html) templates (V1.0 CSD 03) into Mininet, following an [OpenStack Tacker](https://docs.openstack.org/tacker/pike/index.html)'s alike workflow. Within Tacker's documentation it can be found a comprehensive [VNF Descriptor Template Guide](https://docs.openstack.org/tacker/pike/contributor/vnfd_template_description.html).

Mini-nfv uses TOSCA for VNF meta-data definition. Within TOSCA, mini-nfv uses NFV profile schema:
- TOSCA YAML
    - YAML Simple Profile: http://docs.oasis-open.org/tosca/TOSCA-Simple-Profile-YAML/v1.1/csprd02/TOSCA-Simple-Profile-YAML-v1.1-csprd02.html
- TOSCA NFV Profile:
    - Latest spec is available here: https://www.oasis-open.org/committees/document.php?document_id=56577&wg_abbrev=tosca
    - Current latest (as of Oct 2015) is: https://www.oasis-open.org/committees/download.php/56577/tosca-nfv-v1.0-wd02-rev03.doc

Use cases
--------------
In the OpenStack world, Tacker is the project implementing a generic VNFM and NFVO. At the input consumes Tosca-based templates, which are then used to spin up VMs on OpenStack. While it is true that today exist various tools that simplify the deployment of an OpenStack cloud (i.e.: devstack), deploying, configuring and managing OpenStack environments is still a time-consuming process with a considerable learning curve.

On the other hand, Mininet has shown itself as a great tool for agile network/SDN/NFV experimentation. The goal of this tool is to alleviate the developers’ tedious task of setting up a whole service chaining environment and let them focus on their own work (e.g., developing a particular VNF, prototyping, implementing an orchestration algorithm or a customized traffic steering).

VNF Manager Use
--------------
For the VNF Manager functionality:
```
$ sudo ./mininfv.py [--standalone]
```
The `--standalone` option runs mininet with its default controller. This way can be usefull to test the VNF Manager functionality with full connectivity between VNFs and hosts without the need of running POX. However, to have NFV Orchestration capabilites mininfv must be run without the `--standalone` option along with POX controller running in the background.

- **VNFD creation/listing/removal/template**
```
$ sudo ./mininfv.py
*** Configuring hosts
*** Starting controller
*** Starting 0 switches
*** Starting CLI:

mininet> vnfd_<TAB>
vnfd_create         vnfd_delete         vnfd_list           vnfd_template_show  

mininet> vnfd_create
Use: vnfd_create --vnfd-file <yaml file path> <VNFD-NAME>

mininet> vnfd_create --vnfd-file samples/vnfd/tosca-vnfd-userdata.yaml vnfd-userdata

mininet> vnfd_create --vnfd-file samples/vnfd/tosca-vnfd-hello-world.yaml vnfd-helloworld

mininet> vnfd_list
vnfd-helloworld: Demo example
vnfd-userdata: Demo with user-data

mininet> vnfd_template_show vnfd-userdata
{'VDU1': {'type': 'tosca.nodes.nfv.VDU.Tacker', 'properties': {'image': 'cirros-0.3.5-x86_64-disk', 'user_data_format': 'RAW', 'config': 'param0: key1\nparam1: key2\n', 'user_data': '#!/bin/sh\necho "my hostname is `hostname`" > /tmp/hostname\ndf -h > /tmp/diskinfo\n', 'mgmt_driver': 'noop'}, 'capabilities': {'nfv_compute': {'properties': {'mem_size': '512 MB', 'num_cpus': 1, 'disk_size': '1 GB'}}}}, 'CP1': {'type': 'tosca.nodes.nfv.CP.Tacker', 'requirements': [{'virtualLink': {'node': 'VL1'}}, {'virtualBinding': {'node': 'VDU1'}}], 'properties': {'anti_spoofing_protection': False, 'management': True, 'order': 0}}, 'VL1': {'type': 'tosca.nodes.nfv.VL', 'properties': {'network_name': 'net_mgmt', 'vendor': 'ACME'}}}

mininet> vnfd_delete vnfd-userdata

mininet> vnfd_list
vnfd-helloworld: Demo example
```
- **VNF creation/listing/removal**
```
$ sudo ./mininfv.py
*** Configuring hosts
*** Starting controller
*** Starting 0 switches
*** Starting CLI:

mininet> vnf_<TAB>
vnf_create  vnf_delete  vnf_list

mininet> vnf_create
Use: vnf_create --vnfd-name <VNFD-NAME> <VNF-NAME>
     vnf_create --vnfd-file <yaml file path> <VNFD-NAME>
     vnf_create --vnfd-template <yaml file path> <VNFD-NAME>
     
mininet> vnf_create --vnfd-file samples/vnfd/tosca-vnfd-userdata.yaml vnfUD
*** Initializing VDU vnf-userdata ...
*** user-data : ('#!/bin/sh\necho "my hostname is `hostname`" > /tmp/hostname\ndf -h > /tmp/diskinfo\n',)

mininet> nodes
available nodes are: 
c0 s192.168.1 vnfUD

mininet> vnf_list
['vnfUD']

mininet> vnfUD ifconfig
ud-eth0   Link encap:Ethernet  HWaddr 76:2c:90:f5:72:13  
          inet addr:192.168.120.10  Bcast:192.168.120.255  Mask:255.255.255.0
          inet6 addr: fe80::742c:90ff:fef5:7213/64 Scope:Link
          UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1
          RX packets:41 errors:0 dropped:10 overruns:0 frame:0
          TX packets:8 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:1000 
          RX bytes:6751 (6.7 KB)  TX bytes:648 (648.0 B)

mininet> vnf_delete vnf-userdata

mininet> nodes
available nodes are: 
c0 s192.168.1

mininet> vnf_list
[]
```
- **Adding hosts to the topology**
```
$ sudo ./mininfv.py --standalone
*** Configuring hosts
*** Starting controller
*** Starting 0 switches
*** Starting CLI:

mininet> add_host
Use: add_host <HOST-NAME> [<IP1/masc> <IP2/masc> ...]

mininet> add_host h1 10.0.0.11/24 20.0.0.11/24

mininet> nodes
available nodes are: 
c0 h1 s10.0.0.0 s20.0.0.0 ud

mininet> h1 ifconfig
h1-eth0   Link encap:Ethernet  HWaddr 3e:b2:ba:99:4e:dc  
          inet addr:10.0.0.11  Bcast:10.255.255.255  Mask:255.255.255.0
          inet6 addr: fe80::3cb2:baff:fe99:4edc/64 Scope:Link
          UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1
          RX packets:24 errors:0 dropped:1 overruns:0 frame:0
          TX packets:7 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:1000 
          RX bytes:3445 (3.4 KB)  TX bytes:578 (578.0 B)

h1-eth1   Link encap:Ethernet  HWaddr aa:08:cf:38:e8:d5  
          inet addr:20.0.0.10  Bcast:20.255.255.255  Mask:255.255.255.0
          inet6 addr: fe80::a808:cfff:fe38:e8d5/64 Scope:Link
          UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1
          RX packets:25 errors:0 dropped:1 overruns:0 frame:0
          TX packets:7 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:1000 
          RX bytes:3515 (3.5 KB)  TX bytes:578 (578.0 B)
          
mininet> add_host h2 10.0.0.12/24

mininet> switch s10.0.0.0 start

mininte> h1 ping h2
PING 10.0.0.12 (10.0.0.12) 56(84) bytes of data.
64 bytes from 192.168.120.2: icmp_seq=1 ttl=64 time=2.84 ms
```
NFV Orchestrator Use
--------------
In order to use the NFV Orchestrator [POX](https://github.com/noxrepo/pox) must be installed.
Place [`l3_mininfv.py`](https://github.com/josecastillolema/mini-nfv/blob/master/l3_mininfv.py) in the `pox/ext` folder.
To have NFV Orchestration capabilites mininfv must be run without the `--standalone` option allong with POX controller running in the background.
```
./pox.py l3_mininfv openflow.discovery                              or
./pox.py log.level --DEBUG l3_mininfv openflow.discovery           (debug mode)
```

- **VNFFG creation/listing/removal**
```
$ sudo ./mininfv.py
*** Configuring hosts
*** Starting controller
*** Starting 0 switches
*** Starting CLI:

mininet> vnf_create --vnfd-file samples/vnfd/tosca-vnfd-userdata.yaml vnfUD
*** Initializing VDU vnf-userdata ...
*** user-data : ('#!/bin/sh\necho "my hostname is `hostname`" > /tmp/hostname\ndf -h > /tmp/diskinfo\n',)

mininet> add_host http_cl 192.168.120.1/24

mininet> add_host http_sr 192.168.120.2/24

mininet> vnffg_<TAB>
vnffg_create  vnffg_delete  vnffg_list    

mininet> vnffg_create --vnffgd-template samples/vnffgd/tosca-vnffgd-helloworld2.yaml --vnf-mapping vnfd-helloworld:'vnfUD' --symmetrical false vnffg-sample

mininet> nodes
available nodes are: 
c0 h99 s99

mininet> vnf_list
['vnffg-sample]

mininet> vnffg_delete vnffg-sample

mininet> vnffg_list
[]
```

Characteristics
--------------
NFV Catalog
- VNF Descriptors
- Network Services Decriptors
- VNF Forwarding Graph Descriptors

VNF Manager
- Basic life-cycle of VNF (create/update/delete)
- Facilitate initial configuration of VNF

NFVO Orquestrator
- Templatized end-to-end Network Service deployment using decomposed VNFs
- VNF placement policy – ensure efficient placement of VNFs
- VNFs connected using an SFC - described in a VNF Forwarding Graph Descriptor

Mini-nfv supports:
- network definition via VL [&#8629;](https://github.com/josecastillolema/mini-nfv/blob/master/README.md#network-definition)
- IP/mac definition via CP [&#8629;](https://github.com/josecastillolema/mini-nfv/blob/master/README.md#ipmac-definition)
- emulation of num CPUs and flavor properties through Mininet's CPULimitedHost [&#8629;](https://github.com/josecastillolema/mini-nfv/blob/master/README.md#flavor-and-number-of-cpus)
- cloud-init scripts [&#8629;](https://github.com/josecastillolema/mini-nfv/blob/master/README.md#cloud-init)

Mini-nfv ignores:
- RAM and disk properties
- floating ips
- NUMA topology
- SRiOV

Network definition
--------------
If not specified otherwise, mini-nfv will create 3 standards networks:
- net_mgmt: 192.168.120.0/24
- net0: 10.10.0.0/24
- net1: 10.10.1.0/24

It is also possible to manually define the networks, within the Virtual Link (VL) definition, see [tosca-vnfd-network.yaml](https://github.com/josecastillolema/mini-nfv/blob/master/samples/vnfd/tosca-vnfd-network.yaml):
```
    VL2:
      type: tosca.nodes.nfv.VL
      properties:
        network_name: custom_net0
        vendor: Tacker
        ip_version: 4
        cidr: '20.0.0.0/24'
        start_ip: '20.0.0.50'
        end_ip: '20.0.0.200'
        gateway_ip: '20.0.0.1'
```

IP/MAC definition
--------------
If not specified otherwise, mini-nfv will assign random IPs within the defined networks.
However, it is also possibly to manually define IP/MAC for a VNF, within the Connection Point (CP) definition, see [tosca-vnfd-mac-ip.yaml](https://github.com/josecastillolema/mini-nfv/blob/master/samples/vnfd/tosca-vnfd-mac-ip.yaml):
```
    CP1:
      type: tosca.nodes.nfv.CP.Tacker
      properties:
        management: true
        mac_address: 6c:40:08:a0:de:0a
        ip_address: 10.10.1.12
        order: 0
        anti_spoofing_protection: false
      requirements:
        - virtualLink:
            node: VL1
        - virtualBinding:
            node: VDU1
```

Flavor and number of cpus
--------------
Mini-nfv emulates VNF resource configuration defined via num_cpus properties:
```
    VDU1:
      type: tosca.nodes.nfv.VDU.Tacker
      capabilities:
        nfv_compute:
          properties:
            num_cpus: 1
            mem_size: 512 MB
            disk_size: 1 GB
```
or through flavor:
```
    VDU1:
      type: tosca.nodes.nfv.VDU.Tacker
      properties:
        flavor: m1.tiny
```
Mini-nfv maps flavors and number of cpus property configuration into [Mininet's CPULimitedHost](http://mininet.org/api/classmininet_1_1node_1_1CPULimitedHost.html).
Currently, mini-nfv support the folowing flavors:
- m1.tiny: 1 cpu
- m1.small: 1 cpu
- m1.medium: 2 cpus
- m1.large: 4 cpus
- m1.xlargue: 8 cpus

Mini-nfv will assign 1/(8-num_cpus))) to each VNF.

Cloud-init
--------------
Mini-nfv supports VNFs configuration through user-data,  see [tosca-vnfd-userdata.yaml](https://github.com/josecastillolema/mini-nfv/blob/master/samples/vnfd/tosca-vnfd-userdata.yaml):
```
    VDU1:
      type: tosca.nodes.nfv.VDU.Tacker
      properties:
        user_data_format: RAW
        user_data: |
          #!/bin/sh
          echo "my hostname is `hostname`" > /tmp/hostname
          df -h > /tmp/diskinfo
```

Dependencies
--------------
Mini-nfv was tested on Ubuntu 14.04 and 16.04.

APT dependencies:
- mininet
- python-netaddr (it can also be installed via `pip`)
- python-yaml (it can also be installed via `pip`)
