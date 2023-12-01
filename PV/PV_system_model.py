import numpy as np
import pandas as pd
import pvlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates   
from pvlib.modelchain import ModelChain
from pvlib.location import Location
from pvlib.pvsystem import PVSystem
from pvlib.temperature import TEMPERATURE_MODEL_PARAMETERS

# Start with system design and modelling
#-------------------#

# Define the system parameters
system_capacity = 2 * 8 * 0.375  # Total capacity of 2 strings of 8 panels, each 375Wp
azimuth = -10.0  # degrees (west-facing, positive values are west)
tilt = 28.0  # degrees
latitude = -33.9321  # Latitude of the location (Southern Hemisphere)
longitude = 18.8602  # Longitude of the location
surface_tilt = tilt  # Tilt of the panels
surface_azimuth = azimuth  # Azimuth of the panels

# Load your weather data into a DataFrame
data = pd.read_csv('Final_Data.csv')  # Replace with the actual path to your data
# Convert the 'TmStamp' column to datetime
data['TmStamp'] = pd.to_datetime(data['TmStamp'], format='%d/%m/%Y %H:%M:%S')
# Set the 'TmStamp' column as the index of the DataFrame
data.set_index('TmStamp', inplace=True)

# Define location for PV
location = Location(latitude, longitude, tz='Africa/Johannesburg', altitude=136)  # Create a Location object

# Define PV temperature model parameters
temp_parameter = TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_glass']

# Define PV system
panel_database = pvlib.pvsystem.retrieve_sam('CECMod')  # Retrieve the CEC module database
inverter_database = pvlib.pvsystem.retrieve_sam('CECInverter')  # Retrieve the CEC inverter database

panel = panel_database['Jinko_Solar_Co___Ltd_JKM375M_72'] #Jinko_Solar_Co___Ltd_JKM375M_72 LG_Electronics_Inc__LG375N2W_G4
inverter = inverter_database['ABB__PVI_5000_OUTD_US__240V_'] #ABB__PVI_5000_OUTD_US__240V_  Fronius_USA__IG_Plus_A_5_0__240V_

system = PVSystem(surface_tilt = tilt, surface_azimuth = azimuth, module_parameters = panel, inverter_parameters = inverter,
                  temperature_model_parameters = temp_parameter, modules_per_string = 8, strings_per_inverter = 2)  # Create a PVSystem object

# Extract relevant weather data
dni = data['TrackerWM_Avg']
ghi = data['SunWM_Avg']
temperature = data['AirTC_Avg']
windspeed = data['WS_ms_S_WVT']

# Calculate solar position for the given location and time
solar_position = location.get_solarposition(data.index)

# Calculate the cell temperature
cell_temperature = pvlib.temperature.sapm_cell(
    poa_global=dni,
    temp_air=temperature,
    wind_speed= windspeed,
    a=temp_parameter['a'],
    b=temp_parameter['b'],
    deltaT=temp_parameter['deltaT']
)

# Initialize a ModelChain
mc = ModelChain(system, location, aoi_model='physical')
                #, dc_model= 'cec', ac_model= inverter, aoi_model='no_loss')
                #temperature_model= cell_temperature)


# Construct a DataFrame for weather data
weather_data_for_model = pd.DataFrame({
    'ghi': data['SunWM_Avg'],  
    'dni': data['TrackerWM_Avg'],
    'dhi': data['ShadowWM_Avg'],  
    'temp_air': temperature,  # Optional
    'wind_speed': windspeed,  # Optional
    'cell_temperature': cell_temperature,  # Optional
    'precipitable_water': 0.1  # Optional
    
})

# Run the simulation
mc.run_model(weather_data_for_model)

# Get the total DC & AC power output
total_dc_power = mc.results.dc
total_ac_power = mc.results.ac
#mc.results.ac.plot(figsize=(12,6), grid=True, legend=True, title='DC Power Output')
#plt.show() 

#print(mc.results.weather[16070:16120])
#print(mc.results.times[16070:16120], mc.results.dc[16070:16120])

# Append 'p_mp' to the DataFrame and save it to a CSV file
data['p_dc_m'] = total_dc_power['p_mp']
data.to_csv('Final_Data_PV.csv', index=True)

# Start plotting
#-------------------#

# Highlight the specified date ranges
highlight_start = pd.Timestamp('2021-12-29 6:30:00')
highlight_end = pd.Timestamp('2022-03-13 19:30:00')

holiday_start = pd.Timestamp('2022-06-19 19:30:00')
holiday_end = pd.Timestamp('2022-07-13 15:30:00')

# Define the start and end of the "Missing Dates" period
missing_dates_start = pd.Timestamp('2022-06-02 14:00:00')
missing_dates_end = pd.Timestamp('2022-06-17 14:30:00')

# Define the start and end of the "Missing Dates" period (teal highlight)
missing_dates_start2 = pd.Timestamp('2022-08-15 13:30:00')
missing_dates_end2 = pd.Timestamp('2022-08-25 14:30:00')

