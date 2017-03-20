import hashlib
import re
import os
import socket
import mimetypes
import sys
import struct

curr_path = './client/'
shared_files = []
for file in os.listdir(curr_path):
    if os.path.isfile(os.path.join(curr_path, file)):
        shared_files.append(file)

############## Download

def download_file(name, sock):
    path = curr_path + name
    with open(path, 'wb') as file:
        while True:
            data = sock.recv(2048)
            if not data:
                break
            file.write(data)

def download_index(sock):
    while True:
        data = sock.recv(2048)
        if not data:
            break
        print(data.decode())

############## Comms

def comms(command, argv):
    sock = socket.socket()
    sock.connect((host, port))
    if command == 1:
        sock.send(struct.pack('II', 1, sys.getsizeof(argv)))
        sock.send(argv.encode())
        download_index(sock)
        pass
    elif command == 2:
        sock.send(struct.pack('II', 2, sys.getsizeof(argv)))
        sock.send(argv.encode())
        download_index(sock)
        pass
    elif command == 3:
        sock.send(struct.pack('II', 3, sys.getsizeof(argv)))
        sock.send(argv.encode())
        download_file(argv, sock)
    sock.close()

############## Main

if __name__ == '__main__':
    port = 60000
    host = ""
    while True:
        command = input('>> ')
        command = command.split(' ', 1)
        if command[0] == 'index':
            if len(command) <= 1:
                print('use arguments: longlist/ shortlist/ regex')
            else:
                if command[1] == 'regex' and len(command) <= 2:
                    print('use arguments: regex missing')
                else:
                    comms(1, command[1])
            pass
        elif command[0] == 'hash':
            if len(command) <= 1:
                print('use arguments: name of the file')
            else:
                comms(2, command[1])
            pass
        elif command[0] == 'download':
            comms(3, command[1])
        else:
            print(command[0], 'is an invalid command')
