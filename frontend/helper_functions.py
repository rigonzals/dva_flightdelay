

import pydeck as pdk
import streamlit as st
import pandas as pd
import datetime
import requests
import ast
import altair as alt



def draw_map(tool_tip_data_df, mid_lat, mid_long):
    map_layers = [
        pdk.Layer(
            "ScatterplotLayer",
            data=tool_tip_data_df,
            get_position=["LONGITUDE", "LATITUDE"],
            get_color=[64, 89, 168, 160],
            get_radius=25000,
            pickable=True
        )
    ]
    # Add the line layer if the search has been clicked
    if st.session_state.get("search_clicked", False) and "route_data" in st.session_state:
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
            "backgroundColor": "#4059A8",
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
    today = datetime.date.today()
    max_date = today + datetime.timedelta(days=90)
    col1, col2 = st.columns(2)
    with col1:
        flight_date = st.date_input(
            "Flight date",
            datetime.date.today(),
            max_value=max_date)
    with col2:
        flight_time = st.time_input(
            "Flight time",
            datetime.time(9, 0))
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
        st.session_state.flight_date = flight_date
        st.session_state.flight_time = flight_time
        st.session_state.airline = flight_start_location.split(' ')[0]


        # get the flight information and route to show on the map
        selected_flight = flight_start_location
        searched_flight_data = flight_list_data[flight_list_data['flight_number'] == selected_flight]
        origin_airport_code = searched_flight_data['origin'].values[-1]
        dest_airport_code = searched_flight_data['dest'].values[-1]

        origin_airport = tool_tip_data_df[tool_tip_data_df['AIRPORT'] == origin_airport_code].iloc[0]
        dest_airport = tool_tip_data_df[tool_tip_data_df['AIRPORT'] == dest_airport_code].iloc[0]

        st.session_state.origin_airport_code = origin_airport_code
        st.session_state.destination_airport_code = dest_airport_code

        route_data = pd.DataFrame([{
            "from_lon": origin_airport["LONGITUDE"],
            "from_lat": origin_airport["LATITUDE"],
            "to_lon": dest_airport["LONGITUDE"],
            "to_lat": dest_airport["LATITUDE"]
        }])
        st.session_state.route_data = route_data
        # reload the screen
        st.rerun()
    elif st.session_state.get("search_clicked", False) and "route_data" not in st.session_state:
        st.session_state.search_clicked = False

def get_prediction(flight_date, flight_time, airline_code, origin, destination):
    """call the model and save it to the state"""
    model_results = requests.get(
        "http://localhost:5000/",
        params={
        "airline_code":airline_code,
        "flight_date": flight_date,
        "flight_time": flight_time,
        "airline":airline_code,
        "origin": origin,
        "destination": destination,
    },timeout = 600)
    model_results_dict = ast.literal_eval(model_results.text)
    st.session_state.prediction = model_results_dict['prediction']
    st.session_state.on_time_chance = model_results_dict['on_time_chance']
    st.session_state.really_late_chance = model_results_dict['really_late_chance']
    st.session_state.a_little_late_chance = model_results_dict['a_little_late_chance']


def tooltip(text, tip):
    return f'{text} <span title="{tip}">ℹ️</span>'


def show_results():
    # get values from the session state
    get_prediction(
        flight_date = st.session_state.get('flight_date'),
        flight_time = st.session_state.get('flight_time'),
        airline_code = st.session_state.get('airline'),
        origin = st.session_state.get('origin_airport_code'),
        destination = st.session_state.get('destination_airport_code')
    )
    prediction= st.session_state.prediction
    on_time_chance = st.session_state.on_time_chance
    really_late_chance = st.session_state.really_late_chance
    a_little_late_chance = st.session_state.a_little_late_chance
    # lookup the correct color based on the prediction
    image_path = 'ontime.png'

    if prediction == 'A little Late':
        image_path = 'late.png'
    elif prediction == 'Very late':
        image_path = 'very_late.png'

    results_col1, results_col2 = st.columns([2,1])
    with results_col1:
        # Sample data
        data = pd.DataFrame({
            'Labels': ['On Time', 'Late', 'Very Late'],
            'Chance': [on_time_chance, a_little_late_chance, really_late_chance],
            'ToolTip':['<15 min late','15-45 min late','45+ min late']
        })
        data = data.sort_values(by='Chance', ascending=False)

        # data.sort_values('Chance',inplace=True)
        chart = alt.Chart(data).mark_bar(color='#4059A8').encode(
            y=alt.Y('Labels', title=''),
            x='Chance',
            tooltip=['Labels', 'Chance', 'ToolTip']
        ).properties(
            width=600,
            height=150
        )

        st.altair_chart(chart, use_container_width=True)
    with results_col2:
        st.image(image_path)


def add_header():
    st.image("logo_with_text.png", width=400)

def add_footer():

    footer_images = ["gatech_logo.png",
                     "clouds_only.png",
                     "clouds_only.png",
                     "clouds_only.png",
                     "clouds_only.png",
                     "clouds_only.png",
                     "clouds_only.png",
                     "clouds_only.png"]

    width_list = [50,250,250,250,250,250,250,250]

    with st.container():
        cols = st.columns(len(footer_images))  # Create columns based on number of images

        for idx, col in enumerate(cols):
            w = width_list[idx]
            with col:
                st.image(footer_images[idx], width=w)  # Adjust the width as needed
