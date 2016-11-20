import sys
import os

directory = sys.argv[1]
pred_file = sys.argv[2]

file1 = os.path.join(directory, pred_file)
file2 = os.path.join(directory, 'response.txt')

with open(file2, 'r') as f:
    links = [[int(x) for x in (line.rstrip()).split('\t')] for line in f]

correct_count, total_count = 0, 0
with open(file1, 'r') as f:
    pred_links = [[int(x) for x in (line.rstrip()).split(' ')] for line in f]

l = len(pred_links)

for i, pred_link in enumerate(pred_links):
    if i % 1000 == 0:
        print(100 * i / l, '% compared.')
    if pred_link[:2] in links:
        if pred_link[2] == 1:
            correct_count += 1
    else:
        if pred_link[2] == 0:
            correct_count += 1
    total_count += 1

print(correct_count, '/', total_count, '=', correct_count / total_count)
