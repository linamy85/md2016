import sys

if __name__ == '__main__':
  print "Usage:", sys.argv[0], " [input] [output] [known? (y/n)]"
  
  output = open(sys.argv[2], 'w')

  if sys.argv[3] == "y":  # known (source & train)
    with open(sys.argv[1], 'r') as file:
      line = file.readline()
      while line:
        l = line.split()
        output.write("%s %s:1 %d:1\n" % (l[2], l[0], int(l[1]) + 50000))
        line = file.readline()
  else:  # unknown (test)
    with open(sys.argv[1], 'r') as file:
      line = file.readline()
      while line:
        l = line.split()
        output.write("0 %s:1 %d:1\n" % (l[0], int(l[1]) + 50000))
        line = file.readline()
