#!/usr/bin/env python3

"""
----------------------------------------------------------------------------------------------------
COMP 8005 Network Security & Applications Development
Assignment 2
Student:
    - Hung Yu (Angus) Lin, A01034410, Set 6J
----------------------------------------------------------------------------------------------------
server.py
    The server of a client/server secure SSL chat application. The server accepts connections
    on a specific port and once clients have established a connection with it, it will echo
    whatever it receivers to other connected clients.
----------------------------------------------------------------------------------------------------
"""
import sys
import time
import threading
from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing import freeze_support
from socket import *
from _thread import *
import selectors
import asyncio
import ssl
from pathlib import Path

NUMBERS_PATH = "numbers.txt"
LOG_PATH = "log_threads.txt"

sel = selectors.DefaultSelector()
clients = {}


def read_user_input(sock):
    """
    Display simple command line UI for Chat Client, prompts and reads user input.
    Commands:
        Enter 0 - Exit program.
        Enter anything else - Send input to chat server.
    :return: none
    """

    try:
        print('--------------------------------------\n'
              'Chat Server Menu.\n'
              'Server will display client connections and echo back what is sent.\n'
              'Commands:\n'
              '    Enter number 0      --- Exit program.\n'
              '    Enter anything else --- Send input to chat server.\n'
              '--------------------------------------')
        print("Type and press enter to begin chatting, or type \"0\" to quit: ")
        keep_running = True
        while keep_running:
            user_command = input()

            if user_command == "0":
                keep_running = False
                print("Exiting...")
                sys.exit()
            else:
                print(f"You: {user_command}")
                sock.sendall(user_command.encode('utf8'))

    except OSError as msg:
        print('Error Code : ' + msg.strerror)
        sys.exit()


def read_server_messages(conn):
    while True:
        data = conn.recv(1024)
        if data:
            print(data.decode('utf8'))
        else:
            print('Server closed connection.')
            print('Closing client.')
            conn.close()
            sys.exit()


def start_client():

    print("Starting Chat Client.")
    HOST = input("Please Enter Server IP: ")
    PORT = input("Please Enter Server PORT: ")

    try:
        with socket(AF_INET, SOCK_STREAM) as normal_sock:
            sock = ssl.wrap_socket(normal_sock, ssl_version=ssl.PROTOCOL_TLS,
                                   certfile="client_cert.pem", keyfile="client_cert.pem", )

            if not PORT.isdigit():
                raise ValueError
            sock.connect((HOST, int(PORT)))
            print(f"Connecting to Server: IP = {HOST}, Port = {PORT}")

            start_new_thread(read_server_messages, (sock,))

            read_user_input(sock)

    except error as msg:
        print('Error Code : ' + str(msg[0]) + ' Message ' + msg[1])


if __name__ == "__main__":
    start_client()

