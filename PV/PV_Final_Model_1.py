import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from PV_bat_model import BatteryModel
from scipy.optimize import curve_fit
from pathlib import Path
from tqdm import tqdm
from numba import njit, prange

# All assignment and loading work to be done here
def get_battery_info(battery):
    battery_capacity = None
    n_charge = None
    n_discharge = None

    if battery.battery_name == '48V_80Ah_3p84kWh' and battery.c_rate == 0.5:
        battery_capacity = 3840
        n_charge = 0.99
        n_discharge = 0.99
        discharge_max = 80
    elif battery.battery_name == '48V_100Ah_5kWh' and battery.c_rate == 0.2:
        battery_capacity = 5120
        n_charge = 0.99
        n_discharge = 0.99
        discharge_max = 130
    elif battery.battery_name == '48V_100Ah_5kWh' and battery.c_rate == 0.5:
        battery_capacity = 5120
        n_charge = 0.99
        n_discharge = 0.98
        discharge_max = 130
    elif battery.battery_name == '48V_100Ah_5kWh' and battery.c_rate == 1:
        battery_capacity = 5120
        n_charge = 0.99
        n_discharge = 0.96
        discharge_max = 130
        
    return battery_capacity, n_charge, n_discharge, discharge_max

# Intialize the battery information
def initialize_battery_variables(data_length):
    # Initialize battery variables
    battery_SoC_min = 20
    battery_SoC_max = 100
    battery_SoC_initial = 50
    battery_energy = np.zeros(data_length)
    battery_energy[0] = 0
    SoC = np.zeros(data_length)
    SoC[0] = 0
    battery_voltage = np.zeros(data_length)
    
    # Initialize charging and discharging arrays
    battery_charging = np.zeros(data_length)
    battery_discharge = np.zeros(data_length)

    return (battery_SoC_min, battery_SoC_max, battery_SoC_initial, battery_energy,
        SoC, battery_voltage, battery_charging, battery_discharge,
    )

# Load the 'Final_Data_PV.csv' file
data = pd.read_csv('Final_Data_PV.csv')

# Convert 'TmStamp' column to datetime format
data['TmStamp'] = pd.to_datetime(data['TmStamp'], format='%Y/%m/%d %H:%M:%S')

'''
# Read the clear sky dates from the text file
clear_sky_dates = []
with open('clear_sky_days.txt', 'r') as file:
    for line in file:
        clear_sky_dates.append(line.strip())
'''

# Filter the data for the clear sky dates
# filtered_data = data[data['TmStamp'].dt.strftime('%d/%m/%Y').isin(clear_sky_dates)]
filtered_data = pd.read_csv('Final_Data_PV_Clear.csv')

# Convert 'TmStamp' column to datetime format
filtered_data['TmStamp'] = pd.to_datetime(data['TmStamp'], format='%Y/%m/%d %H:%M:%S')
filtered_data['Time'] = pd.to_datetime(filtered_data['Time'], format='%H:%M:%S')
time_stamp = filtered_data['TmStamp']
time = filtered_data['Time'].dt.time

# Assign load data
load_energy = filtered_data['Total E']

# Read PV power data from the filtered data and convert to Wh
pv_energy = filtered_data['p_dc_m']*0.5

#Calculate the difference between the total load energy and total PV energy
required_energy = load_energy - pv_energy
excess_energy = pv_energy - load_energy
# Set negative values to 0
for i in range(len(required_energy)):
    if required_energy.iloc[i] < 0:
        required_energy.iloc[i] = 0
    elif excess_energy.iloc[i] < 0:
        excess_energy.iloc[i] = 0

# Assign the grid energy
grid_energy = np.zeros(len(filtered_data))    

# Assign different charge states
battery_charging_pv = np.zeros(len(filtered_data))
battery_charging_grid = np.zeros(len(filtered_data))   
     
# Assign the battery model to a variable
battery = BatteryModel('48V_100Ah_5kWh', 0.5, 25)
battery_max = BatteryModel('48V_100Ah_5kWh', 1, 25)

# Call the battery function and assign the returned values to variables
battery_voltage_plot1, battery_current_plot1, battery_power_plot1, battery_cd_times_plot1 = battery.battery()
battery_voltage_plot_max, battery_current_plot_max, battery_power_plot_max, battery_cd_times_plot_max = battery_max.battery()
# Additional battery information
(battery_capacity, n_charge, n_discharge, discharge_max) = get_battery_info(battery)

