import pandas as pd
import numpy as np
import pickle
from sklearn.model_selection import train_test_split
from sklearn import ensemble
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import StandardScaler

data = pd.read_csv("traffic volume.csv")
data['temp'].fillna(data['temp'].mean(),inplace=True)
data['rain'].fillna(data['rain'].mean(),inplace=True)
data['snow'].fillna(data['snow'].mean(),inplace=True)
data['weather'].fillna('Clouds',inplace=True)

data[["day","month","year"]]=data["date"].str.split("-",expand=True)
data[["hours","minutes","seconds"]]=data["Time"].str.split(":",expand=True)
data.drop(columns=['date','Time'],axis=1,inplace = True)

y=data['traffic_volume']
x=data.drop(columns=['traffic_volume'],axis=1)

encoder = LabelEncoder()
x['holiday'] = encoder.fit_transform(x['holiday'])
x['weather'] = encoder.fit_transform(x['weather'])

scale = StandardScaler()
x_scaled = scale.fit_transform(x)
x = pd.DataFrame(x_scaled, columns=x.columns)

x_train,x_test,y_train,y_test=train_test_split(x,y,test_size=0.2,random_state=0)

Rand = ensemble.RandomForestRegressor()
Rand.fit(x_train,y_train)

pickle.dump(Rand, open("model.pkl",'wb'))
pickle.dump(scale, open("scale.pkl", 'wb'))
pickle.dump(encoder, open("encoder.pkl", 'wb'))
print("Models saved successfully!")
