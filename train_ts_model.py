import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import pickle

print("Loading data...")
df = pd.read_csv('traffic volume.csv')

# Convert date and time to datetime
df['datetime'] = pd.to_datetime(df['date'] + ' ' + df['Time'], format='%d-%m-%Y %H:%M:%S')
df = df.sort_values('datetime').reset_index(drop=True)

# Drop duplicates if any
df = df.drop_duplicates(subset=['datetime'])

print("Creating features...")
def create_features(df):
    df['hour'] = df['datetime'].dt.hour
    df['dayofweek'] = df['datetime'].dt.dayofweek
    df['month'] = df['datetime'].dt.month
    df['dayofyear'] = df['datetime'].dt.dayofyear
    return df

df = create_features(df)

features = ['hour', 'dayofweek', 'month', 'dayofyear']
target = 'traffic_volume'

X = df[features]
y = df[target]

print("Training model...")
model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
model.fit(X, y)

print("Saving model...")
with open('ts_model.pkl', 'wb') as f:
    pickle.dump(model, f)

print("Saving historical data for visualization...")
last_date = df['datetime'].max()
start_date = last_date - pd.Timedelta(days=7)
historical_data = df[df['datetime'] >= start_date][['datetime', 'traffic_volume']].copy()
historical_data.to_csv('historical_data.csv', index=False)

print("Done!")
