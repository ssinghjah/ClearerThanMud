#!/usr/bin/env python
import os
DB_DIR_PATH="./database/"

def asFile(deviceName, packetCounter, features):
    # Check if file database directory already exists for the device. If not, create it
    deviceDbDir = DB_DIR_PATH + deviceName
    if not os.path.isdir(deviceDbDir):
        os.mkdir(deviceDbDir)
    f = open(deviceDbDir + "/packet" + str(packetCounter)+".json","w+")
    f.write(features)
    f.close()
    
