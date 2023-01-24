# Multi-User Chatroom Application

An advanced python chat room application with tkinter GUI.

## Features

- User registration via terminal
- Login system and authentication
- Logout funcitonality
- Chat history
- Option to clear messages
- block/unblock other users

### `chat_server.py`

The chat server spawns a thread to serve each client. The server has access to all client sockets and could write data to clients in other threads when serving a client in one thread. The chat server uses the SQL database created by register_user.py. The chat server also handles the authentication functionality. Whenever a client trys to log in, it checks if the username and passward matches its record. If a user logs out, the chat server removes the user from the online user list. `block`, `insertBlock`, and `deleteBlock` manages functionality of blocking /unblocking user on the server side.

### `chat_client.py`

The chat client is multi-threaded. Sockets read and write data respectively from the chat server. The chat client utilizes tkinter module and classes from GUI_utility.py to build the GUI. The chat client prompts the user to enter their username and password and forwards the information to the chat server for authentication. After login succeeds, the chat client conitinuously reads data from the socket with the server and displays it in the GUI. It also continuously reads data from user input and writes it to the server.

### `GUI_utility.py`

Contains two important classes `StartPage` and `MainPage` for GUI. Handles most GUI settings, including page settings, login window, buttons, messagebox sidebar and menubar. It also enables the functionality of message clearing.

### `register_user.py`

Handles user registration. Initializes a SQL database if none exists. The database stores user information including username and password.

### `user_list.sql`

SQL file for creating the database.

## How to run the code?

Open a terminal, run

```
python3 register_user.py
```

to add users.

Then run

```
python3 chat_server.py
```

Follow the instructions displayed on the terminal to add users.

After you see "You are ready to chat!", open another terminal, run

```
python3 chat_client.py
```

You can now log in to chat!
