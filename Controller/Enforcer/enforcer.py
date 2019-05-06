#!/usr/bin/env python
import subprocess
import csv
import json
import time
import numpy as np
import os
from scipy.spatial import distance
import emailer
import datetime
import socket

normalBehaviourDir = '../Learning/NormalBehaviour/'
normalBehaviourFile = 'normalBehaviour.json'
# If the observation's distance from a centroid is greater than the DISTANCE_THRESHOLD, the observation is considered abnormal. The distance is in terms of standard deviations
DISTANCE_THRESHOLD=1.0
devicesStatus={}

# Enum for colors - used to print colored text to console
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def exit():
	pass

# Read the normal behaviour file
def readNormalBehaviour():
        normalBehaviours={}
        deviceIds=[folder for folder in os.listdir(normalBehaviourDir) if os.path.isdir(os.path.join(normalBehaviourDir, folder))]
        for deviceId in deviceIds:
                deviceNormalBehaviourSpec = os.path.join(normalBehaviourDir + deviceId, normalBehaviourFile)
                with open(deviceNormalBehaviourSpec) as f:
                        normalBehaviour = json.load(f)
                        normalBehaviours[deviceId] = normalBehaviour
        return normalBehaviours


def readNormalBehaviourYang():
    pass

# Applies an IP table rule at the Gateway to block the misbehaving device
def takeAction(deviceName):
	global deviceStatus
	if not deviceName in devicesStatus or devicesStatus[deviceName] is not 'blocked':
		print(bcolors.FAIL + "The Controller is blocking " + str(deviceName) + bcolors.ENDC)
		devicesStatus[deviceName] = 'blocked'                
		p = subprocess.Popen("ssh root@192.168.10.10 'iptables -I FORWARD -s " + deviceName + " -j DROP'" , stdout=subprocess.PIPE, shell=True) 


# Check if the observation is normal or abnormal
def testPacket(deviceName, packetFeatures, bTakeAction):
	isPacketAnomaly=False
	for feature in packetFeatures:
                if packetFeatures[feature] is None:
                        return False
                    
	if deviceName in normalBehaviours:
                normalBehaviour = normalBehaviours[deviceName]
                for clusteringType in normalBehaviour['normalClusterCentroids']:
                        isAnomalyForthisClusteringType=True
                        features=clusteringType.split("_")
                        normalCentroids=normalBehaviour['normalClusterCentroids'][clusteringType]
                        featureValues=[]
                        for feature in features:
                                featureValue=packetFeatures[feature]
                                if normalBehaviour['stds'][feature] != 0:
                                        standardizedFeatureValue=(featureValue-normalBehaviour['means'][feature])/(normalBehaviour['stds'][feature])
                                else:
                                        standardizedFeatureValue=(featureValue-normalBehaviour['means'][feature])
                                featureValues.append(standardizedFeatureValue)
                        
                                for normalCentroid in normalCentroids:
                                        distanceFromCentroid = distance.euclidean(featureValues, normalCentroid)
#                                        print(distanceFromCentroid)
#                                        print(DISTANCE_THRESHOLD)
                                        if(distanceFromCentroid < DISTANCE_THRESHOLD):
                                                isAnomalyForthisClusteringType=False
                                                break
#					print(isAnomalyForthisClusteringType)
#                                        print("-------------------------")
                                if isAnomalyForthisClusteringType:
                                        isPacketAnomaly=True
                                        break
                if not isPacketAnomaly:
                    devicesStatus[deviceName] = 'unblocked'

                if bTakeAction and isPacketAnomaly:
                        takeAction(deviceName)
                        
	return isPacketAnomaly

normalBehaviours = readNormalBehaviour()
