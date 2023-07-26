import socket
HOST = socket.gethostname()
IP = socket.gethostbyname(HOST)
print(f"HOST: {HOST}")
print(f"IP: {IP}")