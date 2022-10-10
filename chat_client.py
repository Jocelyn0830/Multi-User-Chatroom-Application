#!/usr/bin/python3
#
# COMP 411, Fall 2022
# Chat client
#
# Example usage:
#
#   python3 chat_client.py <chat_host> <chat_port>
#

import socket
import sys
import threading
import datetime
import header_constants as const
import util


class ChatClient:

    def __init__(self, chat_host, chat_port, username):
        self.chat_host = chat_host
        self.chat_port = chat_port
        self.username = username
        self.start()

    def start(self):

        # Open connection to chat
        try:
            chat_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            chat_sock.connect((self.chat_host, self.chat_port))
            print("Connected to socket")
        except OSError as e:
            print("Unable to connect to socket: ")
            if chat_sock:
                chat_sock.close()
            sys.exit(1)

        threading.Thread(target=self.write_sock, args=(chat_sock,)).start()
        threading.Thread(target=self.read_sock, args=(chat_sock,)).start()

    # ToDo: countinuously read data from user input, put protocol header on it
    # (Needs to determine when the header terminates and data begins)
    # Then write it to the chat server
    def write_sock(self, sock):
        while True:
            # Takes user input
            str_msg = input("Type your message: ")
            current_time = datetime.datetime.now()

            # Add headers and send to server
            bin_msg = str_msg.encode('utf-8')
            length_header = 'Length: ' + str(len(bin_msg)) + const.END_LINE
            username_header = 'Username: ' + self.username + const.END_LINE
            date_header = 'Date: ' + str(current_time) + const.END_LINE
            data = 'Data: ' + str_msg + const.END_LINE
            msg_to_send = length_header + username_header + \
                date_header + data + const.END_LINE

            bin_msg_to_send = msg_to_send.encode('utf-8')
            sock.send(bin_msg_to_send)
            # Check if the user leaves the chat room
            if not str_msg:
                break

    # ToDo: continuously read data from the socket with the server,
    # parse the portocol header the server put, determine
    # how much data to read and read until that amount
    # Then display it to the screen with the format "user:data"

    def read_sock(self, sock):
        bin_msg = b''
        while True:
            more = sock.recv(4096)
            bin_msg += more
            if const.END_MSG.encode('utf-8') in more:
                break
        msg_recvd = bin_msg.decode('utf-8')
        username = util.get_field(msg_recvd, 'Username: ', const.END_LINE)
        data = util.get_field(msg_recvd, 'Data: ', const.END_MSG)
        print(username, end=': ')
        print(data)


def main():
    print('<<<<< Welcome to the chat room >>>>>')
    username = input('Please type your username: ')
    print('Start chatting! Hit return if you want to leave the chat room.')
    print(sys.argv, len(sys.argv))
    chat_host = 'localhost'
    chat_port = 50007

    if len(sys.argv) > 1:
        chat_host = sys.argv[1]
        chat_port = int(sys.argv[2])

    chat_client = ChatClient(chat_host, chat_port, username)


if __name__ == '__main__':
    main()
