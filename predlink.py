from functions import *

from math import exp
from operator import add

# T = #(lines in pred.id) / 2
with open("pred.id", "r") as f:
    T = len(f.readlines())
T /= 2

x = Potential('./')

eta = 0.1
loop_num = 10

# Determine required yi = (ui, ri) and store as a list Y

# Compute f', g' for all yi

# Initialize all elements in theta to 1
alpha, beta, gamma = [1, 1, 1], [1, 1, 1, 1], [1]
theta = [alpha, beta, gamma]

# Repeat until converge
for n in range(loop_num):

    # Run inference method using current theta to obtain P(yi=1) for all yi, return as a dictionary P

    def P(y):
        return P[y]

    # Compute h' for all yi
    def hp(y):
        return 1 - (x.messages[y[1]][2] - sum(map(lambda (uj, rj): P[(uj, rj)] if rj == y[1] else 0, Y))) / x.userN

    # Compute potential function values S = [sum(f'), sum(g'), sum(h')]
    

    # For each item r in R, compute dO_dtheta and update theta
    theta_next = theta
    for r in x.messages:
        Y_r = filter(lambda (ui, ri): ri == r, Y)   # not finished
        Y_r.sort(key = P, reverse = True)
        # item r has r[2] hidden links
        Y_upper = Y_r[:r[2]]
        Y_lower = Y_r[r[2]:]
        # Compute dO_dtheta        

        theta_next += eta * dO_dtheta
    theta = theta_next

# Run inference method using final theta to obtain P(yi=1) for all yi, return as a dictionary P

# Sort P and output top T links