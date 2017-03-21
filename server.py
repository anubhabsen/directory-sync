import hashlib
import re
import os
import socket
import mimetypes
import sys
import struct

port = 60000
sock = socket.socket()
host = ""

curr_path = './server/'

sock.bind((host, port))
sock.listen(5)

def format_data(table):
    file_list = ''
    max = 0
    for row in table:
        for word in row:
            if max < len(word):
                max = len(word)
    col = max + 3
    for row in table:
        file_list += "".join(word.ljust(col) for word in row) + '\n'
    return file_list

def send_index(flag, argv, conn):

    shared_files = []
    for file in os.listdir(curr_path):
        if os.path.isfile(os.path.join(curr_path, file)):
            shared_files.append(file)
    table = [['Title', 'Size', 'TimeStamp', 'Type']]
    for file in shared_files:
        time = os.path.getmtime(os.path.join(curr_path, file))
        path = os.path.join(curr_path, file)
        if flag == 'shortlist':
            start_time = float(argv[0])
            end_time = float(argv[1])
            if time < start_time or time > end_time:
                continue
        elif flag == 'regex':
            if not re.fullmatch('.*' + argv[0], file):
                continue
        table.append([file, str(os.path.getsize(path)), str(time), mimetypes.guess_type(path)[0] or 'text/plain'])
    sending = format_data(table)
    conn.send(sending.encode())

def send_hash(flag, argv, conn):
    def get_hash(path):
        with open(path, 'rb') as file_hash:
            hash_val = hashlib.md5()
            while True:
                data = file_hash.read(4096)
                if not data:
                    break
                hash_val.update(data)
            return hash_val.hexdigest()

    def change_details(path):
        return(get_hash(path), os.path.getmtime(path))

    shared_files = []
    for file in os.listdir(curr_path):
        if os.path.isfile(os.path.join(curr_path, file)):
            shared_files.append(file)
    table = [['File', 'Hash Value', 'Time Modified']]
    if flag != 'verify' and flag != 'checkall':
        sending = 'incorrect flag given. Usage: flag: verify/ checkall'
        conn.send(sending.encode())
    else:
        if flag == 'verify':
            shared_files = [argv[0]]
        for file in shared_files:
            path = os.path.join(curr_path, file)
            if not os.path.isfile(path):
                # print('The file', argv[0], 'doesn\'t exist.')
                sending = 'The file ' + argv[0] + ' doesn\'t exist.'
                conn.send(sending.encode())
                return
            else:
                time = os.path.getmtime(path)
                table.append([file, str(get_hash(path)), str(time)])
        sending = format_data(table)
        conn.send(sending.encode())

def send_file(name, conn):
    path = curr_path + name
    file = open(path, 'rb')
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
        print(command, flag, argv)
        send_index(flag, argv, conn)
        pass
    elif command == 2:
        cmd = conn.recv(argv_size).decode().split(' ')
        flag = cmd[0]
        argv = cmd[1:]
        print(command, flag, argv)
        send_hash(flag, argv, conn)
        pass
    elif command == 3:
        argv = conn.recv(argv_size)
        print(command, argv.decode())
        send_file(argv.decode(), conn)

while True:
    conn, address = sock.accept()
    print('Got a connection from ', address)
    comms()
    print('Commenced sending')
    conn.close()