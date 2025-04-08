"""
# My first app
Here's our first attempt at using data to create a table:
"""

import streamlit as st
import pandas as pd
import pydeck as pdk
import datetime
import numpy as np
import pickle
from flask import Flask
# Pickles!
app = Flask(__name__)

# load the model on load
with open('gradient_boost_model.pkl','rb') as file:
    model = pickle.load(file)



@app.route('/')
def get_prediction(model=model, model_inputs={}):
    """call the prediction of the model and return a dictionary with the responses"""

    # call the model
    return {
        'prediction':'On Time',
        'on_time_chance':85,
        'a_little_late_chance':10,
        'really_late_chance':5
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
