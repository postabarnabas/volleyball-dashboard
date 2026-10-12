from __future__ import annotations

import panel as pn
import plotly.express as px
import pandas as pd

from src.data_loader import filter_by_metric


def create_scatter(df: pd.DataFrame) -> pn.Column:
    """Támadás% vs. tökéletes fogadás% scatter.

    Csak azok a játékosok jelennek meg, akiknek:
    - legalább 50 ütése van (AttackTotal >= 50)
    - legalább 50 fogadása van (ReceiveTotal >= 50)
    """
    # Metrika-specifikus szűrés
    plot_df = filter_by_metric(df, "Receive%")
    plot_df = filter_by_metric(plot_df, "Attack%")

    # Csak azok, akiknek van mindkét értéke
    plot_df = plot_df.dropna(subset=["Attack%", "PerfectReceive%"]).copy()

    if plot_df.empty:
        return pn.Column(
            pn.pane.Markdown("### 🎯 Támadás vs. Fogadás"),
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
            "AttackTotal": True,
            "ReceiveTotal": True,
            "Team": False,
        },
        title="Támadáshatékonyság vs. Tökéletes nyitásfogadás",
        labels={
            "Attack%": "Támadás %",
            "PerfectReceive%": "Tökéletes fogadás %",
            "Points": "Pontok",
            "Team": "Csapat",
            "AttackTotal": "Összes ütés",
            "ReceiveTotal": "Összes fogadás",
        },
    )

    fig.update_layout(
        height=500,
        legend_title_text="Csapat",
        margin=dict(l=40, r=20, t=60, b=40),
    )

    return pn.Column(
        pn.pane.Markdown("### 🎯 Támadás vs. Fogadás"),
        pn.pane.Markdown(
            f"_Megjelenítve: {len(plot_df)} játékos "
            f"(min. 50 ütés és 50 fogadás)._"
        ),
        pn.pane.Plotly(fig, config={"responsive": True}),
    )