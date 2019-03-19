from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import os
import sys

def accept_incoming_connections():
    """Sets up handling for incoming clients."""
    while True:
        client, client_address = server.accept()
        print("%s:%s has connected." % client_address)
        client.send(bytes("Greetings! Please enter your chat name! ", "utf8"))
        addresses[client] = client_address
        Thread(target=handle_client, args=(client,)).start()


def handle_client(client): 
    """Handles a single client connection."""

    try:
    	name= client.recv(BUFSIZ).decode("utf8")
    except:
    	print("Connection lost to:", addresses[client])
    	del addresses[client]
    	return

    welcome = 'Welcome %s! Press Quit to exit the chat anytime!' % name
    list_of_users = []
    for c in clients:
        list_of_users.append(clients[c])
        print(clients[c])
    if len(list_of_users) != 0:
        welcome += "These users are online -  \n"
        for user in list_of_users:
            welcome += user + "\n"

    try:
    	client.send(bytes(welcome, "utf8"))
    except:
    	print("Connection Lost to", addresses[client])
    	del addresses[client]

    msg = "%s has joined the chat!" % name
    broadcast(bytes(msg, "utf8"))
    clients[client] = name

    while True:
        try:
        	msg = client.recv(BUFSIZ)
        except:
        	print("Connection lost to %s:%s" % addresses[client])
        	del clients[client]
        	return

        if msg != bytes("{quit}", "utf8"):
            broadcast(msg, name+": ")
        else:
            client.close()
            client_address, clinet_port = addresses[client]
            print("%s:%s alias %s has disconnected" % (client_address, clinet_port, name))
            del clients[client]
            del addresses[client]
            broadcast(bytes("%s has left the chat." % name, "utf8"))
            break


def broadcast(msg, prefix=""):
    """Broadcasts a message to all the clients."""

    for sock in clients:
        sock.send(bytes(prefix, "utf8")+msg)

        
clients = {}
addresses = {}

HOST = "127.0.0.1"
PORT = 2500
BUFSIZ = 1024

if len(sys.argv) == 3:
	HOST = str(sys.argv[1])
	PORT = int(sys.argv[2])
else:
	print("No Host:Port provided")
	print("Default: 127.0.0.1:2500")

ADDR = (HOST, PORT)
server = socket(AF_INET, SOCK_STREAM)
server.bind(ADDR)


if __name__ == "__main__":
    server.listen(5)
    print()
    print("Server started at %s:%d" % ADDR)
    print("Waiting for connection...")
    print("Type 'quit' to quit...")
    accept_thread = Thread(target=accept_incoming_connections)
    accept_thread.start()

    while True:
    	com = input()
    	if com == "quit":
    		server.close()
    		os._exit(1)
    accept_thread.join()
    server.close()