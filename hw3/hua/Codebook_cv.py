
# coding: utf-8

# In[1]:

import pandas as pd
import numpy as np
import sys
from mf import matrix_factorization
import random
from numpy.linalg import multi_dot
import math
from sklearn.cluster import KMeans
from scipy.cluster.vq import vq, kmeans


if len(sys.argv) != 5:
    print("usage: python3 CodebookTransfer.py [mf_steps] [user_clusterN] [item_clusterN] [transfer_T]")
    sys.exit(0)

# In[2]:

#0: origin, 1: small
TYPE = 0


# In[11]:

N1_r = [500, 6]
N1_c = [500, 6]
N2_r = [500, 7]
N2_c = [1000, 5]
mf_steps = int(sys.argv[1])
threshold = [1e-10, 1e-10]
user_clusterN = [int(sys.argv[2]), 3]
item_clusterN = [int(sys.argv[3]), 3]
transfer_T = [int(sys.argv[4]), 1000]
interval = [10, 500]
filename = [["cv/source.txt", "cv/train.txt", "cv/test.txt"], ["test3/my/source.txt", "test3/my/train.txt", "test3/my/test.txt"]]


# ## Data processing

# In[12]:

source = pd.read_csv(filename[TYPE][0], sep=" ", header = None, skipinitialspace=True)  

R1 = np.zeros((N1_r[TYPE], N1_c[TYPE]))
W1 = np.zeros((N1_r[TYPE], N1_c[TYPE]))

source_m = source.as_matrix()
for i in range(source_m.shape[0]):
    user, item, rating = int(source_m[i][0]), int(source_m[i][1]), int(source_m[i][2])
    R1[user-1][item-1] = rating
    W1[user-1][item-1] = 1

nP, nQ = matrix_factorization(R1, mf_steps)                                                                                           
R1_mf = np.dot(nP, nQ.T)

for i in range(N1_r[TYPE]):
    for j in range(N1_c[TYPE]):
        if W1[i][j] == 1:
            R1_mf[i][j] = R1[i][j]

print('R1_mf')
print(R1_mf)

# In[13]:

target = pd.read_csv(filename[TYPE][1], sep=" ", header = None, skipinitialspace=True)  

R2 = np.zeros((N2_r[TYPE], N2_c[TYPE]))
W2 = np.zeros((N2_r[TYPE], N2_c[TYPE]))

target_m = target.as_matrix()
for i in range(target_m.shape[0]):
    user, item, rating = int(target_m[i][0]), int(target_m[i][1]), int(target_m[i][2])
    R2[user-1][item-1] = rating
    W2[user-1][item-1] = 1

print('R2')
print(R2)


# ## codebook construction
# input:  
# $n \times m\ \ X_{aux}$  
# user_clusterN: $k$    
# item_clusterN: $l$  
# 
# output:  
# $l \times l$ codebook $B$  
# 
# inside:  
# $U:\ n \times k$  
# $S:\ k \times l$  
# $V:\ m \times l$  
# 
# <img src="https://i.imgur.com/0tLbUWj.png" width="500px">
# <img src="https://i.imgur.com/TrXJgBQ.png" width="500px">
# <img src="https://i.imgur.com/CFaTc6A.png" width="500px">
# <img src="https://i.imgur.com/e3OyVUc.png" width="500px">
# 

# In[6]:

def squareSum(arr):
    sum = 0
    for i in range(arr.shape[0]):
        for j in range(arr.shape[1]):
            sum += (arr[i][j])**2;
    return math.sqrt(sum / (arr.shape[0]*arr.shape[1]))


# In[11]:

