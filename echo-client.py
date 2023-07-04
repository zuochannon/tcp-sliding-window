import socket

HOST = "127.0.0.1"
PORT = 50000
PACKET_SIZE = 1024

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))  # creates a socket object
    s.sendall(b"Hello, world!")  # sends message
    data = s.recv(PACKET_SIZE)  # read server's reply and print
print(f"Received {data!r}")
