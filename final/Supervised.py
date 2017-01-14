# coding: utf-8

from __future__ import print_function

# Retrieves data from MySQL
from Feature import Feature

# Reduces dimension
import AE
import numpy as np
from sklearn.decomposition import PCA

# Model training & predicting
from sklearn import svm

import sys
import math

BATCH = 128

def evaluate(ans, res):
    total = 0.0
    for i in range(len(ans)):
        total += math.abs(ans[i] - res[i])
    return total

if __name__ == '__main__':
    # Parses arguments
    if len(sys.argv) != 3 or (sys.argv[1] not in ['pca', 'ae']):
        print ("Usage:", sys.argv[0], "[dim reduce method (pca/ae)] [dimension]")
        sys.exit(1)

    DIM = int(sys.argv[2])

    feature = Feature()

    train_X, train_Y = feature.getYearFeatures(2015)

    test_X, test_Y = feature.getYearFeatures(2010)
    print ("All data prepared.")

    train_X_reduce = None
    test_X_reduce = None
    if sys.argv[1] == 'pca':
        pca = PCA(n_components = DIM)
        train_X_reduce = pca.fit_transform(np.array(train_X))
        # Applies same model on test data.
        test_X_reduce = pca.transform(np.array(test_X))
        print ("Dimension reduction done with PCA")
    else:
        train_X_reduce, ae_w, ae_b = AE.dim_reduce(np.array(train_X), DIM, BATCH, 50, 0.01)
        test_X_reduce = pca.forward2hidden(np.array(test_X), ae_w, ae_b, DIM)
        print ("Dimension reduction done with AE")

    clf = svm.SVR(verbose=True)
    clf.fit(train_X_reduce, train_Y)

    print ("Support vector machine fitting done.")

    # Predict
    test_Y_result = clf.predict(test_X_reduce)

    error = evaluate(test_Y, test_Y_result)
    print ("L1 error for 2010:", error)
    print ("Ans:", test_Y[:20])
    print ("SVM:", test_Y_result[:20])


