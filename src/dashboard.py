from __future__ import annotations

import sys
from pathlib import Path

# --- A projekt gyökere a sys.path-hoz ---
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import panel as pn

from src.data_loader import load_data
from src.components.radar import create_radar
from src.components.scatter import create_scatter
from src.components.scatter_serve import create_scatter_serve
from src.components.team_compare import create_team_compare
from src.components.map import create_map
from src.components.data_table import create_data_table

# Panel extension (plotly a diagramokhoz, tabulator a táblázathoz)
pn.extension("plotly", "tabulator", sizing_mode="stretch_width")

# --- Adat betöltés ---
df = load_data()

# --- Fejléc ---
header = pn.pane.Markdown(
    """
    # 🏐 Férfi NBI Extraliga 2025/26 – Interaktív Dashboard
    **Adatforrás:** HVF statisztika | **Készítette:** [Neved]
    """,
    sizing_mode="stretch_width",
    styles={"margin-bottom": "20px"},
)

# --- Komponensek létrehozása ---
scatter = create_scatter(df)
scatter_serve = create_scatter_serve(df)
radar = create_radar(df)
team_map = create_map(df)
team_compare = create_team_compare(df)
data_table = create_data_table(df)

# --- Lábléc ---
footer = pn.pane.Markdown(
    """
    ---
    **Technológiák:** Python, Panel, Plotly, pandas |
    **Adat:** HVF Férfi NBI Extraliga 2025/26
    """,
    sizing_mode="stretch_width",
)

# --- Elrendezés (Layout) ---
# Egy kis térköz a komponensek közé
spacer = pn.Spacer(height=20)

dashboard = pn.Column(
    header,
    # Első sor: a két scatter
    pn.Row(scatter, scatter_serve),
    spacer,
    # Második sor: radar és térkép
    pn.Row(radar, team_map),
    spacer,
    # Harmadik sor: csapat-összehasonlítás
    team_compare,
    spacer,
    # Negyedik sor: adattábla
    data_table,
    spacer,
    footer,
    sizing_mode="stretch_width",
)

# --- Servable ---
dashboard.servable()