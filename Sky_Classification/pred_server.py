from socket import *
import async2
from sklearn.externals import joblib
from sklearn.tree import export_graphviz
from numpy import array
from json import loads, dumps
import os.path
import asyncio

from_nested_bjson_list = lambda x: array(loads(x.decode()))

classifier_pickle = 'sky_classifier.joblib.pkl'

if not os.path.isfile(classifier_pickle):
	import dec_tree # runs the module, training the decision tree

clf = joblib.load(classifier_pickle)

with open('translation.pyout', 'r') as f:
	translation = eval(f.read())

assert type(translation) == dict, "The file should have a dict in it."

async def make_prediction(x, translation, clf):
	prediction = clf.predict(x)
	if len(prediction) == 1:
		try:prediction = translation[prediction]
		except:prediction = translation[prediction[0]]
	else:
		prediction = [translation[p] for p in prediction]
	return prediction


async def prediction_server(address, max_connections=2000):
	sock = socket(AF_INET, SOCK_STREAM)
	sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
	sock.bind(address)
	sock.listen(max_connections)
	sock.setblocking(False)
	n_con = 1
	while True:
		client, addr = await loop.sock_accept(sock)
		#print('Connection from', addr, 'Total:', n_con)
		loop.create_task(prediction_handler(client, clf))
		n_con += 1

async def prediction_handler(client, clf):
	maxbytes = 10000
	help_message = dumps({'maxbytes': maxbytes,
							'clf': repr(clf),
							'dot': export_graphviz(clf.steps[-1][1],
													out_file=None),
							'feature_importances': list(clf.steps[-1][1].feature_importances_),
						}).encode()

	with client:
		while True:
			data = await loop.sock_recv(client, maxbytes)
			if not data or data in (b'q', b'quit', b'exit'): 
				break
			elif data in (b'help', b'-h', b'-help', b'--help'):
				data = help_message
			elif data in (b'max', b'maxbytes', b'maxdata'):
				data = str(maxbytes).encode()
			else:
				try:
					data = from_nested_bjson_list(data)
					data = await make_prediction(data, translation, clf)
					data = dumps(data).encode()
				except (TypeError, ValueError) as e:
					print(e) # Prints the error message for debugging 
					data = bytes(str(e), encoding = 'utf-8')
			await loop.sock_sendall(client, data)	
	#print('Connection closed')

# The two loops are kept for benchmarking.
#loop = async2.Loop(); print('Using Custom Loop')
loop = asyncio.get_event_loop(); print('Using Built-in Loop')
loop.create_task(prediction_server(('', 5555), max_connections=5))
loop.run_forever()
