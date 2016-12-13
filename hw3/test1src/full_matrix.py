import sys


if __name__ == '__main__':
    with open(sys.argv[1], 'w') as file:
        for i in range(50000):
            for j in range(5000):
                file.write("%d %d\n" % (i, j))

