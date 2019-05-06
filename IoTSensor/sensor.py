#!/usr/bin/env python3
import socket                   
import time
import random
from threading import Thread, Lock

# The simulated sensor sends out a random latitude and longitude at fixed intervals of time, 3 sec by default.
# Once in a while, after every 3 messages by default, it sends out altitude along with the latitude and longitude, after a longer interval of time (4 sec by default).
#The behaviour is as: (lat,long)<-- 3 sec -->(lat,long)<-- 3 sec -->(lat,long)<-- 4 sec -->(alt,lat,long)<-- 3 sec -->(lat,long)<-- 3 sec -->(lat,long)<-- 3 sec -->(lat,long)<-- 4 sec -->(alt,lat,long) and so on.
# In this way, the normal behaviour of the sensor is to send shorter messages with shorter inter-arrival times, and longer messages with a larger inter-arrival time.

# Server's IP and Port
serverIP = '192.168.20.20'     	     
serverPort = 3000                    

# Global settings that define the simulated sensor's behaviour
# Interarrival time of shorter messages
shortInterArrivalTime=3
# After every "longPacketInterval" messages, send a longer message.
longPacketInterval=3
# Interarrival time of longer messages.
longInterArrivalTime=4
# Abnormal value of short interarrival time
abnormalShortInterArrivalTime=1.5
# Abnormal value of long interarrival time
abnormalLongInterArrivalTime=2

# Global variables
shortPacketCounter=0
messageIntervalMutex = Lock()
counter=1

# Sets the message interval to an abnormal value
def singOffkey():
 global abnormalShortInterArrivalTime, abnormalLongInterArrivalTime, shortInterArrivalTime, longInterArrivalTime, messageIntervalMutex
 messageIntervalMutex.acquire()
 # Set inter arrival times to abnormal values
 shortInterArrivalTime=abnormalShortInterArrivalTime 
 longInterArrivalTime=abnormalLongInterArrivalTime 
 print("Behaving abnormally")
 messageIntervalMutex.release()

def singInkey():
 global normalShortInterArrivalTime, normalLongInterArrivalTime, shortInterArrivalTime, longInterArrivalTime, messageIntervalMutex
 messageIntervalMutex.acquire()
 # Set inter arrival times to abnormal values
 shortInterArrivalTime=normalShortInterArrivalTime 
 longInterArrivalTime=normalLongInterArrivalTime 
 print("Behaving normally")
 messageIntervalMutex.release()

 
# Start sending messages to the Server
def startSinging():
	global counter, longPacketInterval, serverIP, serverPort, messageIntervalMutex
	while (1):
		messageIntervalMutex.acquire()
                # Longer messages are sent with a larger inter-arrival time
		if counter % longPacketInterval == 0:
			time.sleep(longInterArrivalTime)
		else:
    			time.sleep(shortInterArrivalTime)
		messageIntervalMutex.release()
                # Choose a random latitude and longitude
		latitude = round(random.uniform(38.0, 39.0), 3)
		longitude = round(random.uniform(-78.0, -80.0), 3)
                # Form the message to be sent
		messageStr = "Coordinates: " + " longitude: %.3f " % longitude + ", latitude: %.3f" % latitude
		if counter % longPacketInterval == 0:
                        # Choose a random altitude
			altitude = random.uniform(200.0, 300.0)
			messageStr += ", altitude: %.3f" % altitude
		messageByte = messageStr.encode('utf-8')
		counter += 1
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)            
		s.sendto(messageByte, (serverIP, serverPort))
		print('Sent ', repr(messageByte))
	s.close()

singingThread = Thread(target=startSinging)
singingThread.start()

# Create a TCP socket to receive messages from the hacker
TCP_IP = '127.0.0.1'
TCP_PORT = 8008
BUFFER_SIZE = 1024  
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)
conn, addr = s.accept()
while 1:
    data = conn.recv(BUFFER_SIZE)
    if not data: break
    dataStr = data.decode('utf-8')
    if dataStr == 'Kindly behave abnormally.':
     singOffkey()
    elif dataStr == 'Kindly behave normally.':
     singInkey()
conn.close()

