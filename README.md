# tcp-sliding-window
Note: Open a port in your OS's firewall.

Server side:
Open a port in your OS's firewall -- outbound
Start the socket by running this first: python echo-server.py

Client side:
Open a port in your OS's firewall -- inbound
Establish the handshake by running the server side and then running: python echo-client.py
