import socket

HOST = socket.gethostname()
IP = socket.gethostbyname(HOST)

PORT = 50000
PACKET_SIZE = 1024

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((IP, PORT))  # creates a socket object
    s.sendall(b"Network")  # sends message
    data = s.recv(PACKET_SIZE)  # read server's reply and print

    for n in range(5):
        s.sendall(str(n).encode('utf8'))
        data = s.recv(PACKET_SIZE)
print(f"Received {data!r}")
