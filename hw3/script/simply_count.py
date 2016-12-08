#!/usr/bin/python

import sys

if __name__ == '__main__':
    n = 0
    column = int(sys.argv[2])
    
    counts = []
    for i in range(column):
        counts.append(0.0)

    with open(sys.argv[1], 'r') as file:
        line = file.readline()
        while line:
            l = line.split()
            for i in range(column):
                counts[i] += float(l[i])

            n += 1
            line = file.readline()

    print "Total: ", " ".join((str(v) for v in counts[:-1]))
    print "MF total: ", counts[-1]
    print "Average: ",  " ".join((str(v / n) for v in counts[:-1]))
    print "MF average: ", counts[-1] / n
