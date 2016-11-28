#!/usr/bin/python

import sys

if __name__ == '__main__':
    count = 0.0
    n = 0
    with open(sys.argv[1], 'r') as file:
        line = file.readline()
        while line:
            count += float(line.split()[0])
            n += 1
            line = file.readline()

    print "Total: ", count
    print "Average: ", count / n
