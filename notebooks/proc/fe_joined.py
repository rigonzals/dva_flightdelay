# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: -all
#     custom_cell_magics: kql
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.11.2
#   kernelspec:
#     display_name: genv
#     language: python
#     name: python3
# ---

# %%
import polars as pl
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

def shift_date(date_str, days=0, months=0, years=0, date_format="%Y-%m-%d"):
    """
    Shifts a given date by the specified number of days, months, and years.
    
    :param date_str: The original date as a string (formatted as YYYY-MM-DD by default)
    :param days: Number of days to shift (positive or negative)
    :param months: Number of months to shift (positive or negative)
    :param years: Number of years to shift (positive or negative)
    :param date_format: Format of the input and output date string
    :return: Shifted date as a string
    """
    original_date = datetime.strptime(date_str, date_format)
    shifted_date = original_date + relativedelta(days=days, months=months, years=years)
    return shifted_date.strftime(date_format)

# %%
path_raw = "../../data/"
path_proc = "../../outputs/proc/"

fe_type = "flight"

# %%
for col in [
     "FlightDate", 
    "CRSDepTime",
    "DepDelay",
    "ActualElapsedTime",
    "ArrDelay"
]:

    print(col.lower())

# %%
cols_unique_key = ["unique_key"]

dic_cols_fe = {
  "time": [
    "flightdate",
    "crsdeptime",
    "depdelay",
    "actualelapsedtime",
    "arrdelay",
],
"flight":[
  "origin",
  "originstatename",
  "dest",
  "deststatename",
  "distance",
  "operating_airline",
  "originstate",
  "airport",
],
"stats":[
      "rank",
      'air_safety__general_aviation_fatalities',
      'us_airline_traffic__total__seasonally_adjusted',
      'us_airline_traffic__international__seasonally_adjusted',
      'us_airline_traffic__domestic__seasonally_adjusted',
      'state_and_local_government_construction_spending__conservation_and_development',
      'state_and_local_government_construction_spending__lighting',
      'state_and_local_government_construction_spending__power',
      'state_and_local_government_construction_spending__air_passenger_terminal',
      'state_and_local_government_construction_spending__air',
      'state_and_local_government_construction_spending__transportation',
      'state_and_local_government_construction_spending__other_public_safety',
      'state_and_local_government_construction_spending__infrastructure',
      'highway_fuel_price__onhighway_diesel',
      'highway_fuel_price__regular_gasoline',
      'transportation_employment__air_transportation',
      'personal_spending_on_transportation__transportation_services__seasonally_adjusted',
      'personal_spending_on_transportation__gasoline_and_other_energy_goods__seasonally_adjusted',
      'personal_spending_on_transportation__motor_vehicles_and_parts__seasonally_adjusted',
      'unemployment_rate__seasonally_adjusted',
      'labor_force_participation_rate__seasonally_adjusted',
      'unemployed__seasonally_adjusted',
      'real_gross_domestic_product__seasonally_adjusted',
      'transportation_services_index__freight',
      'transportation_services_index__passenger',
      'transportation_services_index__combined',
      'air_safety__air_taxi_and_commuter_fatalities',
      'air_safety__air_carrier_fatalities',
      'us_air_carrier_cargo_millions_of_revenue_tonmiles__international',
      'us_air_carrier_cargo_millions_of_revenue_tonmiles__domestic',
      'us_airline_traffic__total__non_seasonally_adjusted',
      'us_airline_traffic__international__non_seasonally_adjusted',
      'us_airline_traffic__domestic__non_seasonally_adjusted',
      'us_marketing_air_carriers_ontime_performance_percent',
      'unemployment_rate__seasonally_adjusted',
      'labor_force_participation_rate__seasonally_adjusted',
      'unemployed__seasonally_adjusted',
      'real_gross_domestic_product__seasonally_adjusted',
      'transportation_services_index__freight',
      'transportation_services_index__passenger',
      'transportation_services_index__combined',
      'air_safety__air_taxi_and_commuter_fatalities',
      'air_safety__air_carrier_fatalities',
      'us_air_carrier_cargo_millions_of_revenue_tonmiles__international',
      'us_air_carrier_cargo_millions_of_revenue_tonmiles__domestic',
      'us_airline_traffic__total__non_seasonally_adjusted',
      'us_airline_traffic__international__non_seasonally_adjusted',
      'us_airline_traffic__domestic__non_seasonally_adjusted',
      'us_marketing_air_carriers_ontime_performance_percent',
      'year_right',
      'avionics_technicians',
      'aircraft_mechanics_and_service_technicians',
      'aircraft_structure_surfaces_rigging_and_systems_assemblers',
      'aircraft_cargo_handling_supervisors',
      'airline_pilots_copilots_and_flight_engineers',
      'commercial_pilots',
      'air_traffic_controllers',
      'airfield_operations_specialists',
      'flight_attendants',
      'transportation_attendants_except_flight_attendants',
      'aircraft_service_attendants_and_transportation_workers_all_other',
      ]
}

# %% [markdown]
# # 1. Data

# %%
dt_year = 2019
dt_ini = f"{dt_year}-01-01"
dt_prev = shift_date(dt_ini, years=-1)
dt_year_prev = dt_prev[:4]
years = [dt_year_prev, dt_year]
years


# %%
# Yearly labor statistics
df_joined = pl.DataFrame()
for year in years:
    try:
        path = f'{path_proc}{year}_join_datasets.parquet'
        df_joined = pl.concat([df_joined, pl.read_parquet(path)], how="diagonal")
    except: 
        print(f"Couldn't find data for year {year}")

# %%
df_joined.shape

# %%


# %% [markdown]
# # 2. Processing

# %%
df_joined.shape, df_joined["unique_key"].n_unique()

# %%
df_joined.columns[100:120]

# %%
df_joined.select( 'avionics_technicians',
 'aircraft_mechanics_and_service_technicians',
 'aircraft_structure_surfaces_rigging_and_systems_assemblers',
 'aircraft_cargo_handling_supervisors')

# %%
null_percentages = df_joined.select([
    ((pl.col(c).is_null().sum() / df_joined.height) * 100).alias(c + "_null_percentage")
    for c in df_joined.columns
])

# Sort the null percentages in descending order (highest null percentage first)
null_percentages_sorted = null_percentages.to_pandas().transpose().sort_values(0, ascending=False)

#display(null_percentages_sorted.iloc[:20])
#display(null_percentages_sorted.iloc[20:40])
display(null_percentages_sorted.iloc[0:30])

# %%



