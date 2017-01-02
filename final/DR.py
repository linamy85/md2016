import AE

import numpy as np

data = np.array([[1, 2, 3, 4, 5], [5, 2, 4, 1, 3], [1, 2, 3, 4, 5], [5, 2, 4, 1, 3]])

X = AE.dim_reduce(data, 2, 3, 20, 0.01)
#dim_reduce (data, batch_size, HIDDEN_N, training_epochs=20, learning_rate=0.01):

print(X)
