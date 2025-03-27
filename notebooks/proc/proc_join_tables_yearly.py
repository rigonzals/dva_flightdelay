#!/usr/bin/env python
# coding: utf-8
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


# %% [markdown]
# # 0. Functions

# %%
## Function to read in and convert columns of the ACFTREF_20XX.txt
def read_ACFT(filepath):
    # read in the dataframe
    df = pl.read_csv(filepath
                , ignore_errors = True
                , infer_schema = False
                , quote_char = None)
    #cast number columns to int and manipulate some string columns to get rid of leading and trailing spaces
    df = df.with_columns(pl.col('MODEL').str.strip_chars()
                        , pl.col('CODE').str.strip_chars()
                        , pl.col('TYPE-ENG').str.strip_chars()
                        , pl.col('NO-ENG').cast(pl.UInt32)
                        , pl.col('NO-SEATS').cast(pl.UInt32))

    # get rid of what I am assuming are test rows
    df = df.filter(pl.col('MODEL')!= 'UNKNOWN')

    #select the neccesary columns
    df = df.select(['CODE'
                   , 'MODEL'    #we might be able to drop this one
                   , 'TYPE-ENG'
                   , 'AC-CAT'
                   , 'NO-ENG'
                   , 'NO-SEATS'
                   , 'AC-WEIGHT'])

    #get rid of engine types that are clearly not commercial aircraft
    df = df.filter(df['TYPE-ENG'].is_in(['2'    #turboprop
                                       , '4'   #turbo jet
                                       , '5'   #turbo fan
                                        ]))

    #for categorical variables let's create some dummies
    df = df.to_dummies(['TYPE-ENG'
                        , 'AC-CAT'
                        , 'AC-WEIGHT'])

    new_columns = [clean_name(col) for col in df.columns]

    df.columns = new_columns
    
    return df


# function to read in the master file
def read_master(filepath):
    #read in the filepath
    df = pl.read_csv(filepath
                , ignore_errors = True
                , infer_schema = False
                , quote_char = None)
    #keep only the columns that we need to join the aircraft ref files
    df = df.select(['N-NUMBER'
                   , 'MFR MDL CODE'])

    new_columns = [clean_name(col) for col in df.columns]

    df.columns = new_columns

    return df

import re

def clean_name(name: str) -> str:
    name = name.lower()  # Convert to lowercase
    name = re.sub(r"[^a-z0-9_ ]", "", name)  # Remove special characters
    name = name.replace(" ", "_")  # Replace spaces with underscores
    return name
#function to read in the labor statistics data
def read_labor_stats(filepath):
    #get year from the filepath name
    year = int(filepath.split('.xlsx')[0][-4:])
    
    #read in the labor excel files
    df = pl.read_excel(filepath)
    
    #some files have upper case names, and some lower.  let's make all lower
    df = df.with_columns(pl.all().name.to_lowercase())
    
    #filter to only the specific careers that are related to the airports, airlines, and air craft
    df = df.filter(df['occ_title'].str.contains('Avionics')\
                  | df['occ_title'].str.starts_with('Air')\
                  | df['occ_title'].str.contains('Commercial Pilots')\
                  | df['occ_title'].str.contains('Flight Attendants'))
    
    #area/state/city specific data is too messy to join and is missing a lot of values. filter to US level data
    #we also want the detailed o-group data, and cross industry i group
    df = df.filter((df['area_title']== 'U.S.')\
                  & (df['o_group']== 'detailed')\
                  & (df['i_group']== 'cross-industry'))
    
    #add year column for joining, make sure total employment is an int
    df =df.with_columns(pl.lit(year).alias('year')
                       , pl.col('tot_emp').cast(pl.Int64))
    
    #we only need the job titles, year, and total employment figures
    df = df.select(['year'
                   , 'occ_title'
                   , 'tot_emp'])
    df = df.pivot(on = 'occ_title'
                         , index = 'year')


    
    new_columns = [clean_name(col) for col in df.columns]

    df.columns = new_columns

    return df