## Plot 1
# Extract 'p_mp', 'v_mp', and 'i_mp' from total_dc_power
p_mp = total_dc_power['p_mp']
v_mp = total_dc_power['v_mp']
i_mp = total_dc_power['i_mp']

# Plot the PV production, 'p_mp', 'v_mp', and 'i_mp' over time
fig, ax1 = plt.subplots(figsize=(12, 6))

# Plot for 'p_mp'
ax1.plot(data.index, p_mp, label='Maximum Power (W)', color='royalblue', alpha=0.8)
ax1.set_xlabel('Date and Time')
ax1.set_ylabel('Maximum Power (W)')
ax1.tick_params('y')
ax1.grid(True)
plt.xticks(rotation=30)

# Create a secondary y-axis for 'v_mp' and 'i_mp'
ax2 = ax1.twinx()
ax2.plot(data.index, v_mp, label='Voltage at Maximum Power (V)', color='r', alpha=0.6)
ax2.plot(data.index, i_mp, label='Current at Maximum Power (A)', color='forestgreen', alpha=0.7)
ax2.set_ylabel('Voltage (V) and Current (A)')
ax2.tick_params('y')
ax2.grid(True)
ax2.set_ylim(-25,500)

# Format the date and time labels on the x-axis
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y %H:%M:%S'))

# Set x-axis limits to span the full extent of the data
ax1.set_xlim(data.index[0], data.index[-1])
plt.xticks(rotation=30)

# Highlight the specified date ranges
ax1.axvspan(highlight_start, highlight_end, alpha=0.3, color='yellow', label='Geyser Off Summer')
ax1.axvspan(holiday_start, holiday_end, facecolor='lightgray', alpha=0.5, label='Holiday Period')
ax1.axvspan(missing_dates_start, missing_dates_end, facecolor='pink', alpha=0.5, label='Missing Data 1')
ax1.axvspan(missing_dates_start2, missing_dates_end2, alpha=0.4, color='teal', label='Missing Data 2')

# Create separate legends for each axis
handles, labels = [], []
for ax in [ax1, ax2]:
    h, l = ax.get_legend_handles_labels()
    handles.extend(h)
    labels.extend(l)

ax1.legend(handles, labels, loc='upper right')

plt.title('Average PV Production and Maximum Power Variables Over 30-min Intervals')

# Show the plot
plt.grid()
plt.tight_layout()
plt.show()

# Plot 2
# Plot 'p_mp' and 'GHI' on two separate y-axes with adjusted y-axis limits for 'GHI'
fig, ax1 = plt.subplots(figsize=(12, 6))
line2, = ax1.plot(data.index, p_mp, label='Maximum Power (W)', color='royalblue', alpha=0.7)
ax1.set_xlabel('Date and Time')
ax1.set_ylabel('PV Production (W)')
ax1.tick_params(axis='y')
ax1.grid(True)
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y %H:%M:%S'))  # Updated date format
plt.xticks(rotation=30)

# Create a new y-axis for 'GHI'
ax2 = ax1.twinx()
line1, = ax2.plot(data.index, ghi, label='Global Horizontal Irradiance ($W/m^2$)', color='r', alpha=0.6)
ax2.set_ylabel('Globl Horizontal Irradiance ($W/m^2$)')
ax2.tick_params(axis='y')
ax2.grid(True)
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y %H:%M:%S'))  # Updated date format
plt.xticks(rotation=30)

plt.title('PV Production and Globl Horizontal Irradiance Over 30-min Intervals')

# Highlight the specified date ranges
line3 = ax1.axvspan(highlight_start, highlight_end, alpha=0.3, color='yellow', label='Geyser Off Summer')
line4 = ax1.axvspan(holiday_start, holiday_end, facecolor='lightgray', alpha=0.5, label='Holiday Period')
line5 = ax1.axvspan(missing_dates_start, missing_dates_end, facecolor='pink', alpha=0.5, label='Missing Data 1')
line6 = ax1.axvspan(missing_dates_start2, missing_dates_end2, alpha=0.4, color='teal', label='Missing Data 2')

# Set x-axis limits to span the full extent of the data
ax1.set_xlim(data.index[0], data.index[-1])

# Create a single legend in the upper right corner
handles = [line1, line2, line3, line4, line5, line6]

# Show the legend
ax1.legend(handles, [handle.get_label() for handle in handles], loc='upper right')

# Show plot
plt.tight_layout()
plt.grid()
plt.show()

# Plot 3
# Plot total AC power
plt.figure(figsize=(12, 6))
plt.plot(data.index, total_ac_power, label='Total AC Power (W)', color='darkorange', alpha=0.8)
plt.xlabel('Date and Time')
plt.ylabel('Total AC Power (W)')
plt.title('Total AC Power Over 30-min Intervals')

# Format the date and time labels on the x-axis
plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%d/%m/%Y %H:%M:%S'))

# Set x-axis limits to span the full extent of the data
plt.xlim(data.index[0], data.index[-1])
plt.xticks(rotation=30)

