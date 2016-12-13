import sys


if __name__ == '__main__':
    with open(sys.argv[1], 'w') as file:
        for i in range(50000):
            for j in range(5000):
                file.write("0 %d:1 %d:1\n" % (i, j + 50000))

