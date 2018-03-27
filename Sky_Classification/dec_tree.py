from sklearn.tree import DecisionTreeClassifier as Tree
from sklearn.feature_selection import VarianceThreshold
from sklearn.pipeline import make_pipeline
from sklearn.externals import joblib
from load_sky_data import main as load
from sklearn.model_selection import cross_val_score
from sklearn.metrics import confusion_matrix
from pandas import DataFrame as DF


clf = make_pipeline(
	VarianceThreshold(0.1),
	Tree(criterion="entropy", min_samples_leaf=12, max_depth=5, min_samples_split=6)
)


X_train, X_test, Y_train, Y_test, translation = load()

clf.fit(X_train, Y_train)
print(clf.score(X_test, Y_test))

filename = 'sky_classifier.joblib.pkl'
joblib.dump(clf, filename, compress=9)

with open('feature_importances.pyout', 'w') as f:
	print({'Feature importances': list(clf.steps[-1][1].feature_importances_)}, file=f)

with open('translation.pyout', 'w') as f:
	print(translation, file=f)


Y_pred = clf.predict(X_test)

conf_matrix = confusion_matrix(y_pred=Y_pred, y_true=Y_test, labels=[0, 1, 2])
translations = [translation[i] for i in range(3)]
assert len(translations) == 3

conf_df = DF(conf_matrix, columns=translations, index=translations)

conf_df.to_csv('conf_matrix.csv')
