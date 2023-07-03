import sys
import socket
PORT_NUMBER = 6969
SIZE = 1024
# print ("Test client sending packets to IP {0}, via port {1}\n".format(SERVER_IP, PORT_NUMBER))

hostName = socket.gethostname()

mySocket = socket.socket( socket.AF_INET, socket.SOCK_STREAM)
mySocket.connect((hostName,PORT_NUMBER))

msg = mySocket.recv(SIZE)
print(msg.decode("utf-8"))
# while True:
#         mySocket.sendto('cool',(SERVER_IP,PORT_NUMBER))
