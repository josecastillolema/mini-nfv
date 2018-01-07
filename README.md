# mini-nfv
Enables loading TOSCA templates into mininet, [Tacker](https://docs.openstack.org/tacker/pike/index.html) style.


Use
--------------
```
sudo ./mini-nfv.py
```

Network definition
--------------
If not specified otherwise, mini-nfv will create 3 standards networks:
- net_mgmt: 192.168.120.0/24
- net0: 10.10.0.0/24
- net1: 10.10.1.0/24

It is also possible to manually define the networks, in the Virtual Link (VL) definition, see [tosca-vnfd-network.yaml](https://github.com/josecastillolema/mini-nfv/blob/master/samples/vnfd/tosca-vnfd-network.yaml):
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
If not specified otherwise, mini-nfv will assign random IPs within the defined netwroks.
However, it is also possibly to manually define IP/MAC for a VNF, in the Connection Point (CP) definition, see [tosca-vnfd-mac-ip.yaml](https://github.com/josecastillolema/mini-nfv/blob/master/samples/vnfd/tosca-vnfd-mac-ip.yaml):
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
