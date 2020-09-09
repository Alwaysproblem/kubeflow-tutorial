#%%
import os
import time
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split as tvsplit
from tensorflow.keras import Input, layers

# disable logging warning and error
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
# tf.config.experimental_run_functions_eagerly(True)
#%%
sample_n = 100
epochs = 50
#%%
meana = np.array([1, 1])
cova = np.array([[0.1, 0],[0, 0.1]])

meanb = np.array([2, 2])
covb = np.array([[0.1, 0],[0, 0.1]])

x_red = np.random.multivariate_normal(mean=meana, cov = cova, size=sample_n)
x_green = np.random.multivariate_normal(mean=meanb, cov = covb, size=sample_n)

y_red = np.array([1] * sample_n)
y_green = np.array([0] * sample_n)

# plt.scatter(x_red[:, 0], x_red[:, 1], c = 'red' , marker='.', s = 30)
# plt.scatter(x_green[:, 0], x_green[:, 1], c = 'green', marker='.', s = 30)
# plt.show()

X = np.concatenate([x_red, x_green]).astype(np.float32)
y = np.concatenate([y_red, y_green]).astype(np.float32)

X_train, X_test, y_train, y_test = tvsplit(X, y, test_size=0.33, random_state=42)

data = tf.data.Dataset.from_tensor_slices((2 * X_train, y_train))
Data = tf.data.Dataset.from_tensor_slices((2 * X_test, y_test))

data = data.shuffle(10)
data = data.repeat()
data = data.batch(10)



InputLayer = Input(shape=(2, ))
OutputLayer = layers.Dense(1, activation='sigmoid')(InputLayer)
model = tf.keras.Model(inputs=InputLayer, outputs=OutputLayer)


callbacks = [
    tf.keras.callbacks.TensorBoard(
        log_dir='logs', histogram_freq=1, profile_batch = 3),
    tf.keras.callbacks.EarlyStopping(
            monitor='val_auc', min_delta=1e-3, patience=5, verbose=1, mode='max',
            baseline=None, restore_best_weights=True
        ),
    ]


model.compile('adam', loss = tf.keras.losses.Huber(), metrics=[tf.keras.metrics.AUC()])
# model.build(input_shape=(None, 2))
model.fit(data, epochs = 50, steps_per_epoch = 20, validation_data=Data.batch(10), callbacks=callbacks)

# save the first version of model.
savedir = './save/'
model.save(savedir)

# check if saved model is correct.
new_model = tf.keras.models.load_model(savedir)
# print(new_model.summary())
print(new_model.evaluate(Data.batch(10)))
print(new_model(np.array([[1., 1.], [1., 2.]])))
