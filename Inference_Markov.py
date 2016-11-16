
# coding: utf-8

# In[ ]:

import pandas as pd
import numpy as np

#from pgmpy.models import FactorGraph
from pgmpy.models import MarkovModel
#from pgmpy.models import BayesianModel
#from pgmpy.factors.discrete import DiscreteFactor
from pgmpy.factors import Factor

from pgmpy.inference import Sampling


# In[40]:

sampleN = 3


# In[41]:

# userIDs: u[i]
u = pd.read_csv("user_s.txt", header = None, skipinitialspace=True)
user = u[0].as_matrix()

userN = len(user)

# userRelations (directed): relation[i][0] -> relation[i][1]
r = pd.read_csv("relation_s.txt", sep = "\t", header = None, skipinitialspace=True)
relationN = r.shape[0]
relation = r.as_matrix()


# msg: ownerUID, itemID, catID, linkCount => u(y_i), r(y_i), c(y_i), t(y_i)
m = pd.read_csv("message_s.txt", sep = "\t", header = None, skipinitialspace=True)
mN = m.shape[0]
msg = m.as_matrix()

rmax = max(m[1].unique())

print(u)
print(r)
print(m)


# In[42]:

aggName = [rID * 5 for rID in m[1].unique()]
yName = [(uID * rmax + rID) * 5 + 1 for uID in u[0].unique() for rID in m[1].unique() ]
userName = [uID * 5 + 2 for uID in u[0].unique()]
itemName = [rID * 5 + 3 for rID in m[1].unique()]
catName = [cID * 5 + 4 for cID in m[2].unique()]

aggN = len(aggName)
yN = len(yName)
userN = len(userName)
itemN = len(itemName)
catN = len(catName)

print(aggName)
print(yName)
print(userName)
print(itemName)
print(catName)

#print([(uID, rmax, rID, (uID * rmax + rID) * 5 + 1) for uID in u[0].unique() for rID in m[1].unique() ])


# In[43]:

# PGM - FactorGraph (undirected)
#G = FactorGraph()
#G = BayesianModel()
G = MarkovModel()
G.add_nodes_from(aggName)
G.add_nodes_from(yName)
G.add_nodes_from(itemName)
G.add_nodes_from(userName)
G.add_nodes_from(catName)
print(G.check_model())


# In[70]:

PHI = {}
for y in yName:
    PHI[y] = []


# In[111]:

# count <-> candidate

for tID in m[1].unique():
    for uID in u[0].unique():
        (a, b) = (tID * 5, (uID * rmax + tID) * 5 + 1)
        # f[a][b][0][0/1]
        phi = Factor.Factor([a, b], [1, 2], np.random.rand(2))
        G.add_factors(phi)
        PHI[b].append(phi)
        G.add_edges_from([(a,b)])
        
print(G.check_model())



# In[112]:

# candidate <-> candidate
for i in range(0, relationN):
    #print(relation[i][0], relation[i][1])
    for j in range(0, itemN):
        for k in range(0, itemN):
            (a, b) = ((relation[i][0] * rmax + m[1].unique()[j]) * 5 + 1, (relation[i][1] * rmax + m[1].unique()[j]) * 5 + 1)
            # g[a][b][0/1][0/1]
            phi = Factor.Factor([a, b], [2, 2], np.random.rand(4))
            G.add_factors(phi)
            PHI[a].append(phi)
            PHI[b].append(phi)
            
            G.add_edges_from([(a, b)])

print(G.check_model())



# In[113]:

# attribute <-> candidate
#print(r2u_dict)
for i in range(0, mN):
    (a, b, c, d) = ((msg[i][0] * rmax + msg[i][1]) * 5 + 1, msg[i][0] * 5 + 2, msg[i][1] * 5 + 3, msg[i][2] * 5 + 4)
    # h[a][b][c][d][0/1]
    phi = Factor.Factor([a, b, c, d], [2, 1, 1, 1], np.random.rand(2))
    G.add_factors(phi)
    PHI[a].append(phi)
    G.add_edges_from([(a,b), (b,c), (c,d), (d, a), (a, c), (b, d)])

print(G.check_model())



# In[114]:

print(PHI[21][1])


# In[103]:

# Sampling
gibbs = Sampling.GibbsSampling(G)

sam = gibbs.sample(size=sampleN)
print(sam)


# In[110]:

print(sam.iloc[[sampleN-1]])

print(sam[21].iloc[[sampleN-1]])


# In[102]:

print(aggName)
print(yName)
print(userName)
print(itemName)
print(catName)


# In[87]:

# Inference
p = []
for yi in yName:
    up = 0
    down = 0
    for nb in G.markov_blanket(yi):
        # only care the link between candidates when inferencing
        if nb%5 == 1:
            # g[yi][nb][yi=0 or 1][nb=sample_res]
            down += g[yi][nb][0][sam[nb].iloc[[sampleN-1]]] + g[yi][nb][1][sam[nb].iloc[[sampleN-1]]]
            up += g[yi][nb][1][sam[nb].iloc[[sampleN-1]]]
    
    p[yi] = up / down

print(p[yi])


# In[ ]:



