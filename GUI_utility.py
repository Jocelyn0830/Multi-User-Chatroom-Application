#!/usr/bin/python3
#
# COMP 411, Fall 2022
# Utility file for user interface

import threading
from tkinter import *

DEFAULT_FONT = ("Arial", 12)

# tkinter class for start page


class StartPage(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        label_1 = Label(self, text='Username')
        label_2 = Label(self, text='Password')
        self.entry_1 = Entry(self)
        self.entry_2 = Entry(self, show="*")
        self.entry_1.bind("<Return>", lambda e: controller.logIn())
        self.entry_2.bind("<Return>", lambda e: controller.logIn())
        label_1.grid(row=0)
        label_2.grid(row=1)
        self.entry_1.grid(row=0, column=1)
        self.entry_2.grid(row=1, column=1)
        button = Button(self, text='Log in', command=controller.logIn)
        button.grid(row=2, columnspan=2)

# tkinter class for main page


class MainPage(Frame, threading.Thread):
    def __init__(self, parent, controller, database, new_messages):
        threading.Thread.__init__(self)
        Frame.__init__(self, parent)
        self.controller = controller
        self.new_messages = new_messages
        self.database = database

        # menubar button for unblocking user
        menubar = Menu(self)
        self.unblock = Menu(self, tearoff=0)
        menubar.add_cascade(label='Unblock', menu=self.unblock)
        self.controller.config(menu=menubar)

        # Button for clearing messages
        menu = Menu(self, tearoff=0)
        menu.add_command(
            label=u'Block', command=lambda: self.controller.blockUser())
        menu.add_command(label=u'Clear messages',
                         command=lambda: self.clearMsg())

        # create side bar
        self.sideframe = Frame(self)
        self.listbox = Listbox(self.sideframe)
        self.listbox.pack(fill=BOTH, expand=True, side=TOP, pady=5)
        self.listbox.bind("<1>", lambda e: self.rename(e))
        aqua = self.controller.call('tk', 'windowingsystem') == 'aqua'
        self.listbox.bind('<2>' if aqua else '<3>',
                          lambda e: self.listboxMenu(e, menu))
        self.listbox.bind("<Key>", self.noP)
        # button for log out
        self.label = Label(
            self.sideframe, text=self.controller.client.capitalize())
        self.logout = Button(self.sideframe, text="Log Out",
                             command=self.controller.logOut)
        self.logout.pack(side=RIGHT)
        self.label.pack(side=LEFT)
        self.sideframe.grid(row=0, rowspan=3, column=0,
                            sticky='nswe', padx=5, pady=5)
        self.current = Label(self)
        self.current.grid(row=0, column=1, pady=5, )
        self.chats = {}
        self.text = Text(self, font=DEFAULT_FONT, height=2, width=50)
        self.text.grid(row=2, sticky='nswe', column=1, padx=5, pady=5)
        self.text.bind("<Return>", lambda e: self.controller.sendMsg())
        # create button for sending
        self.button = Button(
            self, text="Send", command=self.controller.sendMsg)
        self.button.grid(row=2, sticky='w', column=2)
        self.begin = 1
        self.daemon = True
        self.start()

    # function to handle message clearing
    def clearMsg(self):
        database = self.database
        new_messages = self.new_messages
        self.chats[self.menu_active][0].config(state=NORMAL)
        self.chats[self.menu_active][0].delete('1.0', END)
        self.chats[self.menu_active][0].config(state=DISABLED)
        database.execute("DELETE FROM {}_{}".format(
            self.controller.client, self.menu_active))
        database.commit()
        arr = []
        for item in new_messages:
            if item[0] == self.menu_active:
                arr.append(item)
        for item in arr:
            new_messages.remove(item)

        pass

    # function to create listbox menu
    def listboxMenu(self, event, menu):
        if self.listbox.size() == 0:
            return
        widget = event.widget
        index = widget.nearest(event.y)
        _, yoffset, _, height = widget.bbox(index)
        if event.y > height + yoffset + 5:
            return
        item = widget.get(index)
        self.menu_active = item
        menu.post(event.x_root, event.y_root)

    def noP(self, event):
        return "break"

    def run(self):

        while True:
            rec = self.controller.q.get()
            if rec[0] == 1:
                try:
                    self.chats[rec[1]]
                    main = self.chats[rec[1]][0]
                except:
                    s = Scrollbar(self)
                    s.grid(row=1, column=3, sticky='ns')
                    main = Text(self, height=10, width=50, font=DEFAULT_FONT)
                    main.grid(row=1, columnspan=2, column=1,
                              sticky='nswe', padx=5, pady=5)
                    s.config(command=main.yview)
                    main.config(yscrollcommand=s.set)
                    main.lower()
                    s.lower()
                    main.configure(bg=self.cget('bg'),
                                   relief=GROOVE, state='disabled')
                    main.tag_config('other', foreground='red')
                    main.tag_config('me', foreground='green',
                                    justify=RIGHT, lmargin1=100)
                    main.tag_config('justify', lmargin2=100)
                    self.chats[rec[1]] = (main, s)
                    pass
                main.configure(state='normal')
                main.insert(END, rec[1], 'other')
                str = rec[2][1]
                if len(rec[2][0]) != 0:
                    str = rec[2][1][:rec[2][0][0]]
                    for a in range(len(rec[2][0])):
                        if a != len(rec[2][0]) - 1:
                            str = str + '.' + \
                                rec[2][1][rec[2][0][a] -
                                          a:rec[2][0][a + 1] - a - 1]
                        else:
                            str = str + '.' + rec[2][1][rec[2][0][a] - a:]
                self.new_messages.append((rec[1], 1, str))
                main.insert(END, ': ' + str + '\n')
                main.configure(state='disabled')
                main.see(END)
            elif rec[0] == 2:
                main = self.chats[self.controller.to][0]
                main.configure(state='normal')
                main.insert(END, rec[1], 'me')
                main.insert(END, ': ' + rec[2] + '\n', 'justify')
                main.configure(state='disabled')
                main.see(END)
            elif rec[0] == -1:
                break
        pass

    def oldMsg(self, dat, user):

        main = self.chats[user][0]
        for sender, message in dat:
            if sender == 2:
                main.configure(state='normal')
                main.insert(END, 'You', 'me')
                main.insert(END, ': ' + message + '\n')
                main.configure(state='disabled')
            else:
                main.configure(state='normal')
                main.insert(END, user, 'other')
                main.insert(END, ': ' + message + '\n')
                main.configure(state='disabled')
                pass
        main.see(END)

        pass

    # function for renaming
    def rename(self, event):

        if self.listbox.size() == 0:
            return
        index = self.listbox.nearest(event.y)
        _, yoffset, _, height = self.listbox.bbox(index)
        if event.y > height + yoffset + 5:
            return
        self.controller.to = self.listbox.get(index)
        self.current.config(text=self.controller.to)
        main = self.chats[self.controller.to][0]
        temp = self.chats[self.controller.to][1]
        main.grid(row=1, columnspan=2, column=1, sticky='nswe', padx=5, pady=5)
        temp.grid(row=1, column=3, sticky='ns')
        temp.lift()
        main.lift()

    def update(self):
        self.listbox.delete(0, END)
        database = self.database

        for user in self.controller.users:
            try:
                self.chats[user]
                self.chats[user][0].grid(
                    row=1, columnspan=2, column=1, sticky='nswe', padx=5, pady=5)
                self.chats[user][1].grid(row=1, column=3, sticky='ns')
                self.listbox.insert(END, user)

            except:
                s = Scrollbar(self)
                temp = Text(self, height=10, width=50, font=DEFAULT_FONT)
                temp.grid(row=1, columnspan=2, column=1,
                          sticky='nswe', padx=5, pady=5)
                s.grid(row=1, column=3, sticky='ns')
                s.config(command=temp.yview)
                temp.config(yscrollcommand=s.set)
                temp.lower()
                s.lower()

                temp.configure(bg=self.cget('bg'),
                               relief=GROOVE, state='disabled')
                temp.tag_config('other', foreground='red')
                temp.tag_config('me', foreground='green',
                                justify=RIGHT, lmargin1=100)
                temp.tag_config('justify', lmargin2=100, lmargin1=100)
                self.chats[user] = (temp, s)
                self.listbox.insert(END, user)
                try:
                    cur = database.cursor()
                    cur.execute(
                        """select * from {}_{}""".format(self.controller.client, user))
                    dat = cur.fetchall()
                    self.oldMsg(dat, user)
                    pass
                except:
                    database.execute(
                        'create table {}_{}( sender INT, message VARCHAR(4000))'.format(self.controller.client, user))
                    pass

        if len(self.controller.users) == 0:
            self.controller.to = None
            self.current.config(text='')
            self.button.configure(state='disabled')
            for a in list(self.chats.keys()):
                self.chats[a][0].grid_forget()
                self.chats[a][1].grid_forget()
            pass
        else:
            if self.controller.to not in self.controller.users:
                self.controller.to = self.listbox.get(0)
                self.current.config(text=self.controller.to)
                self.listbox.activate(0)
                self.chats[self.controller.to][0].grid(
                    row=1, columnspan=2, column=1, sticky='nswe', padx=5, pady=5)
                self.chats[self.controller.to][1].grid(
                    row=1, column=3, sticky='ns')
                self.chats[self.controller.to][0].lift()
                self.chats[self.controller.to][1].lift()
                self.button.configure(state='normal')
                pass
            else:
                pass
