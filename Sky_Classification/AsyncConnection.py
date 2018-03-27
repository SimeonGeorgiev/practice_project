from json import dumps, loads
from sys import getsizeof
from math import floor
from socket import *
import asyncio
from numpy import ndarray

to_nested_bjson_list = lambda x: \
				dumps([list(i) for i in x]).encode()

to_bjson_list = lambda x: \
				dumps(list(x)).encode()

from_bjson = lambda x: \
				loads(x.decode())

class AsyncConnection(object):
	"""
	Run get_predictions in an event loop to get predictions from a server.
	After get_predictions the object will have a .help attribute.
	This is not an asynchronous context manager
	"""
	def __init__(self, address, loop=False, mode=[AF_INET, SOCK_STREAM]):
		self.sock = socket(*mode)
		self.mode = mode
		self.loop = loop if loop else asyncio.get_event_loop()
		self.address = address

	async def set_server_help(self):
		resp = await self.send_recv(message=b'-h', nbytes=10000)
		self.help = loads(resp.decode())

	async def set_maxbytes(self):
		resp = await self.send_recv(message=b'maxbytes', nbytes=512)
		self.maxbytes = int(resp.decode())

	async def send_recv(self, message: bytes, nbytes: int) -> bytes:
		await self.loop.sock_sendall(sock=self.sock, data=message)
		return await self.loop.sock_recv(sock=self.sock, n=nbytes)

	async def get_predictions(self,  X: ndarray) -> list:
		await self.loop.sock_connect(sock=self.sock, address=self.address)
		shape = X.shape
		if len(shape) == 1: # if there is only one element

			prediction = from_bjson(await self.send_recv(
							nbytes=10000,
							message=to_nested_bjson_list(X.reshape(1, -1))),
							)

		else:
			await self.set_maxbytes()
			one_element_size = getsizeof(to_bjson_list(X[0]))
			max_elements = floor(self.maxbytes / one_element_size)
			index_to = map(lambda x: [x, x+max_elements],
								range(0, shape[0], max_elements))
			# index_to contains the indexes used to send the array in chunks
			
			resp = await asyncio.gather(*[self.send_recv(
							message=to_nested_bjson_list(X[index:to]),
							nbytes=self.maxbytes) for index, to in index_to],
						loop=self.loop) # asyncio.gather(list of coroutines) -> list[results]

			prediction = map(from_bjson, resp); del resp, X

		await self.set_server_help()
		await self.loop.sock_sendall(sock=self.sock, data=b'exit')
		self.loop.call_soon(self.sock.close)
		return list(prediction)

if __name__ == '__main__':
	c = AsyncConnection(address=('localhost', 5555))