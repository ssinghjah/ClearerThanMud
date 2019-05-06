#!/bin/bash                                                                                                                                    
PORT=5005
IP='192.168.10.20'

nc -l $IP $PORT | stdbuf -o0 tshark -r - -T json  > pcap.json

