from __future__ import annotations

import panel as pn
import plotly.express as px
import pandas as pd


def create_scatter_serve(df: pd.DataFrame) -> pn.Column:
    """Rontott nyitás % vs. Ász nyitás % scatter."""
    
    # Csak azok, akiknek van értelme (pl. legalább 10 nyitásuk van)
    plot_df = df[df["ServeTotal"] >= 10].copy()
    
    # Kiszámoljuk a százalékokat
    plot_df["ServeError%"] = (plot_df["ServeErrors"] / plot_df["ServeTotal"]) * 100
    plot_df["Ace%"] = (plot_df["Aces"] / plot_df["ServeTotal"]) * 100

    plot_df = plot_df.dropna(subset=["ServeError%", "Ace%"]).copy()

    if plot_df.empty:
        return pn.Column(
            pn.pane.Markdown("###  Nyitás Hatékonyság"),
            pn.pane.Markdown("_Nincs elég adat a megjelenítéshez._"),
        )

    fig = px.scatter(
        plot_df,
        x="ServeError%",
        y="Ace%",
        size="ServeTotal",
        color="Team",
        hover_name="Player",
        hover_data={
            "ServeTotal": True,
            "ServeErrors": True,
            "Aces": True,
            "ServeError%": ":.1f",
            "Ace%": ":.1f",
            "Team": False,
        },
        title="Nyitás Kockázat vs. Hatékonyság",
        labels={
            "ServeError%": "Rontott nyitás %",
            "Ace%": "Ász nyitás %",
            "ServeTotal": "Összes nyitás",
            "Team": "Csapat",
        },
    )

    fig.update_layout(
        height=500,
        legend_title_text="Csapat",
        margin=dict(l=40, r=20, t=60, b=40),
    )

    return pn.Column(
        pn.pane.Markdown("###  Nyitás Kockázat vs. Hatékonyság"),
        pn.pane.Markdown(
            f"_Megjelenítve: {len(plot_df)} játékos (min. 10 nyitás)._"
        ),
        pn.pane.Plotly(fig, config={"responsive": True}),
    )