#function to read in the labor statistics data
def read_monthly_transport_stats(filepath):
    #read in the file
    df = pl.read_csv(filepath)
    
    #conver date column to datetime
    df = df.with_columns(pl.col('Date').str.to_datetime('%m/%d/%Y %I:%M:%S %p', strict = False))
    
    #to join the other tables, we need to create year and month columns
    df = df.with_columns(pl.col('Date').dt.year().alias('year')
                        , pl.col('Date').dt.month().alias('month'))
    
    #select the columns relevant to air travel
    df = df.select(['year'
                    , 'month'
                    , 'Air Safety - General Aviation Fatalities'
                    , 'U.S. Airline Traffic - Total - Seasonally Adjusted'
                    , 'U.S. Airline Traffic - International - Seasonally Adjusted'
                    , 'U.S. Airline Traffic - Domestic - Seasonally Adjusted'
                    , 'State and Local Government Construction Spending - Runway'
                    , 'State and Local Government Construction Spending - Air Passenger Terminal'
                    , 'State and Local Government Construction Spending - Air'
                    , 'State and Local Government Construction Spending - Transportation'
                    , 'State and Local Government Construction Spending - Infrastructure'
                    , 'Transportation Employment - Air Transportation'
                    , 'Air Safety - Air Taxi and Commuter Fatalities'
                    , 'Air Safety - Air Carrier Fatalities'
                    , 'U.S. Air Carrier Cargo (millions of revenue ton-miles) - International'
                    , 'U.S. Air Carrier Cargo (millions of revenue ton-miles) - Domestic'
                    , 'U.S. Airline Traffic - Total - Non Seasonally Adjusted'
                    , 'U.S. Airline Traffic - International - Non Seasonally Adjusted'
                    , 'U.S. Airline Traffic - Domestic - Non Seasonally Adjusted'
                    , 'U.S. marketing air carriers on-time performance (percent)'])
    
    new_columns = [clean_name(col) for col in df.columns]

    df.columns = new_columns
    
    return df

def read_proc_monthly_transport_stats(filepath):
    df = pl.read_csv(filepath)
    new_columns = [clean_name(col) for col in df.columns]

    df.columns = new_columns
    return df

def read_proc_airport_departure_stats(filepath):
    df = pl.read_csv(filepath)
    
    new_columns = [clean_name(col) for col in df.columns]
    df.columns = new_columns
    return df


