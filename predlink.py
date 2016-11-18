from functions import *
from Inference_Markov import *

from math import exp
from math import atan
from math import pi
import numpy as np

# positive number to probability function1
def ptop1(x):
    return (2 / (1 + exp(-d * x))) -1
vptop1 = np.vectorize(ptop1)

# positive number to probability function2
def ptop2(x):
    return atan(x) * 2 / pi
vptop2 = np.vectorize(ptop2)

def two_stage_inference():
    # g_dict((hashed_y0, hashed_y1)) = np_array of data.gp(y0, y1)
    # TODO : 
    # global gp_dict
    # gp_dict = data.gp()
    global g_dict
    g_dict = {k : ptop(np.dot(array, beta)) for k, array in gp_dict.items()}

    # fh_dict(hashed_y) = [f(y), h(y)]  <=  this is a list instead of a tuple since only h(y) needs to change in stage 2
    global fh_dict
    fh_dict = {hash_y(y[0], itemN, y[1]) : [(ptop(np.dot(fp_array[i], alpha)), 1)] for i, y in enumerate(Y)}

    # inference stage 1
    P = inference(fh_dict, g_dict)

    # Compute h(y) in stage 2 and modify fh_dict
    for y in Y:
        fh_dict[hash_y(y[0], itemN, y[1])][1] = 1 - (data.messages[y[1]][2] - sum(map(lambda yp: P[hash_y(yp[0], itemN, yp[1])] if yp[1] == y[1] else 0, Y))) / data.userN

    # inference stage 2
    P = inference(fh_dict, g_dict)
    return P

# python predlink.py $(d) $(loop_num) $(eta) $(ptop function number)
d, loop_num, eta = float(sys.argv[1]), int(sys.argv[2]), float(sys.argv[3])
ptop = ptop1 if int(sys.argv[4]) == 1 else ptop2

# T = #(lines in pred.id) / 2
with open("pred.id", "r") as f:
    T = len(f.readlines())
T = T // 2

# item number
itemN = len(data.messages)

data = Potential('./')

# Determine required yi = (ui, ri) and store as a list Y
Y_layer2 = data.layer2()
Y = []
for item, user_list in enumerate(Y_layer2):
    for user in user_list:
        Y.append((user, item))
del Y_layer2

# Compute f' for all yi
# fp_array is a numpy array with dim = 2
fp_array = np.array([data.fp(y) for y in Y])

# Initialize all elements in theta to 1
alpha, beta, gamma = np.ones(3), np.ones(4), np.ones(1)
theta = np.array([alpha, beta, gamma])

# Repeat until converge
for n in range(loop_num):
    
    # Run two-stage inference algorithm to obtain P(yi=1) for all yi, return as a dictionary P

    P = two_stage_inference()
    
    # Compute h(y), temp_sum = sum h(y)
    temp_h_sum = 0
    for y in Y:
        h_y = 1 - (data.messages[y[1]][2] - sum(map(lambda yp: P[hash_y(yp[0], itemN, yp[1])] if yp[1] == y[1] else 0, Y))) / data.userN
        fh_dict[hash_y(y[0], itemN, y[1])][1] = h_y
        temp_h_sum += h_y


    # Compute potential function values S
    sum_f = np.array(sum(fp_array))
    sum_g = np.array(sum(gp_dict.values()))
    sum_h = np.array([temp_h_sum])
    S = np.array([sum_f, sum_g, sum_h])

    # For each item r in R, compute dO_dtheta and update theta
    theta_next = theta
    for item_num, r in enumerate(data.messages):

        Y_r = filter(lambda y: y[1] == item_num, Y)
        Y_r.sort(key = (lambda yp: P[hash_y(yp[0], itemN, yp[1])]), reverse = True)

        # item r has r[2] hidden links
        Y_upper = Y_r[:r[2]]
        Y_lower = Y_r[r[2]:]

        # Compute dO_dtheta as numpy array
        v_sum = np.vectorze(sum)
        theta_S = sum(v_sum(theta * S))

        numerator = np.array([np.zeros(3), np.zeros(4), np.zeros(1)])
        denominator = 0
        for y in Y_upper:
            temp = exp(theta_S)
            numerator += temp * S
            denominator += temp
        dO_dtheta = numerator / denominator

        numerator = np.array([np.zeros(3), np.zeros(4), np.zeros(1)])
        denominator = 0
        for y in Y_lower:
            temp = exp(theta_S)
            numerator += temp * S
            denominator += temp
        dO_dtheta -= numerator / denominator

        theta_next += eta * dO_dtheta

    theta = theta_next

# Run inference method using final theta to obtain P(yi=1) for all yi, return as a dictionary P
P = two_stage_inference()

# Sort by P and pred top T links
with open("pred.id", "r") as f:
    temp_pred = [[x for x in (line.rstrip()).split('\t')] for line in f]
pred = [(int(x[0]), int(x[1])) for x in temp_pred_list]

sorted_pred = sorted(pred, key = (lambda yp: P[hash_y(yp[0], itemN, yp[1])]), reverse = True)
pred_dict = {y : (1 if i < T else 0) for i, y in enumerate(sorted_pred)}

with open("pred.id", "w") as f:
    for i in range(T):
        f.write(str(pred[i][0]) + ' ' + str(pred[i][1]) + ' ' + str(pred_dict[pred[i]]) + '\n')