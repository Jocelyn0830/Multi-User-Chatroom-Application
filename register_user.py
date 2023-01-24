#!/usr/bin/python3
#
# COMP 411, Fall 2022
# Utility file for user registration
#

import os
import sqlite3

db_name = 'chat-application.db'
schema = 'user_list.sql'
is_new_db = not os.path.exists(db_name)

# Generate a sql database if not existed in the path
with sqlite3.connect(db_name) as conn:
    if is_new_db:
        with open(schema, 'rt') as file:
            schema = file.read()
        conn.executescript(schema)
        print("Please add user")
    else:
        pass

    # Prompt user to registrate
    add_user = input("Do you want to add a user? y/n ")
    if add_user == 'y':
        while True:

            while True:
                username = input("Please enter your username: ")
                if username == '' or len(username) > 45:
                    username = input("Please re-enter a qulified username")
                else:
                    break

            while True:
                password = input("Please enter your password: ")
                if password == '' or len(password) > 45:
                    password = input("Please re-enter a qulified password")
                else:
                    break

            # Save user info in the database
            try:
                conn.execute("""
                        insert into user_info (username,password)
                        values (?, ?)
                        """, (username, password))
            except sqlite3.IntegrityError as e:
                print("Username has already existed. Choose another one")
                continue

            con = input("Do you want to add another user? y/n ")
            if con == 'n':
                break