# Battery variables
(battery_SoC_min, battery_SoC_max, battery_SoC_initial, battery_energy, SoC, 
 battery_voltage, battery_charging, battery_discharge) = initialize_battery_variables(len(filtered_data))

# State variables, for different priorities throughout day
state_priority_grid = False
state_priority_battery = True
state_priority_pv = False
state_check = True

#-------------Simulate System-----------------

for i in range(len(filtered_data)):
    # Check if the current time_stamp is the first time_stamp
    if time_stamp[i] == filtered_data['TmStamp'].iloc[0]:
        battery_voltage[i] = battery_voltage_plot1(battery_SoC_initial)
        print(battery_voltage[i])
        print(battery_voltage_plot1(0))       
        print(battery_voltage_plot1(100))
        SoC[i] = battery_SoC_initial
        battery_energy[i] = battery_capacity * SoC[i] / 100
        # Set state to grid
        state_priority_grid = True
    
    # For subsequent time_stamps
    elif time_stamp[i] > filtered_data['TmStamp'].iloc[0]:
        # Convert the strings to datetime objects
        start_time1 = pd.to_datetime('06:00:00').time()         # Start1-End1 for monrings
        end_time1 = pd.to_datetime('9:00:00').time()            # End1-Start2 for midday
        start_time2 = pd.to_datetime('18:00:00').time()         # Start2-End2 for evenings
        end_time2 = pd.to_datetime('21:00:00').time()           # End2-Start1 for nights
        
        #-------------System Requires Energy-----------------
        
        # Check if required_energy is greater than zero, meaning load is more than PV can supply
        if required_energy.iloc[i] > 0:
            current_time = time[i]  # Update current_time
            
        #-------------All instances-----------------
        # Make the grid carry load only export if excess, battery is always at 100%
    
            #-------------Scenario 1: Grid to charge battery and supply load-----------------  
            # Check if states are changed
            # Calculate battery energy but first charging required, note grid used due to battery unable to supply load
            battery_charging_grid[i] = battery_power_plot1(SoC[i-1]) * n_charge * 0.5
            if battery_charging_grid[i] < 0:
                battery_charging_grid[i] = 0
            battery_charging_pv[i] = excess_energy[i] * n_charge                            # Excess energy is used as pv charging
            # Assign charge energy, note no battery discharge will happen due to state                    
            battery_charging[i] = battery_charging_grid[i] + battery_charging_pv[i]
            # Check that charge does not exceed 1C charge
            if battery_charging[i] > battery_power_plot_max(SoC[i-1]) * n_charge * 0.5:
                battery_charging[i] = battery_power_plot_max(SoC[i-1]) * n_charge * 0.5     # If it does, set to 1C
                if battery_charging[i] < 0:
                    battery_charging[i] = 0
                battery_charging_grid[i] = battery_charging[i] - battery_charging_pv[i]     # If charge greater than 1C, change grid value to use full pv charge, negative is push back
            else:
                battery_charging[i] = battery_charging[i]                    
            # Calculate battery energy
            battery_energy[i] = battery_energy[i-1] + battery_charging[i]                   # Takes into account excess
            # Calculate grid energy meaning load (required) and charge
            grid_energy[i] = required_energy[i] + battery_charging_grid[i]              
            # Check if battery energy is greater than battery capacity, if yes, assign to grid
            if battery_energy[i] > battery_capacity:
                grid_energy[i] = grid_energy[i] - (battery_energy[i] - battery_capacity)   # If battery is over push excess to grid
                battery_charging[i] = battery_charging[i] - (battery_energy[i] - battery_capacity)                          
                battery_energy[i] = battery_capacity                                       # NB if error on charge values subtract excess amount form battery_charging[i], check next line
            elif battery_energy[i] < 0:
                battery_energy[i] = 0
            else:
                battery_energy[i] = battery_energy[i]
            # Calculate SoC
            SoC[i] = battery_energy[i] / battery_capacity * 100
            # Check SoC to ensure it is within limits and state transition
            if SoC[i] < 0:
                SoC[i] = 0
                #state_priority_grid = True
                #state_priority_battery  = False                        
            elif SoC[i] >= 100:
                SoC[i] = 100
                #state_priority_grid = True
                #state_priority_battery  = False
                #state_check = False
            elif SoC[i] >= battery_SoC_initial:
                state_priority_grid = True
                #state_priority_battery = False
                #state_check = False
            elif SoC[i] < battery_SoC_min:
                #state_priority_battery = False
                state_priority_grid = True
            # Get battery voltage form SoC
            battery_voltage[i] = battery_voltage_plot1(SoC[i])
            # Check battery voltage
            if battery_voltage[i] < battery_voltage_plot1(0):
                battery_voltage[i] = battery_voltage_plot1(0)
            elif battery_voltage[i] > battery_voltage_plot1(100):
                battery_voltage[i] = battery_voltage_plot1(100)
            else:
                battery_voltage[i] = battery_voltage[i]

        #-------------System has Excess Energy-----------------
        # Check if excess energy is greater than zero, meaning PV is more Load can supply
        if excess_energy.iloc[i] > 0:
            current_time = time[i]  # Update current_time
            #-------------Mornings and Afternoons-----------------
            # Check if the current time is within the specified range for day time
            if start_time1 <= current_time <= start_time2:
                
                #-------------Battery & PV can supply in time-----------------                               
                # Calculate battery energy but first charging required, note PV only used due to excess energy no grid
                battery_charging_pv[i] = excess_energy[i] * n_charge                            # Excess energy is used as pv charging
                # Assign charge energy, note only form PV and discharge should be zero due to excess > 0                    
                battery_charging[i] = battery_charging_grid[i] + battery_charging_pv[i]         # Grid charge will be zero
                # Check that charge does not exceed 1C charge
                if battery_charging[i] > battery_power_plot_max(SoC[i-1]) * n_charge * 0.5:
                    battery_charging[i] = battery_power_plot_max(SoC[i-1]) * n_charge * 0.5     # If it does, set to 1C
                    if battery_charging[i] < 0:
                        battery_charging[i] = 0
                    battery_charging_grid[i] = battery_charging[i] - battery_charging_pv[i]     # If charge greater than 1C, change grid value to use full pv charge, negative is push back     
                    battery_charging_pv[i] = battery_charging[i]                                # If charge greater than 1C, change pv value to use full max charge value with excess, negative is push back into grid               
                else:
                    battery_charging[i] = battery_charging_grid[i] + battery_charging_pv[i]
                
                # Calculate battery energy
                battery_energy[i] = battery_energy[i-1] + battery_charging[i]                   # Takes into account excess, make sure not exceeding charge limit plus load supplied by pv
                # Calculate grid energy meaning only excess energy being pushed back
                grid_energy[i] = battery_charging_grid[i]/n_charge
                # Check if battery energy is greater than battery capacity, if yes, assign to grid
                if battery_energy[i] > battery_capacity:
                    grid_energy[i] = grid_energy[i] - (battery_energy[i] - battery_capacity)   # If battery is over push excess to grid   
                    battery_charging[i] = battery_charging[i] - (battery_energy[i] - battery_capacity)                    
                    battery_energy[i] = battery_capacity
                elif battery_energy[i] < 0:
                    battery_energy[i] = 0
                else:
                    battery_energy[i] = battery_energy[i]
                # Calculate SoC
                SoC[i] = battery_energy[i] / battery_capacity * 100
                # Check SoC to ensure it is within limits and state transition
                if SoC[i] < 0:
                    SoC[i] = 0
                    state_priority_grid = True
                elif SoC[i] >= 100:
                    SoC[i] = 100
                    state_priority_grid = False
                    state_priority_battery  = True
                    state_check = True
                elif SoC[i] >= battery_SoC_initial:
                    state_priority_grid = False
                    state_priority_battery = True
                    state_check = True
                elif SoC[i] < battery_SoC_min:
                    state_priority_battery = False
                    state_priority_grid = True
                # Get battery voltage form SoC
                battery_voltage[i] = battery_voltage_plot1(SoC[i])
                # Check battery voltage
                if battery_voltage[i] < battery_voltage_plot1(0):
                    battery_voltage[i] = battery_voltage_plot1(0)
                elif battery_voltage[i] > battery_voltage_plot1(100):
                    battery_voltage[i] = battery_voltage_plot1(100)
                else:
                    battery_voltage[i] = battery_voltage[i]               

        #-------------No Data for Days-----------------
        # Check for instances that do not have data
        elif excess_energy.iloc[i] == 0 and required_energy.iloc[i] ==0:
            SoC[i] = 0
            battery_voltage[i] = battery_voltage_plot1(SoC[i])
            battery_energy[i] = battery_capacity * SoC[i] / 100
            #print("No data")
                   

