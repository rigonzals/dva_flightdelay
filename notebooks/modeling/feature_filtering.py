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
import numpy as np
import polars as pl

# %% [markdown]
# # 0. Config

# %%
path_raw = "../../data/"
path_proc = "../../outputs/proc/"
path_fe = "../../outputs/fe/"

dt_years = [2018,2019, 2020, 2021]

# %% [markdown]
# # 1. Data

# %%
df_fe_joined = pl.DataFrame()
for year in dt_years:

    df_fe = pl.read_parquet(f"{path_fe}{year}_fe_time.parquet")
    print(df_fe.shape)

    #df_fe = pl.concat([df_fe,  pl.read_parquet(f"{path_fe}{year}_fe_stats.parquet").drop("unique_key")], how="horizontal")
    df_fe = df_fe.join(pl.read_parquet(f"{path_fe}{year}_fe_stats.parquet"), on="unique_key")
    print(df_fe.shape)

    #df_fe = pl.concat([df_fe,  pl.read_parquet(f"{path_fe}{year}_fe_flight.parquet").drop("unique_key")], how="horizontal")
    df_fe = df_fe.join(pl.read_parquet(f"{path_fe}{year}_fe_flight.parquet"), on="unique_key")
    print(df_fe.shape)  

    #df_fe = pl.concat([df_fe,  pl.read_parquet(f'{path_proc}{year}_join_datasets.parquet', columns=["arrdelay"])], how="horizontal")
    df_fe = df_fe.join(pl.read_parquet(f"{path_proc}{year}_join_datasets.parquet", columns=["unique_key","arrdelay"]), on="unique_key")
    print(df_fe.shape)
   # try:
    df_fe_joined = pl.concat([df_fe_joined, df_fe], how="diagonal")
# %% [markdown]
# # 2. Filter

# %% [markdown]
# ## 2.0 Processing

# %% [markdown]
# ### Imputation

# %%
list_cols_impute = [
    'typeeng_2',
 'typeeng_4',
 'typeeng_5',
 'accat_1',
 'accat_2',
 'accat_3',
 'acweight_class_1',
 'acweight_class_2',
 'acweight_class_3',
 'acweight_class_4',
 'originstate_AK',
 'originstate_AL',
 'originstate_AR',
 'originstate_AZ',
 'originstate_CA',
 'originstate_CO',
 'originstate_CT',
 'originstate_FL',
 'originstate_GA',
 'originstate_HI',
 'originstate_IA',
 'originstate_IL',
 'originstate_IN',
 'originstate_KY',
 'originstate_LA',
 'originstate_MA',
 'originstate_MD',
 'originstate_ME',
 'originstate_MI',
 'originstate_MN',
 'originstate_MO',
 'originstate_MT',
 'originstate_NC',
 'originstate_NE',
 'originstate_NH',
 'originstate_NJ',
 'originstate_NM',
 'originstate_NV',
 'originstate_NY',
 'originstate_OH',
 'originstate_OK',
 'originstate_OR',
 'originstate_PA',
 'originstate_PR',
 'originstate_RI',
 'originstate_SC',
 'originstate_SD',
 'originstate_TN',
 'originstate_TX',
 'originstate_UT',
 'originstate_VA',
 'originstate_VI',
 'originstate_VT',
 'originstate_WA',
 'originstate_WI',
 'originstate_WY',
 'deststate_AK',
 'deststate_AL',
 'deststate_AR',
 'deststate_AZ',
 'deststate_CA',
 'deststate_CO',
 'deststate_CT',
 'deststate_FL',
 'deststate_GA',
 'deststate_HI',
 'deststate_IA',
 'deststate_IL',
 'deststate_IN',
 'deststate_KY',
 'deststate_LA',
 'deststate_MA',
 'deststate_MD',
 'deststate_ME',
 'deststate_MI',
 'deststate_MN',
 'deststate_MO',
 'deststate_MT',
 'deststate_NC',
 'deststate_NE',
 'deststate_NH',
 'deststate_NJ',
 'deststate_NM',
 'deststate_NV',
 'deststate_NY',
 'deststate_OH',
 'deststate_OK',
 'deststate_OR',
 'deststate_PA',
 'deststate_PR',
 'deststate_RI',
 'deststate_SC',
 'deststate_SD',
 'deststate_TN',
 'deststate_TX',
 'deststate_UT',
 'deststate_VA',
 'deststate_VI',
 'deststate_VT',
 'deststate_WA',
 'deststate_WI',
 'deststate_WY',
 'operating_airline_9E',
 'operating_airline_AA',
 'operating_airline_AS',
 'operating_airline_AX',
 'operating_airline_B6',
 'operating_airline_C5',
 'operating_airline_DL',
 'operating_airline_EV',
 'operating_airline_F9',
 'operating_airline_G4',
 'operating_airline_G7',
 'operating_airline_HA',
 'operating_airline_MQ',
 'operating_airline_NK',
 'operating_airline_OH',
 'operating_airline_OO',
 'operating_airline_PT',
 'operating_airline_UA',
 'operating_airline_VX',
 'operating_airline_WN',
 'operating_airline_YV',
 'operating_airline_YX',
 'operating_airline_ZW',
  'originstate_ID',
 'deststate_ID'
]