def codebook_constuct(X, threshold, k, l):
    (n, m) = X.shape
    #U: n \times k
    #S: k \times l  
    #V: m \times l
    #row: k (user_clusterN)
    #col: l (item_clusterN)
    
    #k-means (row in python)
    
    V_old = np.zeros(shape=(m, l))
    U_old = np.zeros(shape=(n, k))
    
    #item
    kmeans = KMeans(n_clusters=l, random_state=0).fit(np.transpose(X)) #X^T: m*n
    labels = kmeans.labels_           # 1*m
    print('V: ', labels)
    
    for i in labels:
        V_old[i] = np.zeros(shape=(1, l))
        V_old[i][labels[i]] = 1
        
    tmp = np.zeros(shape=(m, l))      
    tmp.fill(0.2)
    V_old = np.add(V_old, tmp)    #V: m*l
    
    #user
    kmeans = KMeans(n_clusters=k, random_state=0).fit(X)              #X: n*m
    labels = kmeans.labels_           # 1*n
    print('U: ', labels)
    
    for i in labels:
        U_old[i] = np.zeros(shape=(1, k))
        U_old[i][labels[i]] = 1
        
    tmp = np.zeros(shape=(n, k))      
    tmp.fill(0.2)
    U_old = np.add(U_old, tmp)      #U: n*k
    
    #k*l = k*n  n*m m*l
    
    S_old = multi_dot([np.transpose(U_old), X, V_old])
    
    print('finish k-means')
    
    
    eta = 1   #any number > threshold
    #t = 0
    while eta > threshold:
        up = multi_dot([np.transpose(X), U_old, S_old])
        down = multi_dot([V_old, np.transpose(V_old), np.transpose(X), U_old, S_old])
        V_new = np.sqrt(np.multiply(V_old, np.divide(up, down)))
        
        eta = squareSum(np.subtract(V_new, V_old))
        
        up = multi_dot([np.transpose(X), V_new, np.transpose(S_old)])
        down = multi_dot([U_old, np.transpose(U_old), X, V_new, np.transpose(S_old)])
        U_new = np.sqrt(np.multiply(U_old, np.divide(up, down)))
        
        eta += squareSum(np.subtract(U_new, U_old))
        
        up = multi_dot([np.transpose(U_new), X, V_new])
        down = multi_dot([np.transpose(U_new), U_new, S_old, np.transpose(V_new), V_new])
        S_new = np.sqrt(np.multiply(S_old, np.divide(up, down)))
        
        eta += squareSum(np.subtract(S_new, S_old))
        eta /= 3
        #print(t, eta)
        #t += 1
        
        V_old = V_new
        U_old = U_new
        S_old = S_new
        
    print('U: ', U_new)
    print('V: ', V_new)
    print('finish initialization')
        
    
    U_aux = np.zeros(shape=(n, k))
    V_aux = np.zeros(shape=(m, l))
    
    
    for i in range(n):
        j_max = np.argmax(U_new[i])
        U_aux[i] = np.zeros(shape=(1, k))
        U_aux[i][j_max] = 1
        #print('U: ', i, j_max)

    #print('finish U_aux:\n', U_aux)
    
    for i in range(m):
        j_max = np.argmax(V_new[i])
        #print('V: ', i, j_max)
        V_aux[i] = np.zeros(shape=(1, l))
        V_aux[i][j_max] = 1

    #print('finish V_aux:\n', V_aux)
    
    one = np.zeros(shape=(n, 1))
    one.fill(1)
    one2 = np.zeros(shape=(1, m))
    one2.fill(1)
    #print(np.transpose(U_aux).shape, one.shape, one2.shape, V_aux.shape)
    up = multi_dot([np.transpose(U_aux), X, V_aux])
    down = multi_dot([np.transpose(U_aux), one, one2, V_aux])
    print('X\n', X)
    print('up\n', up)
    print('down\n', down)
    
    B = np.divide(up, down)
    print('Got B\n', B)
    for i in range(B.shape[0]):
        for j in range(B.shape[1]):
            if np.isnan(B[i][j]):
                B[i][j] = 0
    return B

# In[12]:

B = codebook_constuct(R1_mf, threshold[TYPE], user_clusterN[TYPE], item_clusterN[TYPE])
print('B\n', B)


