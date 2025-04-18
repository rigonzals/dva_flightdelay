
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
with open('gradient_boost_model_final.pkl','rb') as file:
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

    # feature creation for the dates
    flight_date_parsed = pd.to_datetime(flight_date)
    month = flight_date_parsed.month
    flight_day = flight_date_parsed.day
    flight_time_obj = datetime.strptime(str(flight_time), "%H:%M:%S").time()
    hour = flight_time_obj.hour
    day_short = flight_date_parsed.day_name()[:3]
    flight_features = pd.DataFrame([{
        'month': month,
        'day': flight_day,
        'hour': hour,
        'DayShort': day_short
    }])

    # loop up the date holiday info
    date_dimensions_in['Date'] = pd.to_datetime(date_dimensions_in['Date'])
    date_dims_filtered = date_dimensions_in[date_dimensions_in['Date']==flight_date]

    # loop up the other flight info
    flight_info = lookup_flight_data_in[
                                (lookup_flight_data_in['airline']==airline_code)
                                     & (lookup_flight_data_in['origin']==origin)
                                     & (lookup_flight_data_in['destination']==destination)
                                     ]

    # combine all the things
    date_dims_filtered = date_dims_filtered.reset_index(drop=True)
    flight_info = flight_info.reset_index(drop=True)
    combined_features = pd.concat(
        [flight_features, date_dims_filtered, flight_info],
        axis=1)

    # one hot encode the time variables
    combined_features = pd.get_dummies(combined_features, columns= ['month'
                                            ,'day'
                                            , 'hour'
                                            , 'DayShort'])

    # check for missing columns
    current_columns = model_in.feature_names_in_
    missing_columns = set(current_columns).difference(combined_features.columns)
    missing_columns = list(missing_columns)
    missing_columns.sort()
    for col in missing_columns:
        combined_features[col] = False
    print('missing_columns',missing_columns)

    missing_columns = [x for x in model_in.feature_names_in_ if x not in combined_features.columns]
    missing_columns = list(missing_columns)
    missing_columns.sort()

    print('missing_columns after',missing_columns)
    print('verison',sklearn.__version__)


    combined_features = combined_features[model_in.feature_names_in_]
    print([x for x in combined_features.columns if '.1' in x])
    print(combined_features[['month_4','month_5']].head())
    combined_features.to_csv('combined_features.csv')

    # call the model
    predicted_res = model_in.predict(combined_features)
    print('predicted_res',predicted_res)

    return {
        'prediction':'Very late',
        'on_time_chance':15,
        'a_little_late_chance':25,
        'really_late_chance':100-15-25
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
