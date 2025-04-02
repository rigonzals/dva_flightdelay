"""
# My first app
Here's our first attempt at using data to create a table:
"""

import streamlit as st
import pandas as pd
import pydeck as pdk
import datetime
import numpy as np

# these are all hard coded and will be replated with stuff from the models
prediction = "A little Late"
on_time_chance = 15
a_little_late_chance=65
really_late_chance = 100-a_little_late_chance-on_time_chance
reason_list = ['reason_1','reason_2','reason_3']
dest_airport_code = 'ATL'
origin_airport_code = 'JFK'

# Data!
tool_tip_data_df = pd.read_csv('tooltip_data.csv')
flight_list_data = pd.read_csv("flight_list.csv")

# filter the data to just the united states
tool_tip_data_df = tool_tip_data_df[tool_tip_data_df['AIRPORT_COUNTRY_NAME']=='United States']

# filtering out the airports in the territories and non-continental us
tool_tip_data_df = tool_tip_data_df[(~tool_tip_data_df['AIRPORT_STATE_NAME'].isin([
    'U.S. Pacific Trust Territories and Possessions',
    'U.S. Virgin Islands',
    'Puerto Rico',
    'Alaska',
    'Hawaii'
    ]))]

# filter out closed airporst
tool_tip_data_df = tool_tip_data_df[tool_tip_data_df['AIRPORT_IS_CLOSED']==0]

# Enable wide layout
st.set_page_config(layout="wide")

# Session State setup
# search clicked
if "search_clicked" not in st.session_state:
    st.session_state.search_clicked = False

# calculate the center of the map
mid_lat = tool_tip_data_df['LATITUDE'].mean()
mid_long = tool_tip_data_df['LONGITUDE'].mean()

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
flight_list = list(set(flight_list_data['flight_number']))
flight_list.sort()


# create columns to represent the width of the screen.
col1, col2 = st.columns([3,2])

# left part of the screen
with col1:
    st.container()

    # create the map
    map_layers = [
        pdk.Layer(
            "ScatterplotLayer",
            data=tool_tip_data_df,
            get_position=["LONGITUDE", "LATITUDE"],
            get_color=[0, 0, 255, 160],
            get_radius=25000,
            pickable=True
        )
    ]
    # Add the line layer if the search has been clicked
    if st.session_state.get("search_clicked", False) and "route_data" in st.session_state:
        print('session state trigger', 92)
        line_layer = pdk.Layer(
            "LineLayer",
            data=st.session_state.route_data,
            get_source_position="[from_lon, from_lat]",
            get_target_position="[to_lon, to_lat]",
            get_color=[255, 0, 0],  # Red line
            get_width=5
        )
        map_layers.append(line_layer)

    st.pydeck_chart(pdk.Deck(
        map_style = "mapbox://styles/mapbox/light-v9",
        initial_view_state= pdk.ViewState(
            latitude=mid_lat,
            longitude=mid_long,
            zoom=3,
            pitch=0
        ),
        layers=map_layers,
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
            st.session_state.selected_flight = flight_start_location

            # get the flight information and route to show on the map
            selected_flight = flight_start_location
            print('selected_flight',selected_flight)
            searched_flight_data = flight_list_data[flight_list_data['flight_number'] == selected_flight]
            origin_airport_code = searched_flight_data['origin'].values[-1]
            dest_airport_code = searched_flight_data['dest'].values[-1]

            origin_airport = tool_tip_data_df[tool_tip_data_df['AIRPORT'] == origin_airport_code].iloc[0]
            dest_airport = tool_tip_data_df[tool_tip_data_df['AIRPORT'] == dest_airport_code].iloc[0]

            route_data = pd.DataFrame([{
                "from_lon": origin_airport["LONGITUDE"],
                "from_lat": origin_airport["LATITUDE"],
                "to_lon": dest_airport["LONGITUDE"],
                "to_lat": dest_airport["LATITUDE"]
            }])
            st.session_state.route_data = route_data


    # if seach button is clicked, then we will show the results sections and the line on the map
    if st.session_state.get("search_clicked", False) and "route_data" in st.session_state:
        # bottom right part for the results
        with st.expander("Results",expanded=True):

            # lookup the correct color based on the prediction
            prediction = 'Very late'
            RESULTS_COLOR = 'LightGreen'
            if prediction == 'A little Late':
                RESULTS_COLOR = 'LemonChiffon'
            elif prediction == 'Very late':
                RESULTS_COLOR = 'Salmon'

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
                    background-color: {RESULTS_COLOR};
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
                        margin-bottom: 24px;
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

            st.rerun()