# Update the 'Final_Data_PV_Clear.csv' file with the new data
data_to_append = pd.DataFrame({
    'TmStamp': time_stamp,
    'PV Energy': pv_energy,
    'Battery Energy': battery_energy,
    'SoC': SoC,
    'Battery Voltage': battery_voltage,
    'Required Energy': required_energy,
    'Excess Energy': excess_energy,
    'Grid Energy': grid_energy,
    'Charging': battery_charging,
    'Discharging': battery_discharge
})

# Write the combined DataFrame back to 'PV_Final_Model_Bat.csv' with column headings
data_to_append.to_csv('Final_Data_Bat_1.csv', index=False, header=True)
            
# Create a figure and axis
fig, ax = plt.subplots(figsize=(12, 6))
# Plot total_load_energy with a blue line and label
ax.plot(time_stamp, load_energy, label='Total Load Energy (Wh)', color='blue', alpha = 0.7)
#ax.plot(time_stamp, data['SunWM_Avg'], label='Ghi(W/m2)', color='blue', alpha = 0.7)
# Plot total_pv_energy with a green line and label
ax.plot(time_stamp, pv_energy, label='Total PV Energy (Wh)', color='green', alpha = 0.7)
# Plot required_energy with a red line and label
ax.plot(time_stamp, required_energy, label='Total Needed Energy (Wh)', color='red', alpha = 0.7)
# Plot excess_energy with a orange line and label
ax.plot(time_stamp, excess_energy, label='Total Excess Energy (Wh)', color='orange', alpha = 0.7)
# Plot battery_energy with a purple line and label
ax.plot(time_stamp, battery_energy, label='Battery Energy (Wh)', color='purple', alpha = 0.7)
# Plot grid_energy with a gray line and label
ax.plot(time_stamp, grid_energy, label='Grid Energy (Wh)', color='gray', alpha = 0.7)
# Set labels and title
ax.set_xlabel('Date and Time')
ax.set_ylabel('Energy (Wh)')
ax.set_title('Total Load Energy and Total PV Energy')
# Format the date and time_stamp labels on the x-axis
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y %H:%M:%S'))
# Set x-axis limits to span the full extent of the data
plt.xlim(filtered_data['TmStamp'].iloc[0], filtered_data['TmStamp'].iloc[-1])
plt.xticks(rotation=30)
plt.tight_layout()
# Increase white space below the image
plt.subplots_adjust(bottom=0.2)
ax.legend(loc = 'upper right')
plt.show()

