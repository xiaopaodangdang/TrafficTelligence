import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

data = pd.read_csv('traffic volume.csv')
data[['day','month','year']] = data['date'].str.split('-', expand=True)
data[['hours','minutes','seconds']] = data['Time'].str.split(':', expand=True)
data.drop(columns=['date','Time'], inplace=True)

# Imputation (fill missing)
data['temp'].fillna(data['temp'].mean(), inplace=True)
data['rain'].fillna(data['rain'].mean(), inplace=True)
data['snow'].fillna(data['snow'].mean(), inplace=True)

# Encoding (as done in notebook based on the HTML options)
from sklearn.preprocessing import LabelEncoder
le = LabelEncoder()
data['holiday'] = le.fit_transform(data['holiday'].astype(str))
data['weather'] = le.fit_transform(data['weather'].astype(str))

y = data['traffic_volume']
x = data.drop(columns=['traffic_volume'])

x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=0)

# Scale
scale = StandardScaler()
x_train = scale.fit_transform(x_train)
x_test = scale.transform(x_test)
pickle.dump(scale, open('scale.pkl', 'wb'))

# Train
rf = RandomForestRegressor(n_estimators=100)
rf.fit(x_train, y_train)

# Save
pickle.dump(rf, open('model.pkl', 'wb'))
print("Model trained and saved as model.pkl")
