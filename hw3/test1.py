import numpy as np
import nimfa
from sklearn.metrics import mean_squared_error
import hungarian

import os
import sys

import math

N_USER = 50000
N_ITEM = 5000

class Model:
    def __init__(self):
        if len(sys.argv) < 2:
            print("Usage:", sys.argv[0], "[dir]")
            sys.exit(1)
        
        self.r1 = [[0 for i in range(N_USER)] for j in range(N_ITEM)]
        self.r2 = [[0 for i in range(N_USER)] for j in range(N_ITEM)]
        self.__readfile__()

    def train(self):
        # Run MF
        model = nimfa.Nmf(self.r1, max_iter=200)

        source_result = model.basis() * model.coef()

        # Turn vector of per user into distribution
        # And calculate the dot similarity
        # Then find the best data
        print("Transfer user vector into distribution.")

        item_pdf1 = []
        for i in range(N_ITEM):
            count = 0
            pdf = np.zeros(10)
            for j in range(N_USER):
                t = self.r1[i][j]
                if t == 0.0:
                    t = source_result[i][j]
                # ignore the count if it is 0.
                if t < 1e-9:
                    continue
                pdf[ math.floor(t/0.1) ] += 1
                count += 1
            pdf = pdf / count
            item_pdf1.append(pdf)
        
        item_pdf2 = []
        for i in range(N_ITEM):
            count = 0
            pdf = np.zeros(10) 
            for j in range(N_USER):
                if self.r2[i][j] > 0:
                    count += 1
                    pdf[ math.floor(self.r2[i][j] / 0.1) ] += 1
            pdf = pdf / count
            item_pdf2.append(pdf)

        # Transform now for further use: matrix[user]
        self.r1 = self.r1.T
        self.r2 = self.r2.T


        # Calculate cost matrix for items
        # matrix[item r1][item r2]
        matrix = np.array()
        for i in range(N_ITEM):
            l = np.array([
                matrix[j][i] if j < i
                else 0 if j == i
                else mean_squared_error(item_pdf1[i], item_pdf2[j])
            ])
            l[i][i] = 10000
            matrix.append(l)

        print "Hungarian running maximum matching...."
        match1to2, match2to1 = hungarian.lap(matrix)
        print "End of matching!"

        # Create item-matching version
        # trans[item in r2]
        trans = np.array()
        for item2 in range(N_ITEM):
            trans.append(source_result[match2to1[item2]])
        trans = trans.T

        # Find most similar user pair
        for user1 in range(N_USER):
            maxdot = -1
            bestmatch = -1
            for user2 in range(N_USER):
                dot = self.r2[user2] * trans[user1]
                if dot > maxdot:
                    maxdot = dot
                    bestmatch = user2
            self.r2[user1] = np.array([
                self.r2[user1][x] if self.r2[user1][x] > 0.0 
                else trans[user1][x]
                for x in range(N_USER)
            ])

        # MF again for the combined matrix.
        model = nimfa.Nmf(self.r2, max_iter=200)

        self.result = model.basis() * model.coef()

    def writeResult (self):
        test_file = os.path.join(sys.argv[1], "test.txt")
        with open(test_file, "w") as file:
            query = file.readlines()
            file.seek(0)
            file.truncate()

            for line in query:
                list = line.split()
                newline = "%s %s %f\n" % (
                    list[0], list[1],
                    self.result[int(list[0])][int(list[1])]
                )
                file.write(newline)
        


    def __readfile__(self):
        source_file = os.path.join(sys.argv[1], "source.txt")
        with open(source_file, "r") as file:
            line = file.readline()
            while line:
                l = line.split()
                self.r1[ int(l[1]) ][ int(l[0]) ] = float(l[2])
                line = file.readline()
        self.r1 = np.matrix(self.r1)

        target_file = os.path.join(sys.argv[1], "train.txt")
        with open(target_file, "r") as file:
            line = file.readline()
            while line:
                l = line.split()
                self.r2[ int(l[0]) ][ int(l[1]) ] = float(l[1])
                line = file.readline()
        self.r2 = np.matrix(self.r2)



if __name__ == '__main__':
    model = Model()
    model.train()
    model.writeResult()


