#!/usr/bin/python

import os
import sys
import random

if __name__ == '__main__':
    original_file_name = os.path.join(sys.argv[1], "train.txt")
    original = open(original_file_name, 'r')

    new_train_file = os.path.join(sys.argv[2], "train.txt")
    new_train = open(new_train_file, 'w')

    new_test_file = os.path.join(sys.argv[2], "test.txt")
    new_test = open(new_test_file, 'w')

    new_pred_file = os.path.join(sys.argv[2], "cross.txt")
    new_pred = open(new_pred_file, 'w')

    line = original.readline()
    while line:
        if random.random() < 0.2:  # test
            l = line.split()
            new_test.write("%s %s ?\n" % (l[0], l[1]))
            new_pred.write(line)
        else:
            new_train.write(line)

        line = original.readline()

    original.close()
    new_test.close()
    new_pred.close()
    new_train.close()
