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

# %%
path_raw = "../../data/"
path_proc = "../../outputs/proc/"
path_fe = "../../outputs/fe/"

dt_year = 2019

# %%
df_fe = pl.read_parquet(f"{path_fe}{dt_year}_fe_time.parquet")
df_fe.shape

# %%
df_fe = pl.concat([df_fe,  pl.read_parquet(f"{path_fe}{dt_year}_fe_stats.parquet").drop("unique_key")], how="horizontal")
df_fe.shape

# %%
df_fe = pl.concat([df_fe,  pl.read_parquet(f"{path_fe}{dt_year}_fe_flight.parquet").drop("unique_key")], how="horizontal")
df_fe.shape

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
    if v>96: # percentage bigger than 
        list_remove.append(k)

# %%
list_remove

# %%
df_fe = df_fe.drop(list_remove)

# %%
df_fe.shape

# %%
df_fe

# %% [markdown]
# # Export

# %%
df_fe.write_parquet(f"{path_fe}{dt_year}_joined_fe.parquet", compression="snappy")

# %%

# %%
