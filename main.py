import hashlib
import re
import os
import socket
import mimetypes
import sys
import struct

curr_path = '.'
shared_files = []
for file in os.listdir(curr_path):
    if os.path.isfile(os.path.join(curr_path, file)):
        shared_files.append(file)

def format_data(table):
    max = 0
    for row in table:
        for word in row:
            if max < len(word):
                max = len(word)
    col = max + 3
    for row in table:
        print("".join(word.ljust(col) for word in row))

def get_type(path):
    return mimetypes.guess_type(path)[0] or 'text/plain'

def list_files(flag, argv):
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
        table.append([file, str(os.path.getsize(path)), str(time), get_type(path)])
    format_data(table)

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

def comms(command, argv):
    sock = socket.socket()
    sock.connect((host, port))
    if command == 1:
        pass
    elif command == 2:
        pass
    elif command == 3:
        sock.send(struct.pack('II', 3, sys.getsizeof(argv)))
        sock.send(argv.encode())
    sock.close()

if __name__ == '__main__':
    port = 60000
    host = ""
    while True:
        command = input('>> ')
        command = command.split(' ')
        if command[0] == 'index':
            pass
        elif command[0] == 'hash':
            pass
        elif command[0] == 'download':
            comms(3, command[-1])
