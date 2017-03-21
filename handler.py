import os
import mimetypes
import hashlib
import re
import sys
import datetime

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
    print(file_list)
    return file_list

def list_dir(flag, argv, curr_path):
    shared_files = []
    for file in os.listdir(curr_path):
        if os.path.isfile(os.path.join(curr_path, file)):
            shared_files.append(file)
    table = [['Title', 'Size', 'TimeStamp', 'Type']]
    for file in shared_files:
        time = (datetime.datetime.fromtimestamp(os.path.getmtime(os.path.join(curr_path, file))).strftime('%Y-%m-%d %H:%M:%S'))
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
    return table

def get_hash(path):
    with open(path, 'rb') as file_hash:
        hash_val = hashlib.md5()
        while True:
            data = file_hash.read(4096)
            if not data:
                break
            hash_val.update(data)
        return hash_val.hexdigest()

def list_hash(flag, argv, curr_path):
    shared_files = []
    for file in os.listdir(curr_path):
        if os.path.isfile(os.path.join(curr_path, file)):
            shared_files.append(file)
    table = [['File', 'Hash Value', 'Time Modified']]
    if flag != 'verify' and flag != 'checkall':
        sending = 'incorrect flag given. Usage: flag: verify/ checkall'
        return sending
    else:
        if flag == 'verify':
            shared_files = [argv[0]]
        for file in shared_files:
            path = os.path.join(curr_path, file)
            if not os.path.isfile(path):
                # print('The file', argv[0], 'doesn\'t exist.')
                sending = 'The file ' + argv[0] + ' doesn\'t exist.'
                return sending
            else:
                time = (datetime.datetime.fromtimestamp(os.path.getmtime(os.path.join(curr_path, file))).strftime('%Y-%m-%d %H:%M:%S'))
                table.append([file, str(get_hash(path)), str(time)])
                return table
