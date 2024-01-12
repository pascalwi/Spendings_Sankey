#%% IMPORTS
import pandas as pd
import plotly.graph_objects as go


#%% READ DATA
data_path = r"C:\Users\pasca\Documents\FastBudget\CSV_12_19__18_01_02.csv"
data_path = r"G:\Meine Ablage\Backups\Fast budget\Fast Budget 01-24.csv"
data = pd.read_csv(data_path, delimiter=";", 
                   header=1, index_col="Id", 
                   parse_dates=[5], 
                   dayfirst=True, 
                   keep_default_na=False,
                   )

#%% MAIN CATEGORIES
categories = {  "Einkaufen": ["Lebensmittel", "Baumarkt", "Technik", "Verbrauchsartikel", "Geschenke", "Kleidung", "Essen arbeit", "Supplements", "Einkaufen"],
                "Freizeit": ["Bar Alkohol", "Ausflug", "Kultur", "Aktivität", "Sport", "Restaurant", "PC", "Urlaub", "Software" ],
                "Transport": ["Tanken", "OPVN", "Auto", "Reparatur", "Motorrad"],
                "Wohnung": ["Wohnung", "Miete", "Strom", "Internet", "GEZ"],                
                "Abos": ["Handyvertrag", "Netflix", "Spotify", "Lastpass", "Headspace", "Laufende Kosten"],
                "Sonstiges": ["Sonstiges", "Ausgleich", "Friseur", "Ausgelegt"],               
                "Sparen": ["Sparen", "Vanguard all world"], 
                "Versicherung": ["Krankenversicherung", "Versicherung"],
                "Archiv": ["Uni"]
                }


#%%
year = 2022
data = data[data["Fecha"] >= pd.Timestamp(year,1,1)]
data = data[data["Fecha"] <= pd.Timestamp(year,12,31)]

earnings = data[data["Valor"] > 0][["Categoría", "Fecha", "Valor", "Notas"]]
earnings_categorized = earnings.groupby("Categoría").sum("Valor")

spendings = data[data["Valor"] < 0][["Categoría", "Fecha", "Valor", "Notas"]]
spendings_categorized = spendings.groupby("Categoría").sum("Valor").abs()

if year == 2022:
    earnings_categorized.loc["Schulden"] = 900
    spendings_categorized.loc["Rent"] = 4600
    earnings_categorized = earnings_categorized.drop("Miete")
   



spendings_categorized.loc["Sparen"] = earnings_categorized.sum()-spendings_categorized.sum()
# %%




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
count = earnings_categorized.Valor.tolist()
for category, vals in categories.items():
    count.append(spendings_categorized.loc[vals].Valor.sum())
count += spendings_categorized.loc[remaining].Valor.tolist()
count += spendings_categorized.loc[flat_cats].Valor.tolist()

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
