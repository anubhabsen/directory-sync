import os
import socket
import json
import sys
import handler
import struct

curr_path = './client/'
shared_files = []
for file in os.listdir(curr_path):
    if os.path.isfile(os.path.join(curr_path, file)):
        shared_files.append(file)

############## Download

def download_file(name, sock):
    # server_hash = struct.unpack('256s', sock.recv(256))[0].decode()
    path = curr_path + name
    with open(path, 'wb') as file:
        while True:
            data = sock.recv(2048)
            if not data:
                break
            file.write(data)

    client_hash = handler.get_hash(path)
    server_hash = comms(2, 'verify ' + name, True)[1][1]
    os.utime(path, (os.path.getatime(path), int(comms(2, 'verify ' + name, True)[1][2])))
    print('server hash', server_hash, 'client hash', client_hash)
    if server_hash.startswith(client_hash):
        print('file transfer successful')
    else:
        print('file transfer unsuccessful')

def download_index(sock, neg_print = False):
    res = ''
    while True:
        data = sock.recv(2048)
        if not data:
            break
        res += data.decode()
    if neg_print:
        return json.loads(res)
    handler.format_data(json.loads(res))

############## Comms

def comms(command, argv, neg_print = False):
    sock = socket.socket()
    sock.connect((host, port))
    if command == 1:
        sock.send(struct.pack('II', 1, sys.getsizeof(argv)))
        sock.send(argv.encode())
        print('Server files')
        print('=============')
        retval = download_index(sock, neg_print)
        print('CLient files')
        print('=============')
        argv = argv.split(' ')
        flag = argv[0]
        arg = argv[1:0]
        handler.format_data(handler.list_dir(flag, arg, curr_path))
        pass
    elif command == 2:
        sock.send(struct.pack('II', 2, sys.getsizeof(argv)))
        sock.send(argv.encode())
        retval = download_index(sock, neg_print)
        pass
    elif command == 3:
        sock.send(struct.pack('II', 3, sys.getsizeof(argv)))
        sock.send(argv.encode())
        retval = download_file(argv, sock)
    sock.close()
    return retval

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
            elif (command[1].startswith('longlist') == False and command[1].startswith('shortlist') == False and command[1].startswith('regex') == False):
                print('incorrect flag')
            else:
                if command[1] == 'regex' and len(command) <= 2:
                    print('use arguments: regex missing')
                elif command[1] == 'shortlist' and len(command) != 4:
                    print('limits of shortlist not proper')
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
            splitarg = command[1].split(' ')
            if splitarg[0] == 'TCP':
                comms(3, splitarg[1])
            elif splitarg[0] == 'UDP':
                print('todo')
            else:
                print('Flags are incorrect. Usage: TCP or UDP')
        else:
            print(command[0], 'is an invalid command')
