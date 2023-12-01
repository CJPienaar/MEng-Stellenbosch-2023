import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Load the 'Final_Data_PV.csv' file
data = pd.read_csv('Final_Data_PV.csv')

# Convert 'TmStamp' column to datetime format
data['TmStamp'] = pd.to_datetime(data['TmStamp'], format='%Y/%m/%d %H:%M:%S')

# Read the clear sky dates from the text file
clear_sky_dates = []
with open('clear_sky_days.txt', 'r') as file:
    for line in file:
        clear_sky_dates.append(line.strip())
        
# Count the number of items in the list
num_items = len(clear_sky_dates)
print(f'The number of items in the file is: {num_items}')

# Create a new DataFrame with the same length as data and set all values to 0
filtered_data = pd.DataFrame(0, columns=data.columns, index=data.index)

# Copy the 'Time', 'Date', 'Weekday', and 'Season' columns from the original data
filtered_data['Time'] = data['Time']
filtered_data['Date'] = data['Date']
filtered_data['Weekday'] = data['Weekday']
filtered_data['Season'] = data['Season']

# Convert 'TmStamp' column to the same datetime format
filtered_data['TmStamp'] = data['TmStamp']

# Filter the data for the clear sky dates and set the corresponding rows to the original data
mask = data['TmStamp'].dt.strftime('%d/%m/%Y').isin(clear_sky_dates)
filtered_data.loc[mask] = data.loc[mask]

filtered_data.to_csv('Final_Data_PV_Clear.csv', index=False)

# Plot 1
# Create a plot of GHI for clear sky days
plt.figure(figsize=(12, 6))
plt.plot(filtered_data['TmStamp'], filtered_data['SunWM_Avg'], label='GHI', color='royalblue', alpha=0.8)
#plt.plot(data['TmStamp'], data['SunWM_Avg'], label='GHI', color='forestgreen', alpha=0.3)
plt.xlabel('Date and Time')
plt.ylabel('GHI $(W/m^2)$')
plt.title('Global Horizontal Irradiance (GHI) for Clear Sky Days')

# Format the date and time labels on the x-axis
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y %H:%M:%S'))

# Set x-axis limits to span the full extent of the data
plt.xlim(filtered_data['TmStamp'].iloc[0], filtered_data['TmStamp'].iloc[-1])
plt.xticks(rotation=30)

# Show the plot
plt.legend(loc='upper right')
plt.grid()
plt.tight_layout()
plt.show()

# Plot 2
start_date_1 = pd.Timestamp('2022-01-19 00:00:00')
end_date_1 = pd.Timestamp('2022-01-28 00:00:00')

fig, ax1 = plt.subplots(figsize=(12, 6))

# Plot for GHI
ax1.plot(filtered_data['TmStamp'], filtered_data['SunWM_Avg'], label='GHI', color='royalblue', alpha=0.8)
ax1.set_xlabel('Date and Time')
ax1.set_ylabel('GHI $(W/m^2)$')
ax1.tick_params(axis='y')
ax1.grid(True)
plt.xticks(rotation=30)

# Create a secondary y-axis for PV production
ax2 = ax1.twinx()
ax2.plot(filtered_data['TmStamp'], filtered_data['p_dc_m'], label='PV Production', color='red', alpha=0.8)
ax2.set_ylabel('PV Production $(W)$')
ax2.tick_params(axis='y')
ax2.grid(True)

# Format the date and time labels on the x-axis
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y %H:%M:%S'))

# Set x-axis limits to the specified date range
ax1.set_xlim(start_date_1, end_date_1)
plt.xticks(rotation=30)

# Combine legends
handles, labels = ax1.get_legend_handles_labels()
handles2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(handles + handles2, labels + labels2, loc='upper right')

plt.title('GHI and PV Production for Group 3')

# Show the plot
plt.grid()
plt.tight_layout()
plt.show()

# Plot 3
start_date_2 = pd.Timestamp('2021-06-18 00:00:00')
end_date_2 = pd.Timestamp('2021-06-22 00:00:00')

fig, ax1 = plt.subplots(figsize=(12, 6))

# Plot for GHI
ax1.plot(filtered_data['TmStamp'], filtered_data['SunWM_Avg'], label='GHI', color='royalblue', alpha=0.8)
ax1.set_xlabel('Date and Time')
ax1.set_ylabel('GHI $(W/m^2)$')
ax1.tick_params(axis='y')
ax1.grid(True)
plt.xticks(rotation=30)

# Create a secondary y-axis for PV production
ax2 = ax1.twinx()
ax2.plot(filtered_data['TmStamp'], filtered_data['p_dc_m'], label='PV Production', color='r', alpha=0.8)
ax2.set_ylabel('PV Production $(W)$')
ax2.tick_params(axis='y')
ax2.grid(True)

# Format the date and time labels on the x-axis
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y %H:%M:%S'))

# Set x-axis limits to the specified date range
ax1.set_xlim(start_date_2, end_date_2)
plt.xticks(rotation=30)

# Combine legends
handles, labels = ax1.get_legend_handles_labels()
handles2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(handles + handles2, labels + labels2, loc='upper right')

plt.title('GHI and PV Production for Group 1')

# Show the plot
plt.grid()
plt.tight_layout()
plt.show()

# Plot 4
start_date_3 = pd.Timestamp('2022-09-06 00:00:00')
end_date_3 = pd.Timestamp('2022-09-09 00:00:00')

fig, ax1 = plt.subplots(figsize=(12, 6))

# Plot for GHI
ax1.plot(filtered_data['TmStamp'], filtered_data['SunWM_Avg'], label='GHI', color='royalblue', alpha=0.8)
ax1.set_xlabel('Date and Time')
ax1.set_ylabel('GHI $(W/m^2)$')
ax1.tick_params(axis='y')
ax1.grid(True)
plt.xticks(rotation=30)

# Create a secondary y-axis for PV production
ax2 = ax1.twinx()
ax2.plot(filtered_data['TmStamp'], filtered_data['p_dc_m'], label='PV Production', color='r', alpha=0.8)
ax2.set_ylabel('PV Production $(W)$')
ax2.tick_params(axis='y')
ax2.grid(True)

# Format the date and time labels on the x-axis
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y %H:%M:%S'))

# Set x-axis limits to the specified date range
ax1.set_xlim(start_date_3, end_date_3)
plt.xticks(rotation=30)

# Combine legends
handles, labels = ax1.get_legend_handles_labels()
handles2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(handles + handles2, labels + labels2, loc='upper right')

plt.title('GHI and PV Production for Group 2')

# Show the plot
plt.grid()
plt.tight_layout()
plt.show()