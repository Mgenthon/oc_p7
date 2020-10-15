import numpy as np
from flask import Flask, request, jsonify, render_template
import pickle

app = Flask(__name__)
model = pickle.load(open('LGBM_predict_default_credit.pkl', 'rb'))

@app.route('/')
def home():
    return render_template('docs.html')


@app.route('/predict_api',methods=['POST'])
def predict_api():
    '''
    For direct API calls trought request
    '''
    data = request.get_json(force=True)
    prediction = model.predict_proba([np.array(list(data.values()))])

    output = prediction[0][1].tolist()
    return jsonify(output)

if __name__ == "__main__":
    app.run()
