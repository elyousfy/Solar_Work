# Import necessary libraries
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from battery import Battery


# Load the data into the variable DF
df = pd.read_csv('Data Analysis\PV_raw_data.csv')

# Drop data points that have zero AC output and unneeded columns
df_cleaned = df.copy()
df_cleaned.drop(columns=['Beam Irradiance (W/m2)', 'Diffuse Irradiance (W/m2)', 
                         'Ambient Temperature (C)', 'Wind Speed (m/s)', 
                         'Plane of Array Irradiance (W/m2)', 'Cell Temperature (C)', 
                         'DC Array Output (W)', 'Albedo'], inplace=True)

# Transform the DF into datetime
df_cleaned['year'] = 2023
df_cleaned['datetime'] = pd.to_datetime(df_cleaned[['year', 'Month', 'Day', 'Hour']])
df_cleaned.set_index('datetime', inplace=True)
df_cleaned.drop(columns=['Month', 'Day', 'Hour', 'year'], inplace=True)

# Convert AC power output into MWh
df_cleaned['Energy Generated (MWh)'] = df_cleaned['AC System Output (W)'] * 0.000001

# Set some parameters
min_energy_consumption = 6
max_energy_consumption = 100

# Create lists to store results
battery_sizes = list(range(12, 121, 1))
yearly_energy_stored = []

# Loop through different battery sizes and calculate the yearly energy stored
# for energy_capacity in battery_sizes:
#     Battery_12MW_XMWh = Battery(power_capacity=12, energy_capacity=energy_capacity, efficiency=1)
    
#     # Create Series to save data in and join to the main data frame later
#     energy_consumption_battery = pd.Series(0, index=df_cleaned.index)
#     energy_consumption_no_battery = pd.Series(0, index=df_cleaned.index)
#     excess_energy = pd.Series(0, index=df_cleaned.index)
#     Battery_charge = pd.Series(0, index=df_cleaned.index)
    
#     for date, ac_output_mwh in df_cleaned['Energy Generated (MWh)'].items():
#         Battery_charge[date] = Battery_12MW_XMWh.get_charge()
#         if ac_output_mwh > min_energy_consumption:  # Minimum to enter the grid
#             if ac_output_mwh > max_energy_consumption:  # Maximum to enter the grid
#                 energy_consumption_battery[date] = max_energy_consumption
#                 energy_consumption_no_battery[date] = max_energy_consumption
#                 excess_energy[date] = ac_output_mwh - max_energy_consumption
#                 Battery_12MW_XMWh.charge(power=excess_energy[date]) 
#             else:  # Energy is within the max and min
#                 energy_consumption_battery[date] = ac_output_mwh
#                 energy_consumption_no_battery[date] = ac_output_mwh
#         else:  # Energy less than min
#             if Battery_12MW_XMWh.get_charge() > min_energy_consumption:
#                 energy_consumption_battery[date] = Battery_12MW_XMWh.discharge(power=12-ac_output_mwh) + ac_output_mwh
#             energy_consumption_no_battery[date] = 0
#         if energy_consumption_battery[date] <= min_energy_consumption:
#             Battery_12MW_XMWh.charge(power=ac_output_mwh)
#             energy_consumption_battery[date] = 0

#     # Explicitly set any 0 values to NaN if needed
#     energy_consumption_battery.replace(0, np.nan, inplace=True)
#     energy_consumption_no_battery.replace(0, np.nan, inplace=True)
    
#     # Drop NaN values
#     energy_consumption_battery_cleaned = energy_consumption_battery.dropna()
#     energy_consumption_no_battery_cleaned = energy_consumption_no_battery.dropna()
    
#     # Calculate energy differences
#     energy_consumption_cleaned_month = energy_consumption_battery_cleaned.resample('M').sum()
#     energy_consumption_no_battery_cleaned_month = energy_consumption_no_battery_cleaned.resample('M').sum()
#     energy_difference = energy_consumption_cleaned_month - energy_consumption_no_battery_cleaned_month
    
