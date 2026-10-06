from __future__ import annotations

import panel as pn

from src.data_loader import load_data
from src.components.radar import create_radar

pn.extension("plotly", sizing_mode="stretch_width")

df = load_data()
create_radar(df).servable()