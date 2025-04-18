
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
    # drop flight_info columns that are in date_dimensions_in
    flight_info.drop(columns=[
        'DayShort','isUSA_Holiday','isUSA_Workingday','isLongweekend','MonthPart','DatePart','YearPart','FirstDayofMonth'],
        inplace=True)

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

    # get the original model columns for comparison
    model_columns_data = pd.read_csv('data_for_columns.csv')

    # check for missing columns
    combined_features = combined_features.loc[:, ~combined_features.T.duplicated()]
    missing_columns = [x for x in model_columns_data.columns if x not in combined_features.columns]
    missing_columns = list(missing_columns)
    missing_columns.sort()
    for col in missing_columns:
        combined_features[col] = False


    combined_features = combined_features[list(model_columns_data.columns)]
    col_names = list(combined_features.columns)
    col_names.sort()

    combined_features.to_csv('combined_features.csv')


    # call the model
    predicted_res = model_in.predict(combined_features)
    predict_proba_res= model_in.predict_proba(combined_features)

    late_prob = int(predict_proba_res[0][0]*100)
    on_time_prob = int(predict_proba_res[0][1]*100)
    very_late_prob = int(predict_proba_res[0][2]*100)

    return {
        'prediction':predicted_res[0],
        'on_time_chance':on_time_prob,
        'a_little_late_chance':late_prob,
        'really_late_chance':very_late_prob
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
