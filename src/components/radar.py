from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go


def render_radar(df: pd.DataFrame, player_name: str):
    row = df[df["Player"] == player_name].iloc[0]
    categories = ["Pontok", "BP", "S #", "R #", "A #", "B #"]
    values = [
        float(row.get("Pontok", 0) or 0),
        float(row.get("BP", 0) or 0),
        float(row.get("S #", 0) or 0),
        float(row.get("R #", 0) or 0),
        float(row.get("A #", 0) or 0),
        float(row.get("B #", 0) or 0),
    ]

    fig = go.Figure(
        data=go.Scatterpolar(
            r=values,
            theta=categories,
            fill="toself",
            name=player_name,
        )
    )
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True)),
        title=f"Performance profile: {player_name}",
        template="plotly_white",
    )
    return fig
