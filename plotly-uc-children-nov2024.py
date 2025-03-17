# %%
from __future__ import annotations

import json
import os

import geopandas as gpd
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn import preprocessing

df = pd.read_csv(
    'data/households_uc_nov2024.csv', header=None,
    skiprows=11, skipfooter=19, engine='python',
)

# Select first two columns and rename them
df = df.iloc[:, 0:2]

df.columns = ['OA21CD', 'num_households']

# Read the GeoJSON from local storage
gdf = gpd.read_file(
    'data/Output_Areas_2021_EW_BFC_V8_-4558466797057254853.geojson',
)\
    .set_crs('EPSG:3857', allow_override=True)
# Only common OA21CD areas
df = df[df['OA21CD'].isin(gdf['OA21CD'])].reset_index(drop=True)
content = json.loads(gdf.to_json())

df['num_households'] = df['num_households'].replace(
    '..', '0',
).apply(lambda x: int(x))

# scaling not currently relevant
scaler = preprocessing.MinMaxScaler()
x = df['num_households'].values.reshape(-1, 1)
x_scaled = scaler.fit_transform(x)
df['num_households_norm'] = pd.Series(x_scaled.flatten())

df['uc_decile'] = pd.qcut(
    df['num_households_norm'],
    10, labels=np.arange(1, 11, 1),
)
df['uc_decile'] = df['uc_decile'].astype('int')

# %%
# Create a Plotly choropleth
fig = px.choropleth_map(
    df, geojson=content,
    locations='OA21CD',
    featureidkey='properties.OA21CD',
    color='uc_decile',
    hover_name='OA21CD',
    hover_data={
        'num_households': True,
        'OA21CD': False,
        'uc_decile': False,
    },
    map_style='open-street-map',
    color_continuous_scale='Viridis',
    zoom=8, center={'lat': 54.3721, 'lon': -1.5791},
    opacity=0.5,
    range_color=(1, 10),
    labels={
        'num_households': 'Number of households',
        'uc_decile': 'Universal Credit <br>households by decile',
    },
    title="""Households on Universal Credit (Nov 2024, deciles)
    in North Yorkshire and surrounding geographies.""",
    subtitle='For illustration purposes only.',
)


fig.add_trace(
    go.Scattermap(
        mode='markers',
        lon=[-1.5791], lat=[54.3721],
        marker={'size': 20, 'symbol': 'museum'},
        hoverinfo='skip',   # disable hover info box
    ),
)

# Save as current filenamme with html extension
filename = os.path.basename(__file__).replace('.py', '.html')
fig.write_html(f"outputs/{filename}")

# %%
