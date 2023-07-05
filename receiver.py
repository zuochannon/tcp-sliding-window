# server code
import socket
import sys

PORT_NUMBER = 6969
SIZE = 1024

hostName = socket.gethostname()
mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
mySocket.bind((hostName, PORT_NUMBER))
mySocket.listen(5)  # queue of 5

print("Test server listening on port {0}\n".format(PORT_NUMBER))

while True:
    data, addr = mySocket.accept()
    print(f"Connection from {addr} has been established")
    data.send(bytes("Welcome", "utf-8"))  # prints to sender console
