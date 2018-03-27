from concurrent.futures import ThreadPoolExecutor as TPE
from Connection import Connection
from AsyncConnection import AsyncConnection
from load_sky_data import main as load
from time import time
from sys import argv
import asyncio

THREADS = 1 if (len(argv) < 2) else int(argv[1])
CHUNKS = 1 if (len(argv) < 3) else int(argv[2])
THREADS_P = int(THREADS / CHUNKS)

def use_server():
	with Connection(address=('localhost', 5555)) as c:
		return c.get_predictions(X_test, opt=True)

X_train, X_test, Y_train, Y_test, translation = load()
del X_train, Y_train, Y_test, translation


def main(THREADS):
	futures = []
	start = time()
	with TPE(max_workers=THREADS) as executor:
		for _ in range(THREADS):
			futures.append(executor.submit(use_server))
	while not all(future.done() for future in futures):
		pass
	
	result = [future.result() for future in futures]

	print('{} threaded predictions of {} lines took {:.4} seconds'.format(THREADS, len(X_test), time()-start))
	return result

if __name__ == "__main__":
	"""
	Benchmark results
	1. 1016+ connections lead to OSError- Too many open files.
	On my Ubuntu OS.
	2. The below benchmarsk take 50-80 seconds per iteration, with significant variation.
	"""
# Threaded connections.
	for _ in range(CHUNKS):
		main(THREADS_P)

#Asynchronous/event-driven connections.
	loop = asyncio.get_event_loop()
	for _ in range(CHUNKS):
		connections = [AsyncConnection(
					address=('localhost', 5555), loop=loop) for _ in range(THREADS_P)]

		assert all(loop is c.loop for c in connections), "Event loop is not the same"
		actions = [c.get_predictions(X_test) for c in connections]
		start = time()
		results = loop.run_until_complete(asyncio.gather(*actions, loop=loop))
		print('{} async predictions of {} lines took {:.4} seconds'.format(THREADS_P, len(X_test), time()-start))

	loop.close()
