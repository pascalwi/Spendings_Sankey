#%% IMPORTS
import pandas as pd
import plotly.graph_objects as go


data_path = r"fastbudget.csv"
YEAR = 2022

data = pd.read_csv(data_path, delimiter=";", 
                   header=1, index_col="Id", 
                   parse_dates=[5], 
                   dayfirst=True, 
                   keep_default_na=False,
                   )


categories = {  "Einkaufen": ["Lebensmittel", "Baumarkt", "Technik", "Verbrauchsartikel", "Geschenke", "Kleidung", "Essen Arbeit", "Supplements", "Einkaufen"],
                "Freizeit": ["Bar Alkohol", "Ausflug", "Kultur", "Aktivität", "Sport", "Restaurant", "PC", "Urlaub", "Software", "Eissport"],
                "Transport": ["Tanken", "OPVN", "Auto", "Reparatur", "Motorrad", "Motorrad Tanken"],
                "Wohnung": ["Wohnung", "Miete", "Strom", "Internet", "GEZ"],                
                "Abos": ["Handyvertrag", "Netflix", "Spotify", "Lastpass", "Headspace", "Laufende Kosten", "Boxen"], 
                "Sonstiges": ["Ausgleich", "Friseur", "Ausgelegt", "sonstige Ausgaben", "Spenden"],               
                "Sparen": ["Sparen", "Vanguard all world"], 
                "Versicherung": ["Krankenversicherung", "Versicherung"],
                "Archiv": ["Uni"]
                }

data = data[data["Date"] >= pd.Timestamp(YEAR,1,1)]
data = data[data["Date"] <= pd.Timestamp(YEAR,12,31)]
data.to_clipboard(sep=";")

earnings = data[data["Value"] > 0][["Category", "Date", "Value", "Notes"]]
earnings_categorized = earnings.groupby("Category").sum("Value")
earnings_categorized = earnings_categorized[earnings_categorized.index != "Transfer between accounts"]

spendings = data[data["Value"] < 0][["Category", "Date", "Value", "Notes"]]
spendings_categorized = spendings.groupby("Category").sum("Value").abs()
spendings_categorized = spendings_categorized[spendings_categorized.index != "Transfer between accounts"]

# Remove subcategories in categories that have no entries in earnings_categorized
for main_category, subcategories in categories.items():
    categories[main_category] = [sub for sub in subcategories if sub in spendings_categorized.index]
categories = {k: v for k, v in categories.items() if v}

# sum up common categories from dept payback
common_categories = set(earnings_categorized.index).intersection(spendings_categorized.index)
for category in common_categories:
    spendings_categorized.loc[category] -= earnings_categorized.loc[category]
    earnings_categorized = earnings_categorized.drop(category)

if YEAR == 2022:
    earnings_categorized.loc["Schulden"] = 900
    spendings_categorized.loc["Rent"] = 4600
    earnings_categorized = earnings_categorized.drop("Miete")
   
#spendings_categorized.loc["Sparen"] = earnings_categorized.sum()-spendings_categorized.sum()

flat_cats = [item for sublist in categories.values() for item in sublist]
flat_cats = [item for item in flat_cats if item in spendings_categorized.index]
remaining = [item for item in spendings_categorized.index if item not in flat_cats]

# LABEL
label_list = earnings_categorized.index.tolist() + ["Gesamt"]
label_list += [key for key, vals in categories.items() if any(val in spendings_categorized.index for val in vals)]
label_list += remaining
label_list += flat_cats

#SOURCE
ear_L = len(earnings_categorized)
cat_L = len(categories)
rem_L = len(remaining)
flat_L = len(flat_cats)

# EARNINGS
source = list(range(0,ear_L))

source += [ear_L]*(cat_L+rem_L) # Gesamt as second column
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
