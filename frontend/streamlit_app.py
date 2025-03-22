"""
# My first app
Here's our first attempt at using data to create a table:
"""

import streamlit as st
import pandas as pd
import pydeck as pdk
import datetime


df = pd.read_csv('Airport_Location_Data.csv')

# filter