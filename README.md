# mini-nfv
Enables loading [OASIS TOSCA](http://docs.oasis-open.org/tosca/TOSCA/v1.0/TOSCA-v1.0.html) templates into mininet, [Tacker](https://docs.openstack.org/tacker/pike/index.html) style.


Use
--------------
```
$ sudo ./mininfv.py
*** Configuring hosts

*** Starting controller

*** Starting 0 switches

*** Starting CLI:
mininet> vnfd_create --vnfd-file samples/vnfd/tosca-vnfd-userdata.yaml vnfd-userdata
mininet> vnfd_list
['vnfd-userdata']
mininet> vnfd_delete vnfd-userdata
mininet> vnfd_list
[]
```

Characteristics
--------------
Mini-nfv supports:
- network definition via VL
- IP/mac definition via CP
- emulation of num CPUs and flavor properties through Mininet's CPULimitedHost
- cloud-init scripts

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
