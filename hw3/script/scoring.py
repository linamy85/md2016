#!/usr/bin/python

import sys
import os


if __name__ == '__main__':
    total = 0.0

    if len(sys.argv) != 3:
        print ("Usage: ", sys.argv[0], "[test.txt] [score.txt]")
        sys.exit(1)

    ans = dict()
    count = 0

    with open(sys.argv[2], 'r') as score_file:
        line = score_file.readline()
        while line:
            count += 1
            l = line.split()
            ans[(l[0], l[1])] = float(l[2])
            line = score_file.readline()

    with open(sys.argv[1], 'r') as pred_file:
        line = pred_file.readline()
        while line:
            l = line.split()
            total += (ans[(l[0], l[1])] - float(l[2])) ** 2
            line = pred_file.readline()

    print ((total / count) ** 0.5)