# %%
#function to read in and do some cleaning on combined flights files
def read_combined_flights_parquet(filepath, list_airport_codes):
    #read in the file and keep some data columns from becoming forced to ints
    # filter columns
    list_cols_keep = ['FlightDate', 'Airline', 'Origin', 'Dest', 'Cancelled', 'Diverted',
       'CRSDepTime', "DepTime",'DepDelay', 'AirTime', 'CRSElapsedTime',
       'ActualElapsedTime', 'Distance',
       'Operated_or_Branded_Code_Share_Partners', 'DOT_ID_Marketing_Airline',
       'IATA_Code_Marketing_Airline', 'Flight_Number_Marketing_Airline',
       'Operating_Airline', 'DOT_ID_Operating_Airline', 'Tail_Number',
       'Flight_Number_Operating_Airline', 'OriginAirportSeqID',
       'OriginCityMarketID', 'OriginCityName', 'OriginState',
       'OriginStateFips', 'OriginStateName', 'OriginWac', 'DestAirportSeqID',
       'DestCityMarketID', 'DestCityName', 'DestState', 'DestStateFips',
       'DestStateName', 'DestWac', 'CRSArrTime', 'ArrDelay', 'ArrDel15', "ArrTime",
       'DivAirportLandings']


    df = pl.read_parquet(filepath
                    #, ignore_errors = True
                  #  , infer_schema = False 
                   # , schema_overrides = {'CRSDepTime':pl.String
                   #                       , 'DepTime':pl.String
                   #                       , 'CRSArrTime':pl.String
                   #                       , 'ArrTime':pl.String
                                        #  , 'Year':pl.Int64
                                        #  , 'Month':pl.Int64
                   #                     }
                    , columns=list_cols_keep)
                    
    df = df.filter(
      df["Origin"].is_in(list_airport_codes) | df["Dest"].is_in(list_airport_codes)
)

    df = df.with_columns(pl.col("FlightDate").cast(pl.String).str.head(10) )
    df = df.with_columns(pl.col("CRSDepTime").cast(pl.String))
    df = df.with_columns(pl.col("DepTime").cast(pl.String).str.replace(r"\.0$", ""))
    df = df.with_columns(pl.col("CRSArrTime").cast(pl.String).str.replace(r"\.0$", ""))
    df = df.with_columns(pl.col("ArrTime").cast(pl.String).str.replace(r"\.0$", ""))
    
    display(df[["FlightDate", "DepTime", "ArrTime"]])
    #make sure that we have a consistent style fo the departure and arrival times
    df = df.with_columns(pl.col('DepTime').str.strip_chars('.0').str.pad_start(4,'0')
                , pl.col('ArrTime').str.strip_chars('.0').str.pad_start(4,'0'))
    
    #create a departure date time so we know exactly when the flight took off.
    df = df.with_columns(pl.concat_str(
                            [pl.col('FlightDate').str.head(10)
                            , pl.lit(' ')
                            , pl.col('DepTime').str.head(2)
                            , pl.lit(':')
                            , pl.col('DepTime').str.tail(2)])
                         .str.to_datetime('%Y-%m-%d %H:%M', strict = False)
                         .alias('dep_datetime'))
    
    #get the arrival datetime by adding the elapsed time to the departure time
    df = df.with_columns((pl.col('dep_datetime')+pl.duration(minutes = 'ActualElapsedTime'))
                            .alias('arr_datetime')
                        )
    #filter out cancelled and diverted flights, since we cannot control for that.  
    #Make sure that we remove nulls and unclean rows
    display(df[["Cancelled", "Diverted", "ArrDelay", "dep_datetime"]])
    df = df.filter((df['Cancelled']==False)\
                    &(df['Diverted']==False)\
                    &(~df['ArrDelay'].is_null())
                    &(~df['dep_datetime'].is_null()))

    new_columns = [clean_name(col) for col in df.columns]
    df.columns = new_columns

    return df

# %%
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
# # 1. Data
#
# * Load data for target year and prev, as we may need to associate prev year data to the target (because if not it could induce data leak)
# * Join at the target year level

# %%
path_raw = "../../data/"
path_proc = "../../outputs/proc/"

# %%
dt_year = 2020#2019#2019#2020#
dt_ini = f"{dt_year}-01-01"
dt_prev = shift_date(dt_ini, years=-1)
dt_year_prev = dt_prev[:4]
years = [dt_year_prev, dt_year]
years


# %%
list_filter_airport_codes = ["EWR", "JFK", "LGA"]

# %%
# Monthly transport stats
filepath = f'{path_proc}transport_monthly_proc.csv'
monthly_transport_stats = read_proc_monthly_transport_stats(filepath)

# %%
monthly_transport_stats.shape

# %%
# Yearly labor statistics
labor = pl.DataFrame()
for year in years:
   # try:
    filepath_labor = f'{path_raw}labor statistics data_'+str(year)+'.xlsx'
    labor = pl.concat([labor, read_labor_stats(filepath_labor)], how="diagonal")
    #except: 
    #    print(f"Couldn't find data for year {year}")


# %%
labor.shape

# %%
# airport departure stats
filepath = f'{path_proc}airport_departure_stats_proc.csv'
airport_departure = read_proc_airport_departure_stats(filepath)
airport_departure.shape

# %%
# Aircraft registration
filepath_acft = f'{path_raw}ACFTREF_2022.txt'
acftref = read_ACFT(filepath_acft)
acftref.shape

# %%
# Master 
filepath_master = f'{path_raw}MASTER_2024.csv'
master = read_master(filepath_master)
master.shape


# %%
# Flights combined, # Only use objective year
filepath_cf = f'{path_raw}Combined_Flights_'+str(dt_year)+'.parquet'
df_merge = read_combined_flights_parquet(filepath_cf, list_airport_codes=list_filter_airport_codes)
df_merge.shape

