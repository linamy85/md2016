
# coding: utf-8

# In[ ]:

# f(u, i) = (# of friends of u + # of items owned by the u) * # of hidden links of i


# In[242]:

import pandas as pd
import sys
import numpy as np


# In[243]:

dir = sys.argv[1]

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



# In[244]:

# Count friendsN of each user
friendsN_U = [0 for i in range(userN)]


for i in range(relN):
    friendsN_U[int(r[i][0])] += 1

# Count itemsN of each user
# Count links of each item
# Count maxOwnedItemCategory(MOIC) of each user

items_U = []
for i in range(userN):
    items_U.append(set())
    cats_U.append([])

links_I = [0 for i in range(itemN)]
MOIC_U = [0 for i in range(userN)]


for i in range(msgN):
    items_U[int(m[i][0])].add(int(m[i][1]))
    links_I[int(m[i][1])] = int(m[i][3])
    cats_U[int(m[i][0])].append(int(m[i][2]))
    
itemsN_U = [len(items_U[i]) for i in range(userN)]

for i in range(userN):
    MOIC_U[i] = max(set(cats_U[i]), key=cats_U[i].count)




# In[245]:

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

    #score[t] = tmpScore[u] * links_I[i]
    score[t] = itemsN_U[u] if links_I[i] != 0 else 0;
    
# first half 
arg = np.argsort(score)[::-1]
predto1_arg = arg[0:predL//2]
#print(pL, pL//2)


# In[246]:

with open(dir+"/pred_baseline_"+ dir+ ".txt", "w") as f:
    for i in range(predL):
        if i in predto1_arg:
            f.write(str(predID[i][0])+ " " +str(predID[i][1])+ " " + str(1) + '\n')
        else:
            f.write(str(predID[i][0])+ " " +str(predID[i][1])+ " " + str(0) + '\n')

print('end')


# In[ ]:




# In[267]:

'''
my = pd.read_csv(dir+"/pred_baseline.txt", sep = " ", header = None, skipinitialspace=True)
myL = my.shape[0]

res = pd.read_csv(dir+"/response.txt", sep = "\t", header = None, skipinitialspace=True)
resL = res.shape[0]
#print(myL, resL)

my = my.sort([0, 1], ascending=[True, True])
#print(my)
print(my.head(10))
my = my.as_matrix()

res = res.sort([0, 1], ascending=[True, True])
print(res.head(10))
res = res.as_matrix()


#print(res[resIndex][0], res[resIndex][1], my[0][0], my[0][1])
myIndex = 0
resIndex = 0

count = 0
ya = 0

while(resIndex != resL & myIndex != myL):
    if (res[resIndex][0] == my[myIndex][0]) & (res[resIndex][1] == my[myIndex][1]):
        ya += 1
    
        resIndex += 1
        if (my[myIndex][2] == 1):
                count += 1
    else:
        if (my[myIndex][2] == 0):
            count += 1
    myIndex += 1
    
    
# print(resL, myL)
print('count: ', count)
accuracy = count / myL
print(accuracy)
'''


# In[257]:

'''
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
'''


# In[ ]:



