import pandas as pd
import numpy as np
import pickle
import os
from flask import Flask, request, render_template, jsonify
from datetime import timedelta

app = Flask(__name__)

# Load model
try:
    with open('ts_model.pkl', 'rb') as f:
        model = pickle.load(f)
    print("Model loaded successfully.")
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

# Load historical data
try:
    hist_df = pd.read_csv('historical_data.csv')
    hist_df['datetime'] = pd.to_datetime(hist_df['datetime'])
    print("Historical data loaded successfully.")
except Exception as e:
    print(f"Error loading historical data: {e}")
    hist_df = None

@app.route('/')  
def home():
    return render_template('index.html')  

@app.route('/api/predict', methods=["GET"])
def get_prediction():
    if model is None or hist_df is None:
        return jsonify({'error': 'Model or data not available'})

    # Provide the last 7 days of historical data
    # Sort just in case
    hist_sorted = hist_df.sort_values('datetime')
    hist_times = hist_sorted['datetime'].dt.strftime('%Y-%m-%d %H:%M:%S').tolist()
    hist_values = hist_sorted['traffic_volume'].tolist()
    
    # Predict the next 48 hours
    last_time = hist_sorted['datetime'].max()
    future_times = [last_time + timedelta(hours=i) for i in range(1, 49)]
    
    future_df = pd.DataFrame({'datetime': future_times})
    future_df['hour'] = future_df['datetime'].dt.hour
    future_df['dayofweek'] = future_df['datetime'].dt.dayofweek
    future_df['month'] = future_df['datetime'].dt.month
    future_df['dayofyear'] = future_df['datetime'].dt.dayofyear
    
    features = ['hour', 'dayofweek', 'month', 'dayofyear']
    preds = model.predict(future_df[features])
    
    pred_times = future_df['datetime'].dt.strftime('%Y-%m-%d %H:%M:%S').tolist()
    pred_values = [float(v) for v in preds]
    
    return jsonify({
        'historical': {
            'times': hist_times,
            'values': hist_values
        },
        'prediction': {
            'times': pred_times,
            'values': pred_values
        }
    })

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False)
