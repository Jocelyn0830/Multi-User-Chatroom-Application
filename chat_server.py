#!/usr/bin/python3
#
# COMP 411, Fall 2022
# Chat server

import os
import sys
import socket
import pickle
import sqlite3
import threading


class ChatProxy():

    def __init__(self, server_host, server_port):
        self.server_host = server_host
        self.server_port = server_port
        self.database = None
        self.server_backlog = 100
        self.chat_list = []
        self.new_users = []
        self.user_list = []
        self.lock = threading.Lock()
        self.start()

    def start(self):
        db_name = 'chat-application.db'
        is_new_db = not os.path.exists(db_name)
        if is_new_db:
            print("Please run register_user.py first to add users!")

        self.database = sqlite3.connect(
            'chat-application.db', check_same_thread=False)

        # Get all user info stored in the database
        cur = self.database.cursor()
        get_data = "SELECT * FROM USER_INFO"
        cur.execute(get_data)
        self.user_list = cur.fetchall()
        print("users: ", end='')
        for user in self.user_list:
            print(user[0], end=' ')

        print('\n')
        print("You are ready to chat! Run chat_client.py to log in")

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
        # Store threads in list to avoid daemon thread
        thread_holder = []
        for i in range(10):
            thread_holder.append(threading.Thread(
                target=self.receive, args=[i, server_sock]))
            thread_holder[i].start()

    # broadcast message
    def broadcast(self, user, conn, choice):
        if choice == 0:
            data_to_send = pickle.dumps((2, self.new_users), -1)
            for user in self.chat_list:
                if user[1] != conn:
                    try:
                        user[1].send(data_to_send)
                    except Exception as e:
                        print(e)
                pass

        elif choice == 1:
            data_to_send = pickle.dumps((4, user), -1)
            try:
                conn.send(data_to_send)
            except Exception as e:
                print(e)
            pass

        else:
            data_to_send = pickle.dumps((3, user), -1)
            try:
                conn.send(data_to_send)
            except Exception as e:
                print(e)

    # user authentication
    def authenticate(self, login_info):
        for user in self.user_list:
            if user[0].lower() == login_info[0]:
                if user[1] == login_info[1]:
                    return 1
                else:
                    return 0
        return -1
    # block user

    def block(self, conn, login_info):
        try:
            cur = self.database.cursor()
            cur.execute("SELECT * FROM {}_blocked_users".format(login_info[0]))
            self.broadcast((self.new_users, cur.fetchall()), conn, 1)
            self.broadcast(None, conn, 0)
        except Exception as e:
            # create a table for blocked users if no such database already
            self.database.execute(
                "CREATE TABLE {}_blocked_users(username VARCHAR(4000) NOT NULL PRIMARY KEY)".format(login_info[0]))
            self.broadcast(None, conn, 0)

    # Insert blocked user into database

    def insertBlock(self, login_info, str_w_choice):
        temp = (str_w_choice[1],)
        try:
            self.database.execute(
                "INSERT INTO {}_blocked_users VALUES( ? )".format(login_info[0]), temp)
            self.database.commit()
        except Exception as e:
            print(e)

    # delete user from database if unblocked

    def deleteBlock(self, login_info, str_w_choice):
        temp = (str_w_choice[1],)
        try:
            self.database.execute(
                "DELETE FROM {}_blocked_users WHERE username = ?".format(login_info[0]), temp)
            self.database.commit()
        except Exception as e:
            print(e)

    # receive messages

    def receive(self, user, sock):
        while True:
            try:
                conn, addr = sock.accept()
                print('Connected from', addr, user)
                logged_in = 0

                # Check if user is logged in
                while logged_in != 1:
                    login_info = conn.recv(4096)

                    login_info = pickle.loads(login_info)
                    logged_in = self.authenticate(login_info)
                    self.lock.acquire()

                    if login_info[0] in self.new_users:
                        logged_in = -2

                    data_to_send = pickle.dumps(logged_in, -1)
                    conn.send(data_to_send)

                    if logged_in == 1:
                        self.chat_list.append((login_info[0], conn))
                        self.new_users.append(login_info[0])

                    self.lock.release()

            except Exception as e:
                print(e)
                continue

            finally:
                pass

            self.lock.acquire()
            print(login_info[0] + ' has connected')

            self.block(conn, login_info)

            self.lock.release()
            str_w_choice = ''

            try:
                while True:

                    msg = conn.recv(4096)
                    if msg == b'-3':
                        self.lock.acquire()
                        self.chat_list.remove((login_info[0], conn))
                        self.new_users.remove(login_info[0])
                        self.broadcast(None, conn, 0)
                        self.lock.release()
                        print(login_info[0] + ' left the chatroom')
                        pass
                    lis = msg.split(b'.')

                    for i in range(len(lis)-1):
                        str_w_choice = pickle.loads(lis[i]+b'.')
                        self.lock.acquire()

                        if str_w_choice[0] == 1:
                            if str_w_choice[1] not in self.new_users:
                                self.broadcast(str_w_choice[1], conn, 2)
                            else:
                                for user in self.chat_list:
                                    if user[1] != conn and user[0] == str_w_choice[1]:
                                        new_data = pickle.dumps(
                                            (1, (login_info[0], str_w_choice[2])), -1)
                                        user[1].send(new_data)

                        elif str_w_choice[0] == 2:
                            self.insertBlock(login_info, str_w_choice)

                        elif str_w_choice[0] == 3:
                            self.deleteBlock(login_info, str_w_choice)
                        self.lock.release()

            except Exception as e:
                self.lock.acquire()
                self.chat_list.remove((login_info[0], conn))
                self.new_users.remove(login_info[0])
                self.broadcast(None, conn, 0)
                self.lock.release()
                print(login_info[0] + ' left the chatroom')
                pass

            finally:
                conn.close()


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
