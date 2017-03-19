import struct
import socket

port = 60000
sock = socket.socket()
host = ""

curr_path = './server/'

sock.bind((host, port))
sock.listen(5)

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
		pass
	elif command == 2:
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