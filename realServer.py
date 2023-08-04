# Selective Repeat ARQ - Server Side Code

import socket
import time


class Server:
    def __init__(self):
        self.host = socket.gethostname()
        self.ip = socket.gethostbyname(self.host)
        self.port = 12344
        self.socket = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)  # get instance

        self.win_size = 4
        self.win_start = 0
        self.pkt_counter = 0
        self.packet_buffer = [False for i in range(
            self.win_start, self.win_size)]
        self.MAX_WIN_SIZE = 2**16  # 2^16 max window size

        self.fin = False

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
        Maintains the buffer when new packets arrive and marks
        the packets as received
        Updates: start of window and buffer list
        Assumption: window size on server side doesn't need to 
        follow AIMD because we can't assume client's loss
        """
        # update the start of the window
        while self.packet_buffer[self.win_start]:
            print(
                f"Index {self.win_start} is {self.packet_buffer[self.win_start]}")
            print("incrementing window start")
            self.win_start += 1
            print(f"New window start is {self.win_start}")
            print(f"list size is {len(self.packet_buffer)}")
            if self.win_start >= len(self.packet_buffer):
                self.packet_buffer.append(False)
            print(f"Packet buffer: {self.packet_buffer}")

        # add space to window
        pkts_to_add = self.win_end() - len(self.packet_buffer)
        if pkts_to_add > 0:
            for i in range(pkts_to_add):
                self.packet_buffer.append(False)

    def mark_packet_received(self, seq_num):
        buff_size = len(self.packet_buffer)
        # if the sequence number is out of order,
        # create space for other packets to arrive later
        if seq_num >= buff_size - 1:
            print(f"Adding space to the buffer")
            for i in range(buff_size, seq_num + 1):
                self.packet_buffer.append(False)

        # Mark the received packet in the buffer as received
        print(f"---------- MARKING PACKET {seq_num} AS RECEIVED -----------")
        self.packet_buffer[seq_num] = True
        # print(f"New buffer: {self.packet_buffer}")

    def receive_packets(self, data):
        """
        Parses the packets. Packets can be received in a concatenated order
        and must be separated for the packets to be processed individually
        """
        # receive data stream. it won't accept data packet greater than 1024 bytes
        pkt_received = data.split(",")
        pkt_received = [x for x in pkt_received if len(x) != 0]     # remove empty list items
        try:
            pkt_received.remove("FIN")
        except ValueError:
            print(f"Client is not done sending packets")
        else:
            self.fin = True
        print(f"-------------- RECEIVED PACKET {pkt_received} --------------")
        self.pkt_counter += len(pkt_received)
        return [int(i) for i in pkt_received]

    def send_ack(self, ack):
        print(f"-------------- SENDING ACK {ack} --------------\n\n")
        self.conn.send(ack.encode())


def server_program():
    server = Server()
    print(f"Server IP: {server.ip}")

    start = time.time()
    server.handshake()
    rtt = time.time() - start

    while not server.fin:
        data = server.conn.recv(1024).decode()
        if not data and rtt < time.time() - start:
            print("Closing socket, no packets being sent")
            server.conn.close()
        elif data:
            # create 1:1 ack for packet received
            ack = server.receive_packets(data)
            print(f"Acks to send: {ack}")
            for i in ack:
                server.mark_packet_received(i)
                server.update_win_size(i)
                server.send_ack(str(i) + ",")
            if server.fin:
                server.send_ack("FIN,")

        # try:
        #     data = server.conn.recv(1024).decode()
        # except TimeoutError:
        #     print("Closing socket, no packets being sent")
        #     server.conn.close()
        #     is_open = False
        # else:
        #     if data:
        #         ack = server.receive_packets(data)
        #         for i in ack:
        #             server.mark_packet_received(i)
        #             server.update_win_size(i)
        #             server.send_ack(str(i) + ",")


if __name__ == '__main__':
    server_program()
