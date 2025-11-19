import numpy as np
import pickle
import pandas as pd
import os
from flask import Flask, request, render_template

app = Flask(__name__)
model = pickle.load(open('D:/SmartBridge-Project/model.pkl', 'rb'))
scale = pickle.load(open('D:/SmartBridge-Project/scale.pkl', 'rb'))

@app.route('/')  
def home():
    return render_template('index.html')  

@app.route('/predict', methods=["POST", "GET"]) 
@app.route('/predict', methods=["POST"])
def predict():
    input_feature = [float(x) for x in request.form.values()]
    features_values = [np.array(input_feature)]

    data = pd.DataFrame(features_values, columns=scale.feature_names_in_)
    data = scale.transform(data)

    prediction = model.predict(data)
    text = "Estimated Traffic Volume is : "
    return render_template("result.html", prediction_text=text + str(int(prediction[0])))


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))

    app.run(port=port, debug=True, use_reloader=False)