# %%
df_merge = df_merge.with_columns(
    pl.concat_str([pl.col("flightdate"), pl.lit('-'),pl.col("crsdeptime"), pl.lit('-'),pl.col("operating_airline"), pl.lit('-'),
                    pl.col("origin"),  pl.lit('-'),pl.col("dest")]).alias("unique_key")
)
df_merge = df_merge.unique(subset=["unique_key"]) 
df_merge.shape, df_merge["unique_key"].n_unique()

# %%
df_merge["unique_key"]

# %% [markdown]
# # 2. Processing

# %% [markdown]
# * Create key for aircraft description using master that contains "tail_number"

# %%
master_acft = master.join(acftref , left_on = 'MFR_MDL_CODE'.lower() , right_on = 'CODE'.lower())
master_acft.shape

# %% [markdown]
# * Combine year stats

# %%
monthly_transport_stats = monthly_transport_stats.with_columns(pl.col("dt").str.head(4).cast(pl.Int32).alias("year"))

# %%
labor_monthly_transport = monthly_transport_stats.join(labor
                                                      , on = 'year')
labor_monthly_transport.shape

# %% [markdown]
# * Add to combined flights the aircraft information

# %%
df_combine1 = df_merge.select("unique_key", "tail_number").join(master_acft, left_on = 'tail_number', right_on = 'nnumber' , how="inner")
df_combine2 = df_merge.select("unique_key", "tail_number").join(master_acft.with_columns((pl.lit('N')+pl.col('nnumber')).alias("nnumber")), left_on = 'tail_number', right_on = 'nnumber' , how="inner")
df_combined = pl.concat([df_combine1, df_combine2]).unique(subset=["unique_key"], keep="first")
df_combined.shape


# %%
df_merge = df_merge.join(df_combined.drop("tail_number","mfr_mdl_code"), on="unique_key", how="left")
df_merge.shape, df_merge["unique_key"].n_unique()

# %% [markdown]
# * Add to combined flights the airport departure information

# %%
df_merge = df_merge.with_columns( year=pl.col("flightdate").str.slice(0, 4).cast(pl.Int32),
                         month=pl.col("flightdate").str.slice(5, 2).cast(pl.Int32))

# %%
airport_departure = airport_departure.with_columns((pl.col("year").cast(pl.Int32)  + 1).alias("year_ref"))

# %%
df_merge = df_merge.join(airport_departure.drop("year"), left_on=["origin", "year"], right_on=["airport_code","year_ref"], how="left")

# %%
df_merge.shape, df_merge["unique_key"].n_unique()

# %% [markdown]
# * Add to combined flights monthly transport and labor stats 

# %%
labor_monthly_transport = labor_monthly_transport.with_columns(
    (pl.col("dt").map_elements(lambda x: shift_date(x, months=1))).alias("dt_ref")
)

labor_monthly_transport = labor_monthly_transport.with_columns(
    year_ref=pl.col("dt_ref").str.slice(0, 4).cast(pl.Int32),
    month_ref=pl.col("dt_ref").str.slice(5, 2).cast(pl.Int32))

# %%
df_merge = df_merge.join(labor_monthly_transport
                                    , left_on = ['year'
                                                , 'month']
                                    , right_on = ['year_ref'
                                                , 'month_ref'],
                                    how="left")


# %%
df_merge.shape, df_merge["unique_key"].n_unique()

# %%
df_merge["arrdel15"].mean()

# %% [markdown]
# # Export

# %%
dt_year

# %%
df_merge.write_parquet(f"{path_proc}{dt_year}_join_datasets.parquet", compression="snappy")

# %%
df_merge.columns

# %%

# %%

null_percentages = df_merge.select([
((pl.col(c).is_null().sum() / df_merge.height) * 100).alias(c + "_null_percentage")
for c in df_merge.columns
])

# Sort the null percentages in descending order (highest null percentage first)
null_percentages_sorted = null_percentages.to_pandas().transpose().sort_values(0, ascending=False)

# %%
for i in range(null_percentages_sorted.shape[0]):
    if null_percentages_sorted.iloc[i].values[0] >0:
        display(null_percentages_sorted.iloc[i])

# %%
for col in df_merge.columns:
    print(col)

# %%
