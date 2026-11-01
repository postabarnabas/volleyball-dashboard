from __future__ import annotations

import panel as pn
import plotly.express as px
import pandas as pd


def create_scatter(df: pd.DataFrame) -> pn.Column:
    """Támadás% vs. tökéletes fogadás% scatter."""
    
    # Csak azok, akiknek van mindkét értéke
    plot_df = df.dropna(subset=["Attack%", "PerfectReceive%"]).copy()

    if plot_df.empty:
        return pn.Column(
            pn.pane.Markdown("###  Támadás vs. Fogadás"),
            pn.pane.Markdown("_Nincs elég adat a megjelenítéshez._"),
        )

    fig = px.scatter(
        plot_df,
        x="Attack%",
        y="PerfectReceive%",
        size="Points",
        color="Team",
        hover_name="Player",
        hover_data={
            "Points": True,
            "Sets": True,
            "Attack%": ":.1f",
            "PerfectReceive%": ":.1f",
            "Team": False,
        },
        title="Támadáshatékonyság vs. Tökéletes nyitásfogadás",
        labels={
            "Attack%": "Támadás %",
            "PerfectReceive%": "Tökéletes fogadás %",
            "Points": "Pontok",
            "Team": "Csapat",
        },
    )

    fig.update_layout(
        height=500,
        legend_title_text="Csapat",
        margin=dict(l=40, r=20, t=60, b=40),
    )

    return pn.Column(
        pn.pane.Markdown("###  Támadás vs. Fogadás"),
        pn.pane.Markdown(
            f"_Megjelenítve: {len(plot_df)} játékos (nyers adat, szűrés nélkül)._"
        ),
        pn.pane.Plotly(fig, config={"responsive": True}),
    )