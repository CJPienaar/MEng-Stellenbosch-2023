import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd

# Filter the data for the clear sky dates
data = pd.read_csv('Final_Data_PV.csv')
filtered_data = pd.read_csv('Final_Data_PV_Clear_3B.csv')

# Get ToU tariff information
ToU = pd.read_csv('ToU_Stellenbosch.csv')
ToU_Low = pd.read_csv('ToU_Low_Stellenbosch.csv')
ToU_High = pd.read_csv('ToU_High_Stellenbosch.csv')

# Convert 'TmStamp' column to datetime format
filtered_data['TmStamp'] = pd.to_datetime(filtered_data['TmStamp'], format='%Y/%m/%d %H:%M:%S')
filtered_data['Time'] = pd.to_datetime(filtered_data['Time'], format='%H:%M:%S')
time_stamp = filtered_data['TmStamp']
time = filtered_data['Time']
weekday = filtered_data['Weekday']

# Get the grid information Wh from 'Grid Energy' column convert to kWh
grid_energy = filtered_data['Grid Energy']/1000
import_enrgy = filtered_data['Import amount']/1000
export_enrgy = filtered_data['Export amount']/1000

# Define cost variable
cost_back = np.zeros(len(time_stamp))
cost_pay = np.zeros(len(time_stamp))

# Function to determine the tariff based on date, time, and demand period
def get_tariff(row):
    date = pd.to_datetime(row['TmStamp']).date()

    if pd.to_datetime('2021-05-01').date() <= date <= pd.to_datetime('2021-06-30').date():
        demand_period = '2020/21'
    elif pd.to_datetime('2021-07-01').date() <= date <= pd.to_datetime('2022-06-30').date():
        demand_period = '2021/22'
    elif pd.to_datetime('2022-07-01').date() <= date <= pd.to_datetime('2023-06-30').date():
        demand_period = '2022/23'
    else:
        demand_period = 'Unknown'

    if pd.to_datetime('2021-05-01').date() <= date <= pd.to_datetime('2021-06-30').date():
        demand_season = 'Low' if date.month >= 9 or date.month <= 5 else 'High'
    elif pd.to_datetime('2021-07-01').date() <= date <= pd.to_datetime('2022-06-30').date():
        demand_season = 'Low' if date.month >= 9 and date.month <= 6 else 'High'
    elif pd.to_datetime('2022-07-01').date() <= date <= pd.to_datetime('2023-06-30').date():
        demand_season = 'Low' if date.month >= 9 and date.month <= 6 else 'High'
    else:
        demand_season = 'Unknown'

    return demand_period, demand_season

    
