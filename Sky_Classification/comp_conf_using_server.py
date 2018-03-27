from Connection import Connection
from sklearn.metrics import confusion_matrix
from load_sky_data import main as load
from time import time

start = time()
X_train, X_test, Y_train, Y_test, translation = load()
print('data loading takes: {:.3}'.format(time()-start))
start = time()

with Connection(address=('localhost', 5555)) as c:
	Y_pred = c.get_predictions(X_test)
	c.set_server_help()

rev_trans = {v: k for k, v in translation.items()}
Y_pred = list(map(lambda x: rev_trans[x], Y_pred))
Y_test = list(Y_test)

cf = confusion_matrix(y_pred=Y_pred, y_true=Y_test, labels=[0, 1, 2])

print('Confusion matrix:', cf, '', sep='\n')

print('Feature importances:{}'.format(c.help['feature_importances']))
print('Connection, prediction, help message and confusion_matrix took:',
		time()-start, sep='\n')