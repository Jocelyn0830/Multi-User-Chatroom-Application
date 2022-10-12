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

HEADER_LENGTH = 10


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

        try:
            # Recive the message header
            msg_header = conn.recv(HEADER_LENGTH + 9)
            # Checks if there is a message
            if msg_header:
                msg_len = int(msg_header.decode(
                    'utf-8').strip().replace('Msg-Len: ', ''))
                # Receives the message
                data_with_uname = conn.recv(msg_len)

                return msg_header+data_with_uname
            # If there is no message, client left, return -1
            else:
                return -1
        except:
            print("Unable to read message from the client")

    # ToDo: loop through all connections and send message to
    # clients except the sending client
    def send_data(self, user, data):
        self.lock.acquire()
        try:
            # loop through chat_list and skip the sender
            for chat_id in (self.chat_list).keys():
                # Skips the user that sends the message
                if (chat_id == user):
                    continue
                (conn, addr) = self.chat_list.get(chat_id)
                conn.send(data)
        except:
            print("Unable to broadcast data")

        self.lock.release()

    # close the socket being served and remove the connection
    # from list of available connections
    def cleanup(self, conn):
        self.lock.acquire()
        try:
            conn.close()
            for chat_id in (self.chat_list).keys():
                (this_conn, this_addr) = self.chat_list.get(chat_id)
                if (this_conn == conn):
                    del self.chat_list[chat_id]
                    break
        except:
            print("Unable to close connection: ")

        self.lock.release()

    # Use the read_data function to continuously read data from socket in that thread
    # Whenever a complete message read, send using send_data
    def serve_user(self, conn, addr, user):
        while True:
            data = self.read_data(conn)
            if (data == -1):
                self.cleanup(conn)
                break
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
