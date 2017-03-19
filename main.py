import os
import mimetypes
import sys

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
    col = max
    for row in table:
        print("".join(word.ljust(col) for word in row))

def get_type(path):
    return mimetypes.guess_type(path)[0] or 'text/plain'

def list_files(flag, argv):
    table = [['Title', 'Size', 'TimeStamp', 'Type']]
    for file in shared_files:
        path = os.path.join(curr_path, file)
        table.append([file, str(os.path.getsize(path)), str(os.path.getmtime(path)), get_type(path)])
    format_data(table)

if __name__ == '__main__':
    if sys.argv[1] == 'index':
        list_files(sys.argv[2], sys.argv[3:])
