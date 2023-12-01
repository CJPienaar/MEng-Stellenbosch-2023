
import pandas as pd
import os

# Load the data
file_path = "Load Shedding/Loadshedding_Stage_4.csv"
df_schedule = pd.read_csv(file_path, index_col=0)

# Create a date range from 2021/05/01 00:00:00 to 2023/06/01 01:00:00 at 30-minute intervals
date_range = pd.date_range("2021-05-01 00:00:00", "2023-06-01 01:00:00", freq="30T")

# Create a new DataFrame to store the results
result_df = pd.DataFrame(index=date_range, columns=["Timestamp", "Loadshedding"])

# Iterate over the date range
for i, timestamp in enumerate(date_range):
    load_shedding_status = "no"

    # Extract the day from the timestamp
    day = timestamp.day

    # Check if the day column is present in the schedule
    if str(day) in df_schedule.columns:
        # Check if the timestamp exists in the index
        if timestamp.strftime("%H:%M") in df_schedule.index:
            value_at_time_on = df_schedule.at[timestamp.strftime("%H:%M"), str(day)]

            if value_at_time_on == 2:
                load_shedding_status = "yes"
                # Set the next two timestamps to "yes" as well
                for j in range(1, min(3, len(date_range) - i)):
                    result_df.loc[date_range[i + j], "Loadshedding"] = "yes"

    result_df.loc[timestamp, "Timestamp"] = timestamp.strftime("%Y-%m-%d %H:%M:%S")
    result_df.loc[timestamp, "Loadshedding"] = load_shedding_status

# Write the results to Stage4.csv in the Load Shedding folder
result_df.to_csv("Load Shedding/Stage4.csv", index=False)

# Read the Stage4.csv file
file_path = "Load Shedding/Stage4.csv"
df_stage4 = pd.read_csv(file_path)

# Find the index of the first "yes"
yes_indices = df_stage4.index[df_stage4['Loadshedding'] == 'yes'].tolist()

# Adjust the following three "no" values to "yes" after the first "yes"
for index in yes_indices:
    if index + 3 < len(df_stage4):
        df_stage4.loc[index + 1:index + 4, 'Loadshedding'] = 'yes'

# Write the adjusted DataFrame back to Stage4.csv
df_stage4.to_csv("Load Shedding/Stage4.csv", index=False)

