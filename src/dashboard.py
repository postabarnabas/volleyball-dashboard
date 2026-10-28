from __future__ import annotations

import sys
from pathlib import Path

# --- A projekt gyökere a sys.path-hoz ---
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import panel as pn

from src.data_loader import load_data
from src.components.radar import create_radar
from src.components.scatter import create_scatter
from src.components.team_compare import create_team_compare

# Panel extension
pn.extension("plotly", sizing_mode="stretch_width")

# --- Adat betöltés ---
df = load_data()

# --- Fejléc ---
header = pn.pane.Markdown(
    """
    # 🏐 Férfi NBI Extraliga 2025/26 – Interaktív Dashboard
    **Adatforrás:** HVF statisztika | **Készítette:** [Neved]
    """,
    sizing_mode="stretch_width",
)

# --- Komponensek ---
scatter = create_scatter(df)
radar = create_radar(df)
team_compare = create_team_compare(df)

# --- Lábléc ---
footer = pn.pane.Markdown(
    """
    ---
    **Technológiák:** Python, Panel, Plotly, pandas |
    **Adat:** HVF Férfi NBI Extraliga 2025/26
    """,
    sizing_mode="stretch_width",
)

# --- Elrendezés ---
dashboard = pn.Column(
    header,
    pn.Row(scatter, radar),
    team_compare,
    footer,
    sizing_mode="stretch_width",
)

# --- Servable ---
dashboard.servable()