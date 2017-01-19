import AE

import numpy as np

data = np.array([[1, 2, 3, 4, 5, 1, 2, 3, 4, 5], [5, 2, 4, 1, 3, 5, 2, 4, 1, 3], [1, 2, 3, 4, 5, 1, 2, 3, 4, 5], [5, 2, 4, 1, 3, 5, 2, 4, 1, 3]])
print('input:', data.shape[0], ',', data.shape[1])
print(data)
print('==============================')

# API: dim_reduce (dataN, HIDDEN_N, batch_size=256, training_epochs=20, learning_rate=0.01):
################### Training data ############################
# data:         (vectorN, dim of each vector) must be "normalized" before dim_reduce
# batch_size:   since vectorN (i.e.data.shape[0]) may be very large, we devides them into batches and train each batch.
#               e.g. data: (256000, 999) and we set batch_size to 256, we train data of size (256, 999) each time
#
################### Parameters to adjust ############################
# HIDDEN_N:             #neuron in the hidden layer
# training_epochs:      iteration
# learning_rate:        :)

################### output ############################
# data after dim_reduce: (vectorN, HIDDEN_N)
# w
# b

X, w, b = AE.dim_reduce(data, 3, 2, 20, 0.01)

print('==============================')
print('answer:', X.shape[0], ',', X.shape[1])
print(X)

#forward2hidden(data, w, b, batch_size):
XX = AE.forward2hidden(data, w, b, 2)
print(XX)
