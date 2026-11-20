from __future__ import annotations

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import panel as pn
from src.data_loader import load_data
from src.components.data_table import create_data_table

pn.extension("tabulator", sizing_mode="stretch_width")

df = load_data()
create_data_table(df).servable()