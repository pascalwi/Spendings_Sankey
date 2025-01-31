#%%
import pandas as pd
import plotly.graph_objects as go

#%%
data_path = r"G:\My Drive\Backups\Fast budget\Fast Budget - CSV"
data = pd.read_csv(data_path, delimiter=";", header=1, index_col="Id", parse_dates=[5], dayfirst=True, keep_default_na=False)
# filter year
year = 2022
data = data[data["Date"] >= pd.Timestamp(year,1,1)]
data = data[data["Date"] <= pd.Timestamp(year,12,31)]
# filer unwanted columns
data = data.drop(columns=['Value (EUR)', 'Currency'])
# separater income and costs
earnings = data[data["Value"] > 0]
earnings_categorized = earnings.groupby("Category").sum("Value").sort_values(by=["Value"])
print("Einnahmen:", earnings_categorized)

spendings = data[data["Value"] < 0].sort_values(by=["Category", "Value"])
spendings_categorized = spendings.groupby("Category").sum("Value").abs().sort_values(by=["Value"])
print("Ausgaben:", spendings_categorized)
# new category to account for difference between in and out
spendings_categorized.loc["Sparen"] = earnings_categorized.sum()-spendings_categorized.sum()
# %%


categories = {"Wohnung":["Miete", "Wohnung", "GEZ", "Internet", "Strom"],
                "Transport": ["Auto", "Tanken"],
                "Abos": ["Handyvertrag", "Headspace", "Lastpass", "Netflix", "Spotify"],
                #"Einkaufen": ["Kleidung", "Essen", "Baumarkt", "Essen arbeit", "Fahrrad/Sport", "Technik", "Geschenke", "Sonstige einkäufe", "Computer", "Verbrauchsartikel"],
                "Einkaufen": ["Kleidung", "Essen", "Baumarkt", "Essen Arbeit", "Sport", "Technik", "Geschenke", "Einkaufen", "Verbrauchsartikel"],
                "Sparen": ["Sparen", "Vanguard all world"], 
                "Freizeit": ["Ausflug", "Bar Alkohol", "Restaurant", ]}

flat_cats = [item for sublist in categories.values() for item in sublist]
remaining = [item for item in spendings_categorized.index if item not in flat_cats]

# LABEL
label_list = earnings_categorized.index.tolist() + ["Gesamt"]
label_list += categories.keys()
label_list += remaining
label_list += flat_cats

#SOURCE
ear_L = len(earnings_categorized)
cat_L = len(categories)
rem_L = len(remaining)
flat_L = len(flat_cats)

source = list(range(0,ear_L))
source += [ear_L]*(cat_L+rem_L)
inx = ear_L + 1
for category, vals in categories.items():
    source += [inx]*len(vals)
    inx += 1

#TARGET
target = [ear_L]*ear_L
target += list(range(ear_L+1, ear_L + 1 + cat_L + rem_L + flat_L))

#COUNT
count = earnings_categorized.Value.tolist()
for category, vals in categories.items():
    count.append(spendings_categorized.loc[vals].Value.sum())
count += spendings_categorized.loc[remaining].Value.tolist()
count += spendings_categorized.loc[flat_cats].Value.tolist()

offset = 0
for i , val in enumerate(count):
    if i == ear_L:
        offset = 1
    label_list[i+offset] = label_list[i+offset] +f" [{count[i]:.0f} €]"


# %%
fig = go.Figure(data=[go.Sankey(
    node = {"label": label_list},
    link = {"source": source, "target": target, "value": count}
    )])
fig.show()
# %%
