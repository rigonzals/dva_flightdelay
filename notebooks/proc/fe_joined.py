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

# %% [markdown]
# # 0. Config

# %%
path_raw = "../../data/"
path_proc = "../../outputs/proc/"
path_fe = "../../outputs/fe/"

fe_type = "stats"#"flight" # "time" #

dt_year = 2021
dt_ini = f"{dt_year}-01-01"
if fe_type == "time":
    dt_prev = shift_date(dt_ini, years=-1)
    dt_year_prev = dt_prev[:4]
    years = [dt_year_prev, dt_year]
else:
    years = [dt_year]

years

# %%
cols_unique_key = ["unique_key"]

dic_cols_fe = {
  "time": [
    "flightdate",
    "crsdeptime",
    "depdelay",
    "actualelapsedtime",
    "arrdelay",
    "airline",
    "origin",
     "dest",
],
"flight":[
  "origin",
 # "originstatename",
  "dest",
  #"deststatename",
  "distance",
  "operating_airline",
  "originstate",
  "deststate",
#  "airport",
"airline",
"typeeng_2",
"typeeng_4",
"typeeng_5",
"accat_1",
"accat_2",	
"accat_3",	
"noeng",	
"noseats",	
"acweight_class_1",	
"acweight_class_2",	
"acweight_class_3",	
"acweight_class_4",
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
    #  'transportation_attendants_except_flight_attendants',
      'aircraft_service_attendants_and_transportation_workers_all_other',
    #  "aircraft_service_attendants",
      ]
}
list_cols_use = cols_unique_key + dic_cols_fe[fe_type]

list_cols_use

# %% [markdown]
# # 1. Data

# %%
for col in list_cols_use:
    print(col)
    path = f'{path_proc}{dt_year}_join_datasets.parquet'
    pl.read_parquet(path, columns=[col])

# %%
# Yearly labor statistics
df_joined = pl.DataFrame()
for year in years:
    try:
        path = f'{path_proc}{year}_join_datasets.parquet'
        df_joined = pl.concat([df_joined, pl.read_parquet(path,
                                                          columns=list_cols_use)], how="diagonal")
    except: 
        print(f"Couldn't find data for year {year}")

# %%
nunique_counts = df_joined.select([
    pl.col(c).n_unique().alias(c + "_nunique") for c in df_joined.columns
])

# View the result
print(nunique_counts)

# %%
df_joined

# %%
df_joined.shape, df_joined["unique_key"].n_unique()


# %% [markdown]
# # 2. Processing

# %%
def agg_timedelta_features(df_joined, cols_agg, feature_name, n_days, metric_agg):
    """ 
    Create time agg features
    """
    
    unique_months = df_joined.filter(pl.col("flightdate").str.contains(dt_year)).select("month").unique().to_series().to_list()

    results = []

    for month in unique_months:
        
        start_date = month - timedelta(days=n_days)  # 3 months before the month start
        end_date = month + timedelta(days=31)  # Include full month

        # Filter only relevant flights (reduce data size before joining)
        df_current = df_joined.lazy().filter((pl.col("flightdate_obj") >= month) & (pl.col("flightdate_obj") <= end_date))
        df_past = df_joined.lazy().filter((pl.col("flightdate_obj") >= start_date) & (pl.col("flightdate_obj") < end_date)).rename({"flightdate_obj": "past_date",
                                                                                                                                     "arrdelay": "past_arrdelay"})

        rolling_avg = (
            df_past.select(cols_agg + ["past_arrdelay", "past_date"])
            .join(df_current.select(cols_agg + ["flightdate_obj"]), on=cols_agg, how="inner")
            .filter( (pl.col("past_date") <= (pl.col("flightdate_obj") - pl.duration(days=1) ) ) &  # Only past flights
                    (pl.col("past_date") >= (pl.col("flightdate_obj") - pl.duration(days=n_days) ) ) )  # Exclude same day
            .group_by(cols_agg + ["flightdate_obj"])
            #.agg(pl.col("past_arrdelay").mean().alias(f"{feature_name}_last_{n_days}d"))
            .agg(metric_agg.alias(f"{feature_name}_last_{n_days}d"))
        ).collect()
        
        # Merge with current month's data
        #df_month_result = df_current.join(rolling_avg, on=cols_agg + ["flightdate_obj"], how="left").collect()
        print(month, rolling_avg.shape)
        results.append(rolling_avg)

    # Combine all months
    return pl.concat(results).unique(subset=cols_agg + ["flightdate_obj"], keep="first")#.select("unique_key", f"{feature_name}_last_{n_days}d")


