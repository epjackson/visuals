# %%
from __future__ import annotations

import geopandas as gpd
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

postcodes = pd.read_csv('data/ONSPD_FEB_2025_UK.csv')
postcodes = postcodes[['pcds', 'oa21', 'lat', 'long']]

gdf = gpd.read_file(
    'data/Output_Areas_2021_EW_BFC_V8_-4558466797057254853.geojson',
)\
    .set_crs('EPSG:3857', allow_override=True)
postcodes = postcodes[
    postcodes['oa21'].isin(
        gdf['OA21CD'],
    )
].reset_index(drop=True)
postcodes['visits'] = 0
visit_postcodes = postcodes.sample(1000, random_state=42)

# apply random visit numbers per postcode
visit_postcodes['visits'] = np.random.randint(
    1, 100, size=len(visit_postcodes),
)
postcodes = postcodes[~postcodes['oa21'].isin(visit_postcodes['oa21'])]
postcodes = pd.concat([postcodes, visit_postcodes]).reset_index(drop=True)
# postcodes["colour"] = np.where(postcodes["visits"]==0, "red", "blue")

fig = px.scatter_map(
    postcodes,
    lat='lat',
    lon='long',
    size='visits',
    size_max=8,
    hover_name='pcds',
    hover_data={'lat': False, 'long': False},
    map_style='open-street-map',
)

fig.add_trace(
    go.Scattermap(
        mode='markers',
        lon=[-1.5791], lat=[54.3721],
        marker={'size': 20, 'symbol': 'museum'},
        hoverinfo='skip',   # disable hover info box
    ),
)

# Save map
fig.write_html('outputs/plotly-random-postcode-visits.html')

# %%
