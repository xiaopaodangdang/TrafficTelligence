import numpy as np
import pickle
import pandas as pd
import os
from flask import Flask, request, render_template

app = Flask(__name__)
model = pickle.load(open('model.pkl', 'rb'))
scale = pickle.load(open('scale.pkl', 'rb'))

@app.route('/')  
def home():
    return render_template('index.html')  

@app.route('/predict', methods=["POST"])
def predict():
    # Retrieve values using keys to ensure correct order
    feature_dict = request.form.to_dict()
    
    # Extract in the exact order the model expects
    expected_order = ['holiday', 'temp', 'rain', 'snow', 'weather', 'day', 'month', 'year', 'hours', 'minutes', 'seconds']
    input_feature = [float(feature_dict[col]) for col in expected_order]
    
    features_values = [np.array(input_feature)]

    data = pd.DataFrame(features_values, columns=expected_order)
    data = scale.transform(data)

    prediction = model.predict(data)
    text = "Estimated Traffic Volume is : "
    return render_template("result.html", prediction_text=text + str(int(prediction[0])))


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))

    app.run(port=port, debug=True, use_reloader=False)
