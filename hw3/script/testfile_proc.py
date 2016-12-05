# This file is used for removing trailing ? of test file

import sys

if __name__ == '__main__':
    write_file = open(sys.argv[1] + '.proc', 'w')
    with open(sys.argv[1], 'r') as file:
        line = file.readline()
        while line:
            strs = line.split()
            write_file.write("%s %s\n" % (strs[0], strs[1]))
            line = file.readline()
    write_file.close()
    print("Remove trailing question mark done.")
