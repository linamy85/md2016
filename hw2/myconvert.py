import sys
filename = sys.argv[1]

with open(filename, 'r') as f:
    temp = [[x for x in (line.rstrip()).split(' ')] for line in f]
with open(filename, 'w') as f:
    for y in temp:
        f.write(y[0] + '\t' + y[1] + '\t' + y[2] + '\n')
