'''
Created on Apr 28, 2020

@author: thaih
'''
import pandas as pd
import keras
from keras.models import Sequential
from keras.layers import Dense
input_data = pd.read_csv("train.csv")
y = input_data['label']
input_data.drop('label',axis=1,inplace = True)
X = input_data
y = pd.get_dummies(y)
classifier = Sequential()
classifier.add(Dense(units = 600, kernel_initializer ='uniform', activation = 'relu', input_dim = 784))
classifier.add(Dense(units = 400, kernel_initializer ='uniform', activation = 'relu'))
classifier.add(Dense(units = 200, kernel_initializer ='uniform', activation = 'relu'))
classifier.add(Dense(units = 10, kernel_initializer ='uniform', activation = 'sigmoid'))
classifier.compile(optimizer = 'sgd', loss = 'mean_squared_error', metrics = ['accuracy'])
classifier.fit(X, y, batch_size = 10, epochs = 10)
test_data = pd.read_csv("test.csv")
y_pred = classifier.predict(test_data)