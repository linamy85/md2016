
# coding: utf-8

# ### This version hasn't been neither COMPILED or UNIT-TESTED

# In[19]:

import pandas as pd
import numpy as np
import sys
import random

#from pgmpy.models import MarkovModel
from pgmpy_onGithub.pgmpy.models import MarkovModel
#from pgmpy.factors import Factor
from pgmpy_onGithub.pgmpy.factors.discrete import DiscreteFactor

#from pgmpy.inference import Sampling
from pgmpy_onGithub.pgmpy.sampling import Sampling


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
# rmax  
# sampleN: gibbs sampling times  

# # buildModel (userN, rmax, y_list, y_pair_list)
# 
# G = buildModel(y_list, y_pair_list)  
# 
# Build nodes, edges, factors with random values  
# Return an MM model

# In[20]:

def buildModel(userN, rmax, y_list, y_pair_list):
    
    countID = userN * rmax + 100
    attriID = userN * rmax + 101
    print('start building model')
    
    G = MarkovModel()
    G.add_nodes_from([countID, attriID])

    tmp = 0
    print(len(y_list))
    for y in y_list:
        tmp = tmp+1
        G.add_node(y)
        G.add_edges_from([(y, attriID)])
        phi = DiscreteFactor([y, attriID], [2, 1], np.random.rand(2))
        G.add_factors(phi)
        
        G.add_edges_from([(y, countID)])
        phi = DiscreteFactor([y, countID], [2, 1], np.random.rand(2))
        G.add_factors(phi)

        if (tmp % 1000 == 0):
            print(tmp/len(y_list) * 100, "% completed")

    print('finish adding nodes and layer1->2, 3->2 factors')
        
    tmp = 0
    print(len(y_pair_list))
    for y_pair in y_pair_list:
        tmp = tmp+1
        G.add_edges_from([(y_pair[0], y_pair[1])])
        phi = DiscreteFactor([y_pair[0], y_pair[1]], [2, 2], np.random.rand(4))
        G.add_factors(phi)

        if (tmp % 1000 == 0):
            print(tmp/len(y_pair_list) * 100, "% completed")
        
    print('check model:', G.check_model())
    return G


# ## inference(G, refreshAll, fh_dict, g_dict)
# 
# 更新fgh  
# G, P = inference(G, True, fh_dict, g_dict)  
# 只更新 h  
# G, P = inference(G, False, fh_dict, False)  
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

# In[21]:

def factor_assign_values(G, refreshAll, fh_dict, g_dict):
    Factors = G.get_factors()
    
    index = 0
    if refreshAll:
        # assign new values to factors in the same order
        for y, p in fh_dict.items():
            Factors[index].values = np.array([[1-p[0]], [p[0]]])
            index = index + 1
            Factors[index].values = np.array([[1-p[1]], [p[1]]])
            index = index + 1

        for y_pair, p in g_dict.items():
            Factors[index].values = np.array([[p, 1-p], [1-p, p]])
            index = index + 1

        if(len(Factors) != index):
            print('assign wrongly!')

    else: 
        #only refresh h
        for y, p in fh_dict.items():
            index = index + 1
            Factors[index].values = np.array([[1-p[1]], [p[1]]])

    print('assign new value: check model:', G.check_model())
            


# In[22]:

def GibbsInf(G, countID, attriID, fh_dict, g_dict, sampleN):
    # Sampling
    print('inInf', G.check_model())
    gibbs = Sampling.GibbsSampling(G)
    sam = gibbs.sample(size=sampleN)
    print('sam: ', sam)
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
                if (yi, nb) in g_dict:
                    #print(sam[nb][sampleN-1])
                    rand = random.random() 
                    v0 *= g_dict[(yi, nb)] if (rand == 0) else (1 - g_dict[(yi, nb)])
                    v1 *= g_dict[(yi, nb)] if (rand == 1) else (1 - g_dict[(yi, nb)])
                    #v0 *= g_dict[(yi, nb)] if (sam[nb][sampleN-1] == 0) else (1 - g_dict[(yi, nb)])
                    #v1 *= g_dict[(yi, nb)] if (sam[nb][sampleN-1] == 1) else (1 - g_dict[(yi, nb)])
                else:
                    rand = random.random() 
                    v0 *= g_dict[(nb, yi)] if (rand == 0) else (1 - g_dict[(nb, yi)])
                    v1 *= g_dict[(nb, yi)] if (rand == 1) else (1 - g_dict[(nb, yi)])
                    #v0 *= g_dict[(nb, yi)] if (sam[nb][sampleN-1] == 0) else (1 - g_dict[(nb, yi)])
                    #v1 *= g_dict[(nb, yi)] if (sam[nb][sampleN-1] == 1) else (1 - g_dict[(nb, yi)])
                

        p_dict[yi] = v1 / (v0 + v1)
        
    return p_dict


# In[23]:

def inference(G, userN, rmax, refreshAll, fh_dict, g_dict, sampleN):
    factor_assign_values(G, refreshAll, fh_dict, g_dict)
    countID = userN * rmax + 100
    attriID = userN * rmax + 101
    p_dict = GibbsInf(G, countID, attriID, fh_dict, g_dict, sampleN)
    print(p_dict)
    return G, p_dict
    


# In[ ]:


