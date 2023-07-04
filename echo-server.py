# Server echoes client's messages
# https://realpython.com/python-sockets/
import socket

HOST = "127.0.0.1"  # replace w local IP of server
PORT = 50000
PACKET_SIZE = 1024
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    with conn:
        print(f"Connected by {addr}")
        while True:
            data = conn.recv(PACKET_SIZE)
            if not data:
                break
            conn.sendall(data)  # echoes back the client data
