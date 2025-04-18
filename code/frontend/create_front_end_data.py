import pandas as pd

# import the data
df_2019 = pd.read_parquet('data/2019_join_datasets.parquet', engine='pyarrow')
df_2020 = pd.read_parquet('data/2020_join_datasets.parquet', engine='pyarrow')
df_2021 = pd.read_parquet('data/2021_join_datasets.parquet', engine='pyarrow')
location_data = pd.read_csv('data/Airport_Location_Data.csv')

# stack it and get rid of the extra dfs
df_combo = pd.concat([df_2019, df_2020, df_2021])
del df_2019
del df_2020
del df_2021

# get the stats for arrival delays
arrival_delay_stats = df_combo[df_combo['arrdelay']>0].groupby('dest').agg({
    'arrdelay':['mean','median','std'],

}).reset_index()
arrival_delay_stats.columns = ['dest','arrdelay_mean','arrdelay_median','arrdelay_std']
arrival_delay_stats = arrival_delay_stats.round()

# make a column for how late the planes are:
df_combo['arrival_delay_status'] = 'on time'
df_combo.loc[(df_combo['arrdelay']>15) & (df_combo['arrdelay']<=30),'arrival_delay_status'] = 'little late'
df_combo.loc[(df_combo['arrdelay']>30),'arrival_delay_status'] = 'very late'

# calculate the delay probabilities for each airport
delay_probabilities = df_combo.groupby(['dest']).agg({
    'arrdel15':['sum','count']
}).reset_index()
delay_probabilities.columns=['dest','count_delayed_flights','count_fights']
delay_probabilities['late_prob'] = round(delay_probabilities['count_delayed_flights'] / delay_probabilities['count_fights']*100,1)
delay_probabilities['late_prob'] = delay_probabilities['late_prob'].astype(str) + '%'

# join the data together
location_data = pd.merge(
    location_data,
    arrival_delay_stats,
    left_on='AIRPORT',
    right_on='dest'
)
location_data = pd.merge(
    location_data,
    delay_probabilities,
    left_on='AIRPORT',
    right_on='dest'
)

# save the data
location_data.to_csv('frontend/tooltip_data.csv')

# get the list of all of the flights
df_combo['flight_number'] = df_combo['operating_airline'].astype(str) + ' ' + df_combo['flight_number_marketing_airline'].astype(str)
all_flights = df_combo[['flight_number','origin','dest']].drop_duplicates()
all_flights.to_csv('frontend/flight_list.csv')