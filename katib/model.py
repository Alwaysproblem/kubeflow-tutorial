#%%
import os
import time
import json
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split as tvsplit
from tensorflow.keras import Input, layers

# disable logging warning and error
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
# tf.config.experimental_run_functions_eagerly(True)

# # save the first version of model.
# savedir = './save/'
# model.save(savedir)

# # check if saved model is correct.
# new_model = tf.keras.models.load_model(savedir)
# # print(new_model.summary())
# print(new_model.evaluate(Data.batch(10)))
# print(new_model(np.array([[1., 1.], [1., 2.]])))

def dataloader(sample_n = 100, random_seed=42, test_size=0.33):

    meana = np.array([1, 1])
    cova = np.array([[0.1, 0],[0, 0.1]])

    meanb = np.array([2, 2])
    covb = np.array([[0.1, 0],[0, 0.1]])

    x_red = np.random.multivariate_normal(mean=meana, cov = cova, size=sample_n)
    x_green = np.random.multivariate_normal(mean=meanb, cov = covb, size=sample_n)

    y_red = np.array([1] * sample_n)
    y_green = np.array([0] * sample_n)


    X = np.concatenate([x_red, x_green]).astype(np.float32)
    y = np.concatenate([y_red, y_green]).astype(np.float32)

    X_train, X_test, y_train, y_test = tvsplit(X, y, test_size=test_size, random_state=random_seed)
    return X_train, X_test, y_train, y_test

def TFDataset(X_train, X_test, y_train, y_test, batch_size = 10, shuffle_buffer = 10):

    train = tf.data.Dataset.from_tensor_slices((2 * X_train, y_train))
    validation = tf.data.Dataset.from_tensor_slices((2 * X_test, y_test))

    train = train.shuffle(shuffle_buffer)
    train = train.repeat()
    train = train.batch(batch_size)

    validation = validation.batch(batch_size)
    validation = validation.repeat()

    return train, validation

def TFModel(input_size = 2, output_size = 1, opt="adam", hidden_units = 3):
    InputLayer = Input(shape=(input_size, ))
    hidden = layers.Dense(hidden_units, activation='relu')(InputLayer)
    OutputLayer = layers.Dense(output_size, activation='sigmoid')(hidden)
    model = tf.keras.Model(inputs=InputLayer, outputs=OutputLayer)
    model.compile(opt, loss=tf.keras.losses.Huber(), metrics=[tf.keras.metrics.AUC()])

    return model

def train(epochs = 50, sample_n = 100, batch_size = 10, optim = "Adam", lr = 0.001, hidden_units = 3):
    strategy = tf.distribute.experimental.MultiWorkerMirroredStrategy()
    # options = tf.data.Options()
    # options.experimental_distribute.auto_shard_policy = \
    #                                     tf.data.experimental.AutoShardPolicy.DATA

    tf_config = json.loads(os.environ.get('TF_CONFIG') or '{}')
    # worker_index = tf_config['task']['index']
    # num_workers = strategy.num_replicas_in_sync

    X_train, X_test, y_train, y_test = dataloader(sample_n = sample_n)

    data, Data = TFDataset(X_train, X_test, y_train, y_test, batch_size=batch_size)

    with strategy.scope():
        opt_dic = {
            "Adam": tf.keras.optimizers.Adam(lr),
            "SGD": tf.keras.optimizers.SGD(lr)
        }
        opt = opt_dic[optim]
        model = TFModel(opt=opt, hidden_units=hidden_units)

    callbacks = [
        # tf.keras.callbacks.TensorBoard(
        #     log_dir='logs', histogram_freq=1, profile_batch = 3),
        # tf.keras.callbacks.EarlyStopping(
        #         monitor='val_auc', min_delta=1e-3, patience=5, verbose=1, mode='max',
        #         baseline=None, restore_best_weights=True
        #     ),
        ]
    
    # model.build(input_shape=(None, 2))
    model.fit(data, epochs = epochs, steps_per_epoch = 200 // 3, validation_data=Data, 
                validation_steps = 200//3, callbacks=callbacks)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser("katib tutorial")

    parser.add_argument("--lr", type=float, default=0.001, action = "store", dest = "lr")
    parser.add_argument("--hidden-units", type=int, default=3, action="store", dest = "hidden_units")
    parser.add_argument("--opt", type=str, default = "Adam", action="store", dest = "opt")

    args = parser.parse_args()
    train(epochs = 5, sample_n=1000, optim = args.opt, lr=args.lr, hidden_units=args.hidden_units)