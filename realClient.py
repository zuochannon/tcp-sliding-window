# Authors: Channon Zuo and Sophia Sorensen
# Client
"""
Selective Repeat TCP program
This program simulates the process of a TCP program with a
Selective Repeat sliding window protocol. There are two classes:
Packet and Client.
Packet maintains its data and its timer.
Client interacts with the server program and manages the
Selective Repeat protocol.

To run this program, run the server first and get the IP address of the server.
Next, change the IP line in the Client init method and then run the client.
"""

import socket
import time

# TODO: GRAPH
# csv for pandas
# window size over time (AKA AIMD)
# seq # received over time (1000 over RTT)
# seq # dropped over time
# Set up a try catch statement to handle potential server-client errors

class Packet:
    """
    Packet object that manages its own data (sequence number) and its timer.
    """

    def __init__(self, sequence_num):
        self.sequence_num = sequence_num
        self.received = False
        self.sent = False
        self.start = time.time()
        self.resent_start = 0.0  # Can possibly be unused if packet doesn't need to be resent

    def start_timer(self):
        """
        Starts the timer for packet's rtt
        """
        if not self.received:
            self.start = time.time()
        else:
            print(
                f"Not sending packet {self.sequence_num} because it has been ACKed already.")

    def get_rtt(self):
        """
        Returns the rtt of the packet
        Returns: An integer representing the rtt of the packet
        """
        return time.time() - self.start

    def get_new_rtt(self):
        return time.time() + self.resent_start

class Client:
    """
    Client object that simulates the actions of a client server.
    """

    def __init__(self, total_packets):
        self.ip = "192.168.33.1"  # TODO: Change depending on the host
        self.port = 12344
        self.win_size = 4  # Implement AIMD and intitial size should be 1
        self.win_start = 0
        # self.win_end = 3
        self.packets = [Packet(i) for i in range(total_packets)]
        self.ttl = [Packet(i) for i in range(total_packets)]
        self.client_socket = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)  # instantiate

        self.rtt = 0
        self.estimated_rtt = 0
        self.packets_sent = 0
        self.acks_received = 0

        self.AIMD_FLAG = False  # Triggered when first loss occurs and won't change
        self.loss_occured_flag = False  # Triggered when any loss occurs.
        # Returns to False when no old frames in a window
        # are resent
        self.MAX_WIN_SIZE = 65536  # 2^16 max window size

    def handshake(self):
        """
        Sets the RTT for the program
        Arguments: None
        Return: None
        """
        # Establish the connection
        self.client_socket.connect((self.ip, self.port))
        print("-------------- START of handshake --------------")
        start = time.time()
        self.client_socket.send(b"Network")
        print(f"From Server: {self.client_socket.recv(1024).decode()}")
        self.rtt = time.time() - start
        print("-------------- END of handshake --------------")

    # def get_win_end(self):
    #     """
    #     Returns the end of the sliding window
    #     Returns: An int representing the end of the sliding window
    #     """
    #     return self.win_start + self.win_size - 1

    # TODO: Move self.packets_sent += 1 outside of for loop
    # TODO: Add the AIMD_FLAG when resending packet
    # TODO: Have the ttl for packet 0 be the rtt and then base the ttl on the prev ttl
    # TODO: Turn time_in_flight into a small function
    def send_message(self):
        """
        Sends all messages in the window
        Arguments: None
        Return: list of packets to send
        """
        temp_win_buffer = [
            x for x in self.packets[self.win_start: self.win_size]]
        print("-------------- SUBSET WINDOW --------------")
        print([templist.sequence_num for templist in temp_win_buffer])
        for i in range(self.win_start, self.win_size):
            # check if the packet is already marked as received
            if not self.packets[i].received and not self.packets[i].sent:
                print("-------------- NEW PACKET SENDING --------------")
                msg = self.packets[i].sequence_num
                packet = str(msg)
                self.packets[i].start_timer()
                print(f"Sending packet #{i}")
                self.client_socket.send(packet.encode())
                time_in_flight = time.time() - self.packets[i].start
                print(f"Sent packet #{i}")
                self.ttl[i] = time_in_flight + 0.005
                self.packets_sent += 1      # update counter
                self.packets[i].sent = True
                self.loss_occured_flag = False

            # TODO: Figure out logic of changing the new ttl
            elif not self.packets[i].received and self.packets[i].sent:
                # Timed out. Resend packet
                if self.packets[i].get_rtt() > self.ttl[i]:
                    print("---- OLD PACKET SENDING --------------")
                    self.packets[i].resent_start = time.time()
                    self.AIMD_FLAG = True
                    self.loss_occured_flag = True
                    self.packets[i].sent = False
                    self.send_message()
        print("---- SENT ALL PACKETS IN WINDOW ----")

    # TODO: Change receive_message to receive_ack
    # TODO: Possibly call send_message after we update the win_start
    # TODO: Add AIMD to adjust window size after we update win_start
    def receive_message(self):
        """
        Handles receiving ACKs from server
        """
        data = self.client_socket.recv(1024).decode()
        print(f"-------------- RECEIVED ACK: {data} --------------")
        print(f"-------------- WIN START: {self.win_start} --------------")
        print(
            f"-------------- WIN END: {self.win_start + self.win_size - 1} --------------")
        if data:
            # received message
            msg = str(data)
            ack = int(msg)

            self.packets[ack].received = True
            self.acks_received += 1  # update counter
            self.rtt = self.packets[ack].get_rtt()
            # if ack >= self.win_start:
            if ack == self.win_start:
                self.win_start += 1
                self.update_win_size()
                self.send_message()

    def update_win_size(self):
        """
        Increases or decreases self.win_size whether or not loss occurs
        """
        if self.win_size <= self.MAX_WIN_SIZE:
            '''
            Win size is at most max win size of 2^16
            '''
            if not self.AIMD_FLAG:
                '''
                No packet drop has occured. Slow start is implemented
                '''
                self.win_size *= 2
                print(f"Window size doubled to {self.win_size}")
            elif self.AIMD_FLAG and not self.loss_occured_flag:
                '''
                AIMD Implemented but no packet drop during the window
                Additive Increase
                '''
                self.win_size += 1
                print(f"Window size increased by 1 to {self.win_size}")
            elif not self.AIMD_FLAG and self.loss_occured_flag:
                '''
                AIMD Implemented and packet drop occured during window
                Multiplicative Decrease
                '''
                self.win_size /= 2
                print(f"Window size halved by 2 to {self.win_size}")
        else:
            self.win_size = self.MAX_WIN_SIZE
            print(f"Window size is at it's max of {self.MAX_WIN_SIZE}")


def runner():
    # SET WINDOW
    total_packets = int(input(
        "Enter the number of packets you want to send: "))  # take int input
    client = Client(total_packets)
    print(f"Window Size is {client.win_size}")

    client.handshake()      # perform handshake and set RTT

    while client.acks_received < total_packets:
        client.send_message()
        time.sleep(client.rtt)
        client.receive_message()

    client.client_socket.close()  # close the connection


if __name__ == '__main__':
    runner()
