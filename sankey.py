#%% IMPORTS
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px


YEAR = 2024
data_path = r"files/jan_25.csv"


data = pd.read_csv(data_path, delimiter=";", 
                   header=1, index_col="Id", 
                   parse_dates=[5], 
                   dayfirst=True, 
                   keep_default_na=False,
                   )


categories = {  "Einkaufen": ["Lebensmittel", "Baumarkt", "Hobbyzubehör", "Verbrauchsartikel", "Geschenke", "Kleidung", "Essen Arbeit", "Supplements", "Einkaufen"],
                "Freizeit": ["Bar Alkohol", "Ausflug", "Kultur", "Aktivität", "Sport", "Restaurant", "PC", "Urlaub", "Software", "Eissport"],
                "Transport": ["Tanken", "Fahrrad", "OPVN", "Auto", "Motorrad"],
                "Wohnung": ["Wohnung", "Miete", "Strom", "Internet", "GEZ"],                
                "Abos": ["Handyvertrag", "Netflix", "Spotify", "Lastpass", "Headspace", "Laufende Kosten", "Boxen"], 
                "Sonstiges": ["Ausgleich", "Friseur", "Ausgelegt", "sonstige Ausgaben", "Spenden"], 
                "Versicherung": ["Krankenversicherung", "Versicherung"],
                "Archiv": ["Uni", "Kultur"],
                "Sparen": ["A2PKXG", "Tagesgeld", "Vanguard all world"] 
                }
#%%
# select date range
data = data[data["Date"] >= pd.Timestamp(YEAR,1,1)]
data = data[data["Date"] <= pd.Timestamp(YEAR,12,31)]

# get all earnings, choose columns and remove transfers except saving to A2PKXG
earnings = data[data["Value"] > 0][["Category", "Date", "Value", "Notes", "Account"]]
earnings = earnings[~((earnings["Category"] == "Transfer between accounts") & (earnings["Account"] != "A2PKXG"))]  
earnings_categorized = earnings.groupby("Category").sum("Value").sort_values("Value", ascending=False)

# get all spendings, choose columns and remove transfers
spendings = data[data["Value"] < 0][["Category", "Date", "Value", "Notes", "Account"]]
spendings_categorized = spendings.groupby("Category").sum("Value").abs()
spendings_categorized = spendings_categorized[spendings_categorized.index != "Transfer between accounts"]  # make A2PKXG a a spending

# basically rename
if "Transfer between accounts" in earnings_categorized.index:
    spendings_categorized.loc["A2PKXG"] = earnings_categorized.loc["Transfer between accounts"]
    earnings_categorized = earnings_categorized.drop("Transfer between accounts")

# Remove subcategories in categories that have no entries in earnings_categorized
for main_category, subcategories in categories.items():
    categories[main_category] = [sub for sub in subcategories if sub in spendings_categorized.index]
categories = {k: v for k, v in categories.items() if v}

# sum up categories that are spendings and earnings (from refunds)
common_categories = set(earnings_categorized.index).intersection(spendings_categorized.index)
for category in common_categories:
    spendings_categorized.loc[category] -= earnings_categorized.loc[category]
    earnings_categorized = earnings_categorized.drop(category)

if YEAR == 2022:
    earnings_categorized.loc["Schulden"] = 900
    spendings_categorized.loc["Rent"] = 4600
    earnings_categorized = earnings_categorized.drop("Miete")


flat_cats = [item for sublist in categories.values() for item in sublist]
flat_cats = [item for item in flat_cats if item in spendings_categorized.index]

# LABEL
label_list = earnings_categorized.index.tolist() + ["Gesamt"]
label_list += [key for key, vals in categories.items()] #  if any(val in spendings_categorized.index for val in vals)]
label_list += flat_cats


ear_L = len(earnings_categorized)
cat_L = len(categories)
flat_L = len(flat_cats)

# EARNINGS
source = list(range(0,ear_L))

source += [ear_L]*(cat_L) # Gesamt as second column
inx = ear_L + 1
for category, vals in categories.items():
    source += [inx]*len(vals) # each categrory with length of its subcategories as outgoing links
    inx += 1

#TARGET
target = [ear_L]*ear_L # Gesamt as target
target += list(range(ear_L+1, ear_L + 1 + cat_L + flat_L))  # then always only one target

#COUNT
node_value = earnings_categorized.Value.tolist()
for category, vals in categories.items():
    node_value.append(spendings_categorized.loc[vals].Value.sum())
node_value += spendings_categorized.loc[flat_cats].Value.tolist()

offset = 0
for i , val in enumerate(node_value):
    if i == ear_L:
        label_list[i] = label_list[i] +f" [{sum(node_value[:i]):.0f} €]"
        offset = 1
    label_list[i+offset] = label_list[i+offset] +f" [{node_value[i]:.0f} €]"

# create position list of nodes
x = [0.25]*ear_L + [0.4] + [0.5]*cat_L + [0.7]*flat_L



y = list(np.linspace(0.33, 0.66, ear_L)) + [0.5] # earnings and total
y += list(np.linspace(0.01, 0.99, cat_L)) # categories
y += list(np.linspace(0.01, 0.99, flat_L)) # flat categories


nodes = {"label": label_list, "x": x, "y": y}
links = {"source": source, "target": target, "value": node_value}


# https://stackoverflow.com/questions/69494044/making-the-color-of-links-the-same-as-source-nodes-in-sankey-plot-plotly-in-r

# %%
fig = go.Figure(data=[go.Sankey(
    arrangement = "snap",
    node = nodes,
    link = links
    )])
fig.update_traces(node_pad=10, selector=dict(type='sankey'))
#fig.update_traces(link=dict(color="source"), selector=dict(type='sankey'))
fig.update_layout(title_text=f"Spendings {YEAR}", font_size=10)
fig.show()
