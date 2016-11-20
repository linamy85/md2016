
# coding: utf-8

# In[ ]:

# f(u, i) = (# of friends of u + # of items owned by the u) * # of hidden links of i


# In[165]:

import pandas as pd
import sys
import numpy as np


# In[166]:
dir = './valid'

# userIDs: u[i]
user = pd.read_csv(dir+"/user.txt", header = None, skipinitialspace=True)
userN = user.shape[0]

# userRelations (directed): relation[i][0] -> relation[i][1]
r = pd.read_csv(dir+"/relation.txt", sep = "\t", header = None, skipinitialspace=True)
relN = r.shape[0]
r = r.as_matrix() 

# msg: ownerUID, itemID, categoryID, linkCount
m = pd.read_csv(dir+"/message.txt", sep = "\t", header = None, skipinitialspace=True)
msgN = m.shape[0]
itemN = max(m[1])+1
m = m.as_matrix()



# In[167]:

# Count friendsN of each user
friendsN_U = [0 for i in range(userN)]


for i in range(relN):
    friendsN_U[int(r[i][0])] += 1

# Count itemsN of each user
# count links of each item
items_U = []
for i in range(userN):
    items_U.append(set())

links_I = [0 for i in range(itemN)]

for i in range(msgN):
    items_U[int(m[i][0])].add(int(m[i][1]))
    links_I[int(m[i][1])] = int(m[i][3])
    
itemsN_U = [len(items_U[i]) for i in range(userN)]



# In[168]:

# add friendsN_U, itemsN_U of each user
fr = np.asarray(friendsN_U)
it = np.asarray(itemsN_U)
tmpScore = np.add(fr, it)

# read each pair of pred.id
p = pd.read_csv(dir+"/pred.id", sep = " ", header = None, skipinitialspace=True)
predL = p.shape[0]
predID = p.as_matrix()

# count score of each pair
score = np.empty(predL)

for t in range(predL):
    # f(u, i) = (# of friends of u + # of items owned by the u) * # of hidden links of i
    (u, i) = (int(predID[t][0]), int(predID[t][1]))
    score[t] = tmpScore[u] * links_I[i]
    
# first half 
arg = np.argsort(score)[::-1]
predto1_arg = arg[0:predL//2]


# In[169]:

with open(dir+"/pred_baseline.txt", "w") as f:
    for i in range(predL):
        if i in predto1_arg:
            f.write(str(predID[i][0])+ " " +str(predID[i][1])+ " " + str(1) + '\n')
        else:
            f.write(str(predID[i][0])+ " " +str(predID[i][1])+ " " + str(0) + '\n')

print('end')


# In[164]:

my = pd.read_csv(dir+"/pred_baseline.txt", sep = " ", header = None, skipinitialspace=True)
myL = my.shape[0]
my = my.as_matrix()

res = pd.read_csv(dir+"/response.txt", sep = "\t", header = None, skipinitialspace=True)
resL = res.shape[0]
res = res.as_matrix()

#print(myL, resL)


# In[ ]:




# In[170]:

count = 0
for i in range(resL):
    for j in range(myL):
    # appear in res, correct if predict = 1
        if (res[i][0] == my[j][0]) & (res[i][1] == my[j][1]):
            if (my[j][2] == 1):
                count += 1
        # doesn't appear in res, correct if predict = 0
        else:
            if (my[j][2] == 0):
                count += 1

accuracy = count / mL
print(accuracy)


# In[ ]:



