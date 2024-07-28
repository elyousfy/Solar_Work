import pandas as pd
import matplotlib.pyplot as plt

# Load your data into a pandas DataFrame
df = pd.read_csv('PV_raw_data.csv')

generated_data_analysis=pd.read_csv('generated_power_analysis.csv',header=1)


# # Drop the albedo columns (assuming they are named 'Albedo' or similar)
# df = df.drop(columns=['Albedo'])  # Adjust the column names as necessary

# print(df)

# df = df[df['AC System Output (W)'] != 0]

# df.to_csv('trimmed_data.csv', index=False)

# Select the first 8 columns
df_selected = generated_data_analysis.iloc[:, :6]
print(df_selected)

