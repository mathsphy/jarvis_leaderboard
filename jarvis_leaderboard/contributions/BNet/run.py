import pandas as pd
df= pd.read_csv('ssub.csv')

test_size = 0.2
val_size = 0.2
n_train = int(len(df)*(1-(val_size+test_size)))
n_val = int(len(df)*val_size)
n_test = int(len(df)*test_size)
#for leaderboard
train_df = df[:n_train]
val_df = df[n_train:n_train+n_val]
test_df = df[n_train+n_val:n_train+n_val+n_test]

import data_utils
from jarvis.ai.descriptors.elemental import get_element_fraction_desc
from jarvis.ai.descriptors.cfid import CFID,get_chem_only_descriptors
from tqdm import tqdm
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error

elements = ['H', 'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Na', 'Mg', 'Al', 'Si', 'P', 'S', 'Cl', 'K',
 'Ca', 'Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn', 'Ga', 'Ge', 'As', 'Se',
 'Br', 'Kr', 'Rb', 'Sr', 'Y', 'Zr', 'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd', 'In',
 'Sn', 'Sb', 'Te', 'I', 'Xe', 'Cs', 'Ba', 'La', 'Ce', 'Pr', 'Nd', 'Pm', 'Sm', 'Eu', 'Gd',
 'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb', 'Lu', 'Hf', 'Ta', 'W', 'Re', 'Os', 'Ir', 'Pt', 'Au',
 'Hg', 'Tl', 'Pb', 'Bi', 'Ac','Th', 'Pa', 'U', 'Np', 'Pu']

def formula_to_ef(df):
    df['comp_dict'] = df['formula'].apply(lambda x: data_utils.parse_formula(x))
    df['comp_fractions'] = df['comp_dict'].apply(lambda x: data_utils.get_fractions(x))
    df = df[~df['comp_fractions'].isnull()]

    for i,e in enumerate(elements):
        df[e] = [ x[i] for x in df['comp_fractions']]

    X_df = np.array(df[elements],dtype='float')    
    y_df = np.array(df['formula_energy'],dtype='float')
    list_df = list(df['id'])

    return X_df, y_df, list_df

X_train, y_train, train_ids = formula_to_ef(train_df)
X_val, y_val, val_ids = formula_to_ef(val_df)
X_test, y_test, test_ids = formula_to_ef(test_df)


import numpy as np
np.random.seed(1234567)
import tensorflow as tf
tf.random.set_seed(1234567)
import random
random.seed(1234567)

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LeakyReLU
from tensorflow.keras.layers import Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input
from tensorflow.keras.layers import add
from tensorflow.keras.layers import Activation
from tensorflow.keras import optimizers
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from sklearn.metrics import mean_absolute_error, mean_squared_error

#Network from "BRNet: Branched Residual Network for Fast and Accurate Predictive Modeling of Materials Properties"
#Link to paper: https://epubs.siam.org/doi/10.1137/1.9781611977172.39
in_layer = Input(shape=(X_train.shape[1],))

layer_1 = Dense(1024)(in_layer)
layer_1 = LeakyReLU()(layer_1)

layer_2 = Dense(1024)(layer_1)
layer_2 = LeakyReLU()(layer_2)

rayer_1 = Dense(1024)(in_layer)
rayer_1 = LeakyReLU()(rayer_1)

rayer_2 = Dense(1024)(rayer_1)
rayer_2 = LeakyReLU()(rayer_2)


mayer_1 = add([layer_2, rayer_2])


layer_5 = Dense(512)(mayer_1)
layer_5 = LeakyReLU()(layer_5)

layer_6 = Dense(512)(layer_5)
layer_6 = LeakyReLU()(layer_6)

layer_7 = Dense(512)(layer_6)
layer_7 = LeakyReLU()(layer_7)

layer_8 = Dense(256)(layer_7)
layer_8 = LeakyReLU()(layer_8)


layer_9 = Dense(256)(layer_8)
layer_9 = LeakyReLU()(layer_9)


layer_10 = Dense(256)(layer_9)
layer_10 = LeakyReLU()(layer_10)


layer_11 = Dense(128)(layer_10)
layer_11 = LeakyReLU()(layer_11)

layer_12 = Dense(128)(layer_11)
layer_12 = LeakyReLU()(layer_12)


layer_13 = Dense(128)(layer_12)
layer_13 = LeakyReLU()(layer_13)

layer_14 = Dense(64)(layer_13)
layer_14 = LeakyReLU()(layer_14)

layer_15 = Dense(64)(layer_14)
layer_15 = LeakyReLU()(layer_15)


layer_16 = Dense(32)(layer_15)
layer_16 = LeakyReLU()(layer_16)

out_layer = Dense(1)(layer_16)

model = Model(inputs=in_layer, outputs=out_layer)

adam = optimizers.Adam(lr=0.0001)
model.compile(loss=tf.keras.losses.mean_absolute_error, optimizer=adam, metrics=['mean_absolute_error'])

es = EarlyStopping(monitor='val_loss', mode='min', verbose=1, patience=100, restore_best_weights=True)

model.fit(X_train, y_train, verbose=2, validation_data=(X_val, y_val), epochs=3000, batch_size=32, callbacks=[es])

pred=model.predict(X_test)
print(mean_absolute_error(y_test,pred))

f=open('AI-SinglePropertyPrediction-formula_energy-ssub-test-mae.csv','w')
f.write('id,target,prediction\n')
for i,j,k in zip(test_ids,y_test,pred):
    line=str(i)+','+str(j)+','+str(k)+'\n'
    f.write(line)
f.close()
