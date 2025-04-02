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
# ## 2.1 Mode
#
# * Check features which the most common value has a very high %

# %%
percentages = {
    col: (df_fe.filter(pl.col(col) == df_fe[col].mode()[0]).height / df_fe.height) * 100
    for col in df_fe.columns
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
df_fe = df_fe.drop(list_remove)

# %% [markdown]
# ## 2.2 Null percentage

# %%
null_percentages = df_fe.select([
((pl.col(c).is_null().sum() / df_fe.height) * 100).alias(c + "_null_percentage")
for c in df_fe.columns
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
df_fe.shape

# %% [markdown]
# # Export

# %%
df_fe.write_parquet(f"{path_fe}all_joined_fe_delta_years={len(dt_years)}.parquet", compression="snappy")

# %%
f"{path_fe}all_joined_fe_delta_years={len(dt_years)}.parquet"


# %%
df_fe.columns[:30]


# %%
df_fe.columns[30:]

# %%
df_fe.columns[50:]

# %%
