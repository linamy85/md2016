import AE

import numpy as np

# NOTE: data must be "normalized" before dim_reduce
data = np.array([[1, 2, 3, 4, 5], [5, 2, 4, 1, 3], [1, 2, 3, 4, 5], [5, 2, 4, 1, 3]])

# API: dim_reduce (data, HIDDEN_N, batch_size=256, training_epochs=20, learning_rate=0.01):
X = AE.dim_reduce(data, 3, 2, 20, 0.01)

print(X)
