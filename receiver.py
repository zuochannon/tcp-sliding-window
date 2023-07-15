# server code
import socket

PORT_NUMBER = 6969
SIZE = 1024

hostName = socket.gethostname()
mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
mySocket.bind((hostName, PORT_NUMBER))
mySocket.listen(5)  # queue of 5

print(f"Test server listening on port {PORT_NUMBER}")

while True:
    data, addr = mySocket.accept()
    print(f"Succesful connection from {addr} has been established")
    data.send(bytes("Welcome", "utf-8"))  # prints to sender console
