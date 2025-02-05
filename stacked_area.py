
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import make_interp_spline


df = pd.read_excel(r"C:\Users\pasca\Documents\Python\Spendings_Sankey\XLS_10_18__13_09_00.xls", skiprows=4)
df = df.drop(["Value (EUR)", "Notes", "Account", "Currency", "From/To"], axis=1)
df["Date"] = pd.to_datetime(df["Date"])

pivot = pd.pivot_table(df, values='Value', index=[pd.Grouper(key='Date', freq='Y')], columns='Category', aggfunc='sum', fill_value=0)
#pivot = pivot.rolling(window=16, min_periods=1, center=False).mean()


x_smooth = pd.date_range(pivot.index.min(), pivot.index.max(), 300)
pivot = pd.DataFrame({Category: make_interp_spline(pivot.index, pivot[Category])(x_smooth)
                             for Category in pivot.columns})

pivot.set_index(x_smooth, inplace=True)

for col in pivot.columns:
    mean_val = pivot[col].mean()
    if mean_val < 0:
        pivot.loc[pivot[col] > 0, col] = 0
    else:
        pivot.loc[pivot[col] < 0, col] = 0

abos = ["GEZ", "Handyvertrag", "Lebensmittel", "Internet", "Laufende Kosten", "Miete", "Netflix", "Spotify", "Strom", "Vanguard all world", "Versicherung"]

abos_only = pivot[pivot.columns & abos]
abos_only.plot(kind='area', stacked=True)
#pivot.plot(kind='area', stacked=True)
plt.legend(loc='center left')

plt.show()




print("test")
