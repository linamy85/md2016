import sys

if __name__ == '__main__':
  print "Usage:", sys.argv[0], " [label file] [result file]"

  key_file = open(sys.argv[1], "r")
  value_file = open(sys.argv[2], "r+")

  allvalue = value_file.readlines()
  value_file.seek(0)
  value_file.truncate()

  for line in allvalue:
      key = key_file.readline()
      l = key.split()
      value_file.write("%s %s %s" % (l[0], l[1], line))

  key_file.close()
  value_file.close()

