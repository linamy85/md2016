import sys

if __name__ == '__main__':
    key_file = open(sys.argv[1], "r")
    value_file = open(sys.argv[2], "r+")

    allvalue = value_file.readlines()
    value_file.seek(0)
    value_file.truncate()

    for line in allvalue:
        key = key_file.readline()
        value_file.write("%s %s" % (key[:-1], line))

    key_file.close()
    value_file.close()

