#!/usr/bin/env python3
import socket

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

MY_RCV_IP = "192.168.20.20"
MY_RCV_PORT = 3000
SENSOR1IP = "192.168.100.10"
SENSOR2IP = "192.168.200.10"

sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) # UDP
sock.bind((MY_RCV_IP, MY_RCV_PORT))

# Receive UDP Datagrams and print them to console, using a different color for each of the two sensors
while True:
    data, addr = sock.recvfrom(1024)
    dataString = str(data)
    sourceIP = addr[0]
    if sourceIP == SENSOR1IP:
        color=bcolors.WARNING
        dataString = "Sensor 1: " + dataString
    elif sourceIP == SENSOR2IP:
        color=bcolors.OKBLUE
        dataString = "Sensor 2: " + dataString
    print(color + dataString + bcolors.ENDC)
