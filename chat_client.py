#!/usr/bin/python3
#
# COMP 411, Fall 2022
# Chat client

import time
import socket
import pickle
import sqlite3
import threading
from tkinter import *
from queue import Queue
from tkinter import messagebox
from GUI_utility import StartPage, MainPage

server_IP = ''
database_name = 'chat-client.db'
database = sqlite3.connect(database_name, check_same_thread=False)
new_messages = []
lock = threading.Lock()


class ChatClient(Tk):
    # Get local machine hostname
    host = socket.gethostname()

    def __init__(self, chat_port, *a, **ka):
        self.chat_port = chat_port
        Tk.__init__(self, *a, **ka)
        self.title("Chat Room")
        self.container = Frame(self)
        self.container.pack()
        self.initStartPage(chat_port)
        self.resizable(0, 0)

    # Create start page
    def initStartPage(self, val):
        self.signin = StartPage(self.container, self)
        self.signin.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        # Create a socket object
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while True:
            try:
                self.sock.connect((server_IP, self.chat_port))
                break
            except Exception as e:
                print(e)
                # Try again after some time
                time.sleep(3)

    # Create UI listener
    def initListener(self, sock):
        try:
            while True:
                rec = sock.recv(4096)
                arr = rec.split(b'.')
                for a in range(len(arr)-1):
                    new_data = pickle.loads(arr[a]+b'.')
                    if new_data[0] == 1 and new_data[1][0].capitalize() in self.users:
                        self.q.put(
                            (1, new_data[1][0].capitalize(), new_data[1][1]))

                    elif new_data[0] == 2:
                        self.users = []
                        self.online_users = []
                        for str in new_data[1]:
                            self.online_users.append(str.capitalize())
                            try:
                                if self.blocked_users[str.capitalize()]:
                                    pass
                            except:
                                self.users.append(str.capitalize())
                                pass
                        self.users.remove(self.client.capitalize())

                        self.mainpage.update()
                        pass
                    elif new_data[0] == 3:
                        print("No such user " + new_data[1])
                    elif new_data[0] == 4:
                        self.users = []
                        self.online_users = []
                        for str in new_data[1][1]:
                            self.blocked_users[str[0].capitalize()] = 1
                            self.mainpage.unblock.add_command(label=str[0].capitalize(),
                                                              command=lambda str=str[0].capitalize(): self.unblockUser(str))
                        for str in new_data[1][0]:
                            self.online_users.append(str.capitalize())
                            try:
                                if self.blocked_users[str.capitalize()]:
                                    pass
                            except:
                                self.users.append(str.capitalize())
                                pass
                        self.users.remove(self.client.capitalize())
                        self.mainpage.update()

        except ConnectionResetError:
            messagebox.showerror("Error", "Server stopped")
            self.destroy()
        except ConnectionAbortedError as e:
            print(e)
            pass
        except OSError:
            # Manage the situation when user clicks on the red cross
            print("You logged out")
            sock.close()
            quit()

    # Handle login page and settings
    def logIn(self):
        try:
            sock = self.sock
            username = self.signin.entry_1.get()
            password = self.signin.entry_2.get()
            username = username.strip()
            password = password.strip()
            login_info = (username.lower(), password)
            new_data = pickle.dumps(login_info, -1)
            sock.send(new_data)
            reply = sock.recv(1024)
            choice = pickle.loads(reply)
            if choice == 0:
                print("Incorrect Password")
            elif choice == -1:
                print("Username Doesn't Exist")
            elif choice == -2:
                print("Already logged in")
            elif choice == 1:
                print("You joined the chat room")
                self.client = username.lower()
                self.users = []
                self.online_users = []
                self.blocked_users = {}
                self.to = None
                self.q = Queue()
                self.mainpage = MainPage(
                    self.container, self, database, new_messages)
                self.mainpage.grid(row=0, column=0, sticky='nsew')
                self.signin.destroy()
                self.tkraise(self.mainpage)
                thread = threading.Thread(target=self.initListener, args=[
                    sock], name='Listener')
                thread.daemon = True
                thread.start()

        except ConnectionResetError:
            messagebox.showerror("Error", "Server stopped")
            self.destroy()

    # Handle user logout
    def logOut(self):
        for to, no, message in new_messages:
            database.execute('insert into {}_{} values(?,?)'.format(
                a.client, to), (no, message))
        try:
            self.sock.send(b'-3')
            print('You logged out')
        except Exception as e:
            print(e)
        database.commit()
        new_messages.clear()
        self.mainpage.destroy()
        self.q.put((-1, 0, 0))
        self.mainpage.chats.clear()
        self.initStartPage(self.chat_port)

    # Handle display of messages
    def sendMsg(self):
        sock = self.sock
        string = self.mainpage.text.get(1.0, 'end-1c')
        string = string.strip()
        if string != '' and self.to != None:
            self.q.put((2, 'You', string))
            arr = []
            b = 0
            for a in range(len(string)):
                if string[a] == '.':
                    arr.append(a)
            string = string.replace('.', '')
            message = (1, self.to.lower(), (arr, string))
            message = pickle.dumps(message, -1)
            sock.send(message)
            new_messages.append((self.to, 2, string))
            self.mainpage.text.delete(1.0, END)
        pass

    # Creates block user icon
    def blockUser(self):
        sock = self.sock
        self.blocked_users[self.mainpage.menu_active] = 1
        self.mainpage.chats[self.mainpage.menu_active][0].destroy()
        self.mainpage.chats[self.mainpage.menu_active][1].destroy()
        self.mainpage.chats.pop(self.mainpage.menu_active)
        self.users.remove(self.mainpage.menu_active)
        self.mainpage.unblock.add_command(label=self.mainpage.menu_active,
                                          command=lambda str=self.mainpage.menu_active: self.unblockUser(str))
        self.mainpage.update()
        message = (2, self.mainpage.menu_active.lower())
        message = pickle.dumps(message, -1)
        sock.send(message)

    # Creates unblock user icon
    def unblockUser(self, str):
        self.blocked_users.pop(str)
        index = self.mainpage.unblock.index(str)
        self.mainpage.unblock.delete(index, index)
        if str in self.online_users:
            self.users.append(str)
            self.mainpage.update()
        sock = self.sock
        message = (3, str.lower())
        message = pickle.dumps(message, -1)
        sock.send(message)


if __name__ == '__main__':
    a = ChatClient(50007)
    a.mainloop()
    for to, no, message in new_messages:
        database.execute('insert into {}_{} values(?,?)'.format(
            a.client, to), (no, message))
    try:
        a.sock.send(b'-3')
        a.sock.close()
    except Exception as e:
        print(e)
    database.commit()
    new_messages.clear()
    database.close()
