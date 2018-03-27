from pandas import read_csv
import numpy as np

def transform_df(df, test):
	"""
		Used to drop columns and convert classes to numerical,
		for easier classification. 
		Can be applied to any df in the format of sky_query.csv.
		Use with test=0 to get data in the format the server understands."""
	drop_a_col = lambda x: df.drop(x, axis=1, inplace=True)
	map(drop_a_col, ('objid', 'rerun'))

	np.random.seed(1)
	df = df.reindex(np.random.permutation(df.index), copy=False)
	
	Y = df['class'].copy().astype('category').values
	lenY =  len(Y)
	cat_codes, Y = np.unique(Y, return_inverse=True) #
	# cat_codes is the list of strings that correspond to class names
	# Y is an integer array: each elements corresponds to an index in cat_codes
 
	translation = {i: cat for i, cat in zip(np.unique(Y), cat_codes)}
	# translation is a dictionary/map: {int: cat_code}.

	drop_a_col('class')
	split_on = int(lenY - (lenY*test))
	get_split = lambda ar: [ar[0:split_on], ar[split_on:]]
	# get_split returns a list of the Train/Test split for the input

	X = df.values
	return (get_split(X) + get_split(Y) + [translation])

def main(test=0.1):
	df = read_csv('sky_query.csv')
	return transform_df(df=df, test=test)

if __name__ == '__main__':
	X_train, X_test, Y_train, Y_test, translation = main() # Python tuple/list unpacking
	print([len(i) for i in main()])