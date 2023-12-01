import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

class BatteryModel:
    def __init__(self, battery_name, c_rate, temperature):
        self.battery_name = battery_name
        self.c_rate = c_rate
        self.temperature = temperature

    def battery(self):
        # Define empty lists for the different battery parameters
        battery_percentage = []
        battery_voltage = []
        battery_current = []
        battery_cd_times = []

        # Set the values for different c_rates from the datasheet
        if self.battery_name == "48V_100Ah_5kWh" and self.c_rate == 0.2:
            battery_percentage = [0, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 100]
            battery_voltage = [44.5, 49.1, 50.5, 52.1, 52.5, 52.6, 52.7, 52.8, 52.9, 53, 53.3, 53.8, 55.5]  #45.5, 50.8, 51.3, 52.1, 52.5, 52.6, 52.7, 52.9, 53, 53.1, 53.3, 53.8, 55.5
            battery_current = [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 16, 1, 0.2]
            battery_cd_times = list(reversed( [300, 260, 249, 234, 185, 165, 153, 138, 111, 90, 75, 9, 0]))
        elif self.battery_name == "48V_100Ah_5kWh" and self.c_rate == 0.5:
            battery_percentage = [0, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 100]
            battery_voltage = [44.5, 49.1, 50.5, 52.1, 52.5, 52.6, 52.7, 52.8, 52.9, 53, 53.3, 53.8, 55.5]
            battery_current = [50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 40, 2.5, 0.5]
            battery_cd_times = list(reversed( [120, 98, 83, 40, 23, 18, 13, 11, 2, 0, 0, 0, 0]))
        elif self.battery_name == "48V_100Ah_5kWh" and self.c_rate == 1:
            battery_percentage = [0, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 100]
            battery_voltage = [44.5, 49.1, 50.5, 52.1, 52.5, 52.6, 52.7, 52.8, 52.9, 53, 53.3, 53.8, 55.5]
            battery_current = [100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 80, 5, 1]
            battery_cd_times = list(reversed( [60, 17 , 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]))
        elif self.battery_name == '48V_80Ah_3p84kWh' and self.c_rate == 0.5:
            battery_percentage = [0.1, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100]
            battery_voltage = list(reversed( [53.5, 52.8, 51.7, 51.2, 51.1, 51, 50.8, 50.7, 50.6, 50.5, 50.4, 50.3, 50.2, 50.1, 50, 49.8, 49.2, 48.5, 47.4, 43.8, 39.5] )) 
            battery_current = [40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 20, 10, 4, 2, 0.4, 0.4]
            battery_cd_times = [0, 0, 0, 0, 0, 0, 0, 0.5, 1, 2, 3, 4, 5, 7, 10, 20, 40, 60, 80, 100, 120]
            return self.battery_fit(battery_percentage, battery_current, battery_voltage, battery_cd_times, 5, 5, 4, 3)
        # Return the relative voltage, current battery %, and charge/discharge times with the coeffiecients for degree of polynomial
        return self.battery_fit(battery_percentage, battery_current, battery_voltage, battery_cd_times, 5, 5, 4, 3)            

            
    def battery_fit(self, battery_percentage, battery_current, battery_voltage, battery_cd_times, current_degrees, voltage_degrees, power_degrees, cd_degrees):
        # Get battery power
        battery_power = np.multiply(battery_current, battery_voltage)
        # Perform polynomial fits
        coefficients_voltage = np.polyfit(battery_percentage, battery_voltage, voltage_degrees)
        coefficients_current = np.polyfit(battery_percentage, battery_current, current_degrees)
        coefficients_power = np.polyfit(battery_percentage, battery_power, power_degrees)
        coefficients_cd_times = np.polyfit(battery_cd_times, battery_voltage, cd_degrees)
        # Get polynomial functions
        battery_voltage_plot = np.poly1d(coefficients_voltage)
        battery_current_plot = np.poly1d(coefficients_current)
        battery_power_plot = np.poly1d(coefficients_power)
        battery_cd_times_plot = np.poly1d(coefficients_cd_times)
        # Return the polynomial functions
        return battery_voltage_plot, battery_current_plot, battery_power_plot, battery_cd_times_plot

