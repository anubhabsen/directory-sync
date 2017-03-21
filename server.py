import hashlib
import re
import os
import socket
import json
import mimetypes
import sys
import struct
import handler

port = 60000
sock = socket.socket()
host = ""

curr_path = './server/'

sock.bind((host, port))
sock.listen(5)

def send_index(flag, argv, conn):

    table = handler.list_dir(flag, argv, curr_path)
    sending = json.dumps(table)
    conn.send(sending.encode())

def send_hash(flag, argv, conn):

    table = handler.list_hash(flag, argv, curr_path)
    sending = json.dumps(table)
    conn.send(sending.encode())

def send_file(name, conn):

    path = curr_path + name
    file = open(path, 'rb')
    # conn.send(struct.pack('256s', handler.get_hash(path).encode()))
    file_loc = file.read(2048)
    while file_loc:
        conn.send(file_loc)
        file_loc = file.read(2048)
    file.close()

def comms():

    data = conn.recv(struct.calcsize('II'))
    command, argv_size = struct.unpack('II', data)

    if command == 1:
        cmd = conn.recv(argv_size).decode()
        cmd = cmd.split(' ')
        flag = cmd[0]
        argv = cmd[1:]
        send_index(flag, argv, conn)
        pass
    elif command == 2:
        cmd = conn.recv(argv_size).decode().split(' ')
        flag = cmd[0]
        argv = cmd[1:]
        send_hash(flag, argv, conn)
        pass
    elif command == 3:
        argv = conn.recv(argv_size)
        send_file(argv.decode(), conn)

while True:
    conn, address = sock.accept()
    print('Got a connection from ', address)
    comms()
    print('Commenced sending')
    conn.close()
