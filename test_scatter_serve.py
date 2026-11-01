from __future__ import annotations

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import panel as pn
from src.data_loader import load_data
from src.components.scatter_serve import create_scatter_serve

pn.extension("plotly", sizing_mode="stretch_width")

df = load_data()
create_scatter_serve(df).servable()