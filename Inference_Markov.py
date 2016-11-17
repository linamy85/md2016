
# coding: utf-8

# ### This version hasn't been neither COMPILED or UNIT-TESTED

# In[20]:

import pandas as pd
import numpy as np

from pgmpy.models import MarkovModel
from pgmpy.factors import Factor

from pgmpy.inference import Sampling

from utils import *


# ### hash functions
# Note: rmax is a fixed value, which means max(itemID)

# In[21]:

'''
def hash_agg(rID):
    return rID * 5

def hash_y(uID, rmax, rID):
    return (uID * rmax + rID) * 5 + 1

def hash_y_inv(rmax, hash_y):
    return (((y-1)/5) % rmax, ((y-1)/5) / rmax)

def hash_uID(uID):
    return (uID * 5 + 2)

def hash_rID(rID):
    return (rID * 5 + 3)

def hash_cID(cID):
    return (cID * 5 + 4)
'''

def hash_y(uID, rmax, rID):
    return (uID * rmax + rID)

# return (uID, rID)
def hash_y_inv(rmax, hash_y):
    return (hash_y / rmax, hash_y % rmax)



# ## inference(fh_dict, g_dict)
# 
# ### ARG:
# 1. hf_dict[hash_y] = (h(), f())  
# 這些hash_y是要建node的  
# 還有candidate to count的prob.  
# 還有candidate to attribute的prob.  
# 
# 2. g_dict[(hash_yi, hash_y2)] = g()  
# 這些pair是要建link的 還有candidate to candidate的prob.  
# 
# ### RET:
# 1. prob_dict[hash_yi] = prob. got from inference

# ### nodes
# count layer: 1 node  
# candidate layer: node就看2. 有多少個index  
# attribute: 1 node  
# 
# ### links/factors
# count(1 node) <-> candidate: one link per hash_yi  
# candidate <-> candidate: see g_dict[(hash_yi, hash_y2)]  
# candidate(1 node) <-> attribute: one link per hash_yi  
# 

# ### I need
# userN: from user.txt  
# sampleN: gibbs sampling times  

# In[22]:

# get userN
def getUserN():
    u = pd.read_csv("user.txt", header = None, skipinitialspace=True)
    return u.shape[0]

# get item_list & cat_list
def getRmax():
    # msg: ownerUID, itemID, catID, linkCount => u(y_i), r(y_i), c(y_i), t(y_i)
    m = pd.read_csv("message.txt", sep = "\t", header = None, skipinitialspace=True)
    item_uniq = m[1].unique()
    return max(item_uniq)


# In[24]:

def buildModel():
    G = MarkovModel()
    countID = userN * rmax + 100
    attriID = userN * rmax + 101
    
    G.add_nodes_from(countID, attriID)
    
    # is [1-p, p] in correct order
    for y, p in fh_dict.items():
        G.add_node(y)
        phi = Factor.Factor([y, attriID], [2, 1], [1-p[0], p[0]])
        G.add_factors(phi)
        G.add_edges_from([(y, attriID)])
        
        phi = Factor.Factor([y, countID], [2, 1], [1-p[1], p[1]])
        G.add_factors(phi)
        G.add_edges_from([(y, countID)])
        
    for y_pair, p in g_dict.items():
        phi = Factor.Factor([y_pair[0], y_pair[0]], [2, 2], [1-p, p, p, 1-p])
        G.add_factors(phi)
        G.add_edges_from([(y_pair[0], y_pair[0])])
                            

    print(G.check_model())
    return G


# In[25]:

def GibbsInf(G, sampleN):
    # Sampling
    gibbs = Sampling.GibbsSampling(G)
    sam = gibbs.sample(size=sampleN)
    #print(sam)
    #print(sam.iloc[[sampleN-1]])
    #print(sam[21].iloc[[sampleN-1]])
    
    # Inference
    p_dict = {}
    for yi in fh_dict.keys():
        v0 = 1
        v1 = 1
        for nb in G.markov_blanket(yi):
            # only care the link between candidates when inferencing
            if (nb != countID) & (nb != attriID):
                # is this correct?
                v0 *= g_dict[(yi, nb)] if (sam[nb].iloc[[sampleN-1]] == 0) else 1 - g_dict[(yi, nb)]
                v1 *= g_dict[(yi, nb)] if (sam[nb].iloc[[sampleN-1]] == 1) else 1 - g_dict[(yi, nb)]

        p_dict[yi] = v1 / (v0 + v1)
        
    return p_dict



# In[23]:

def inference(fh_dict, g_dict):
    G = buildModel()
    # sampleN=?
    p_dict = GibbsInf(G, 3)
    return p_dict
    

