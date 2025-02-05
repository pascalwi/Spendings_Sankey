import pandas as pd
import plotly.graph_objects as go

label_list = ['cat', 'dog', 'domesticated', 'female', 'male', 'wild']
# cat: 0, dog: 1, domesticated: 2, female: 3, male: 4, wild: 5
source = [0, 0, 1, 3, 4, 4]
target = [3, 4, 4, 2, 2, 5]
count = [21, 6, 22, 21, 6, 22]

fig = go.Figure(data=[go.Sankey(
    node = {"label": label_list},
    link = {"source": source, "target": target, "value": count}
    )])
fig.show()
# %%