from functions import *
from Inference_Markov import *

from math import exp
from math import atan
from math import pi
import numpy as np
import os

# positive number to probability function1
def ptop1(x):
    return (2 / (1 + exp(-d * x))) -1
vptop1 = np.vectorize(ptop1)

# positive number to probability function2
def ptop2(x):
    return atan(x) * 2 / pi
vptop2 = np.vectorize(ptop2)

# g = 8*g3 + 4*g2 + 2*g1 + 1*g0
def get_g_array(g):
    g_list = []
    for i in range(4):
        g_list.append(g % 2)
        g = g // 2
    return np.array(g_list)

def two_stage_inference():
    # g_dict((hashed_y0, hashed_y1)) = np_array of data.gp(y0, y1)
    global g_dict
    g_dict = {k : ptop(np.dot(get_g_array(g), beta)) for k, g in gp_dict.items()}

    # fh_dict(hashed_y) = [f(y), h(y)]  <=  this is a list instead of a tuple since only h(y) needs to change in stage 2
    global fh_dict
    fh_dict = {hash_y(y[0], itemN, y[1]) : [(ptop(np.dot(fp_array[i], alpha)), 1)] for i, y in enumerate(Y)}

    # inference stage 1
    G, P = inference(G, data.userN, itemN, True, fh_dict, g_dict, converge_num)

    # Compute h(y) in stage 2 and modify fh_dict
    for y in Y:
        fh_dict[hash_y(y[0], itemN, y[1])][1] = 1 - (data.messages[y[1]][2] - sum(map(lambda yp: P[hash_y(yp[0], itemN, yp[1])] if yp[1] == y[1] else 0, Y))) / data.userN

    # inference stage 2 only needs 
    G, P = inference(G, data.userN, itemN, False, fh_dict, False, converge_num)
    return P

# start of _main_
# python predlink.py $(directory) $(ptop function number) $(loop_num) $(converge number) $(d) $(eta) $(famousN) $(mult) $(node_file)
directory               = sys.argv[1]
ptop                    = ptop1 if int(sys.argv[2]) == 1 else ptop2
loop_num, converge_num  = int(sys.argv[3]), int(sys.argv[4])
d, eta                  = float(sys.argv[5]), float(sys.argv[6])
famousN, mult           = int(sys.argv[7]), int(sys.argv[8])
node_file               = sys.argv[9]


# T = #(lines in pred.id) / 2
pred_file = os.path.join(directory, 'pred.id')
with open(pred_file, "r") as f:
    T = len(f.readlines())
T = T // 2
print('T = ', T)

data = Potential(directory, famousN, mult, filename = node_file)
itemN = data.itemN
nodes, links = data.layer2_node_link()

# Determine required yi = (ui, ri) and store as a list Y
Y = []
for item, user_list in enumerate(nodes):
    for user in user_list:
        Y.append((user, item))
del nodes

# Compute f' for all yi
# fp_array is a numpy array with dim = 2
fp_array = np.array([data.fp(y) for y in Y])

# Initialize all elements in theta to 1
alpha, beta, gamma = np.ones(3), np.ones(4), np.ones(1)
theta = np.array([alpha, beta, gamma])


# Build graph G
gp_dict = links
del links
G = buildModel(data.userN, itemN, [hash_y(y[0], itemN, y[1]) for y in Y], gp_dict.keys())
print('Build graph : Done')

# Repeat until converge
for n in range(loop_num):
    
    # Run two-stage inference algorithm to obtain P(yi=1) for all yi, return as a dictionary P
    print('loop_num = ', n+1)
    P = two_stage_inference()
    print('two_stage_inference : Done')

    # Compute h(y), temp_sum = sum h(y)
    temp_h_sum = 0
    for y in Y:
        h_y = 1 - (data.messages[y[1]][2] - sum(map(lambda yp: P[hash_y(yp[0], itemN, yp[1])] if yp[1] == y[1] else 0, Y))) / data.userN
        fh_dict[hash_y(y[0], itemN, y[1])][1] = h_y
        temp_h_sum += h_y


    # Compute potential function values S
    sum_f = np.array(sum(fp_array))
    sum_g = np.array(sum(map( get_g_array ,gp_dict.values() )))
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
    print('theta = ', theta)

# Run inference method using final theta to obtain P(yi=1) for all yi, return as a dictionary P
P = two_stage_inference()

# Sort by P and pred top T links
with open(pred_file, "r") as f:
    temp_pred = [[x for x in (line.rstrip()).split('\t')] for line in f]
pred = [(int(x[0]), int(x[1])) for x in temp_pred_list]

sorted_pred = sorted(pred, key = (lambda yp: P[hash_y(yp[0], itemN, yp[1])]), reverse = True)
pred_dict = {y : (1 if i < T else 0) for i, y in enumerate(sorted_pred)}

with open(pred_file, "w") as f:
    for i in range(T):
        f.write(str(pred[i][0]) + ' ' + str(pred[i][1]) + ' ' + str(pred_dict[pred[i]]) + '\n')
