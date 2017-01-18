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
        total += math.fabs(ans[i] - res[i])
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
        train_X_reduce = np.concatenate((
            pca.fit_transform(np.array([ x[0]+x[1] for x in train_X ])),
            np.array([ x[2] for x in train_X ])
        ), axis=1)
        # Applies same model on test data.
        test_X_reduce = np.concatenate((
            pca.transform(np.array([ x[0]+x[1] for x in test_X ])),
            np.array([ x[2] for x in test_X ])
        ), axis=1)
        print ("Dimension reduction done with PCA")
    else:
        train_X_reduce, ae_w, ae_b = AE.dim_reduce(
            np.array([ x[0]+x[1] for x in train_X ]), DIM, BATCH, 50, 0.01
        )
        train_X_reduce = np.concatenate((
            train_X_reduce, np.array([ x[2] for x in train_X ])
        ), axis=1)
        # Applies same model on test data
        test_X_reduce = np.concatenate((
            AE.forward2hidden(
                np.array([ x[0]+x[1] for x in test_X ]), ae_w, ae_b, DIM
            ), np.array([ x[2] for x in test_X ])
        ), axis=1)
        print ("Dimension reduction done with AE")

    clf = svm.SVR(verbose=True)
    clf.fit(train_X_reduce, train_Y)

    print ("Support vector machine fitting done.")

    # Predict
    test_Y_result = clf.predict(test_X_reduce)

    error = evaluate(test_Y, test_Y_result)
    print ("L1 error for 2010:", error)
    print ("Average error", error / len(train_Y))
    print ("Ans:", test_Y[:20])
    print ("SVM:", test_Y_result[:20])



