import os
import mimetypes
import sys

curr_path = '.'
shared_files = []
for file in os.listdir(curr_path):
	if os.path.isfile(os.path.join(curr_path, file)):
		shared_files.append(file)

def get_type(path):
	return mimetypes.guess_type(path)[0]

def list_files(flag, argv):
	print('yes')
	print('title\tsize\ttimestamp\ttype')
	for file in shared_files:
		path = os.path.join(curr_path, file)
		print(file + '\t' + str(os.path.getsize(path)) + '\t' + str(os.path.getmtime(path)) + '\t' + get_type(path))

if __name__ == '__main__':
    if sys.argv[1] == 'index':
        list_files(sys.argv[2], sys.argv[3:])
