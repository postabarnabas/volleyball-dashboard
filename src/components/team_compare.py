from __future__ import annotations

import panel as pn
import plotly.express as px
import pandas as pd

from src.data_loader import filter_by_metric


# A metrikák: megjelenített név -> (DataFrame oszlopnév, szűrő kulcs)
TEAM_METRICS = {
    "Pont/szett": ("PointsPerSet", "rate"),
    "Ász/szett": ("AcesPerSet", "rate"),
    "Sánc/szett": ("BlocksPerSet", "rate"),
    "Támadás %": ("Attack%", "Attack%"),
    "Tökéletes fogadás %": ("PerfectReceive%", "Receive%"),
}


def create_team_compare(df: pd.DataFrame) -> pn.Column:
    """Csapatok összehasonlítása csoportosított oszlopdiagramon.

    Minden metrikához a saját metrika-specifikus szűrőjét alkalmazzuk,
    majd csapatonként átlagolunk.
    """
    if df.empty:
        return pn.Column(
            pn.pane.Markdown("### 🏆 Csapat-összehasonlítás"),
            pn.pane.Markdown("_Nincs elég adat a megjelenítéshez._"),
        )

    # Minden metrikához külön aggregálás
    frames = []
    for label, (col, filter_key) in TEAM_METRICS.items():
        if filter_key == "rate":
            sub = filter_by_metric(df, "AcesPerSet")  # Sets >= 20
        else:
            sub = filter_by_metric(df, filter_key)

        # Csak azok, akiknek van értéke az adott metrikában
        sub = sub.dropna(subset=[col])
        if sub.empty:
            continue

        agg = sub.groupby("Team")[col].mean().reset_index()
        agg = agg.rename(columns={col: "Érték"})
        agg["Metrika"] = label
        frames.append(agg)

    if not frames:
        return pn.Column(
            pn.pane.Markdown("### 🏆 Csapat-összehasonlítás"),
            pn.pane.Markdown("_Nincs elég adat a megjelenítéshez._"),
        )

    agg_long = pd.concat(frames, ignore_index=True)

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
        title="Csapatok összehasonlítása (metrika-specifikus átlagok)",
        labels={
            "Team": "Csapat",
            "Érték": "Átlagos érték",
            "Metrika": "Metrika",
        },
    )

    fig.update_layout(
        height=550,
        xaxis_tickangle=-30,
        legend_title_text="Metrika",
        margin=dict(l=40, r=20, t=60, b=140),
    )

    return pn.Column(
        pn.pane.Markdown("### 🏆 Csapat-összehasonlítás"),
        pn.pane.Markdown(
            "_Minden metrika a saját metrika-specifikus szűrőjét használja._"
        ),
        pn.pane.Plotly(fig, config={"responsive": True}),
    )