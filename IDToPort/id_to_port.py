import socket

receive_ip="192.168.1.109"
receive_port=1802

iot_gateway_ip="192.168.1.39"
iot_gateway_port=1509

send_ip="192.168.1.109"

receivesock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
receivesock.bind((receive_ip,receive_port))
while True:
        data,addr=receivesock.recvfrom(1024)
        print "received message is :",data
        data.find
        source_port=2000+int(data[12:data.find(",")])
        data=data[data.find(",")+2:]
        sock1=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        sock1.bind((send_ip,source_port))
        sock1.sendto(data,(iot_gateway_ip,iot_gateway_port))
        data,addr=sock1.recvfrom(1024)
        print "received message:",data
        sock1.close()
