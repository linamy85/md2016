import os
from time import gmtime, strftime
import sys

import numpy as np
import nimfa

class Postcpp:
    def __init__(self, filename):
        self.mat = []

        print "Start reading matching matrix from cpp :", strftime(
            "%Y-%m-%d %H:%M:%S", gmtime())
        with open(filename, "r") as file:
            line = file.readline()
            while line:
                self.mat.append(np.array(map(float, line.split())))
                line = file.readline()

        self.rank = 40
        if len(sys.argv) > 3:
            self.rank = int(sys.argv[3])
        self.iter = 100
        if len(sys.argv) > 4:
            self.iter = int(sys.argv[4])
        self.alpha = 0
        if len(sys.argv) > 5:
            self.alpha = float(sys.argv[5])
        self.method = 'nimfa'
        if len(sys.argv) > 6:
            self.method = sys.argv[6]

        self.mat = np.array(self.mat)
        print "Done. Now enter last step -- MF", strftime(
            "%Y-%m-%d %H:%M:%S", gmtime())

    def run(self, output_file):
        print "Running non-negative MF....", strftime(
            "%Y-%m-%d %H:%M:%S", gmtime())
        if self.method == 'nmf':
            modelnmf = nimfa.Nmf(self.mat, rank=self.rank, max_iter=self.iter)
        elif self.method == "lfnmf":
            modelnmf = nimfa.Lfnmf(self.mat, rank=self.rank, max_iter=self.iter)
        elif self.method == "nsnmf":
            modelnmf = nimfa.Nsnmf(self.mat, rank=self.rank, max_iter=self.iter)
        elif self.method == "pmf":
            modelnmf = nimfa.Pmf(self.mat, rank=self.rank, max_iter=self.iter)
        elif self.method == "psmf":
            modelnmf = nimfa.Psmf(self.mat, rank=self.rank, max_iter=self.iter)
        elif self.method == "snmf":
            modelnmf = nimfa.Snmf(self.mat, rank=self.rank, max_iter=self.iter)
        elif self.method == "sepnmf":
            modelnmf = nimfa.Sepnmf(self.mat, rank=self.rank, max_iter=self.iter)
        else:
            print "No model is being recognized, stopped."
            sys.exit(1)

        model = modelnmf()
        self.result = np.array(model.fitted())
        print "Done MF!", strftime("%Y-%m-%d %H:%M:%S", gmtime())


        print "Write results to file.", strftime("%Y-%m-%d %H:%M:%S", gmtime())
        with open(output_file, "r+") as file:
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

if __name__ == '__main__':
    print "Usage: ", sys.argv[0], "[match file] [output file]"
    if len(sys.argv) < 3:
        sys.exit(1)
    
    post = Postcpp(sys.argv[1])
    post.run(sys.argv[2])

