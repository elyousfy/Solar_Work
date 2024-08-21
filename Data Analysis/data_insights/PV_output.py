import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from battery import Battery

# Load the data into the variable DF
df = pd.read_csv('PV_raw_data.csv')

# Drop data points that have zero AC output and unneeded columns
df_cleaned = df[df['AC System Output (W)'] != 0].copy()
columns_to_drop = [
    'Beam Irradiance (W/m2)', 
    'Diffuse Irradiance (W/m2)', 
    'Ambient Temperature (C)', 
    'Wind Speed (m/s)', 
    'Plane of Array Irradiance (W/m2)',
    'Cell Temperature (C)', 
    'DC Array Output (W)', 'Albedo'
]
df_cleaned.drop(columns=columns_to_drop, inplace=True)

# Set some parameters
min_energy_consumption = 6
max_energy_consumption = 100

# Convert AC power output into MWh
df_cleaned['Energy Generated (MWh)'] = df_cleaned['AC System Output (W)'] * 0.000001

# Define the range of battery capacities to test
capacities = range(12, 121)  # from 12 to 120 in steps of 1

results = []

for capacity in capacities:
    # Create the battery with the current capacity
    Battery_12MW_XMWh = Battery(power_capacity=12, energy_capacity=capacity, efficiency=1)
    
    # Create some Series to save data in and join to the main data frame later
    energy_consumption_battery = pd.Series(0, index=df_cleaned.index)
    energy_consumption_no_battery = pd.Series(0, index=df_cleaned.index)
    excess_energy = pd.Series(0, index=df_cleaned.index)
    Battery_charge = pd.Series(0, index=df_cleaned.index)

    # Process energy generation data
    for date, ac_output_mwh in df_cleaned['Energy Generated (MWh)'].items():
        Battery_charge[date] = Battery_12MW_XMWh.get_charge()
        
        if ac_output_mwh > min_energy_consumption:  # Minimum to enter the grid
            if ac_output_mwh > max_energy_consumption:  # Maximum to enter the grid
                # Set energy consumption to max
                energy_consumption_battery[date] = max_energy_consumption
                energy_consumption_no_battery[date] = max_energy_consumption
                # Find the excess energy
                excess_energy[date] = ac_output_mwh - max_energy_consumption
                # Charge the battery with the excess energy
                Battery_12MW_XMWh.charge(power=excess_energy[date]) 
            else:
                # Energy is within the max and min range
                energy_consumption_battery[date] = ac_output_mwh
                energy_consumption_no_battery[date] = ac_output_mwh
        else:
            # Energy is less than min_energy_consumption
            if Battery_12MW_XMWh.get_charge() > min_energy_consumption:  # Ensure sufficient discharge power to meet grid requirement
                energy_consumption_battery[date] = Battery_12MW_XMWh.discharge(power=min_energy_consumption - ac_output_mwh) + ac_output_mwh
            energy_consumption_no_battery[date] = 0
            
        if energy_consumption_battery[date] <= min_energy_consumption:  # No energy left in the battery
            Battery_12MW_XMWh.charge(power=ac_output_mwh)
            energy_consumption_battery[date] = 0

    # Calculate results for this capacity
    energy_consumption_battery.replace(0, np.nan, inplace=True)
    energy_consumption_no_battery.replace(0, np.nan, inplace=True)
    energy_consumption_battery_cleaned = energy_consumption_battery.dropna()
    energy_consumption_no_battery_cleaned = energy_consumption_no_battery.dropna()
    energy_consumption_cleaned_month = energy_consumption_battery_cleaned.resample('M').sum()
    energy_consumption_no_battery_cleaned_month = energy_consumption_no_battery_cleaned.resample('M').sum()
    df_cleaned_month = df_cleaned.resample('M').sum()
    energy_difference = energy_consumption_cleaned_month - energy_consumption_no_battery_cleaned_month
    total_yearly_energy_stored = energy_difference.sum()

    # Store results
    results.append({
        'capacity': capacity,
        'total_yearly_energy_stored': total_yearly_energy_stored
    })

# Print results for each capacity
for result in results:
    print(f"Battery Capacity: {result['capacity']} MWh")
    print(f"Total Yearly Energy Stored: {result['total_yearly_energy_stored']} MWh\n")

# Plot the results
capacities = [result['capacity'] for result in results]
total_yearly_energy_stored = [result['total_yearly_energy_stored'] for result in results]

plt.figure(figsize=(12, 6))
plt.plot(capacities, total_yearly_energy_stored, marker='o')
plt.title('Total Yearly Energy Stored by Battery vs Battery Capacity')
plt.xlabel('Battery Capacity (MWh)')
plt.ylabel('Total Yearly Energy Stored (MWh)')
plt.grid(True)
plt.show()
