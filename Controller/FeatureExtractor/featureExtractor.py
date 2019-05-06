import subprocess
import csv
import json
import handlers
import saveToDb
import time
import sys

sys.path.insert(0, '../Enforcer')
import enforcer

# Relative path to config files
featureUnitsFile = '../Config/featureUnits.json' 
featuresFile="../Config/features.csv"

# Read configuration 
def readConfig():
        featuresToExtract = []
        featureUnits = {}
        
        # Read the features to be extracted
        with open(featuresFile, 'rb') as csvfile:
                csvReader = csv.reader(csvfile, delimiter=',', quotechar='|')
                for row in csvReader:
                                featuresToExtract.append({"name":row[0], "type":row[1]})
        # Read the feature units
        with open(featureUnitsFile) as jsonFile:
                featureUnits = json.load(jsonFile)

        return featuresToExtract, featureUnits

# The PCAPs from the Gateway are converted to JSON forward by server.sh.
# This function parses this JSON and extracts desired features.
# The JSONs may be incomplete, and this function contains logic to handle that case
def receivePCAP():
    p = subprocess.Popen("./server.sh")
    # Allow the pcap.json file to be created by server.sh script, before attempting to read it.
    time.sleep(1)
    packetLines=[]
    packetCounter=1
    braceOpenCount=0
    nextReadPos=0
    with open("./pcap.json", "r") as pcapJson:
            while True:
                    line = pcapJson.readline()
                    if line!=None and len(line)>0:
                            nextReadPos=pcapJson.tell()+1
                            if(len(packetLines) == 0):
                                    if (line.find('{') > -1):
                                            braceOpenCount=1
                                            packetLines.append(line)
                            elif(len(packetLines)!=0 and braceOpenCount!=0):
                                            if(line.find('{') > -1):
                                                    braceOpenCount+=1
                                            if(line.find('}') > -1):
                                                    braceOpenCount-=1
                                            packetLines.append(line)
                            if(braceOpenCount==0 and len(packetLines)!=0):
                                           # We have a complete JSON, representing a packet, that can be processed
                                           packetString="".join(packetLines)
                                           packetObj=json.loads(packetString)
                                           processPackets(packetObj,packetCounter)
                                           packetCounter+=1
                                           packetLines[:] = []
                                           braceOpenCount=0        
            
                    else:
                            # If the pcap json file does not have anything new, then sleep and dont occupy the CPU
                            time.sleep(1)

# Process the JSON representation of a packet - extract the desired features and test if the packet is valid
def processPackets(packet, counter):
        deviceId, features = extractFeatures(packet)
        isAnomaly = False
        printFeatures(deviceId, features)
        isAnomaly=enforcer.testPacket(deviceId, features, True)
        saveToDb.asFile(deviceId, counter,json.dumps(features))
        counter += 1

# Prints out extracted features
def printFeatures(deviceId, features):
        displayStr = "Device: " + deviceId + ", Features: "
        for feature in features:
                displayStr += feature + " = "
                if features[feature] is not None:
                        if feature == 'interArrivalTime':
                                displayStr += '%0.3f' % features[feature]
                        else:
                                displayStr += str(features[feature])
                        displayStr += " " + featureUnits[feature] + ", "
                else :
                        displayStr += 'undefined,'
        print(displayStr)

# Extract the desired features from the packet
def extractFeatures(packet):
    global featuresToExtract
    packetFeatures={}
    ip = handlers.extract("ip", "",  packet)
    for feature in featuresToExtract:
        featureValue = handlers.extract(feature["name"], ip, packet)
        packetFeatures[feature["name"]] = featureValue
    return ip, packetFeatures

featuresToExtract, featureUnits = readConfig()

while 1:
    receivePCAP()
