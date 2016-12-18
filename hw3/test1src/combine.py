import sys

if __name__ == '__main__':
  print "Usage:", sys.argv[0], " [label file] [result file]"

  key_file = open(sys.argv[1], "r+")
  value_file = open(sys.argv[2], "r")

  allkey = key_file.readlines()
  key_file.seek(0)
  key_file.truncate()

  for line in allkey:
      value = value_file.readline()
      l = line.split()
      key_file.write("%s %s %s" % (l[0], l[1], value))

  key_file.close()
  value_file.close()