# Highlight the specified date ranges
plt.axvspan(highlight_start, highlight_end, alpha=0.3, color='yellow', label='Geyser Off Summer')
plt.axvspan(holiday_start, holiday_end, facecolor='lightgray', alpha=0.5, label='Holiday Period')
plt.axvspan(missing_dates_start, missing_dates_end, facecolor='pink', alpha=0.5, label='Missing Data 1')
plt.axvspan(missing_dates_start2, missing_dates_end2, alpha=0.4, color='teal', label='Missing Data 2')

# Show the plot
plt.grid()
plt.legend(loc='upper right')
plt.tight_layout()
plt.show()

# Plot 4
# Plot 'p_mp' and 'GHI' on two separate y-axes with adjusted y-axis limits for 'GHI
# Assuming data.index is a DateTimeIndex
x_min = pd.Timestamp('2022-01-20 00:00:00')
x_max = pd.Timestamp('2022-01-22 00:00:00')

# Filter data for the specified date range
filtered_data = data.loc[(data.index >= x_min) & (data.index <= x_max)]

fig, ax1 = plt.subplots(figsize=(12, 6))

line2, = ax1.plot(filtered_data.index, filtered_data['p_dc_m'], label='Maximum Power (W)', color='royalblue', alpha=0.7)
ax1.set_xlabel('Date and Time')
ax1.set_ylabel('PV Production (W)')
ax1.tick_params(axis='y')
ax1.grid(True)
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y %H:%M:%S'))  # Updated date format
plt.xticks(rotation=30)

# Create a new y-axis for 'GHI'
ax2 = ax1.twinx()
line1, = ax2.plot(filtered_data.index, filtered_data['SunWM_Avg'], label='Global Horizontal Irradiance ($W/m^2$)', color='r', alpha=0.6)#TrackerWM_Avg 
ax2.set_ylabel('Global Horizontal Irradiance ($W/m^2$)')
ax2.tick_params(axis='y')
ax2.grid(True)
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y %H:%M:%S'))  # Updated date format
plt.xticks(rotation=30)

plt.title('PV Production and Global Horizontal Irradiance for Two Summer Days')

# Set x-axis limits to span the full extent of the data
ax1.set_xlim(filtered_data.index[0], filtered_data.index[-1])
ax2.set_xlim(filtered_data.index[0], filtered_data.index[-1])

# Create a single legend in the upper right corner
handles = [line1, line2]

# Show the legend
ax1.legend(handles, [handle.get_label() for handle in handles], loc='upper right')

# Show plot
plt.tight_layout()
plt.grid()
plt.show()




# Plot GHI, DHI, DNI, DC power, and temperature on one axis
fig, ax1 = plt.subplots(figsize=(12, 6))

# Plot GHI, DHI, and DNI
ax1.plot(data.index, ghi, label='GHI (W/m^2)', color='orange', alpha=0.7)
ax1.plot(data.index, data['ShadowWM_Avg'], label='DHI (W/m^2)', color='skyblue', alpha=0.7)
ax1.plot(data.index, dni, label='DNI (W/m^2)', color='purple', alpha=0.7)

ax1.set_xlabel('Date and Time')
ax1.set_ylabel('Solar Irradiance (W/m^2)')
ax1.tick_params('y')
ax1.grid(True)
plt.xticks(rotation=30)

# Create a secondary y-axis for DC power and temperature
ax2 = ax1.twinx()
ax2.plot(data.index, total_dc_power['p_mp'], label='DC Power (W)', color='royalblue', alpha=0.3)
ax2.set_ylabel('DC Power (W)')
ax2.tick_params('y')

# Highlight the specified date ranges
ax2.axvspan(highlight_start, highlight_end, alpha=0.3, color='yellow', label='Geyser Off Summer')
ax2.axvspan(holiday_start, holiday_end, facecolor='lightgray', alpha=0.5, label='Holiday Period')
ax2.axvspan(missing_dates_start, missing_dates_end, facecolor='pink', alpha=0.5, label='Missing Data 1')
ax2.axvspan(missing_dates_start2, missing_dates_end2, alpha=0.4, color='teal', label='Missing Data 2')

# Create a third y-axis for temperature
ax3 = ax1.twinx()
ax3.plot(data.index, data['AirTC_Avg'], label='Temperature (°C)', color='red', alpha=0.5)
ax3.set_ylabel('Temperature (°C)')
ax3.spines['right'].set_position(('outward', 60))  # Adjust the position of this axis
ax3.tick_params('y')

# Format the date and time labels on the x-axis
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y %H:%M:%S'))

# Set x-axis limits to span the full extent of the data
ax1.set_xlim(data.index[0], data.index[-1])
plt.xticks(rotation=30)

# Show the legend
ax1.legend(loc='upper left')
ax2.legend(loc='upper right')
ax3.legend(loc='upper center')

plt.title('Solar Irradiance, DC Power, and Temperature Over Time')

plt.tight_layout()
plt.show()