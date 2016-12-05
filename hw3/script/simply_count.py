#!/usr/bin/python

import sys

if __name__ == '__main__':
    count = 0.0
    mf_count = 0.0
    n = 0
    with open(sys.argv[1], 'r') as file:
        line = file.readline()
        while line:
            l = line.split()
            count += float(l[0])
            mf_count += float(l[1])
            n += 1
            line = file.readline()

    print "Total: ", count
    print "MF total: ", mf_count
    print "Average: ", count / n
    print "MF average: ", mf_count / n
