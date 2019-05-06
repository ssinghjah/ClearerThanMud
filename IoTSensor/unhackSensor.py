#!/usr/bin/env python3
import socket                  

TCP_IP = '127.0.0.1'
TCP_PORT = 8008
BUFFER_SIZE = 1024
MESSAGE = "Kindly behave normally."

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))
s.send(MESSAGE.encode('utf-8'))
s.close()