for i in range(len(time_stamp)):
    demand_period, demand_season = get_tariff(filtered_data.iloc[i])
    if grid_energy[i] < 0:
        if demand_period == '2020/21':
            Reading_cost_202021 = ToU['2020/21 Reading cost R/pm']*2
            Basic_cost_202021 = ToU['2020/21 Basic Charge']*2
            if demand_season == 'Low':
                if weekday.iloc[i] in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
                    if pd.to_datetime('00:00:00').time() < time[i].time() <= pd.to_datetime('06:00:00').time() or pd.to_datetime('22:00:00').time() < time[i].time() <= pd.to_datetime('00:00:00').time():
                        cost_back[i] =  grid_energy[i] * ToU['2020/21 Export Low Off']/100 
                    elif pd.to_datetime('06:00:00').time() < time[i].time() <= pd.to_datetime('07:00:00').time() or pd.to_datetime('10:00:00').time() < time[i].time() <= pd.to_datetime('18:00:00').time() or pd.to_datetime('20:00:00').time() < time[i].time() <= pd.to_datetime('22:00:00').time():
                        cost_back[i] = grid_energy[i] * ToU['2020/21 Export Low Standard']/100 
                    else:
                        cost_back[i] = grid_energy[i] * ToU['2020/21 Export Low Peak']/100 
                elif weekday.iloc[i] == 'Saturday':
                    if pd.to_datetime('00:00:00').time() < time[i].time() <= pd.to_datetime('07:00:00').time() or pd.to_datetime('12:00:00').time() < time[i].time() <= pd.to_datetime('18:00:00').time() or pd.to_datetime('20:00:00').time() < time[i].time() <= pd.to_datetime('00:00:00').time():
                        cost_back[i] =  grid_energy[i] * ToU['2020/21 Export Low Off']/100 
                    else:
                        cost_back[i] = grid_energy[i] * ToU['2020/21 Export Low Standard']/100 
                elif weekday.iloc[i] == 'Sunday':
                    cost_back[i] = grid_energy[i] * ToU['2020/21 Export Low Off']/100 
            elif demand_season == 'High':
                if weekday.iloc[i] in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
                    if pd.to_datetime('00:00:00').time() < time[i].time() <= pd.to_datetime('06:00:00').time() or pd.to_datetime('22:00:00').time() < time[i].time() <= pd.to_datetime('00:00:00').time():
                        cost_back[i] =  grid_energy[i] * ToU['2020/21 Export Low Off']/100 
                    elif pd.to_datetime('09:00:00').time() < time[i].time() <= pd.to_datetime('17:00:00').time() or pd.to_datetime('19:00:00').time() < time[i].time() <= pd.to_datetime('22:00:00').time():
                        cost_back[i] = grid_energy[i] * ToU['2020/21 Export Low Standard']/100 
                    else:
                        cost_back[i] = grid_energy[i] * ToU['2020/21 Export Low Peak']/100                
                elif weekday.iloc[i] == 'Saturday':
                    if pd.to_datetime('00:00:00').time() < time[i].time() <= pd.to_datetime('07:00:00').time() or pd.to_datetime('12:00:00').time() < time[i].time() <= pd.to_datetime('18:00:00').time() or pd.to_datetime('20:00:00').time() < time[i].time() <= pd.to_datetime('00:00:00').time():
                        cost_back[i] =  grid_energy[i] * ToU['2020/21 Export Low Off']/100 
                    else:
                        cost_back[i] = grid_energy[i] * ToU['2020/21 Export Low Standard']/100                     
                elif weekday.iloc[i] == 'Sunday':
                    cost_back[i] = grid_energy[i] * ToU['2020/21 Export Low Off']/100                    
        elif demand_period == '2021/22':
            Reading_cost_202122 = ToU['2021/22 Reading cost R/pm']*12
            Basic_cost_202122 = ToU['2021/22 Basic Charge']*12
            if demand_season == 'Low':
                if weekday.iloc[i] in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
                    if pd.to_datetime('00:00:00').time() < time[i].time() <= pd.to_datetime('06:00:00').time() or pd.to_datetime('22:00:00').time() < time[i].time() <= pd.to_datetime('00:00:00').time():
                        cost_back[i] =  grid_energy[i] * ToU['2020/21 Export Low Off']/100 
                    elif pd.to_datetime('06:00:00').time() < time[i].time() <= pd.to_datetime('07:00:00').time() or pd.to_datetime('10:00:00').time() < time[i].time() <= pd.to_datetime('18:00:00').time() or pd.to_datetime('20:00:00').time() < time[i].time() <= pd.to_datetime('22:00:00').time():
                        cost_back[i] = grid_energy[i] * ToU['2021/22 Export Low Standard']/100 
                    else:
                        cost_back[i] = grid_energy[i] * ToU['2021/22 Export Low Peak']/100 
                elif weekday.iloc[i] == 'Saturday':
                    if pd.to_datetime('00:00:00').time() < time[i].time() <= pd.to_datetime('07:00:00').time() or pd.to_datetime('12:00:00').time() < time[i].time() <= pd.to_datetime('18:00:00').time() or pd.to_datetime('20:00:00').time() < time[i].time() <= pd.to_datetime('00:00:00').time():
                        cost_back[i] =  grid_energy[i] * ToU['2021/22 Export Low Off']/100 
                    else:
                        cost_back[i] = grid_energy[i] * ToU['2021/22 Export Low Standard']/100 
                elif weekday.iloc[i] == 'Sunday':
                    cost_back[i] = grid_energy[i] * ToU['2021/22 Export Low Off']/100 
            elif demand_season == 'High':
                if weekday.iloc[i] in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
                    if pd.to_datetime('00:00:00').time() < time[i].time() <= pd.to_datetime('06:00:00').time() or pd.to_datetime('22:00:00').time() < time[i].time() <= pd.to_datetime('00:00:00').time():
                        cost_back[i] =  grid_energy[i] * ToU['2021/22 Export Low Off']
                    elif pd.to_datetime('09:00:00').time() < time[i].time() <= pd.to_datetime('17:00:00').time() or pd.to_datetime('19:00:00').time() < time[i].time() <= pd.to_datetime('22:00:00').time():
                        cost_back[i] = grid_energy[i] * ToU['2021/22 Export Low Standard']/100 
                    else:
                        cost_back[i] = grid_energy[i] * ToU['2021/22 Export Low Peak']/100                 
                elif weekday.iloc[i] == 'Saturday':
                    if pd.to_datetime('00:00:00').time() < time[i].time() <= pd.to_datetime('07:00:00').time() or pd.to_datetime('12:00:00').time() < time[i].time() <= pd.to_datetime('18:00:00').time() or pd.to_datetime('20:00:00').time() < time[i].time() <= pd.to_datetime('00:00:00').time():
                        cost_back[i] =  grid_energy[i] * ToU['2021/22 Export Low Off']/100 
                    else:
                        cost_back[i] = grid_energy[i] * ToU['2021/22 Export Low Standard']/100                     
                elif weekday.iloc[i] == 'Sunday':
                    cost_back[i] = grid_energy[i] * ToU['2021/22 Export Low Off']/100   
        elif demand_period == '2022/23':
            Reading_cost_202223 = ToU['2022/23 Reading cost R/pm']*11
            Basic_cost_202223 = ToU['2022/23 Basic Charge']*11
            if demand_season == 'Low':
                if weekday.iloc[i] in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
                    if pd.to_datetime('00:00:00').time() < time[i].time() <= pd.to_datetime('06:00:00').time() or pd.to_datetime('22:00:00').time() < time[i].time() <= pd.to_datetime('00:00:00').time():
                        cost_back[i] =  grid_energy[i] * ToU['2022/23 Export Low Off']/100 
                    elif pd.to_datetime('06:00:00').time() < time[i].time() <= pd.to_datetime('07:00:00').time() or pd.to_datetime('10:00:00').time() < time[i].time() <= pd.to_datetime('18:00:00').time() or pd.to_datetime('20:00:00').time() < time[i].time() <= pd.to_datetime('22:00:00').time():
                        cost_back[i] = grid_energy[i] * ToU['2022/23 Export Low Standard']/100 
                    else:
                        cost_back[i] = grid_energy[i] * ToU['2022/23 Export Low Peak']/100 
                elif weekday.iloc[i] == 'Saturday':
                    if pd.to_datetime('00:00:00').time() < time[i].time() <= pd.to_datetime('07:00:00').time() or pd.to_datetime('12:00:00').time() < time[i].time() <= pd.to_datetime('18:00:00').time() or pd.to_datetime('20:00:00').time() < time[i].time() <= pd.to_datetime('00:00:00').time():
                        cost_back[i] =  grid_energy[i] * ToU['2022/23 Export Low Off']/100 
                    else:
                        cost_back[i] = grid_energy[i] * ToU['2022/23 Export Low Standard']/100 
                elif weekday.iloc[i] == 'Sunday':
                    cost_back[i] = grid_energy[i] * ToU['2022/23 Export Low Off']/100 
            elif demand_season == 'High':
                if weekday.iloc[i] in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
                    if pd.to_datetime('00:00:00').time() < time[i].time() <= pd.to_datetime('06:00:00').time() or pd.to_datetime('22:00:00').time() < time[i].time() <= pd.to_datetime('00:00:00').time():
                        cost_back[i] =  grid_energy[i] * ToU['2022/23 Export Low Off']/100 
                    elif pd.to_datetime('09:00:00').time() < time[i].time() <= pd.to_datetime('17:00:00').time() or pd.to_datetime('19:00:00').time() < time[i].time() <= pd.to_datetime('22:00:00').time():
                        cost_back[i] = grid_energy[i] * ToU['2022/23 Export Low Standard']/100 
                    else:
                        cost_back[i] = grid_energy[i] * ToU['2022/23 Export Low Peak']/100                 
                elif weekday.iloc[i] == 'Saturday':
                    if pd.to_datetime('00:00:00').time() < time[i].time() <= pd.to_datetime('07:00:00').time() or pd.to_datetime('12:00:00').time() < time[i].time() <= pd.to_datetime('18:00:00').time() or pd.to_datetime('20:00:00').time() < time[i].time() <= pd.to_datetime('00:00:00').time():
                        cost_back[i] =  grid_energy[i] * ToU['2022/23 Export Low Off']/100
                    else:
                        cost_back[i] = grid_energy[i] * ToU['2022/23 Export Low Standard']  /100                  
                elif weekday.iloc[i] == 'Sunday':
                    cost_back[i] = grid_energy[i] * ToU['2022/23 Export Low Off']/100 
    elif grid_energy[i] > 0:
        if demand_period == '2020/21':
            cost_pay[i] = grid_energy[i] * ToU['2020/21 Import 600']/100        # Divide by 100 because the tariff is in cents, need R
        elif demand_period == '2021/22':
            cost_pay[i] = grid_energy[i] * ToU['2021/22 Import 600']/100          
        elif demand_period == '2022/23':                
            cost_pay[i] = grid_energy[i] * ToU['2022/23 Import 600']/100
            