if __name__ == '__main__':
    battery1 = BatteryModel('48V_80Ah_3p84kWh', 0.5, 25)
    battery2 = BatteryModel('48V_100Ah_5kWh', 0.2, 25)
    battery3 = BatteryModel('48V_100Ah_5kWh', 0.5, 25)
    battery4 = BatteryModel('48V_100Ah_5kWh', 1.0, 25)

    battery_voltage_plot1, battery_current_plot1, battery_power_plot1, battery_cd_times_plot1 = battery1.battery()
    battery_voltage_plot2, battery_current_plot2, battery_power_plot2, battery_cd_times_plot2 = battery2.battery()
    battery_voltage_plot3, battery_current_plot3, battery_power_plot3, battery_cd_times_plot3 = battery3.battery()
    battery_voltage_plot4, battery_current_plot4, battery_power_plot4, battery_cd_times_plot4 = battery4.battery()

    bp1 = battery_power_plot1(np.linspace(0, 100, 102))
    bp1_positive = bp1[bp1 > 0]
    bp2 = battery_power_plot2(np.linspace(0, 100, 102))
    bp2_positive = bp2[bp2 > 0]
    bp3 = battery_power_plot3(np.linspace(0, 100, 102))
    bp3_positive = bp3[bp3 > 0]
    bp4 = battery_power_plot4(np.linspace(0, 100, 102))
    bp4_positive = bp4[bp4 > 0]

    plt.figure(figsize=(12, 6))
    plt.plot(bp1_positive, label='Battery 1')
    plt.plot(bp2_positive, label='Battery 2')
    plt.plot(bp3_positive, label='Battery 3')
    plt.plot(bp4_positive, label='Battery 4')

    # Plot setttings
    plt.grid(True)
    plt.title('Battery Charging Power at different SoC for different C-rates')
    plt.ylabel('Charging Power (W)')
    plt.xlabel('SoC (State of Charge %)')
    plt.legend(['48V_80Ah_$3.84$kWh', '48V_100Ah_5kWh_$0.2$', '48V_100Ah_5kWh_$0.5$', '48V_100Ah_5kWh_$1.0$'])
    plt.show()

    # Plot the battery voltage
    bv1 = battery_voltage_plot1(np.linspace(0, 100, 102))
    bv1 = bv1[bv1 > 0]
    bv2 = battery_voltage_plot2(np.linspace(0, 100, 102))
    bv2 = bv2[bv2 > 0]
    bv3 = battery_voltage_plot3(np.linspace(0, 100, 102))
    bv3 = bv3[bv3 > 0]
    bv4 = battery_voltage_plot4(np.linspace(0, 100, 102))
    bv4 = bv4[bv4 > 0]

    # Plot the battery current
    bc1 = battery_current_plot1(np.linspace(0, 100, 102))
    bc1 = bc1[bc1 > 0]
    bc2 = battery_current_plot2(np.linspace(0, 100, 102))
    bc2 = bc2[bc2 > 0]
    bc3 = battery_current_plot3(np.linspace(0, 100, 102))
    bc3 = bc3[bc3 > 0]
    bc4 = battery_current_plot4(np.linspace(0, 100, 102))
    bc4 = bc4[bc4 > 0]

    # Create subplots to display both voltage and current
    plt.figure(figsize=(12, 6))
    plt.subplot(121)  # 1 row, 2 columns, plot 1
    plt.plot(bv1, label='48V_80Ah_$3.84$kWh')
    plt.plot(bv2, label='48V_100Ah_5kWh_$0.2$')
    plt.plot(bv3, label='48V_100Ah_5kWh_$0.5$')
    plt.plot(bv4, label='48V_100Ah_5kWh_$1.0$')
    plt.grid(True)
    plt.title('Battery Voltage at different SoC for different C-rates')
    plt.ylabel('Voltage (V)')
    plt.xlabel('SoC (State of Charge %)')
    plt.legend()

    plt.subplot(122)  # 1 row, 2 columns, plot 2
    plt.plot(bc1, label='48V_80Ah_$3.84$kWh')
    plt.plot(bc2, label='48V_100Ah_5kWh_$0.2$')
    plt.plot(bc3, label='48V_100Ah_5kWh_$0.5$')
    plt.plot(bc4, label='48V_100Ah_5kWh_$1.0$')
    plt.grid(True)
    plt.title('Battery Current at different SoC for different C-rates')
    plt.ylabel('Current (A)')
    plt.xlabel('SoC (State of Charge %)')
    plt.legend()

    plt.tight_layout()  # Ensures the subplots do not overlap
    plt.show()

    # Assuming you have the data in cd_times1, cd_times2, cd_times3, and cd_times4
    cd_times1 = battery_cd_times_plot1(np.linspace(0, 120, 120))
    cd_times2 = battery_cd_times_plot2(np.linspace(0, 300, 300))
    cd_times3 = battery_cd_times_plot2(np.linspace(0, 300, 120))
    cd_times4 = battery_cd_times_plot3(np.linspace(0, 120, 60))

    # Plot the charge-discharge times
    plt.figure(figsize=(12, 6))
    plt.plot(cd_times1, label='Battery 1')
    plt.plot(cd_times2, label='Battery 2')
    plt.plot(cd_times3, label='Battery 3')
    plt.plot(cd_times4, label='Battery 4')

    # Plot settings
    plt.grid(True)
    plt.title('Battery Voltage over Charge Time for different C-rates')
    plt.ylabel('Voltage (V)')
    plt.xlabel('Charge-Discharge Time (m)')
    plt.legend(['48V_80Ah_$3.84$kWh', '48V_100Ah_5kWh_$0.2$', '48V_100Ah_5kWh_$0.5$', '48V_100Ah_5kWh_$1.0$'])
    plt.show()
    
# BSLBATT_B_LFP48_100E Battery that can also be used
