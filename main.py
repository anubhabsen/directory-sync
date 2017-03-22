#!/usr/local/bin/python3

import os
import socket
import json
import sys
from threading import Thread, Timer
import handler
import struct
import subprocess
import stat
from server import Server

class Client(Thread):
    def __init__(self, curr_path = './client', port = 60000):
        Thread.__init__(self)
        self.port = port
        self.curr_path = curr_path
        self.host = ""
        self.thread = Timer(15, self.sync_folders)
        self.thread.start()

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
                    self.udp_comms(3, command[1])
                else:
                    print('Flags are incorrect. Usage: TCP or UDP')
            elif command[0] == 'exit':
                quit()
            elif command[0] == '':
                pass
            else:
                print(command[0], 'is an invalid command')

    def udp_comms(self, command, argv, noPrint = False):
        sock = socket.socket()
        sock.connect((self.host, self.port))
        s = bytes(argv, 'utf-8')
        data = struct.pack("II%ds" % (len(s),), command, len(s), s)
        sock.send(data)
        if command == 3:
            argv = argv.split(' ')
            fname = argv[1]
            size = 0
            sock.close()
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.connect((self.host, self.port))
            sock.send(fname.encode())
            size = sock.recv(4)
            size, = struct.unpack('I', size)
            retval = self.download_file_udp(fname, sock, size)
        sock.close()
        return retval

    def download_file_udp(self, fname, sock, size = 0):
        fpath = self.curr_path + fname
        with open(fpath, 'wb') as f:
            recv_now = 0
            while True:
                data = sock.recv(2048)
                if not data:
                    break
                f.write(data)
                recv_now += 2048
                if recv_now > size:
                    break
        client_hash = handler.get_hash(fpath)
        server_hash = self.comms(2, 'verify ' + fname, True)[1][1]
        os.utime(fpath, (os.path.getatime(fpath), int(self.comms(2, 'verify ' + fname, True)[1][2])))
        print('server hash', server_hash, 'client hash', client_hash)
        if server_hash.startswith(client_hash):
            print('file transfer successful')
        else:
            print('file transfer unsuccessful')

    def sync_folders(self):
        self.thread = Timer(15, self.sync_folders)
        self.thread.start()
        print('synchronising')
        files_list1 = self.comms(2, 'checkall', True)[1:]
        files_list2 = []
        for file in os.listdir(self.curr_path):
            if os.path.isfile(os.path.join(self.curr_path, file)):
                files_list2.append(file)
        for file in files_list1:
            name = file[0]
            if name in files_list2:
                # res = handler.change_details(self.curr_path + name)
                res_hash = handler.get_hash(self.curr_path + name)
                res_time = int(os.path.getmtime(self.curr_path + name))
                if res_hash != file[1] and res_time < file[2]:
                    self.comms(3, name)
            else:
                self.comms(3, name)

        if self.curr_path == './dir_one/':
            other_path = './dir_two/'
        else:
            other_path = './dir_one/'

        for file in files_list1:
            name = file[0]
            if name in files_list2:
                if oct(stat.S_IMODE(os.lstat(other_path + name).st_mode)) != oct(stat.S_IMODE(os.lstat(self.curr_path + name).st_mode)):
                    permi = (stat.S_IMODE(os.lstat(other_path + name).st_mode))
                    os.chmod(self.curr_path + name, (permi))

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
        os.utime(path, (os.path.getatime(path), int(self.comms(2, 'verify ' + name, True)[1][2])))
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
        dir2 = './dir_one/'
    else:
        dir2 = './dir_two/'

    server = Server(dir2, port)
    client = Client(dir2, port2)
    server.start()
    client.start()
    server.join()
    client.join()
