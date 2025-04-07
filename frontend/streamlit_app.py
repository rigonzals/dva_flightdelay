"""
# My first app
Here's our first attempt at using data to create a table:
"""

import streamlit as st
import pandas as pd

# import model_things
from helper_functions import draw_map, handle_search, show_results, add_footer,add_header
st.set_page_config(layout="wide", page_title="Flight Prediction App", page_icon="✈️")


# Add the header and footer
add_header()

# these are all hard coded and will be replated with stuff from the models
st.session_state.prediction = 'A little Late'
st.session_state.on_time_chance = 15
st.session_state.a_little_late_chance = 65
st.session_state.really_late_chance = 100-st.session_state.a_little_late_chance -st.session_state.on_time_chance

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

# search clicked
if "search_clicked" not in st.session_state:
    st.session_state.search_clicked = False

# calculate the center of the map
mid_lat = tool_tip_data_df['LATITUDE'].mean()
mid_long = tool_tip_data_df['LONGITUDE'].mean()

# get the airport code lists for later
flight_list = list(set(flight_list_data['flight_number']))
flight_list.sort()

#===============================================================================
# Screen setup
#===============================================================================

# create columns to represent the width of the screen.
col1, col2 = st.columns([3,2])
#=========================
# left part of the screen
#=========================
with col1:
    st.container()

    # create the map
    draw_map(
        tool_tip_data_df=tool_tip_data_df,
        mid_lat=mid_lat,
        mid_long=mid_long)

# make the columns for the search area
search_col1, search_col2, search_col3 = st.columns([1,1,1])
#=========================
# Right part of the screen
#=========================
with col2:
    st.container()

    # top right part which is for the search
    with st.expander("Search",expanded=True):
         handle_search(flight_list_data, tool_tip_data_df, flight_list)

    # if seach button is clicked, then we will show the results sections and the line on the map
    if st.session_state.get("search_clicked", False) and "route_data" in st.session_state:
        # bottom right part for the results
        with st.expander("Results",expanded=True):
            # show the results section
            show_results()

            # force the screen to refresh so the line shows
            st.rerun()
add_footer()