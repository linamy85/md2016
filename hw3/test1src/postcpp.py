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

        self.mat = np.array(self.mat)
        print "Done. Now enter last step -- MF", strftime(
            "%Y-%m-%d %H:%M:%S", gmtime())

    def run(self, output_file):
        print "Running non-negative MF....", strftime(
            "%Y-%m-%d %H:%M:%S", gmtime())
        modelnmf = nimfa.Nmf(self.mat, rank=self.rank, max_iter=self.iter)
        model = modelnmf()
        print "Done MF!", strftime("%Y-%m-%d %H:%M:%S", gmtime())

        # sm = model.summary()
        # print('Sparseness Basis: %5.3f  Mixture: %5.3f' % (
            # sm['sparseness'][0], sm['sparseness'][1]))
        # print('Iterations: %d' % sm['n_iter'])
        # print('Target estimate:\n%s' % np.dot(
            # model.basis().todense(), model.coef().todense()))

        self.result = np.array(model.fitted())


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

