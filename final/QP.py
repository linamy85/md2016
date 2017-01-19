import numpy as np
import sys
#sys.path.append('data/validation')
from Feature import Feature
from pca import DR_PCA
from math import sqrt, fabs
from cvxopt import matrix, spmatrix, solvers
import AE

dim = input('dim = ')
migration_threshold = input('migration_threshold = ')
op = input('type 0 to use PCA, 1 to use AE : ')
f = Feature(node_threshold=180, migration_threshold=migration_threshold)
X, Y = f.getYearFeatures(2015)
X0 = []
X1 = []
for i in range(len(X)):
    X0.append(X[i][0])
    X1.append(X[i][1])
if op == 0:
    x0 = DR_PCA(X0, dim)
    x1 = DR_PCA(X1, dim)
else:
    X0 = np.array(X0)
    X1 = np.array(X1)
    x, w, b = AE.dim_reduce(X0, dim, 2, 20, 0.01)
    x0 = AE.forward2hidden(X0, w, b, 2)
    x, w, b = AE.dim_reduce(X1, dim, 2, 20, 0.01)
    x1 = AE.forward2hidden(X1, w, b, 2)
x = []
for i in range(len(X)):
    x.append(np.concatenate((x0[i], x1[i], X[i][2])))
print ('Dimension reduction done.')
x = np.array(x)
dim = 2*dim+3

num = int(sqrt(len(x)))

O = [sum([Y[i*num+j] for j in range(num)]) for i in range(num)]
I = [sum([Y[i*num+j] for i in range(num)]) for j in range(num)]

q = np.zeros(dim)
p = np.zeros(dim)

for i in range(num):
    temp = np.zeros(dim)
    for j in range(num):
        temp += x[i*num+j]
    q += (temp ** 2)
    p += (temp * O[i] * (-2))

for j in range(num):
    temp = np.zeros(dim)
    for i in range(num):
        temp += x[i*num+j]
    q += (temp ** 2)
    p += (temp * I[j] * (-2))

Q = spmatrix(q, range(dim), range(dim))
P = matrix(p)

g = []

"""
for i in range(num):
    temp = np.zeros(dim)
    for j in range(num):
        temp += x[i*num+j]
    g.append(temp)

for j in range(num):
    temp = np.zeros(dim)
    for i in range(num):
        temp += x[i*num+j]
    g.append(temp)
"""
for i in range(num):
    temp = np.zeros(dim)
    for j in range(num):
        temp += x[i*num+j]
    g.append(-temp)

for j in range(num):
    temp = np.zeros(dim)
    for i in range(num):
        temp += x[i*num+j]
    g.append(-temp)
"""
for i in range(num):
    for j in range(num):
        g.append(-x[i*num+j])
"""

G = matrix(np.array(g), tc='d')
H = matrix(np.zeros(num**2), tc='d')
#H = matrix(np.concatenate((O, I, [0]*(num*2))), tc='d')

A = matrix(np.array([x[i*num+i] for i in range(num)]))
B = matrix(np.zeros(num))

#sol = solvers.qp(Q, P, G, H, A, B)
sol = solvers.qp(Q, P, G, H)

error = 0
y = []

for i in range(num ** 2):
    y.append((sol['x'].trans() * matrix(x[i]))[0])
    error += fabs(y[i] - Y[i])
error /= (num ** 2)

for i in range(num):
    print 'O[i] =', O[i], '\tsum', i, '=', sum([y[i*num+j] for j in range(num)])
for j in range(num):
    print 'I[j] =', I[j], '\tsum', j, '=', sum([y[i*num+j] for i in range(num)])

count = 0
for i in range(num ** 2):
    if Y[i] != 0:
        count += 1
print 'count =', count, 'non-zero :', float(count) / (num**2)
print 'L1 error', error
