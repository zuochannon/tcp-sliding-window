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
import math

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

    def start_timer(self):
        """
        Starts the timer for packet's rtt
        """
        if not self.received:
            self.start = time.time()
        else:
            print(
                f"Not starting packet {self.sequence_num}'s time because it has been ACKed already.")

    def get_time_since_sent(self):
        """
        Returns the rtt of the packet
        Returns: An integer representing the rtt of the packet
        """
        return time.time() - self.start

    def __str__(self):
        return str(self.sequence_num)

    def __repr__(self):
        return str(self.sequence_num) + " " + str(self.received)


class Client:
    """
    Client object that simulates the actions of a client server.
    """

    def __init__(self, total_packets):
        self.ip = ""  # TODO: Change depending on the host
        self.port = 12344
        self.win_size = 4  # Implement AIMD and intitial size should be 1
        self.win_start = 0
        self.packets = [Packet(i) for i in range(total_packets)]
        self.packets.append(Packet("FIN"))
        self.ttl = [Packet(i) for i in range(total_packets)]
        self.client_socket = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)  # instantiate

        self.rtt = 0
        self.estimated_rtt = 0
        self.packets_sent = 0
        self.acks_received = 0

        self.AIMD_FLAG = False  # Triggered when first loss occurs and won't change
        self.loss_occured_flag = False  # Triggered when any loss occurs.
        self.fin = False
        # Returns to False when no old frames in a window
        # are resent
        self.MAX_WIN_SIZE = 2**16  # 2^16 max window size

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
        self.rtt = time.time() - start + 0.02
        print("-------------- END of handshake --------------\n\n")

    def get_win_end(self):
        """
        Returns the end of the sliding window
        Returns: An int representing the end of the sliding window
        """
        win_end = self.win_start + self.win_size
        if win_end >= len(self.packets) - 1:
            print(f"Reaching end of all packets, win_end is end of list")
            return len(self.packets)
        else:
            return win_end

    def send_message(self, packet):
        msg = str(packet.sequence_num) + ","
        self.client_socket.send(msg.encode())
        self.packets_sent += 1

    # TODO: Have the ttl for packet 0 be the rtt and then base the ttl on the prev ttl
    # TODO: Turn time_in_flight into a small function
    def send_window(self):
        """
        Sends all messages in the window. Iterates through the window
        and checks time on the packets. All packets that have surpassed
        their window will be resent.
        Arguments: None
        Return: None
        """
        win_end = self.get_win_end()
        print(f"Sending window: {self.packets[self.win_start: win_end]}")
        for i in range(self.win_start, self.get_win_end()):
            # only send packets that did not receive an ack
            if not self.packets[i].received:
                # check the time on sent packets
                # if they have went over time, set up packet to resend
                if self.packets[i].sent and self.rtt < self.packets[i].get_time_since_sent():
                    print(f"Packet {i} timed out, setting up to resend")
                    # change to unsent to pass sending check
                    self.packets[i].sent = False
                    self.loss_occured_flag = True
                    self.AIMD_FLAG = True

                # only send packets queued to send
                if not self.packets[i].sent:
                    print(f"Sending packet {self.packets[i].sequence_num}")
                    self.packets[i].start_timer()
                    self.send_message(self.packets[i])
                    self.packets[i].sent = True

    def mark_ack_received(self, index):
        packet = self.packets[index]
        if packet.sequence_num == index:
            # update the Client's expected rtt
            self.rtt = self.packets[index].get_time_since_sent() + 0.02
            if not self.packets[index].received:
                print(f"Marking {index} as received")
                self.packets[index].received = True
                self.acks_received += 1
        else:
            print(f"ERROR: index and seq num do not match")
        print(f"----- TOTAL ACKS RECEIVED: {self.acks_received}")

    # TODO: Possibly call send_message after we update the win_start
    # TODO: Add AIMD to adjust window size after we update win_start

    def receive_acks(self):
        """
        Handles receiving ACKs from server
        Arguments: None
        Return: List of acknowledged messages
        """
        data = self.client_socket.recv(1024).decode()
        print(f"-------------- WIN START: {self.win_start} --------------")
        print(
            f"-------------- WIN END: {self.get_win_end()} --------------")
        if data:
            ack_received = data.split(",")
            ack_received = [x for x in ack_received if len(
                x) != 0]     # remove empty list items
            # find "FIN" ack
            try:
                # remove fin to avoid affecting processing remaining packets
                ack_received.remove("FIN")
            except ValueError:
                print(f"Not at end of total packets (no FIN)")
            else:
                self.fin = True
            print(
                f"-------------- RECEIVED ACK {ack_received} --------------\n\n")
            return [int(i) for i in ack_received]

    def update_win_size(self):
        """
        Increases or decreases self.win_size whether or not loss occurs
        """
        # update win_start
        while self.packets[self.win_start].received:
            print("---- MOVING WIN_START ----")
            self.win_start += 1
            self.loss_occured_flag = False
            print(f"Win start is {self.win_start}")

        if self.win_size <= self.MAX_WIN_SIZE:
            # Win size is at most max win size of 2^16
            if not self.AIMD_FLAG:
                # No packet drop has occured. Slow start is implemented
                self.win_size *= 2
                print(f"Window size doubled to {self.win_size}")
            elif self.AIMD_FLAG and not self.loss_occured_flag:
                # AIMD Implemented but no packet drop during the window
                # Additive Increase
                self.win_size += 1
                print(f"Window size increased by 1 to {self.win_size}")
            elif self.AIMD_FLAG or self.loss_occured_flag:
                # AIMD Implemented and packet drop occured during window
                # Multiplicative Decrease
                old_win_size = self.win_size
                self.win_size = math.ceil(old_win_size / 2)
                print(f"Window size halved by 2 to {self.win_size}")
        else:
            self.win_size = self.MAX_WIN_SIZE
            print(f"Window size is at it's max of {self.MAX_WIN_SIZE}")

        # update the window size if we are reaching the end of the packet list
        # if self.get_win_end() == len(self.packets) - 1:
        if self.get_win_end() > len(self.packets) - 1:
            print("Readjusting Window Size")
            self.win_size = len(self.packets) - self.win_start
            print(f"Window size is now {self.win_size}")


def runner():
    # SET WINDOW
    total_packets = int(input(
        "Enter the number of packets you want to send: "))  # take int input
    client = Client(total_packets)
    print(f"Window Size is {client.win_size}")

    client.handshake()      # perform handshake and set RTT
    # window_size_graph = {}

    while not client.fin:
        # print(f"{client.packets}")
        client.send_window()
        # allow time for packets to be sent
        # time.sleep(client.rtt)

        # handle acks
        acks = client.receive_acks()
        print("OUT OF RECEIVE_ACKS()")
        acks.sort()
        print(f"Length of ACK list: {len(acks)}")
        print(f"Acks to mark received: {acks}")
        for i in range(len(acks)):
            client.mark_ack_received(acks[i])
        client.update_win_size()
        print(f"Number of ACKS received: {client.acks_received}")
    print(f"AIMD Flag triggered: {client.AIMD_FLAG}")
    # subtracting 1 bc of FIN ack
    print(f"Packets sent: {client.packets_sent - 1}")
    print(f"Goodput: {client.acks_received/(client.packets_sent - 1)}")
    # print(f"Window Size (value): {window_size_graph.values}")

    client.client_socket.close()  # close the connection


if __name__ == '__main__':
    runner()
