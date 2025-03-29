"""
# My first app
Here's our first attempt at using data to create a table:
"""

import streamlit as st
import pandas as pd
import pydeck as pdk
import datetime
import numpy as np

# Data!
df = pd.read_csv('tooltip_data.csv')
flight_list_data = pd.read_csv("flight_list.csv")

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
# top_50 = df.sample(n=50)
# df = df[df['AIRPORT'].isin(top_50['AIRPORT'].values) | (df['DISPLAY_AIRPORT_NAME'].isin(['Hartsfield-Jackson Atlanta International']))]


# Enable wide layout
st.set_page_config(layout="wide")

# Session State setup
# search clicked
if "search_clicked" not in st.session_state:
    st.session_state.search_clicked = False


# calculate the center of the map
mid_lat = df['LATITUDE'].mean()
mid_long = df['LONGITUDE'].mean()

# define the tooltip
tooltip = {
    "html": "<b>Airport:</b> {DISPLAY_AIRPORT_NAME}<br>"
            "<b>City:</b> {DISPLAY_CITY_MARKET_NAME_FULL}<br>"
            "<b>State:</b> {AIRPORT_STATE_NAME}<br>"
            "<b># of Flights:</b> {count_fights}<br>"
            "<b>Late %:</b> {late_prob}<br>"
            "<b>Average Arrival Delay:</b> {arrdelay_mean}",
    "style": {
        "backgroundColor": "steelblue",
        "color": "white"
    }
}

# get the airport code lists for later
flight_list = list(flight_list_data['flight_number'])

# create columns to represent the width of the screen.
col1, col2 = st.columns([3,2])

# left part of the screen
with col1:
    st.container()

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

    # top right part which is for the search
    with st.expander("Search",expanded=True):

        flight_date = st.date_input("Flight date", datetime.date.today())
        flight_start_location = st.selectbox(
            "Flight Number",
            flight_list,
            index=None,
            placeholder="Search for a flight..."
        )
        search_button = st.button("Search")
        if search_button:
            st.session_state.search_clicked = True

    if search_button:

        # bottom right part for the results
        with st.expander("Results",expanded=True):
            # these are all hard coded and will be replated with stuff from the models
            prediction = "A little Late"
            color = 'orange'
            on_time_chance = 15
            a_little_late_chance=65
            really_late_chance = 100-a_little_late_chance-on_time_chance
            reason_list = ['reason_1','reason_2','reason_3']


            st.markdown(f"""
                <style>
                .prediction-wrapper {{
                    text-align: center;
                    position: relative;
                    margin-bottom: 24px;
                }}

                .prediction-box {{
                    border: 2px solid #ccc;
                    border-radius: 12px;
                    padding: 16px;
                    text-align: center;
                    font-size: 20px;
                    color: #333;
                    background-color: {color};
                    transition: background-color 0.3s ease;
                    width: fit-content;
                    display: inline-block;
                    margin: 0 auto;
                    position: relative;
                }}

                .prediction-box:hover {{
                    background-color: #e0f0ff;
                    cursor: pointer;
                }}

                .tooltip-text {{
                    visibility: hidden;
                    background-color: #555;
                    color: #fff;
                    text-align: center;
                    border-radius: 6px;
                    padding: 5px;
                    position: absolute;
                    z-index: 1;
                    bottom: 125%;
                    left: 50%;
                    transform: translateX(-50%);
                    opacity: 0;
                    transition: opacity 0.3s;
                    width: max-content;
                    max-width: 200px;
                    width: max-content;
                    max-width: 320px;
                }}

                .prediction-box:hover .tooltip-text {{
                    visibility: visible;
                    opacity: 1;
                }}
                </style>

                <div class="prediction-wrapper">
                    <div class="prediction-box">
                        <div class="tooltip-text">
                            Chance of being on time: {on_time_chance}%<br>
                            Chance of being a little late: {a_little_late_chance}%<br>
                            Chance of being very late: {really_late_chance}%
                        </div>
                        <strong>{prediction}</strong>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # add in the section for the reasons
            # make the columns for the search area
            col_list = st.columns(np.ones(len(reason_list)))
            counter = 0
            for col in col_list:
                loop_reason = reason_list[counter]
                counter = counter + 1

                with col:
                    st.container()

                    # add in the box
                    st.markdown(f"""
                    <style>
                    .reason-wrapper {{
                        text-align: center;
                        position: relative;
                    }}

                    .reason-box {{
                        border: 2px solid #ccc;
                        # border-radius: 12px;
                        # padding: 16px;
                        text-align: center;
                        # font-size: 20px;
                        # color: #333;
                        # transition: background-color 0.3s ease;
                        # width: fit-content;
                        # display: inline-block;
                        # margin: 0 auto;
                        # position: relative;
                    }}


                    .prediction-box:hover .tooltip-text {{
                        visibility: visible;
                        opacity: 1;
                    }}
                    </style>

                    <div class="reason-wrapper">
                        <div class="reason-box">
                            <strong>{loop_reason}</strong>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)