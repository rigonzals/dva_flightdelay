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
# Pickles!


# what are the attributes?
# if hasattr(model, 'feature_names_in_'):
#     print('features', model.feature_names_in_)

def load_model():
    """This function reads from the file and loads the model"""
    # with open('/Users/Santosha/Documents/GitHub/dva_flightdelay/data/gradient_boost_model.pkl','rb') as file:
    # model = pickle.load(file)
    model = 1
    return model


def get_model_inputs(flight_number):
    """Look up all of the required model inputs and put them into a dictionary"""
    return {}

def get_prediction(model, model_inputs):
    """call the prediction of the model and set the state variables"""
    st.session_state.prediction = 'A little Late'
    st.session_state.on_time_chance = 15
    st.session_state.a_little_late_chance = 65
    st.session_state.really_late_chance = 100-st.session_state.a_little_late_chance -st.session_state.on_time_chance
    st.session_state.reason_list = ['reason_1','reason_2','reason_3']