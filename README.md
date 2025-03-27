# dva_flightdelay


# Processing datasets

Each step serves as an input for the subsequent one. First, we combine all datasets for each year. Then, for each year, we create separate files based on the feature type (e.g., "flight," "time," etc.). Finally, we merge all feature groups and years with the target into a single file. In the last step, we also apply filters based on variability and completeness.

1. Use **"proc/proc_join_tables_yearly.py"** to join all datasets. Modify the year in the "0.Config" section of the script.

2. Create the features with **"proc/fe_joined.py"**. Specify the year and feature group to generate in the "0.Config" section of the script.

3. Combine all features and targets for each year using **"modeling/feature_filtering.py"**. Define the list of years to merge in the "0.Config" section of the script.