import pandas as pd
import sys
import numpy as np
dir = sys.argv[1]
output_file = sys.argv[2]
print(dir+"/"+output_file)
p = pd.read_csv(dir+"/"+output_file, sep = " ", header = None, skipinitialspace=True)
predL = p.shape[0]
predID = p.as_matrix()
with open(dir+"/"+output_file, "w") as f:
    for i in range(predL):
        f.write(str(predID[i][0])+ "\t" +str(predID[i][1])+ "\t" + str(predID[i][1]) + '\n')
