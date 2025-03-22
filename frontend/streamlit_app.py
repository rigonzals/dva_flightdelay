"""
# My first app
Here's our first attempt at using data to create a table:
"""

import streamlit as st
import pandas as pd
import pydeck as pdk
import datetime


df = pd.read_csv('Airport_Location_Data.csv')

# filter the data to just the united states
df = df[df['AIRPORT_COUNTRY_NAME']=='United States']

# filtering out the airports in the territories and non-continental us
df = df[(~df['AIRPORT_STATE_NAME'].isin([
    'U.S. Pacific Trust Territories and Possessions',
    'U.S. Virgin Islands',
    'Puerto Rico',
    'Alaska',
    'Hawaii'
    ]))]



# filter out closed airporst
df = df[df['AIRPORT_IS_CLOSED']==0]

# filter to just the top 50 airports - THIS SHOULD PROBABLY BE REMOVED LATER?
top_50 = df.sample(n=50)
df = df[df['AIRPORT'].isin(top_50['AIRPORT'].values) | (df['DISPLAY_AIRPORT_NAME'].isin(['Hartsfield-Jackson Atlanta International']))]


print(top_50)

# Enable wide layout
st.set_page_config(layout="wide")

# calculate the center of the map
mid_lat = df['LATITUDE'].mean()
mid_long = df['LONGITUDE'].mean()

# create columns to represent the width of the screen.
col1, col2 = st.columns([3,2])

# define the tooltip
tooltip = {
    "html": "<b>Airport:</b> {DISPLAY_AIRPORT_NAME}<br>"
            "<b>City:</b> {DISPLAY_CITY_MARKET_NAME_FULL}<br>"
            "<b>State:</b> {AIRPORT_STATE_NAME}",
    "style": {
        "backgroundColor": "steelblue",
        "color": "white"
    }
}

# get the airport code lists for later
airport_code_list = list(set(df["AIRPORT"]))
airport_code_list.sort()

# left part of the screen
with col1:
    st.container()
    st.write("This is inside the wide container")

    # st.map(df[["LATITUDE","LONGITUDE"]].dropna())
    st.pydeck_chart(pdk.Deck(
        map_style = "mapbox://styles/mapbox/light-v9",
        initial_view_state= pdk.ViewState(
            latitude=mid_lat,
            longitude=mid_long,
            zoom=3,
            pitch=0
        ),
        layers=[
            pdk.Layer(
                "ScatterplotLayer",
                data=df,
                get_position=["LONGITUDE","LATITUDE"],
                get_color=[0, 0, 255, 160],
                get_radius=25000,
                pickable=True
            )
        ],
        tooltip=tooltip
    ))

# make the columns for the search area
search_col1, search_col2, search_col3 = st.columns([1,1,1])

# Right part of the screen
with col2:
    st.container()
    st.write("this is the smaller container")

    # top right part which is for the search
    with st.expander("Search",expanded=True):
        st.write("this is the top")

        flight_date = st.date_input("Flight date", datetime.date.today())
        flight_start_location = st.selectbox(
            "Origin",
            airport_code_list,
            index=None,
            placeholder="Search for an airport..."
        )
        flight_end_location = st.selectbox(
            "Destination",
            airport_code_list,
            index=None,
            placeholder="Search for an airport..."
        )
        st.button("Search")

    # bottom right part for the results
    with st.expander("Results",expanded=True):
        st.write("this is the bottom")