# ## codeTransfer
# <img src="https://i.imgur.com/LD9xngw.png" width="500px">
# <img src="https://i.imgur.com/89WiA3T.png" width="500px">
# <img src="https://i.imgur.com/xgtW449.png" width="500px">
# 
# input:  
# $p \times q\ \ X_{tgt}$  
# $p \times q\ \ W$  
# $k \times l\ \ B$
# 
# output:  
# $p \times q$ filled-in $\tilde{X}_{tgt}$  
# 
# inside:  
# $U_{tgt}:\ p \times k$  
# $V_{tgt}:\ q \times l$  
# 

# In[16]:

def codeTransfer(X_tgt, W, B, T):
    #
    #X_tgt = np.zeros(shape=(p, q))
    #W = np.zeros(shape=(p, q))
    #B = np.zeros(shape=(k, l))
    #
    (p, q) = X_tgt.shape
    (k, l) = B.shape
    V_tgt = np.zeros(shape=(q,l))
    U_tgt = np.zeros(shape=(p, k))
    print(p, q, k, l)
    

    for i in range(q):
        j = random.randint(0, l-1)
        V_tgt[i][j] = 1
    
    # Should I do it parallelly? But the bottle neck is X_tgt_new
    for t in range(T):
        for i in range(p):
            err = []
            for j in range(k):
                dot_res = np.dot(B, np.transpose(V_tgt))
                tmp = np.subtract(X_tgt[i], dot_res[j])
                err.append(np.dot(np.multiply(tmp, tmp), W[i]))

            j_min = np.argmin(err)
            U_tgt[i] = np.zeros(shape=(1,k))
            U_tgt[i][j_min] = 1
            
        #print(t, ' finish U_tgt')
            

        for i in range(q):
            err = []
            for j in range(l):
                dot_res = np.dot(U_tgt, B)
                tmp = np.subtract(X_tgt[:, i], dot_res[:, j])
                err.append(np.dot(np.multiply(tmp, tmp), W[:, i]))

            j_min = np.argmin(err)
            V_tgt[i] = np.zeros(shape=(1,l))
            V_tgt[i][j_min] = 1
            
        
        #print(t, ' finish V_tgt')
        if t % interval[TYPE] == 0:
            print(t/T*100, ' completed')

    print('U_tgt:\n', U_tgt)
    print('V_tgt:\n', V_tgt)

    one = np.zeros(shape=(p, q))
    one.fill(1)
    X_tgt_new = np.add(np.multiply(W, X_tgt),
                       np.multiply(np.subtract(one, W),
                                   multi_dot([U_tgt, B, np.transpose(V_tgt)])))
    return X_tgt_new
        


# In[17]:

X_tgt_new = codeTransfer(R2, W2, B, transfer_T[TYPE])
print('X_tgt_new\n', X_tgt_new)


# In[53]:

# open test.txt with r+ -> read -> seek0 -> truncate -> write
with open(filename[TYPE][2], "r+") as f:
    testline = f.readlines()
    f.seek(0, 0)
    f.truncate()
    for i in range(len(testline)):
        tmp = testline[i].split(" ")
        user, item = int(tmp[0]), int(tmp[1])
        f.write(tmp[0]+" "+tmp[1]+" "+str(X_tgt_new[user-1][item-1])+"\n")


'''
test = pd.read_csv(filename[TYPE][2], sep=" ", header = None, skipinitialspace=True)
with open(filename[TYPE][3], "w") as f:
    test_m = test.as_matrix()
    for i in range(test_m.shape[0]):
        user, item = int(test_m[i][0]), int(test_m[i][1])
        f.write(str(test_m[i][0])+" "+str(test_m[i][1])+" "+str(X_tgt_new[user-1][item-1])+"\n")
'''
    


# In[52]:

'''
with open(filename[TYPE][4], "w") as f:
    for i in range(X_tgt_new.shape[0]):
        for j in range(X_tgt_new.shape[1]):
            f.write(str(X_tgt_new[i][j]) + " ")
        f.write('\n')
'''


# In[ ]:



