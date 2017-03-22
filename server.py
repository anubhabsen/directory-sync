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
    if os.path.isfile(path):
        file = open(path, 'rb')
    else:
        print('Incorrect file path')
        print('>> ')
        return
    # conn.send(struct.pack('256s', handler.get_hash(path).encode()))
    file_loc = file.read(2048)
    while file_loc:
        conn.send(file_loc)
        file_loc = file.read(2048)
    file.close()

def send_file_udp(fname, conn, curr_path, upd_address):
    fpath = curr_path + fname
    if os.path.isfile(fpath):
        size = os.path.getsize(fpath)
    else:
        print('Incorrect file path')
        print('>> ')
        return
    conn.sendto(struct.pack('I', size), upd_address)
    f = open(fpath, 'rb')
    l = f.read(2048)
    while l:
        conn.sendto(l, upd_address)
        l = f.read(2048)
    f.close()

def comms(conn, curr_path, sudp = None):

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
        argv = conn.recv(argv_size).decode().split(' ')
        flag = argv[0]
        fname = argv[1]
        if flag == 'UDP':
            data, address = sudp.recvfrom(2048)
            send_file_udp(fname, sudp, curr_path, address)
        else:
            send_file(fname, conn, curr_path)

class Server(Thread):
    def __init__(self, curr_path = './server/', port = 60000):
        Thread.__init__(self)
        self.curr_path = curr_path
        host = os.environ.get('host_name') or ""
        self.sudp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sudp.bind((host, port))
        self.sock = socket.socket()
        self.sock.bind((host, port))
        self.sock.listen(5)

    def run(self):
        while True:
            conn, address = self.sock.accept()
            print('Got a connection from ', address)
            comms(conn, self.curr_path, self.sudp)
            print('Commenced sending')
            print('>> ')
            conn.close()

