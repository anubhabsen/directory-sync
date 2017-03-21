#!/usr/local/bin/python3

import hashlib
import re
import os
import socket
import json
from threading import Thread
import mimetypes
import sys
import struct
import handler

def send_index(flag, argv, conn, curr_path):

    table = handler.list_dir(flag, argv, curr_path)
    sending = json.dumps(table)
    conn.send(sending.encode())

def send_hash(flag, argv, conn, curr_path):

    table = handler.list_hash(flag, argv, curr_path)
    sending = json.dumps(table)
    conn.send(sending.encode())

def send_file(name, conn, curr_path):

    path = curr_path + name
    file = open(path, 'rb')
    # conn.send(struct.pack('256s', handler.get_hash(path).encode()))
    file_loc = file.read(2048)
    while file_loc:
        conn.send(file_loc)
        file_loc = file.read(2048)
    file.close()

def comms(conn, curr_path):

    data = conn.recv(struct.calcsize('II'))
    command, argv_size = struct.unpack('II', data)

    if command == 1:
        cmd = conn.recv(argv_size).decode()
        cmd = cmd.split(' ')
        flag = cmd[0]
        argv = cmd[1:]
        send_index(flag, argv, conn, curr_path)
        pass
    elif command == 2:
        cmd = conn.recv(argv_size).decode().split(' ')
        flag = cmd[0]
        argv = cmd[1:]
        send_hash(flag, argv, conn, curr_path)
        pass
    elif command == 3:
        argv = conn.recv(argv_size)
        send_file(argv.decode(), conn, curr_path)

class Server(Thread):
    def __init__(self, curr_path = './server/', port = 60000):
        Thread.__init__(self)
        self.curr_path = curr_path
        host = os.environ.get('host_name') or ""
        self.sock = socket.socket()
        self.sock.bind((host, port))
        self.sock.listen(5)

    def run(self):
        while True:
            conn, address = self.sock.accept()
            print('Got a connection from ', address)
            comms(conn, self.curr_path)
            print('Commenced sending')
            conn.close()

