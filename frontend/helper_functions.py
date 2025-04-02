

import pydeck as pdk
import streamlit as st
import pandas as pd
import numpy as np
import datetime
import model_things

def draw_map(tool_tip_data_df, mid_lat, mid_long):
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
            get_color=[0, 0, 0],
            get_width=5
        )
        map_layers.append(line_layer)

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


def handle_search(flight_list_data, tool_tip_data_df, flight_list):
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

        # call the model
        model = model_things.load_model()
        model_inputs = model_things.get_model_inputs(flight_number = selected_flight)
        model_prediction = model_things.get_prediction(model, model_inputs)


def show_results():
    # get values from the session state
    prediction= st.session_state.prediction
    on_time_chance = st.session_state.on_time_chance
    really_late_chance = st.session_state.really_late_chance
    a_little_late_chance = st.session_state.a_little_late_chance
    reason_list = st.session_state.reason_list
    # lookup the correct color based on the prediction
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