# Create a figure for voltage and SoC
fig, ax1 = plt.subplots(figsize=(12, 6))
# Plot battery voltage with a blue line and label on the left y-axis (ax1)
line1, = ax1.plot(time_stamp, battery_voltage, label='Battery Voltage (V)', color='red', alpha=0.7)
ax1.set_xlabel('Date and Time')
ax1.set_ylabel('Battery Voltage (V)')
ax1.tick_params(axis='y')
plt.xticks(rotation=30)
# Create a secondary y-axis on the right (ax2) for SoC
ax2 = ax1.twinx()
line2, = ax2.plot(time_stamp, SoC, label='State of Charge (SoC)', color='royalblue', alpha=0.7)
ax2.set_ylabel('State of Charge (SoC)')
ax2.tick_params(axis='y')
# Set the title
plt.title('Battery Voltage and State of Charge (SoC)')
# Format the date and time labels on the x-axis
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y %H:%M:%S'))
# Set x-axis limits to span the full extent of the data
plt.xlim(filtered_data['TmStamp'].iloc[0], filtered_data['TmStamp'].iloc[-1])
plt.xticks(rotation=30)
# Show the legend
handles = [line1, line2]
ax1.legend(handles, [handle.get_label() for handle in handles], loc='upper right')
plt.tight_layout()
plt.show()