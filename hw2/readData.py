import pandas as pd

# userIDs: u[i]
u = pd.read_csv("user.txt", header = None, skipinitialspace=True)
user = u[0].as_matrix()

# userRelations (directed): relation[i][0] -> relation[i][1]
r = pd.read_csv("relation.txt", sep = "\t", header = None, skipinitialspace=True)
relation = r.as_matrix()	

# msg: ownerUID, itemID, categoryID, linkCount
m = pd.read_csv("message.txt", sep = "\t", header = None, skipinitialspace=True)
msg = m.as_matrix()

