# Selective Repeat ARQ - Server Side Code

import socket
import random


class Server:
    def __init__(self):
        self.host = socket.gethostname()
        self.ip = socket.gethostbyname(self.host)
        self.port = 12344
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # get instance
        
        self.win_size = 4
        self.win_start = 0
        self.pkt_counter = 0
        self.packet_buffer = [False for i in range(self.win_start, self.win_size)]
        self.MAX_WIN_SIZE = 65536  # 2^16 max window size

    def handshake(self):
        """
        Performs the three way handshake. Creates attributes:
        conn and address.
        Conn: the connection in which we extract client data
        Address: the address of the client
        """
        self.socket.settimeout(20)
        self.socket.bind((self.ip, self.port))

        # configure how many client the server can listen simultaneously
        self.socket.listen(5)
        self.conn, self.address = self.socket.accept()  # accept new connection

        # print data
        print("Connection from: ", str(self.address))
        print(f"From Client: {self.conn.recv(1024).decode()}")
        self.conn.send(b"Success")

    def win_end(self):
        return self.win_start + self.win_size - 1

    def update_win_size(self, seq_num):
        """
        Maintains the buffer when new packets arrive.
        Updates: start of window and buffer list
        Assumption: window size on server size doesn't need to 
        follow AIMD because we can't assume client's loss
        """
        print(f"---------- MARKING PACKET {seq_num} AS RECEIVED -----------")

        buff_size = len(self.packet_buffer)
        if seq_num > buff_size - 1:
            for i in range(buff_size, seq_num + 1):
                self.packet_buffer.append(False)

        # Mark the received packet in the buffer as received
        self.packet_buffer[seq_num] = True

        # increment the start of the window until there is
        # a packet for us to wait for
        while self.packet_buffer[self.win_start]:
            self.win_start += 1


    def receive_packet(self, data):
        # receive data stream. it won't accept data packet greater than 1024 bytes
        self.pkt_counter += 1
        pkt_received = int(data)

        print(f"-------------- RECEIVED PACKET {pkt_received} --------------")
        return pkt_received

    
    def send_ack(self, ack):
        self.conn.send(ack.encode())


def server_program():
    server = Server()
    print(f"Server IP: {server.ip}")

    server.handshake()
    is_open = True
    
    while is_open:
        try:
            data = server.conn.recv(1024).decode()
        except TimeoutError:
            print("Closing socket, no packets being sent")
            server.conn.close()
            is_open = False
        else:
            if data:
                ack = server.receive_packet(data)
                server.update_win_size(ack)
                server.send_ack(str(ack))


if __name__ == '__main__':
    server_program()
