from __future__ import division, print_function, absolute_import

import tensorflow as tf
import numpy as np
import math

def sigmoid(x): 
    return np.divide(1, (np.add(1, np.exp(-x))))

# Building the encoder
def encoder(weights, biases, x):
        # Encoder Hidden layer with sigmoid activation #1
        layer = tf.nn.sigmoid(tf.add(tf.matmul(x, weights['enc_w']), biases['enc_b']))
        return layer


# Building the decoder
def decoder(weights, biases, x):
        # Encoder Hidden layer with sigmoid activation #1
        layer = tf.nn.sigmoid(tf.add(tf.matmul(x, weights['dec_w']), biases['dec_b']))
        return layer

# HIDDEN_N
def dim_reduce (data, HIDDEN_N, batch_size=256, training_epochs=20, learning_rate=0.01):

        DATA_N = data.shape[0]

        # Parameters
        #learning_rate = 0.01
        #training_epochs = 20
        #batch_size = 256
        display_step = 5

        # Network Parameters
        n_hidden_1 = HIDDEN_N # 1st layer feature_num
        n_input = data.shape[1] # input data feature_num

        # tf Graph input (only pictures)
        X = tf.placeholder("float", [None, n_input])

        weights = {
                'enc_w': tf.Variable(tf.random_normal([n_input, n_hidden_1])),
                'dec_w': tf.Variable(tf.random_normal([n_hidden_1, n_input])),
        }
        biases = {
                'enc_b': tf.Variable(tf.random_normal([n_hidden_1])),
                'dec_b': tf.Variable(tf.random_normal([n_input])),
        }



        # Construct model
        encoder_op = encoder(weights, biases, X)
        decoder_op = decoder(weights, biases, encoder_op)

        # Prediction
        y_pred = decoder_op
        # Targets (Labels) are the input data.
        y_true = X

        # Define loss and optimizer, minimize the squared error
        cost = tf.reduce_mean(tf.pow(y_true - y_pred, 2))
        optimizer = tf.train.RMSPropOptimizer(learning_rate).minimize(cost)

        # Initializing the variables
        init = tf.global_variables_initializer()

        # Launch the graph
        with tf.Session() as sess:
                sess.run(init)
                total_batch = int(DATA_N / batch_size)
                print('start training')
                # Training cycle
                for epoch in range(training_epochs):
                        # Loop over all batches
                        for i in range(total_batch):
                                batch_xs = data[i*batch_size : (i+1)*batch_size]
                                # Run optimization op (backprop) and cost op (to get loss value)
                                _, c = sess.run([optimizer, cost], feed_dict={X: batch_xs})
                        # Display logs per epoch step
                        if epoch % display_step == 0:
                                print("Epoch:", '%04d' % (epoch+1), "cost=", "{:.9f}".format(c))

                print("Optimization Finished!")

                # Extract variables
                w_list = sess.run(weights)
                b_list = sess.run(biases)


        # Forward to get X_FE
        w = w_list['enc_w']
        b = b_list['enc_b']

        X_FE = []
        total_batch = int(DATA_N/batch_size)
        for i in range(DATA_N):
                X_FE.append(sigmoid(np.add(np.dot(np.transpose(w), data[i]), b)))
        X_FE = np.asarray(X_FE)

        return X_FE

