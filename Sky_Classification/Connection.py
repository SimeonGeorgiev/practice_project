from json import dumps, loads
from sys import getsizeof
from math import floor
from socket import *

to_nested_bjson_list = lambda x: dumps([list(i) for i in x]).encode()
to_bjson_list = lambda x: dumps(list(x)).encode()
from_bjson = lambda x: loads(x.decode())

class Connection(object):

	def __init__(self, address, mode=[AF_INET, SOCK_STREAM]):
		self.sock = socket(*mode)
		ex = self.sock.connect_ex(address)
		if ex:
			print(ex)
		self.address = address
		self.mode = mode
		self.get_max_bytes()

	def set_server_help(self):
		self.sock.send(b'-help')
		resp = self.sock.recv(10000)
		self.help = loads(resp.decode())
		return self.help

	def get_max_bytes(self):
		# Also resets connections when they are reset by peer
		# The try: except: prevents this error
		# ConnectionResetError: [Errno 104] Connection reset by peer

		try:
			self.sock.send(b'maxbytes')
			resp = self.sock.recv(1024)
			self.maxbytes = int(resp.decode())
		except ConnectionResetError:
			self.sock = socket(*self.mode)
			self.sock.connect(self.address)
			self.sock.send(b'maxbytes')
			resp = self.sock.recv(1024)
			self.maxbytes = int(resp.decode())

	def get_predictions(self,  X, opt=False):
		sock = self.sock
		shape = X.shape

		if len(shape) == 1:
			sock.send(to_nested_bjson_list(X.reshape(1, -1)))
			resp = sock.recv(self.maxbytes)
			prediction = from_bjson(resp)
		else:
			one_element_size = getsizeof(to_bjson_list(X[0]))
			max_elements = floor(self.maxbytes/one_element_size)
			prediction = []

			for index in range(0, shape[0], max_elements):
				to = index + max_elements
				sock.send(to_nested_bjson_list(X[index:to]))
				resp = from_bjson(sock.recv(self.maxbytes))
				prediction.extend(resp)
		if opt:
			self.set_server_help()
			sock.send(b'exit')
		return prediction

	def __del__(self):
		try:
			self.sock.close()
		except AttributeError:
			pass

	def close(self):
		self.sock.close()

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		self.sock.close()