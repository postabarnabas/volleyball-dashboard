from __future__ import annotations

import panel as pn
import plotly.express as px
import pandas as pd


# A metrikák: megjelenített név -> DataFrame oszlopnév
TEAM_METRICS = {
    "Pont/szett": "PointsPerSet",
    "Ász/szett": "AcesPerSet",
    "Sánc/szett": "BlocksPerSet",
    "Támadás %": "Attack%",
    "Fogadás %": "PositiveReceive%",
}


def create_team_compare(df: pd.DataFrame) -> pn.Column:
    """Csapatok összehasonlítása csoportosított oszlopdiagramon.

    Args:
        df: A data_loader-ből származó DataFrame.

    Returns:
        Egy Panel Column, ami a csapat-összehasonlítást tartalmazza.
    """
    # Csak azok a játékosok, akiknek van legalább 1 szettje
    plot_df = df[df["Sets"] > 0].copy()

    if plot_df.empty:
        return pn.Column(
            pn.pane.Markdown("### 🏆 Csapat-összehasonlítás"),
            pn.pane.Markdown("_Nincs elég adat a megjelenítéshez._"),
        )

    # Csapatonkénti átlagok
    agg = (
        plot_df.groupby("Team")[list(TEAM_METRICS.values())]
        .mean()
        .reset_index()
    )

    # Átnevezzük a metrikákat a megjelenített nevekre
    agg = agg.rename(columns={v: k for k, v in TEAM_METRICS.items()})

    # "Melt" – hosszú formátum a diagramhoz
    agg_long = agg.melt(
        id_vars="Team",
        var_name="Metrika",
        value_name="Érték",
    )

    # Csapatok ABC szerint
    team_order = sorted(agg_long["Team"].unique().tolist())

    fig = px.bar(
        agg_long,
        x="Team",
        y="Érték",
        color="Metrika",
        barmode="group",
        category_orders={
            "Team": team_order,
            "Metrika": list(TEAM_METRICS.keys()),
        },
        title="Csapatok összehasonlítása (átlagok)",
        labels={
            "Team": "Csapat",
            "Érték": "Átlagos érték",
            "Metrika": "Metrika",
        },
    )

    fig.update_layout(
        height=500,
        xaxis_tickangle=-30,
        legend_title_text="Metrika",
        margin=dict(l=40, r=20, t=60, b=120),
    )

    return pn.Column(
        pn.pane.Markdown("### 🏆 Csapat-összehasonlítás"),
        pn.pane.Plotly(fig, config={"responsive": True}),
    )