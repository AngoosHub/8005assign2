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
import threading
from socket import *
from _thread import *
import selectors
import asyncio
import ssl

sel = selectors.DefaultSelector()
clients = {}


def read_user_input(sel, sock):
    """
    Display simple command line UI for Chat Server, prompts and reads user input.
    Commands:
        Enter 0 - Exit program.
    :return: none
    """

    try:
        keep_running = True
        while keep_running:
            print('--------------------------------------\n'
                  'Chat Server Menu.\n'
                  'Server will display client connections and echo back what is sent.\n'
                  'Commands:\n'
                  '    Enter number 0 --- Exit program.\n'
                  '--------------------------------------')
            user_command = input("Please Enter Command: ")

            if user_command == "0":
                keep_running = False
                print_all_client_connections()
                print("Exiting...")
                # sock.shutdown(SHUT_RDWR)
                sock.close()
                sel.close()
                sys.exit()
            else:
                print("Invalid input, please re-enter.")

    except OSError as msg:
        print('Error Code : ' + msg.strerror)
        sys.exit()


def accept_client_connection(sock, mask):
    conn, addr = sock.accept()
    clients[conn.getpeername()[0]] = (conn, conn.getpeername())
    print()
    print('Client Connected: ', conn.getpeername())
    # conn.setblocking(False)
    print_all_client_connections()
    start_new_thread(read_client_connection, (conn, mask))
    # sel.register(conn, selectors.EVENT_READ, read_client_connection)


def read_client_connection(conn, mask):
    while True:
        data = conn.recv(1024)
        if data:
            echo_to_all_clients(conn, data)
        else:
            print('Client Disconnected: ', conn.getpeername())
            # sel.unregister(conn)
            clients.pop(conn.getpeername()[0], None)
            conn.close()
            print_all_client_connections()
            break


def print_all_client_connections():
    print('---------------------------------')
    print(f'Current Total Client Connections: {len(clients)}')
    for key, value in clients.items():
        print(f"- {value[1]}")
    print('---------------------------------')


def echo_to_all_clients(conn, data):
    sender_hostname = conn.getpeername()[0]
    message = data.decode('utf8')
    print('echoing', sender_hostname, 'message:', message)
    for key, sock in clients.items():
        if key == sender_hostname:
            continue
        else:
            echo_message = f"{sender_hostname}: {message}"
            sock[0].sendall(echo_message.encode('utf8'))


def start_server():

    print("Starting Chat Server.")
    HOST = input("Please Enter Server IP: ")
    PORT = input("Please Enter Server PORT: ")

    try:
        with socket(AF_INET, SOCK_STREAM) as normal_sock:
            sock = ssl.wrap_socket(normal_sock, ssl_version=ssl.PROTOCOL_TLS,
                                   certfile="server_cert.pem", keyfile="server_cert.pem")

            if not PORT.isdigit():
                raise ValueError

            sock.bind((HOST, int(PORT)))
            sock.listen(10)
            sock.setblocking(False)
            sel.register(sock, selectors.EVENT_READ, accept_client_connection)
            start_new_thread(read_user_input, (sel, sock, ))

            while True:
                events = sel.select()
                for key, mask in events:
                    callback = key.data
                    callback(key.fileobj, mask)

    except error as msg:
        print('Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
    finally:
        sel.close()


if __name__ == "__main__":
    start_server()
