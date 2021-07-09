# -*- coding: utf-8 -*-
"""dicoding-submission-NLP-2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/19c3JIYeTt77qHI-hDUFmVnMCU1VyYWdp

# Data

### Load data
"""

import numpy as np
import pandas as pd
from keras.layers import Dense, LSTM
import matplotlib.pyplot as plt
import tensorflow as tf
import datetime as dt

df = pd.read_csv('/content/D202.csv')
df.tail()

"""### Pre-processing data"""

df_new = df.groupby(['DATE', 'START TIME','END TIME'], as_index=False).mean()
df_new.tail()

print("Sum of NULL")
print(df_new.isnull().sum())
x_data = df_new['DATE'].values
y_data = df_new['USAGE'].values
plt.figure(figsize=(15,5))
plt.plot(x_data, y_data, '-')
plt.title('Electricity Usage in kWh', fontsize=20)
print("Shape = ", df_new.shape)

from sklearn.model_selection import train_test_split
x_train, x_test, y_train, y_test = train_test_split(x_data, y_data, test_size=0.2)

"""### Change series data to batch"""

def windowed_dataset(series, window_size, batch_size, shuffle_buffer):
  series = tf.expand_dims(series, axis=-1)
  ds = tf.data.Dataset.from_tensor_slices(series)
  ds = ds.window(window_size + 1, shift=1, drop_remainder=True)
  ds = ds.flat_map(lambda w: w.batch(window_size + 1))
  ds = ds.shuffle(shuffle_buffer)
  ds = ds.map(lambda w: (w[:-1], w[-1:]))
  return ds.batch(batch_size).prefetch(1)

"""## Model

## Creating callbacks
"""

class myCallback(tf.keras.callbacks.Callback):
  def on_epoch_end(self, epoch, logs={}):
    if(logs.get('mae') < 0.1):
      print("\n MAE < 10%!")
      self.model.stop_training = True
callbacks = myCallback()

"""## Optimizer"""

from matplotlib import pyplot
from time import time

def model_fit_optimizer(train_set, val_set, optimizer):
  start_time = time()
  # create model
  model = tf.keras.Sequential([
    tf.keras.layers.LSTM(60, return_sequences=True),
    tf.keras.layers.LSTM(60),
    tf.keras.layers.Dense(30, activation="relu"),
    tf.keras.layers.Dense(10, activation="relu"),
    tf.keras.layers.Dense(1),
    ])
  # compile model
  model.compile(loss=tf.keras.losses.Huber(),
                optimizer=optimizer,
                metrics=['mae'])
  # fit model
  model_history = model.fit(
                    train_set,
                    epochs=10,
                    validation_data=val_set,
                    verbose=0)
  # time to train model
  finish_time = time()-start_time
  print('Time to train with optimizer ' + optimizer, finish_time)
  # evaluate model
  # eval_results = model.evaluate(train_generator, batch_size=batch_size)
  # print('Model accuracy with optimizer ' + optimizer, eval_results[1])
  # plot learning curves
  pyplot.plot(model_history.history['mae'], label='train')
  pyplot.plot(model_history.history['val_mae'], label='test')
  pyplot.ylim(bottom=0.0, top=0.2)
  pyplot.xlabel('epoch')
  pyplot.ylabel('mae')
  pyplot.legend(['train', 'test'], loc='lower right')
  pyplot.title('optimizer = '+optimizer, pad=-100)

"""### Plotting accuracy for each optimizers"""

# create learning curves for different optimizers
optimizers = ['sgd', 'rmsprop', 'adagrad', 'adam']
train_set = windowed_dataset(y_train, window_size=60, batch_size=100, shuffle_buffer=1000)
val_set = windowed_dataset(y_test, window_size=60, batch_size=100, shuffle_buffer=1000)

for i in range(len(optimizers)):
	# plot position
	plot_no = 220 + (i+1)
	pyplot.subplot(plot_no)
	# fit, evaluate model, determine time to train, and plot learning curves for an optimizer
	model_fit_optimizer(train_set, val_set, optimizers[i])
# show learning curves
pyplot.tight_layout()
pyplot.show()

"""## Learn rate"""

def model_fit_lrate(train_set, val_set, lrate):
  start_time = time()
  # create model
  model = tf.keras.Sequential([
    tf.keras.layers.LSTM(60, return_sequences=True),
    tf.keras.layers.LSTM(60),
    tf.keras.layers.Dense(30, activation="relu"),
    tf.keras.layers.Dense(10, activation="relu"),
    tf.keras.layers.Dense(1),
    ])
  # compile model
  optm = tf.keras.optimizers.Adam(learning_rate=lrate)
  model.compile(loss=tf.keras.losses.Huber(),
                optimizer=optm,
                metrics=['mae'])
  # fit model
  model_history = model.fit(
                    train_set,
                    epochs=5,
                    validation_data=val_set,
                    verbose=0)
  # time to train model
  finish_time = time()-start_time
  print('Time to train with lrate ' + str(lrate), finish_time)
  # evaluate model
  # eval_results = model.evaluate(train_generator, batch_size=batch_size)
  # print('Model accuracy with optimizer ' + optimizer, eval_results[1])
  # plot learning curves
  pyplot.plot(model_history.history['mae'], label='train')
  pyplot.plot(model_history.history['val_mae'], label='test')
  pyplot.ylim(bottom=0.0, top=0.2)
  pyplot.xlabel('epoch')
  pyplot.ylabel('mae')
  pyplot.legend(['train', 'test'], loc='lower right')
  pyplot.title('lrate = '+ str(lrate), pad=-100)

"""### Plotting Learn Rates"""

# create learning curves for different optimizers
lrates = [1.000e-1, 1.000e-3, 1.000e-7, 1.000e-9]

for i in range(len(lrates)):
	# plot position
	plot_no = 220 + (i+1)
	pyplot.subplot(plot_no)
	# fit, evaluate model, determine time to train, and plot learning curves for an optimizer
	model_fit_lrate(train_set, val_set, lrates[i])
# show learning curves
pyplot.tight_layout()
pyplot.show()

"""# Final results"""

model = tf.keras.Sequential([
    tf.keras.layers.LSTM(60, return_sequences=True),
    tf.keras.layers.LSTM(60),
    tf.keras.layers.Dense(30, activation="relu"),
    tf.keras.layers.Dense(10, activation="relu"),
    tf.keras.layers.Dense(1),
    ])
# compile model
optm = tf.keras.optimizers.Adam(learning_rate=1.000e-7)
model.compile(loss=tf.keras.losses.Huber(),
              optimizer=optm,
              metrics=['mae'])
# fit model
model_history = model.fit(
                  train_set,
                  epochs=20,
                  validation_data=val_set,
                  verbose=1, callbacks=[callbacks])
pyplot.plot(model_history.history['mae'], label='train')
pyplot.plot(model_history.history['val_mae'], label='test')
pyplot.ylim(bottom=0.0, top=0.2)
pyplot.xlabel('epoch')
pyplot.ylabel('mae')
pyplot.legend(['train', 'test'], loc='lower right')
pyplot.title('lrate fixed ', pad=-100)

