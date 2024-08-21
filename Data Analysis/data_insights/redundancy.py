#import libraries
import pandas as pd
import matplotlib.pyplot as plt
from battery import Battery

# Load the data
df = pd.read_csv('trimmed_data.csv')

#drop unneeded comlumns
df.drop(columns=['Beam Irradiance (W/m2)'], inplace=True)
df.drop(columns=['Diffuse Irradiance (W/m2)'], inplace=True)
df.drop(columns=['Ambient Temperature (C)'], inplace=True)
df.drop(columns=['Wind Speed (m/s)'], inplace=True)
df.drop(columns=['Plane of Array Irradiance (W/m2)'], inplace=True)
df.drop(columns=['Cell Temperature (C)'], inplace=True)
df.drop(columns=['DC Array Output (W)'], inplace=True)



# Add a dummy year column (if not already present)
df['year'] = 2023

# Create a datetime column
df['datetime'] = pd.to_datetime(df[['year', 'Month', 'Day', 'Hour']])

# Set datetime as the index
df.set_index('datetime', inplace=True)

# Drop the dummy year column as it is no longer needed
df.drop(columns=['year'], inplace=True)


# Initialize the electricity consumption column
electricity_consumption = pd.Series(0,index=df.index)
excess_generated = pd.Series(0,index=df.index)
under_threshold = pd.Series(0, index=df.index)
new_electricity_consumption=pd.Series(0,index=df.index)
ac_output_mw=pd.Series(0,index=df.index)
max_consumption=90
min_consumption=10

#initialize 2 batteries
Battery_20MW_60MWh=Battery(power_capacity=20,energy_capacity=60,efficiency=1)
Battery_10MW_30MWh=Battery(power_capacity=10,energy_capacity=30,efficiency=1)

print(electricity_consumption.dtype)
print(new_electricity_consumption.dtype)




# Apply the conditions on an hourly basis
for date, ac_output in df['AC System Output (W)'].items():
    ac_output_mw[date] = ac_output / 1e6  # Convert W to MW
    
    if ac_output_mw[date] > min_consumption:
        # Cap the AC output at 90 MW for consumption calculations
        if ac_output_mw[date] > max_consumption:
            
            electricity_consumption[date] = max_consumption
            new_electricity_consumption[date] = max_consumption
            excess_generated[date]=ac_output_mw[date]-max_consumption
            
            #charge battery with excess 
            Battery_10MW_30MWh.charge(power=excess_generated[date])
            Battery_20MW_60MWh.charge(power=excess_generated[date])
            
        else:
            electricity_consumption[date] = ac_output_mw[date]
    else:
        electricity_consumption[date] = 0
        under_threshold[date]=ac_output_mw[date]
        new_electricity_consumption[date]=Battery_20MW_60MWh.discharge(power=10.5-under_threshold[date])+ac_output_mw[date]
        
        
        
data_break_down=pd.concat([ac_output_mw,electricity_consumption,excess_generated,under_threshold],axis=1)
data_break_down.columns = ['Total Power Output (MW)', 'Energy Consumption (MW)', 'Power Generated >90(MW)','Power Generated <10(MW)']
data_break_down['Total Redundancy(MW)']=data_break_down['Power Generated >90(MW)'] + data_break_down['Power Generated <10(MW)']
data_break_down

# daily_data_break_down=data_break_down.resample('D').sum()



plt.figure(figsize=(40, 10))
plt.bar(data_break_down.index,data_break_down['Power Generated >90(MW)'],label='Power Generated >90(MW)')



plt.title('Redundent Energy Produced (MW)')
plt.xlabel('Month')
plt.ylabel('kWh')
plt.legend(loc='upper left', fontsize=1, prop={'size': 1})
plt.show()
