#!/usr/bin/env python
# coding: utf-8

# In[2]:


import polars as pl


# In[3]:


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
    
    return df


# In[4]:


#function to read in and do some cleaning on combined flights files
def read_combined_flights(filepath):
    #read in the file and keep some data columns from becoming forced to ints
    df = pl.read_csv(filepath
                    , ignore_errors = True
                    , infer_schema = False 
                    , schema_overrides = {'CRSDepTime':pl.String
                                          , 'DepTime':pl.String
                                          , 'CRSArrTime':pl.String
                                          , 'ArrTime':pl.String
                                          , 'Year':pl.Int64
                                          , 'Month':pl.Int64})
    #make sure that we have a consistent style fo the departure and arrival times
    df = df.with_columns(pl.col('DepTime').str.strip_chars('.0').str.pad_start(4,'0')
                , pl.col('ArrTime').str.strip_chars('.0').str.pad_start(4,'0'))
    
    #create a departure date time so we know exactly when the flight took off.
    df = df.with_columns(pl.concat_str(
                            [pl.col('FlightDate')
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
    df = df.filter((df['Cancelled']==False)\
                  &(df['Diverted']==False)\
                  &(~df['ArrDelay'].is_null())
                  &(~df['dep_datetime'].is_null()))
    return df



# In[5]:


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
    return df


# In[6]:


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
    
    return df


# In[7]:


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
    

    
    return df


# In[8]:


filepath = r'C:\Users\crabt\OneDrive\Documents\GA Tech\Data and Visual Analytics\project\Monthly_Transportation_Statistics_20250220.csv'
monthly_transport_stats = read_monthly_transport_stats(filepath)


# mast_acft = master.join(acftref
#                        , left_on = 'MFR MDL CODE'
#                        , right_on = 'CODE')
# 

# combined1 = mast_acft.join(cf
#                          , left_on = 'N-NUMBER'
#                          , right_on = 'Tail_Number')
# 

# combined2 = mast_acft.with_columns((pl.lit('N')+pl.col('N-NUMBER')).alias('N-NUMBER'))\
#                     .join(cf
#                          , left_on = 'N-NUMBER'
#                          , right_on = 'Tail_Number')

# combined = pl.concat([combined1
#                      , combined2])

# In[9]:


years = list(range(2018,2023))
labor = pl.DataFrame()
for year in years:
    filepath_labor = r'C:\Users\crabt\OneDrive\Documents\GA Tech\Data and Visual Analytics\project\labor statistics data_'+str(year)+'.xlsx'
    labor = pl.concat([labor, read_labor_stats(filepath_labor)])


# In[10]:


labor_pivot = labor.pivot(on = 'occ_title'
                         , index = 'year')


# In[11]:


labor_monthly_transport = monthly_transport_stats.join(labor_pivot
                                                      , on = 'year')


# In[12]:


filepath_acft = r'C:\Users\crabt\OneDrive\Documents\GA Tech\Data and Visual Analytics\project\ACFTREF_2022.txt'
filepath_master = r'C:\Users\crabt\OneDrive\Documents\GA Tech\Data and Visual Analytics\project\MASTER_2024.csv'
acftref = read_ACFT(filepath_acft)
master = read_master(filepath_master)
master_acft = master.join(acftref , left_on = 'MFR MDL CODE' , right_on = 'CODE')


# In[ ]:


years = list(range(2018,2023))

cf = pl.DataFrame()
for year in years:
    filepath_cf = r'C:\Users\crabt\OneDrive\Documents\GA Tech\Data and Visual Analytics\project\Combined_Flights_'+str(year)+'.csv'
    cf_temp = read_combined_flights(filepath_cf)
    combined1 = master_acft.join(cf_temp , left_on = 'N-NUMBER' , right_on = 'Tail_Number')

    combined2 = master_acft.with_columns((pl.lit('N')+pl.col('N-NUMBER')).alias('N-NUMBER'))\
                        .join(cf_temp , left_on = 'N-NUMBER' , right_on = 'Tail_Number')

    combined = pl.concat([combined1 , combined2])
    combined_labor_month = combined.join(labor_monthly_transport
                                       , left_on = ['Year'
                                                   , 'Month']
                                       , right_on = ['year'
                                                   , 'month'])
    cf = pl.concat([cf, combined_labor_month])
    


# In[ ]:


cf


# In[ ]:




