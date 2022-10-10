#!/usr/bin/python3
#
# COMP 411, Fall 2022
# Chat server
#
# Usage:
#   python3 chat_server.py <host> <port>
#

import socket
import sys
import threading
import header_constants as const
import util


class ChatProxy():

    def __init__(self, server_host, server_port):
        self.server_host = server_host
        self.server_port = server_port
        self.server_backlog = 1
        self.chat_list = {}
        self.chat_id = 0
        self.lock = threading.Lock()
        self.start()

    def start(self):

        # Initialize server socket on which to listen for connections
        try:
            server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_sock.bind((self.server_host, self.server_port))
            server_sock.listen(self.server_backlog)
        except OSError as e:
            print("Unable to open server socket")
            if server_sock:
                server_sock.close()
            sys.exit(1)

        # Wait for user connection
        while True:
            conn, addr = server_sock.accept()
            self.add_user(conn, addr)
            thread = threading.Thread(target=self.serve_user,
                                      args=(conn, addr, self.chat_id))
            thread.start()

    def add_user(self, conn, addr):
        print('User has connected', addr)
        self.chat_id = self.chat_id + 1
        self.lock.acquire()
        self.chat_list[self.chat_id] = (conn, addr)
        self.lock.release()

    # ToDo: Read from the socket passed to the function,
    # check if a full message is received and when received
    # return the message
    # An empty string indicates the client left
    def read_data(self, conn):
        bin_msg = b''
        while True:
            more = conn.recv(4096)
            bin_msg += more
            if const.END_MSG.encode('utf-8') in more:
                break
        data = bin_msg
        # Check if the user sends an empty string
        if (int(util.get_field(data.decode('utf-8'), "Length: ", const.END_LINE)) == 0):
            return -1
        else:
            return data

    # ToDo: loop through all connections and send message to
    # clients except the sending client
    def send_data(self, user, data):
        self.lock.acquire()
        # loop through chat_list and skip the sender
        for chat_id in (self.chat_list).keys():
            if (chat_id == user):
                continue
            (conn, addr) = self.chat_list.get(chat_id)
            conn.sendall(data)

        self.lock.release()

    # close the socket being served and remove the connection
    # from list of available connections
    def cleanup(self, conn):
        self.lock.acquire()
        conn.close()
        del self.chat_list[self.chat_id]
        # Fill this out
        print("In cleanup")

        self.lock.release()

    # Use the read_data function to continuously read data from socket
    # Whenever a complete message read, send using send_data
    def serve_user(self, conn, addr, user):
        data = self.read_data(conn)
        if (data == -1):
            self.cleanup(conn)
        else:
            self.send_data(user, data)


def main():

    print(sys.argv, len(sys.argv))
    server_host = 'localhost'
    server_port = 50007

    if len(sys.argv) > 1:
        server_host = sys.argv[1]
        server_port = int(sys.argv[2])

    chat_server = ChatProxy(server_host, server_port)


if __name__ == '__main__':
    main()
