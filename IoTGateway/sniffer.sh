#!/bin/bash
ControllerIP='192.168.10.20'
ControllerPort=5005
Sensor1If='ifSensor1'
Sensor1IP='192.168.100.10'
Sensor2IP='192.168.200.10'
Sensor2If='ifSensor2'
ServerIP='192.168.20.20'
tshark -i $Sensor2If -f "src net $Sensor2IP and dst net $ServerIP" -i $Sensor1If -f "src net $Sensor1IP and dst net $ServerIP" -w - -F pcap | nc $ControllerIP $ControllerPort
