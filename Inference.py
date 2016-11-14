import pandas as pd
import numpy as np
from pgmpy.models import FactorGraph
from pgmpy.models import MarkovModel
from pgmpy.factors.discrete import DiscreteFactor


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


# u2r + r2u dictionary + Node name for y
u2r_dict = {}
r2u_dict = {}
yName = []

for i in range(mN):
	u2r_dict[msg[i][0]] = []
	r2u_dict[msg[i][1]] = []
	yName.append('u'+str(msg[i][0])+'r'+str(msg[i][1]))

yN = mN

for i in range(mN):
	u2r_dict[msg[i][0]].append(msg[i][1])
	r2u_dict[msg[i][1]].append(msg[i][0])


# Length
item = m[1].unique()
itemN = len(item)
cat = m[2].unique()
catN = len(cat)

# Node name for item, agg, cat, user
itemName = ['r'+str(item[i]) for i in range(0, itemN)]	
aggName = ['t'+str(item[i]) for i in range(0, itemN)]	#aggregate statistics
catName= ['c'+str(cat[i]) for i in range(0, catN)]
userName= ['u'+str(user[i]) for i in range(0, userN)]
#print('userN:', userN, 'itemN:', itemN, 'userN*itemN:', userN*itemN)


# PGM - undirected
G = FactorGraph()
G.add_nodes_from(itemName)	#r?
G.add_nodes_from(aggName)	#t?
G.add_nodes_from(catName)	#c?
G.add_nodes_from(userName)	#u?
G.add_nodes_from(yName)		#y?


# count <-> candidate
for i in range (0, itemN):
	for uID in r2u_dict[int(aggName[i][1:])]:	# Note: aggName contains 't'
		phi = DiscreteFactor([aggName[i], 'u'+str(uID)+'r'+aggName[i][1:]], [1, 2], np.random.rand(2))
		G.add_factors(phi)
		G.add_edges_from([(aggName[i], phi), ('u'+str(uID)+'r'+aggName[i][1:], phi)])


# candidate <-> candidate
for i in range(0, relationN):
	#print(relation[i][0], relation[i][1])
	for rID1 in u2r_dict[relation[i][0]]:
		for rID2 in u2r_dict[relation[i][1]]:
			phi = DiscreteFactor(['u'+str(relation[i][0])+'r'+str(rID1), 'u'+str(relation[i][1])+'r'+str(rID2)], [2, 2], np.random.rand(4))
			G.add_factors(phi)
			G.add_edges_from([('u'+str(relation[i][0])+'r'+str(rID1), phi), ('u'+str(relation[i][1])+'r'+str(rID2), phi)])

			
# attribute <-> candidate
#print(r2u_dict)
for i in range(0, mN):
	for uID in r2u_dict[msg[i][1]]:
		phi = DiscreteFactor(['u'+str(uID)+'r'+str(msg[i][1]), 'u'+str(uID), 'c'+str(msg[i][2]), 'r'+str(msg[i][1])], [2, 1, 1, 1], np.random.rand(2))
		G.add_factors(phi)
		G.add_edges_from([('u'+str(uID)+'r'+str(msg[i][1]), phi), ('u'+str(uID), phi), ('c'+str(msg[i][2]), phi), ('r'+str(msg[i][1]), phi)])
	
print(G.check_model())

# Inference


# Input
