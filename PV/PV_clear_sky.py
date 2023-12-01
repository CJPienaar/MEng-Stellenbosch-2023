import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Load the 'Final_Data_PV.csv' file
data = pd.read_csv('Final_Data_PV.csv')

# Convert 'TmStamp' column to datetime format
data['TmStamp'] = pd.to_datetime(data['TmStamp'], format='%Y/%m/%d %H:%M:%S')  # Adjust the format

# Define the time range for filtering (9:00 to 16:00)
start_time = '09:00:00'
end_time = '16:00:00'

# Filter data within the specified time range
filtered_data = data[(data['Time'] >= start_time) & (data['Time'] <= end_time)].copy()

# Calculate differences in consecutive GHI values on the copied DataFrame
filtered_data['GHI_diff'] = filtered_data['SunWM_Avg'].diff()

# Define the maximum daily GHI threshold
max_daily_ghi_threshold = 400

clear_sky_days = []
clear_sky_start_date = None
exclude_day = False

for index, row in filtered_data.iterrows():
    date = row['TmStamp'].date()
    ghi_change_threshold = 135  # Default threshold

    if pd.to_datetime('2021-05-01') <= date < pd.to_datetime('2021-08-14'):
        ghi_change_threshold = 100
    elif pd.to_datetime('2021-08-15') <= date < pd.to_datetime('2021-10-01'):
        ghi_change_threshold = 125
    elif pd.to_datetime('2021-10-01') <= date < pd.to_datetime('2022-05-01'):
        ghi_change_threshold = 140
    elif pd.to_datetime('2022-05-01') <= date < pd.to_datetime('2022-08-14'):
        ghi_change_threshold = 100
    elif pd.to_datetime('2022-08-15') <= date < pd.to_datetime('2022-10-01'):
        ghi_change_threshold = 125
    elif pd.to_datetime('2022-10-01') <= date < pd.to_datetime('2023-06-01'):
        ghi_change_threshold = 140

    if abs(row['GHI_diff']) > ghi_change_threshold:
        exclude_day = True

    # Track the maximum daily GHI
    if clear_sky_start_date is None:
        max_daily_ghi = 0
        clear_sky_start_date = date

    if date == clear_sky_start_date:
        if row['SunWM_Avg'] > max_daily_ghi:
            max_daily_ghi = row['SunWM_Avg']

    if date != clear_sky_start_date:
        if not exclude_day and max_daily_ghi >= max_daily_ghi_threshold:
            clear_sky_days.append(clear_sky_start_date.strftime('%d/%m/%Y'))

        clear_sky_start_date = date
        max_daily_ghi = 0
        exclude_day = False

# Check if the last day was a clear sky day
if not exclude_day and max_daily_ghi >= max_daily_ghi_threshold:
    clear_sky_days.append(clear_sky_start_date.strftime('%d/%m/%Y'))

# Print the identified clear sky days and save to a text file
with open('clear_sky_days.txt', 'w') as file:
    for clear_sky_date in clear_sky_days:
        print(f"Clear Sky Day: {clear_sky_date}")
        file.write(f"{clear_sky_date}\n")
