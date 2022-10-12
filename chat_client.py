
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

HEADER_LENGTH = 10


class ChatClient:

    def __init__(self, chat_host, chat_port):
        self.chat_host = chat_host
        self.chat_port = chat_port
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
        username = input('Username: ')

        while True:
            # Takes user input
            str_msg = input("")
            try:
                if str_msg:
                    # Add username to the message
                    msg_with_uname = username + ': ' + str_msg
                    bin_msg = msg_with_uname.encode('utf-8')

                    # Length header: this header has fixed length 19
                    msg_header = f"Msg-Len: {len(bin_msg ):<{HEADER_LENGTH}}".encode(
                        'utf-8')

                    msg_to_send = msg_header + bin_msg
                    sock.send(msg_to_send)
                else:
                    sock.close()
                    break
            except:
                print("Unable to send message to server")

    # ToDo: continuously read data from the socket with the server,
    # parse the portocol header the server put, determine
    # how much data to read and read until that amount
    # Then display it to the screen with the format "user:data"

    def read_sock(self, sock):
        try:
            while True:
                # Receives the message header
                msg_header = sock.recv(HEADER_LENGTH + 9)
                # Parses the message length
                msg_len = int(msg_header.decode(
                    'utf-8').strip().replace('Msg-Len: ', ''))
                # Receives the message
                bin_data = sock.recv(msg_len)
                data = bin_data.decode('utf-8')
                print(data)
        except:
            print("Connection closed")


def main():
    print('<<<<< Welcome to the chat room >>>>>')
    print('Start chatting! Hit return if you want to leave the chat room.')
    print(sys.argv, len(sys.argv))
    chat_host = 'localhost'
    chat_port = 50007

    if len(sys.argv) > 1:
        chat_host = sys.argv[1]
        chat_port = int(sys.argv[2])

    chat_client = ChatClient(chat_host, chat_port)


if __name__ == '__main__':
    main()
