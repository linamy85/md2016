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

        self.mat = np.array(self.mat)
        print "Done. Now enter last step -- MF", strftime(
            "%Y-%m-%d %H:%M:%S", gmtime())

    def run(self, output_file):
        modelnmf = nimfa.Nmf(self.mat, max_iter=100)
        model = modelnmf()
        print "Done MF!", strftime("%Y-%m-%d %H:%M:%S", gmtime())
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
    if len(sys.argv) != 3:
        sys.exit(1)
    
    post = Postcpp(sys.argv[1])
    post.run(sys.argv[2])

