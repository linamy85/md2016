from functions import *

from math import exp
import numpy as np
import os

# g = 8*g3 + 4*g2 + 2*g1 + 1*g0
def get_g_array(g):
    g_list = []
    for i in range(4):
        g_list.append(g % 2)
        g = g // 2
    return np.array(g_list)

# start of _main_
# python predlink.py $(directory) $(loop_num) $(theta) $(eta) $(famousN) $(mult) $(node_file)
directory               = sys.argv[1]
loop_num                = int(sys.argv[2])
theta, eta              = float(sys.argv[3]), float(sys.argv[4])
famousN, mult           = int(sys.argv[5]), int(sys.argv[6])
node_file               = sys.argv[7]


data = Potential(directory, famousN, mult, filename = node_file)
itemN = data.itemN
nodes, gp_dict = data.layer2_node_link(filename = node_file)

# Determine required yi = (ui, ri) and store as a list Y
Y = []
for item, user_list in enumerate(nodes):
    for user in user_list:
        Y.append((user, item))
del nodes

# Compute f' for all yi
# fp_array is a numpy array with dim = 2
fp_array = np.array([np.array(data.fp(y)) for y in Y])

# Initialize all elements in theta to 1
theta = np.array([ np.array([theta, theta, theta]), np.array([theta, theta, theta, theta]) ])

# Repeat until converge
for n in range(loop_num):
    
    print('loop_num = ', n+1)

    # f_dict[hashed_y] = f(y)
    f_dict = {hash_y(y[0], itemN, y[1]) : fp_array[i] for i, y in enumerate(Y)}

    # g_link_dict[(hashed_y1, hashed_y2)] = g(y1, y2)
    g_link_dict = {k : get_g_array(g) for k, g in gp_dict.items()}

    # g_dict[hashed_y] = g(y)
    g_dict = {hash_y(y[0], itemN, y[1]) : 0 for y in Y}
    for link, g in g_link_dict.items():
        g_dict[link[0]] += g
        g_dict[link[1]] += g

    # Compute dict S[hashed_y] = numpy array of numpy array
    S = {}
    for y in Y:
        hashed = hash_y(y[0], itemN, y[1])
        S[hashed] = np.array([f_dict[hashed], g_dict[hashed]])

    v_sum = np.vectorize(sum)

    # For each item r in R, compute dO_dtheta and update theta
    theta_next = theta
    for item_num, r in enumerate(data.messages):

        Y_r = list(filter(lambda y: y[1] == item_num, Y))
        # Sort by P => Sort by f_dict + g_dict
        Y_r.sort(key = ( lambda y: sum(v_sum(theta * S[hash_y(y[0], itemN, y[1])])) ), reverse = True)

        # item r has r[2] hidden links
        Y_upper = Y_r[:r[2]]
        Y_lower = Y_r[r[2]:]

        # Compute dO_dtheta as numpy array
        numerator = np.array([np.zeros(3), np.zeros(4)])
        denominator = 0
        for y in Y_upper:
            S_y = S[hash_y(y[0], itemN, y[1])]
            #print('thetaS =', sum(v_sum(theta * S_y)))
            exp_thetaS = exp(sum(v_sum(theta * S_y)))
            numerator += exp_thetaS * S_y
            denominator += exp_thetaS
        if denominator == 0:
            dO_dtheta = 0
        else:
            dO_dtheta = numerator * (1 / denominator)

        numerator = np.array([np.zeros(3), np.zeros(4)])
        denominator = 0
        for y in Y_lower:
            S_y = S[hash_y(y[0], itemN, y[1])]
            exp_thetaS = exp(sum(v_sum(theta * S_y)))
            numerator += exp_thetaS * S_y
            denominator += exp_thetaS
        if denominator != 0:
            dO_dtheta -= numerator * (1 / denominator)

        theta_next += eta * dO_dtheta

    temp = sum(v_sum(theta_next))
    theta = theta_next * theta / temp
    print('theta = ', theta)


# f_dict[hashed_y] = f(y) dot theta[0]
f_dict = {hash_y(y[0], itemN, y[1]) : np.dot(fp_array[i], theta[0]) for i, y in enumerate(Y)}

# g_link_dict[(hashed_y1, hashed_y2)] = g(y1, y2) dot theta[1]
g_link_dict = {k : np.dot(get_g_array(g), theta[1]) for k, g in gp_dict.items()}

# g_dict[hashed_y] = g(y) dot theta[1]
g_dict = {hash_y(y[0], itemN, y[1]) : 0 for y in Y}
for link, g in g_link_dict.items():
    g_dict[link[0]] += g
    g_dict[link[1]] += g

# Sort by P and pred top T links
with open(os.path.join(directory, 'pred.id'), "r") as f:
    temp_pred = [[x for x in (line.rstrip()).split(' ')] for line in f]
pred = [(int(x[0]), int(x[1])) for x in temp_pred_list]

sorted_pred = sorted(pred, key = (lambda yp: f_dict[hash_y(yp[0], itemN, yp[1])] + g_dict[hash_y(yp[0], itemN, yp[1])]), reverse = True)
pred_dict = {y : (1 if i < T else 0) for i, y in enumerate(sorted_pred)}

with open(os.path.join(directory, 'pred1.txt'), "w") as f:
    for i in range(T*2):
        f.write(str(pred[i][0]) + ' ' + str(pred[i][1]) + ' ' + str(pred_dict[pred[i]]) + '\n')