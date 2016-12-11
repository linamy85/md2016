import numpy as np
import nimfa
from sklearn.metrics import mean_squared_error
import hungarian

from threading import Thread

import os
import sys

from time import gmtime, strftime

import math

N_USER = 50000
N_ITEM = 5000

class Model:
    def __init__(self):
        if len(sys.argv) < 2:
            print("Usage:", sys.argv[0], "[dir]")
            sys.exit(1)

        self.rank = 40
        if len(sys.argv) > 2:
            self.rank = int(sys.argv[2])
        self.iter = 100
        if len(sys.argv) > 3:
            self.iter = int(sys.argv[3])
        self.alpha = 0
        if len(sys.argv) > 4:
            self.alpha = float(sys.argv[4])
        self.method = 'nmf'
        if len(sys.argv) > 5:
            self.method = sys.argv[5]
        
        self.r1 = [[0 for i in range(N_USER)] for j in range(N_ITEM)]
        self.r2 = [[0 for i in range(N_USER)] for j in range(N_ITEM)]
        self.__readfile__()

    def train(self):
        # Run MF
        print "Running non-negative MF....", strftime(
            "%Y-%m-%d %H:%M:%S", gmtime())
        source_result = None
        if self.method == "nmf":
            modelnmf = nimfa.Nmf(self.r1, rank=self.rank, max_iter=self.iter)
        elif self.method == "lfnmf":
            modelnmf = nimfa.Lfnmf(self.r1, rank=self.rank, max_iter=self.iter)
        elif self.method == "nsnmf":
            modelnmf = nimfa.Nsnmf(self.r1, rank=self.rank, max_iter=self.iter)
        elif self.method == "pmf":
            modelnmf = nimfa.Pmf(self.r1, rank=self.rank, max_iter=self.iter)
        elif self.method == "psmf":
            modelnmf = nimfa.Psmf(self.r1, rank=self.rank, max_iter=self.iter)
        elif self.method == "snmf":
            modelnmf = nimfa.Snmf(self.r1, rank=self.rank, max_iter=self.iter)
        elif self.method == "sepnmf":
            modelnmf = nimfa.Sepnmf(self.r1, rank=self.rank, max_iter=self.iter)
        else:
            print "No model is being recognized, stopped."
            sys.exit(1)

        model = modelnmf()
        source_result = np.array(model.fitted())

        print "Done MF!", strftime("%Y-%m-%d %H:%M:%S", gmtime())


        # Turn vector of per user into distribution
        # And calculate the dot similarity
        # Then find the best data
        print("Transfer user vector into distribution.",
              strftime("%Y-%m-%d %H:%M:%S", gmtime()))

        item_pdf1 = []
        for i in range(N_ITEM):
            count = 0
            pdf = np.zeros(11)
            for j in range(N_USER):
                t = self.r1[i][j]
                if t == 0.0:
                    t = source_result[i][j]

                # ignore the count if it is 0.
                if t < 1e-4:
                    continue

                idx = min(int(math.floor(t / 0.1)), 10)
                pdf[idx] += 1
                count += 1
            if count > 1:
                pdf = pdf / count
            # print count
            item_pdf1.append(pdf)
        
        item_pdf2 = []
        for i in range(N_ITEM):
            count = 0
            pdf = np.zeros(11) 
            for j in range(N_USER):
                if self.r2[i][j] > 0:
                    count += 1
                    pdf[ int(math.floor(self.r2[i][j] / 0.1)) ] += 1
            if count > 1:
                pdf = pdf / count
            item_pdf2.append(pdf)

        # Transform now for further use: matrix[user]
        # self.r1 = self.r1.T
        # self.r2 = self.r2.T


        print "Calculate cost matrix....", strftime(
            "%Y-%m-%d %H:%M:%S", gmtime())
        # Calculate cost matrix for items
        # matrix[item r1][item r2]

        # Uses 5 threads to run this slowest part.
        partition = 5
        matrix = [[] for i in range(partition)] 

        threads = []
        ll = np.split(np.array(range(N_ITEM)), partition)
        for index in range(partition):
            thread = Thread(
                target = self.threadFunc, args = (
                    matrix[index], ll[index], item_pdf1, item_pdf2)
            )
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()
        
        matrix = np.array(np.concatenate(matrix, axis=0))

        print "Matrix shape: ", matrix.shape

        print "Hungarian running maximum matching....", strftime(
            "%Y-%m-%d %H:%M:%S", gmtime())
        match1to2, match2to1 = hungarian.lap(matrix)
        print "End of matching!", strftime("%Y-%m-%d %H:%M:%S", gmtime())

        # Create item-matching version
        # trans[item in r2]
        trans = []
        for item2 in range(N_ITEM):
            trans.append(source_result[match2to1[item2]])
        trans = np.array(trans).T

        # Find most similar user pair
        print "Find most similar user pair..... Write file...", strftime(
            "%Y-%m-%d %H:%M:%S", gmtime())

        self.writeTrans(trans)

        print "Done, enter cpp mode", strftime(
            "%Y-%m-%d %H:%M:%S", gmtime())

        # MF again for the combined matrix.
        # model = nimfa.Nmf(self.r2, max_iter=200)

        # self.result = np.array(model().fitted())

    def threadFunc (self, matrix, list, item_pdf1, item_pdf2):
        for i in list:
            l = np.array([
                mean_squared_error(
                    item_pdf1[i], item_pdf2[j]
                ) for j in range(N_ITEM)
            ])
            matrix.append(l)


    def writeTrans (self, trans):
        tran_file = os.path.join(sys.argv[1], "tran.txt")
        with open(tran_file, "w") as file:
            for user in range(N_USER):
                for item in range(N_ITEM):
                    file.write("%.9f " % trans[user][item])
                file.write("\n")

        


    def __readfile__(self):
        source_file = os.path.join(sys.argv[1], "source.txt")
        with open(source_file, "r") as file:
            line = file.readline()
            while line:
                l = line.split()
                self.r1[ int(l[1]) ][ int(l[0]) ] = float(l[2])
                line = file.readline()
        self.r1 = np.array(self.r1)

        target_file = os.path.join(sys.argv[1], "train.txt")
        with open(target_file, "r") as file:
            line = file.readline()
            while line:
                l = line.split()
                self.r2[ int(l[1]) ][ int(l[0]) ] = float(l[2])
                line = file.readline()
        self.r2 = np.array(self.r2)



if __name__ == '__main__':
    model = Model()
    model.train()
    # model.writeResult()


