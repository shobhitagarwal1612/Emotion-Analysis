import pickle
from time import time

from sklearn.cross_validation import train_test_split as tts
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import classification_report as clsr
from sklearn.neural_network._base import identity
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder

from analyzer.Transformer import NLTKPreprocessor


# @timeit
def build_and_evaluate(X, y, classifier=SGDClassifier, outpath=None, verbose=True):
    # @timeit
    def build(classifier, X, y=None):
        """
        Inner build function that builds a single model.
        """
        if isinstance(classifier, type):
            classifier = classifier()

        model = Pipeline([
            ('preprocessor', NLTKPreprocessor()),
            ('vectorizer', TfidfVectorizer(
                tokenizer=identity, preprocessor=None, lowercase=False)),
            ('classifier', classifier),
        ])

        model.fit(X, y)
        return model

    # Label encode the targets
    labels = LabelEncoder()
    y = labels.fit_transform(y)

    secs = time()

    # Begin evaluation
    if verbose: print("Building for evaluation")
    X_train, X_test, y_train, y_test = tts(X, y, test_size=0.2)
    model = build(classifier, X_train, y_train)

    if verbose:
        print("Evaluation model fit in {:0.3f} seconds".format(time() - secs))
        print("Classification Report:\n")

    y_pred = model.predict(X_test)
    print(clsr(y_test, y_pred, target_names=labels.classes_))

    secs = time()
    if verbose:
        print("Building complete model and saving ...")
    model = build(classifier, X, y)
    model.labels_ = labels

    if verbose:
        print("Complete model fit in {:0.3f} seconds".format(time() - secs))

    if outpath:
        with open(outpath, 'wb') as f:
            pickle.dump(model, f)

        print("Model written out to {}".format(outpath))

    return model
