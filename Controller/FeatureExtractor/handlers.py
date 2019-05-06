#!/usr/bin/env python
import flowStatisticsCalculator

def bandwidth(packet):
    bandwidth = float(packet['_source']['layers']['loratap']['loratap.channel']['loratap.channel.bandwidth'])
    if bandwidth == 4:
        bandwidth = 500
    elif bandwidth == 1:
        bandwidth = 125
    return bandwidth

def snr(packet):
    snr = float(packet['_source']['layers']['loratap']['loratap.rssi']['loratap.rssi.snr'])
    return snr

def frequency(packet):
    frequency = float(packet['_source']['layers']['loratap']['loratap.channel']['loratap.channel.frequency'])
    return frequency

def sf(packet):
    sf = float(packet['_source']['layers']['loratap']['loratap.channel']['loratap.channel.sf'])
    return sf

def interArrivalTime(deviceId, packet):
    packetArrivalInstant = float(packet['_source']['layers']['frame']['frame.time_relative'])
    interArrivalTime = flowStatisticsCalculator.interArrivalTime(deviceId, packetArrivalInstant)
    return interArrivalTime
    
def frameLength(packet):
    frameLength = int(packet['_source']['layers']['frame']['frame.len'])
    return frameLength

def mac(packet):
    mac = packet['_source']['layers']['eth']['eth.src']
    return mac

def ip(packet):
    ip = packet['_source']['layers']['ip']['ip.src']
    return ip

def deviceAddress(packet):
    deviceAddress = packet['_source']['layers']['lorawan']['lorawan.fhdr']['lorawan.fhdr.devaddr']
    return deviceAddress
    
def extract(feature, deviceName, packet):
    featureValue=""
    if(feature == 'snr'):
        featureValue = snr(packet)
    elif(feature == 'frequency'):
        featureValue = frequency(packet)
    elif(feature == 'spreadingFactor'):
        featureValue = sf(packet)
    elif(feature == 'interArrivalTime'):
        featureValue = interArrivalTime(deviceName, packet)
    elif(feature == 'frameLength'):
        featureValue = frameLength(packet)
    elif(feature == "mac"):
        featureValue = mac(packet)
    elif(feature == "ip"):
        featureValue = ip(packet)
    elif(feature == "deviceAddress"):
        featureValue = deviceAddress(packet)
    elif(feature == "bandwidth"):
        featureValue = bandwidth(packet)
    return featureValue
