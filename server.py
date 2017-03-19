import struct
import socket

port = 60000
sock = socket.socket()
host = ""

sock.bind((host, port))
sock.listen(5)

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

while True:
	conn, address = sock.accept()
	print('Got a connection from ', address)
	comms()
	print('Commenced sending')
	conn.send('Thank you for connecting'.encode())
	conn.close()