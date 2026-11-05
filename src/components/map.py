from __future__ import annotations

import panel as pn
import plotly.express as px
import pandas as pd


def create_map(df: pd.DataFrame) -> pn.Column:
    """Térkép a csapatok városaival, OpenStreetMap háttérrel."""
    
    unique_teams = df.drop_duplicates(subset=["Team"]).copy()

    if unique_teams.empty:
        return pn.Column(
            pn.pane.Markdown("### 🗺️ Csapatok földrajzi elhelyezkedése"),
            pn.pane.Markdown("_Nincs elég adat a megjelenítéshez._"),
        )

    # Áttérés az új scatter_map-re (MapLibre alapú)
    fig = px.scatter_map(
        unique_teams,
        lat="Lat",
        lon="Lon",
        hover_name="Team",
        hover_data={
            "City": True,
            "Lat": False,
            "Lon": False,
        },
        title="Csapatok földrajzi elhelyezkedése",
        labels={"City": "Város"},
    )

    # Fix méretű buborékok (line nélkül, mert azt az új API nem támogatja)
    fig.update_traces(
        marker=dict(
            size=16,
            color="#E63946",  # Piros szín
            opacity=0.9
        )
    )

    # Térkép beállításai
    fig.update_layout(
        map_style="open-street-map",  # Részletes utcaszintű háttér
        map_zoom=7,                   # Magyarország méretéhez igazítva
        map_center={"lat": 47.1625, "lon": 19.5033},
        height=600,
        margin={"r": 0, "t": 40, "l": 0, "b": 0},
    )

    return pn.Column(
        pn.pane.Markdown("### 🗺️ Csapatok földrajzi elhelyezkedése"),
        pn.pane.Markdown(
            "_A buborékok mindenhol ugyanakkorák, és kizárólag a csapatok székhelyét jelölik. "
            "A méretük nem hordoz jelentést. Hover-rel látható a csapat neve._"
        ),
        pn.pane.Plotly(fig, config={"responsive": True}),
    )