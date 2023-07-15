# Server echoes client's messages
# https://realpython.com/python-sockets/
import socket
HOST = socket.gethostname()
IP = socket.gethostbyname(HOST)

PORT = 50000
PACKET_SIZE = 1024
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((IP, PORT))
    s.listen()
    conn, addr = s.accept()
    with conn:
        print(f"Success! Connected by {addr}")
        while True:
            data = conn.recv(PACKET_SIZE)
            if not data:
                break
            data_decode = data.decode("utf-8")
            data_decode += " 1"
            data_encode = data_decode.encode('utf-8')
            conn.sendall(data_encode)  # echoes back the client data

            data = conn.recv(PACKET_SIZE)
            if not data:
                break
            data_decode = data.decode("utf-8")
            data_decode = int(data_decode)
            data_decode += 1
            conn.sendall(b"Next: " + str(data_decode).encode('utf-8'))
