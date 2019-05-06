#!/bin/bash

# Create containers
lxc launch ubuntu:16.04 IoTSensor1
lxc launch ubuntu:16.04 IoTSensor2
lxc launch ubuntu:16.04 IoTGateway
lxc launch ubuntu:16.04 IoTServer
lxc launch ubuntu:16.04 Controller

# Create bridges
lxc network create sensor1Gw ipv4.address=192.168.100.1/24 ipv4.nat=true
lxc network create sensor2Gw ipv4.address=192.168.200.1/24 ipv4.nat=true
lxc network create gwControl ipv4.address=192.168.10.1/24 ipv4.nat=true
lxc network create gwServer ipv4.address=192.168.20.1/24 ipv4.nat=true

# Remove old interfaces, if present, before adding new ones
lxc config device remove IoTSensor2 ifGateway 
lxc config device remove IoTGateway ifSensor1 
lxc config device remove IoTGateway ifSensor2 
lxc config device remove IoTGateway ifServer
lxc config device remove IoTGateway ifController
lxc config device remove IoTServer ifGateway
lxc config device remove Controller ifGateway

# Delete existing default gateways configured by lxd
lxc exec IoTSensor1 route del default
lxc exec IoTSensor2 route del default
lxc exec IoTServer route del default

# Add interfaces in containers
lxc config device add IoTSensor1 ifGateway nic name=ifGateway nictype=bridged parent=sensor1Gw 
lxc config device add IoTSensor2 ifGateway nic name=ifGateway nictype=bridged parent=sensor2Gw 
lxc config device add IoTGateway ifSensor1 nic name=ifSensor1 nictype=bridged parent=sensor1Gw 
lxc config device add IoTGateway ifSensor2 nic name=ifSensor2 nictype=bridged parent=sensor2Gw 
lxc config device add IoTGateway ifServer nic name=ifServer nictype=bridged parent=gwServer 
lxc config device add IoTGateway ifController nic name=ifController nictype=bridged parent=gwControl 
lxc config device add IoTServer ifGateway nic name=ifGateway nictype=bridged parent=gwServer
lxc config device add Controller ifGateway nic name=ifGateway nictype=bridged parent=gwControl


# Set IP addresses to interfaces
lxc exec IoTSensor1 ifconfig ifGateway    192.168.100.10/24
lxc exec IoTSensor2 ifconfig ifGateway    192.168.200.10/24
lxc exec IoTServer  ifconfig ifGateway    192.168.20.20/24
lxc exec IoTGateway ifconfig ifSensor1    192.168.100.20/24
lxc exec IoTGateway ifconfig ifSensor2    192.168.200.20/24
lxc exec IoTGateway ifconfig ifServer     192.168.20.10/24
lxc exec IoTGateway ifconfig ifController 192.168.10.10/24
lxc exec Controller ifconfig ifGateway    192.168.10.20/24

# Setup static routes at Server, towards the Sensors, via the Gateway
lxc exec IoTServer ip route add 192.168.100.0/24 via 192.168.20.10 dev ifGateway
lxc exec IoTServer ip route add 192.168.200.0/24 via 192.168.20.10 dev ifGateway

# Setup default routes at Sensors towards the Gateway,
lxc exec IoTSensor1 route add default gw 192.168.100.20
lxc exec IoTSensor2 route add default gw 192.168.200.20


# Push scripts to the Containers
lxc file push ../IoTSensor/sensor.py IoTSensor1/root/
lxc file push ../IoTSensor/sensor.py IoTSensor2/root/
lxc file push ../IoTSensor/hackSensor.py IoTSensor2/root/
lxc file push ../IoTSensor/unhackSensor.py IoTSensor2/root/
lxc file push ../IoTSensor/hackSensor.py IoTSensor1/root/
lxc file push ../IoTSensor/unhackSensor.py IoTSensor1/root/
lxc file push ../IoTServer/server.py IoTServer/root/
lxc file push ../IoTGateway/sniffer.sh IoTGateway/root/
lxc file push ./setupGateway.sh IoTGateway/root/
lxc file push ./unblockAllSensors.sh IoTGateway/root/
lxc file push ./setupController.sh Controller/root/