# %%
if fe_type == "flight":

    list_to_numeric = [
      "distance",
      "typeeng_2",
      "typeeng_4",
      "typeeng_5",
      "accat_1",
      "accat_2",	
      "accat_3",	
      "noeng",	
      "noseats",	
      "acweight_class_1",	
      "acweight_class_2",	
      "acweight_class_3",	
      "acweight_class_4",]
    df_joined = df_joined.with_columns([  pl.col(c).cast(pl.Float32).alias(c) for c in list_to_numeric])

    list_dummify = ["originstate","deststate","operating_airline"] #"origin", "dest",
    df_dummies = df_joined.select(list_dummify).to_dummies()
    df_joined = pl.concat([df_joined.select(["unique_key"] + list_to_numeric), df_dummies], how="horizontal")


    print(df_joined.shape, df_joined["unique_key"].n_unique())

elif fe_type == "stats":
    list_to_numeric = [   
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
    #  'transportation_attendants_except_flight_attendants',
      'aircraft_service_attendants_and_transportation_workers_all_other',
     # "aircraft_service_attendants"
      ]
        
    df_joined = df_joined.with_columns([  pl.col(c).cast(pl.Float32).alias(c) for c in list_to_numeric])
    print(df_joined.shape, df_joined["unique_key"].n_unique())

elif fe_type == "time":
    # pending for recency and money features to be created
    df_joined = df_joined.with_columns( month=pl.col("flightdate").str.slice(5, 2).cast(pl.Int32),
                                        day=pl.col("flightdate").str.slice(8, 2).cast(pl.Int32))
    list_to_numeric = ["crsdeptime"]
    df_joined = df_joined.with_columns([  pl.col(c).cast(pl.Int32).alias(c) for c in list_to_numeric])

    df_joined = df_joined.with_columns(pl.col("flightdate").cast(pl.Date).alias("flightdate_obj"))
    df_joined = df_joined.with_columns(pl.col("flightdate_obj").dt.truncate("1mo").alias("month"))

    # average route delay last month
    df_fe =  agg_timedelta_features(df_joined, cols_agg=["origin","dest"], feature_name="avg_delay_route", n_days=30, metric_agg=pl.col("past_arrdelay").mean())

    df_joined = df_joined.join(df_fe, on=["origin","dest","flightdate_obj"], how="left")


    # average airline_dest  delay last 14days
    df_fe =  agg_timedelta_features(df_joined, cols_agg=["airline", "dest"], feature_name="avg_delay_airline_dest", n_days=14, metric_agg=pl.col("past_arrdelay").mean())


    df_joined = df_joined.join(df_fe, on=["airline","dest","flightdate_obj"], how="left")


    # Number of departing and arriving flights to/from airport
    #df_fe =  agg_timedelta_features(df_joined, cols_agg=["origin"], feature_name="count_flights_origin", n_days=7, metric_agg=pl.col("origin").count())

    # ratio arriving vs departure at airport last week vs month
    print(df_joined.shape, df_joined["unique_key"].n_unique())

    df_joined = df_joined.filter(pl.col("flightdate").str.contains(dt_year)).select(["unique_key", "month", "day", "crsdeptime", "avg_delay_route_last_30d", "avg_delay_airline_dest_last_14d"])

    


# %% [markdown]
# # 3. Export

# %%
df_joined.shape

# %%
df_joined.head(4)

# %%
df_joined.write_parquet(f"{path_fe}{dt_year}_fe_{fe_type}.parquet", compression="snappy")

# %% [markdown]
# # Check
#

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
