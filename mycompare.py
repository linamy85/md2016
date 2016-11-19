import sys
import os

directory = sys.argv[1]

file1 = os.path.join(directory, 'pred.id')
file2 = os.path.join(directory, 'response.txt')

with open(file2, 'r') as f:
	links = [[int(x) for x in (line.rstrip()).split('\t')] for line in f]

correct_count, total_count = 0, 0
with open(file1, 'r') as f:
	pred_links = [[int(x) for x in (line.rstrip()).split('\t')] for line in f]

for pred_link in pred_links:
	if pred_link[:2] is in links:
		if pred_link[2] == 1:
			correct_count += 1
	else:
		if pred_link[2] == 0:
			correct_count += 1
	total_count += 1

print(correct_count, '/', total_count, '=', correct_count / total_count)