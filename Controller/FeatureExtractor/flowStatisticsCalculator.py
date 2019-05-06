#!/usr/bin/env python
import datetime

# Dictionary of device vs last arrival instant
packetArrivalInstants={}
def interArrivalTime(deviceId, packetArrivalInstant):
    interArrivalTime=None
    if deviceId in packetArrivalInstants:
        interArrivalTime=packetArrivalInstant - packetArrivalInstants[deviceId]
    packetArrivalInstants[deviceId]=packetArrivalInstant
    return interArrivalTime
    
