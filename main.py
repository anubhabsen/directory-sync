#!/usr/local/bin/python3

import os
import socket
import json
import sys
from threading import Thread
import handler
import struct
from server import Server

class Client(Thread):
    def __init__(self, curr_path = './client', port = 60000):
        Thread.__init__(self)
        self.port = port
        self.curr_path = curr_path
        self.host = ""

    def run(self):
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
                        self.comms(1, command[1])
                pass
            elif command[0] == 'hash':
                if len(command) <= 1:
                    print('use arguments: name of the file')
                else:
                    self.comms(2, command[1])
                pass
            elif command[0] == 'download':
                splitarg = command[1].split(' ')
                if splitarg[0] == 'TCP':
                    self.comms(3, splitarg[1])
                elif splitarg[0] == 'UDP':
                    print('todo')
                else:
                    print('Flags are incorrect. Usage: TCP or UDP')
            elif command[0] == 'exit':
                print('yas')
                sys.exit()
            else:
                print(command[0], 'is an invalid command')

    def comms(self, command, argv, neg_print = False):
        sock = socket.socket()
        sock.connect((self.host, self.port))
        if command == 1:
            string_form = bytes(argv, 'utf-8')
            data = struct.pack("II%ds" % (len(string_form),), command, len(string_form), string_form)
            sock.send(data)
            print('Server files')
            print('=============')
            retval = self.download_index(sock, neg_print)
            print('CLient files')
            print('=============')
            argv = argv.split(' ')
            flag = argv[0]
            arg = argv[1:0]
            handler.format_data(handler.list_dir(flag, arg, self.curr_path))
            pass
        elif command == 2:
            string_form = bytes(argv, 'utf-8')
            data = struct.pack("II%ds" % (len(string_form),), command, len(string_form), string_form)
            sock.send(data)
            retval = self.download_index(sock, neg_print)
            pass
        elif command == 3:
            string_form = bytes(argv, 'utf-8')
            data = struct.pack("II%ds" % (len(string_form),), command, len(string_form), string_form)
            sock.send(data)
            retval = self.download_file(argv, sock)
        sock.close()
        return retval

    def download_file(self, name, sock):
        # server_hash = struct.unpack('256s', sock.recv(256))[0].decode()
        path = self.curr_path + name
        with open(path, 'wb') as file:
            while True:
                data = sock.recv(2048)
                if not data:
                    break
                file.write(data)

        client_hash = handler.get_hash(path)
        server_hash = self.comms(2, 'verify ' + name, True)[1][1]
        os.utime(path, (os.path.getatime(path), int(comms(2, 'verify ' + name, True)[1][2])))
        print('server hash', server_hash, 'client hash', client_hash)
        if server_hash.startswith(client_hash):
            print('file transfer successful')
        else:
            print('file transfer unsuccessful')

    def download_index(self, sock, neg_print = False):
        res = ''
        while True:
            data = sock.recv(2048)
            if not data:
                break
            res += data.decode()
        if neg_print:
            return json.loads(res)
        temp = json.loads(res)
        handler.format_data(temp)


if __name__ == '__main__':
    port = int(os.environ.get('port_no') or 60000)
    if port % 2 == 0:
        port2 = port + 1
    else:
        port2 = port - 1
    port2 = int(os.environ.get('port2_no') or port2)

    if port % 2 == 0:
        dir2 = './dir_one'
    else:
        dir2 = './dir_two'

    server = Server(dir2, port)
    client = Client(dir2, port2)
    server.start()
    client.start()
    server.join()
    client.join()



