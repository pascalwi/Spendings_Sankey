import pandas as pd
import matplotlib.pyplot as plt

# Read Excel file into a pandas DataFrame, skip the first 4 rows
df = pd.read_excel(r"G:\My Drive\Backups\Fast budget\Fast_Budget_12-23.xls", skiprows=4)

# Convert the 'Date' column to datetime format
df['Date'] = pd.to_datetime(df['Date'])

# Create a new DataFrame with monthly sum for each category
monthly_sum = df.groupby(['Category', pd.Grouper(key='Date', freq='M')])['Value'].sum().unstack(fill_value=0)

# Create another DataFrame with the average value over the last three months for each category
last_three_months = monthly_sum.T.tail(12).mean().round(1)

# Print the results
print("Monthly sum for each category:\n", monthly_sum)
print("\nAverage value over last twelfe months for each category (no decimals):\n", last_three_months)

to_plot = last_three_months[last_three_months < 0].abs()
print(to_plot.sum())

to_plot.sort_values().plot(kind='bar', x='Category', y='Value')
plt.show()