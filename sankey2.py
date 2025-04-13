#%% IMPORTS
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from item import SankeyItem


YEAR = 2020
data_path = r"files/jan_25.csv"


data = pd.read_csv(data_path, delimiter=";", 
                   header=1, index_col="Id", 
                   parse_dates=[5], 
                   #date_format="%m/%d/%Y",
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

#if YEAR == 2022:
#    earnings_categorized.loc["Schulden"] = 900
#    spendings_categorized.loc["Rent"] = 4600
#    earnings_categorized = earnings_categorized.drop("Miete")


flat_cats = [item for sublist in categories.values() for item in sublist]
flat_cats = [item for item in flat_cats if item in spendings_categorized.index]

# CREATE SANKEYITEMS
levels = [[], [], [], []]
# earnings
for i, row in enumerate(earnings_categorized.iterrows()):
    item = SankeyItem(name=row[0], level=0, value=row[1].Value, parents=1, children=0)
    levels[0].append(item)
# gesamt
levels[1].append(SankeyItem("Gesamt", 1, sum(earnings_categorized.Value), 
                        children=len(categories), 
                        parents=len(earnings_categorized)))
# categories
for category, subcategories in categories.items():
    item = SankeyItem(name=category, level=2, value=spendings_categorized.loc[subcategories].sum().Value, 
                      parents=1, children=len(subcategories))
    levels[2].append(item)
# subcategories
for category, subcategories in categories.items():
    for subcategory in subcategories:
        item = SankeyItem(subcategory, 3, spendings_categorized.loc[subcategory].Value, 
                          parents=1, children=0, main_category=category)
        levels[3].append(item)
        # Sort items by value in descending order




# sort items by keep in order of subcategories
levels[0] = sorted(levels[0], key=lambda x: x.value, reverse=True)     
levels[2] = sorted(levels[2], key=lambda x: x.value, reverse=True)
temp_level_3 = []
for category_item in levels[2]:
    category = category_item.name
    subcategorie_items = [x for x in levels[3] if x.main_category == category]
    subcategorie_items = sorted(subcategorie_items, key=lambda x: x.value, reverse=True)
    temp_level_3.extend(subcategorie_items)
levels[3] = temp_level_3

# CREATE LINKS
nodes = {"label": [], "x": [], "y": []}
links = {"source": [], "target": [], "value": []}
positions_x = [0.15, 0.4, 0.6, 0.8]
positions_y = [[0.33, 0.66],
               [0.4, 0.5],
               [0.2, 0.8],
               [0.01, 0.99]]
source_ix = 0
target_ix = 0 
main_category_children = [x.children for x in levels[2]]
children_cumsum = [sum(main_category_children[:i]) for i in range(len(main_category_children))]

for i, items in enumerate(levels):
    if i != 3:    
        y = list(np.linspace(positions_y[i][0], positions_y[i][1], len(items)))
    else:
        cumsum = np.cumsum([x.value for x in items])
        y = cumsum / cumsum[-1]
        y = [float(x) - y[0] + 0.01 for x in y]
        #y = [(y[j] + y[j + 1]) / 2 for j in range(len(y) - 1)]
    for j, item in enumerate(items):        
        nodes["label"].append(f"{item.name} [{item.value:.0f} €]")
        nodes["x"].append(positions_x[i])
        nodes["y"].append(y[j])
        match i:
            case 0: # earnings
                target_ix = len(levels[0]) # alle auf gesamt
                links["target"].append(target_ix)

                links["source"].append(source_ix) # each its own source
                source_ix += 1
                
                links["value"].append(item.value)
            case 1: # gesamt
                target_ix += 1
            case 2: # main categories
                links["source"].append(source_ix) # alle von gesamt
                links["target"].append(target_ix) # jedes mal auf neue main category
                target_ix += 1
                links["value"].append(item.value)
            case 3:                
                if j in children_cumsum: # increase when all subcats are done
                   source_ix += 1                  
                links["source"].append(source_ix)
                links["target"].append(target_ix) # 
                target_ix += 1
                links["value"].append(item.value)

# colors
node_colors = px.colors.qualitative.Set3  # Use a predefined color palette
#nodes["color"] = [node_colors[i % len(node_colors)] for i in range(len(nodes["label"]))]
colors = []
total_len = len(levels[0]) + len(levels[1]) + len(levels[2])
for i in range(len(nodes["label"])):
    if i < total_len:
        color = node_colors[i % len(node_colors)]
        colors.append(color)        
    else:
        colors.append(color)

      
nodes["color"] = colors
links["color"] = [nodes["color"][source] for source in links["source"]]            

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
