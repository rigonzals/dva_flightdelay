
import streamlit as st
import pandas as pd
import pydeck as pdk
import datetime
import numpy as np
import sklearn
import pickle
from flask import Flask, request
from datetime import datetime
# Pickles!
app = Flask(__name__)

# load the model on load
with open('gradient_boost_model.pkl','rb') as file:
    model = pickle.load(file)

lookup_flight_data = pd.read_csv('flight_lookup_data.csv')

date_dimensions = pd.read_csv('DateDimension.csv')


@app.route('/')
def get_prediction(
        model_in=model,
        lookup_flight_data_in = lookup_flight_data,
        date_dimensions_in = date_dimensions,
        ):
    """call the prediction of the model and return a dictionary with the responses"""

    # get the args from the model inputs
    airline_code = request.args.get('airline_code')
    flight_date = request.args.get('flight_date')
    flight_time = request.args.get('flight_time')
    origin = request.args.get('origin')
    destination = request.args.get('destination')
    print(flight_date)
    print(flight_time)

    # feature creation for the dates
    flight_date_parsed = pd.to_datetime(flight_date)
    month = flight_date_parsed.mo