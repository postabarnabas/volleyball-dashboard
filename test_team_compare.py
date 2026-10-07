from __future__ import annotations

import panel as pn

from src.data_loader import load_data
from src.components.team_compare import create_team_compare

pn.extension("plotly", sizing_mode="stretch_width")

df = load_data()
create_team_compare(df).servable()