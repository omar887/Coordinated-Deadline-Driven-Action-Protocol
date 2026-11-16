from socket import *
import struct
import time 
init = 1
data = 2
header = "!BBHIQQQ"
serverport = 5677
serversocket = socket(AF_INET,SOCK_DGRAM) #ipv4 and create a udp socket
serversocket.bind(('',serverport)) #all interfaces and 1200 port numbder
message,clientaddress=serversocket.recvfrom(2048)
t2 = int(time.time()*1000000)
header1=struct.unpack(header,message)
seq_num = header1[3]
t1=header1[4]
t3 = int(time.time()*1000000)
send = struct.pack(header,1,2,0,seq_num,t1,t2,t3)
serversocket.sendto(send,clientaddress)
input("press to send command")
commandtime = int(time.time()*1000000)+500000
text = "SERVER".encode()
command = struct.pack(header,1,3,0,1,commandtime,0,0) + text
serversocket.sendto(command,clientaddress)
recieve,_ = serversocket.recvfrom(2048)
confirm = struct.unpack(header,recieve[:struct.calcsize(header)])
print("Confirmed seq",confirm[3],"executed at",confirm[4])
error = confirm[4] - commandtime
print("Scheduled at",commandtime)
print("Execution error:",error,"us (",error/1000,"ms )")