#     # Sum the yearly energy stored
#     yearly_energy_stored.append(energy_difference.sum())

# print(yearly_energy_stored)
# # Plot the yearly energy stored for different battery sizes
# plt.figure(figsize=(12, 6))
# plt.plot(battery_sizes, yearly_energy_stored, marker='o')
# plt.title('Yearly Energy Stored by Battery vs. Battery Size')
# plt.xlabel('Battery Size (MWh)')
# plt.ylabel('Yearly Energy Stored (MWh)')
# plt.grid(True)
# plt.show()

# Create a heat map of power vs. energy capacity
power_capacities = list(range(7, 24))  # Assuming power capacity ranges from 1MW to 12MW
energy_capacities = range(10,130,10)

heat_map_data = np.zeros((len(power_capacities), len(energy_capacities)))

for i, power_capacity in enumerate(power_capacities):
    for j, energy_capacity in enumerate(energy_capacities):
        Battery_XMW_XMWh = Battery(power_capacity=power_capacity, energy_capacity=energy_capacity, efficiency=1)
        
        # Reset data for the new battery configuration
        energy_consumption_battery = pd.Series(0, index=df_cleaned.index)
        energy_consumption_no_battery = pd.Series(0, index=df_cleaned.index)
        excess_energy = pd.Series(0, index=df_cleaned.index)
        Battery_charge = pd.Series(0, index=df_cleaned.index)
        
        for date, ac_output_mwh in df_cleaned['Energy Generated (MWh)'].items():
            Battery_charge[date] = Battery_XMW_XMWh.get_charge()
            if ac_output_mwh > min_energy_consumption:
                if ac_output_mwh > max_energy_consumption:
                    energy_consumption_battery[date] = max_energy_consumption
                    energy_consumption_no_battery[date] = max_energy_consumption
                    excess_energy[date] = ac_output_mwh - max_energy_consumption
                    Battery_XMW_XMWh.charge(power=excess_energy[date])
                else:
                    energy_consumption_battery[date] = ac_output_mwh
                    energy_consumption_no_battery[date] = ac_output_mwh
            else:
                if Battery_XMW_XMWh.get_charge() > min_energy_consumption:
                    energy_consumption_battery[date] = Battery_XMW_XMWh.discharge(power=power_capacity-ac_output_mwh) + ac_output_mwh
                energy_consumption_no_battery[date] = 0
            if energy_consumption_battery[date] <= min_energy_consumption:
                Battery_XMW_XMWh.charge(power=ac_output_mwh)
                energy_consumption_battery[date] = 0
        
        energy_consumption_battery.replace(0, np.nan, inplace=True)
        energy_consumption_no_battery.replace(0, np.nan, inplace=True)
        
        energy_consumption_battery_cleaned = energy_consumption_battery.dropna()
        energy_consumption_no_battery_cleaned = energy_consumption_no_battery.dropna()
        
        energy_consumption_cleaned_month = energy_consumption_battery_cleaned.resample('ME').sum()
        energy_consumption_no_battery_cleaned_month = energy_consumption_no_battery_cleaned.resample('ME').sum()
        energy_difference = energy_consumption_cleaned_month - energy_consumption_no_battery_cleaned_month
        
        heat_map_data[i, j] = energy_difference.sum()
    
   
# Plot the heat map
plt.figure(figsize=(12, 6))
plt.imshow(heat_map_data, cmap='hot_r', interpolation='nearest', aspect='auto')
plt.colorbar(label='Yearly Energy Stored (MWh)')
plt.title('Heat Map of Yearly Energy Stored by Battery')
plt.xlabel('Energy Capacity (MWh)')
plt.ylabel('Power Capacity (MW)')
plt.xticks(ticks=np.arange(len(energy_capacities)), labels=energy_capacities)
plt.yticks(ticks=np.arange(len(power_capacities)), labels=power_capacities)
plt.show()