for col in list_cols_impute:
    df_fe_joined = df_fe_joined.with_columns([
                    pl.col(col).fill_null(0)])

# %% [markdown]
# ## 2.1 Mode
#
# * Check features which the most common value has a very high %

# %%
percentages = {
    col: (df_fe_joined.filter(pl.col(col) == df_fe_joined[col].mode()[0]).height / df_fe_joined.height) * 100
    for col in df_fe_joined.columns
}

# Print the result
print(percentages)

# %%
sorted_dict = dict(sorted(percentages.items(), key=lambda item: item[1]))

# %%
list_remove = []
for k,v in percentages.items():
    if v>95: # percentage bigger than 
        list_remove.append(k)

# %%
list_remove

# %%
df_fe_joined = df_fe_joined.drop(list_remove)
df_fe_joined.shape

# %% [markdown]
# ## 2.2 Null percentage

# %%
null_percentages = df_fe_joined.select([
((pl.col(c).is_null().sum() / df_fe_joined.height) * 100).alias(c + "_null_percentage")
for c in df_fe_joined.columns
])

# Sort the null percentages in descending order (highest null percentage first)
null_percentages_sorted = null_percentages.to_pandas().transpose().sort_values(0, ascending=False).to_dict()[0]

# %%
list_remove = []
for k,v in null_percentages_sorted.items():
    if v>90: # percentage bigger than 
        list_remove.append(k)
list_remove

# %%
df_fe_joined.shape


# %% [markdown]
# # 3. Split dataset

# %%
def arrival_category(row):

    if row <=15:
        return "On-Time"
    elif row <=45:
        return "Late"
    else:
        return "Very Late"


# %%
def stratified_split(df: pl.DataFrame, target_col: str, test_size: float = 0.2, seed: int = 42):
    np.random.seed(seed)
    train_parts = []
    test_parts = []

    for class_value in df[target_col].unique().to_list():
        class_df = df.filter(pl.col(target_col) == class_value)
        n_total = class_df.height
        n_test = int(n_total * test_size)

        indices = np.random.permutation(n_total)
        test_idx = indices[:n_test]
        train_idx = indices[n_test:]
        print(indices[:20])

        test_parts.append(class_df[test_idx])
        train_parts.append(class_df[train_idx])

    train_df = pl.concat(train_parts)
    train_df = train_df.sample(n=train_df.shape[0], shuffle=True, seed=seed)
    test_df = pl.concat(test_parts)
    test_df = test_df.sample(n=test_df.shape[0], shuffle=True, seed=seed)
        
    return train_df, test_df


# %%
df_fe_joined = df_fe_joined.with_columns([
    pl.col("arrdelay").map_elements(arrival_category).alias("arrival_category")]
)

# %%
df_fe_joined.select(pl.col("arrival_category").value_counts(normalize=True))  

# %%
df_fe_joined.shape

# %%
train_df, test_df = stratified_split(df_fe_joined, target_col="arrival_category", test_size=0.2)

# %%
train_df.shape, test_df.shape

# %%
df_fe_joined.shape[0] - (train_df.shape[0] + test_df.shape[0])

# %%
train_df.select(pl.col("arrival_category").value_counts(normalize=True))  

# %%
test_df.select(pl.col("arrival_category").value_counts(normalize=True))  

# %%
test_df = test_df.drop(["arrival_category"])
test_df.shape

# %%
train_df = train_df.drop(["arrival_category"])
train_df.shape

# %%
train_df.select(pl.col("year_right").value_counts(normalize=True))  

# %%
test_df.select(pl.col("year_right").value_counts(normalize=True))  

# %% [markdown]
# # Export

# %%
df_fe_joined.write_parquet(f"{path_fe}all_joined_fe_delta_years={len(dt_years)}.parquet", compression="snappy")

# %%
f"{path_fe}all_joined_fe_delta_years={len(dt_years)}.parquet"


# %%
train_df.write_parquet(f"{path_fe}train_all_joined_fe_delta_years={len(dt_years)}.parquet", compression="snappy")

# %%
test_df.write_parquet(f"{path_fe}val_all_joined_fe_delta_years={len(dt_years)}.parquet", compression="snappy")

# %%
df_fe_joined.columns[:30]


# %%
df_fe_joined.columns[30:]

# %%
df_fe_joined.columns[50:]

# %%
