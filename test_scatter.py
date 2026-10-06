from __future__ import annotations

import panel as pn

from src.data_loader import load_data
from src.components.scatter import create_scatter

pn.extension("plotly", sizing_mode="stretch_width")

df = load_data()
create_scatter(df).servable()