# Calculate LCOE variables
initial_investment = 110000  # Initial investment cost in rands
operating_costs = 3000      # Annual operating and maintenance costs in rands
total_operating_costs = 0.0 # Variable to sum the total operating costs over the lifetime
lifetime_years = 20         # System lifetime in years
electricity_price = 245.71  # Initial price per kilowatt-hour in cents
average_electricity_price = 0.0  # Average electricity price over the lifetime
annual_price_increase = 0.07  # Annual increase in electricity price
total_electricity_generated = np.zeros(lifetime_years)  # Total electricity generated over the lifetime
sum_total_electricity_generated = 0.0   # Variable to sum the total electricity generated over the lifetime

# Apply 1% degradation per year for the PV panels
for i in range(lifetime_years):
    # Calculate total electricity generated over the lifetime
    if i == 0:
        total_electricity_generated[i] = (data['p_dc_m'].sum()/2)/1000  # Considering the variable for 2 years and 1 month amd 1000 for W to kW
    else:
        total_electricity_generated[i] = total_electricity_generated[i - 1] * (1 - 0.01)

    sum_total_electricity_generated += total_electricity_generated[i]
    average_electricity_price += electricity_price * (1 + annual_price_increase) ** i
    total_operating_costs += operating_costs * (1 + annual_price_increase) ** i

average_electricity_price /= lifetime_years

total_cost = initial_investment + total_operating_costs
total_revenue = sum_total_electricity_generated * (average_electricity_price / 100)  # Convert cents to rands
# Get LCOE
lcoe = total_cost / sum_total_electricity_generated

print("The Levelized Cost of Electricity (LCOE) is:", lcoe, "rands per kilowatt-hour")
    
# Create a DataFrame with the required columns
result_df = pd.DataFrame({
    'time_stamp': time_stamp,
    'grid_energy': grid_energy,
    ' import_energy': import_enrgy,
    'export_energy': export_enrgy,
    'cost_pay': cost_pay,
    'cost_back': cost_back
})

# Save the DataFrame to a CSV file
result_df.to_csv('Cost_3B.csv', index=False)
