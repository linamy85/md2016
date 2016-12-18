import sys
import os

if __name__ == '__main__':
    n_line = int(sys.argv[4])
    index = int(sys.argv[3])  # 1-based

    print ("HHHHHHHHHHHHHHHH index %d line %d" % (index, n_line))

    original_file_name = os.path.join(sys.argv[1], "train.txt")
    original = open(original_file_name, 'r')

    new_train_file = os.path.join(sys.argv[2], "train.txt")
    new_train = open(new_train_file, 'w')

    new_test_file = os.path.join(sys.argv[2], "test.txt")
    new_test = open(new_test_file, 'w')

    new_pred_file = os.path.join(sys.argv[2], "cross.txt")
    new_pred = open(new_pred_file, 'w')

    count = 0
    low = (index - 1) * n_line // 5
    high = index * n_line // 5

    print("Fold %d : line %d to %d" % (index, low, high-1))

    line = original.readline()
    while line:
        if (count >= low) and (count < high):
            l = line.split()
            new_test.write("%s %s ?\n" % (l[0], l[1]))
            new_pred.write(line)
        else:
            new_train.write(line)

        count += 1
        line = original.readline()

    original.close()
    new_test.close()
    new_pred.close()
    new_train.close()
