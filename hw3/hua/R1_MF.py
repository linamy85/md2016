
# coding: utf-8

# In[16]:

import pandas as pd
import numpy as np
import sys
from mf import matrix_factorization
import random
from numpy.linalg import multi_dot


# In[17]:

#0: origin, 1: small
TYPE = 0
N1_r = [500, 6]
N1_c = [500, 6]
filename = [["test3/source.txt", "test3/R1_mf_5000.txt"], 
            ["test3/my/source.txt", "test3/my/R1_mf_5000.txt"]]


# In[18]:

source = pd.read_csv(filename[TYPE][0], sep=" ", header = None, skipinitialspace=True)  

R1 = np.zeros((N1_r[TYPE], N1_c[TYPE]))
W1 = np.zeros((N1_r[TYPE], N1_c[TYPE]))

source_m = source.as_matrix()
for i in range(source_m.shape[0]):
    user, item, rating = int(source_m[i][0]), int(source_m[i][1]), int(source_m[i][2])
    R1[user-1][item-1] = rating
    W1[user-1][item-1] = 1

print(R1)
nP, nQ = matrix_factorization(R1)                                                                                           
R1_mf = np.dot(nP, nQ.T)


# In[19]:

with open(filename[TYPE][1], "w") as f:
    for i in range(N1_r[TYPE]):
        for j in range(N1_c[TYPE]):
            if W1[i][j] == 0:
                f.write(str(i+1)+" "+str(j+1)+" "+str(R1_mf[i][j])+"\n")
            else:
                f.write(str(i+1)+" "+str(j+1)+" "+str(R1[i][j])+"\n")
            


# In[ ]:




# In[ ]:



