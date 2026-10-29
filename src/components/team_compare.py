from __future__ import annotations

import panel as pn
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from src.data_loader import filter_by_metric


# Csoportosított metrikák
PERCENT_METRICS = {
    "Támadás %": ("Attack%", "Attack%"),
    "Tökéletes fogadás %": ("PerfectReceive%", "Receive%"),
}

RATE_METRICS = {    
    "Ász/meccs": ("Aces", "rate"),
    "Sánc/meccs": ("Blocks", "rate"),
    "Rontott nyitás/meccs": ("ServeErrors", "rate"),
}


def _create_grouped_chart(
    df: pd.DataFrame,
    metrics: dict[str, tuple[str, str]],
    title: str,
    y_axis_title: str,
    fmt: str,
) -> go.Figure:
    """Csoportosított oszlopdiagram, azonos skálájú metrikákkal."""
    frames = []
    for label, (col, filter_key) in metrics.items():
        if filter_key == "rate":
            # A csapat szintű mutatóknál NINCS egyéni szűrés!
            sub = df.copy()
        else:
            sub = filter_by_metric(df, filter_key)

        sub = sub.dropna(subset=[col])
        if sub.empty:
            continue

        if filter_key == "rate":
            # ÖSSZEADÁS: csapat összes pontja / csapat összes meccse
            # A "Games" itt a játékosok meccseit jelenti, de a csapat meccseit
            # a legtöbbet játszó játékos adja. Ezt használjuk nevezőnek.
            team_games = sub.groupby("Team")["Games"].max()
            agg = sub.groupby("Team")[col].sum().reset_index()
            agg = agg.merge(team_games, on="Team")
            agg["Érték"] = agg[col] / agg["Games"]
        else:
            # ÁTLAG: százalékos metrikáknál marad az átlag
            agg = sub.groupby("Team")[col].mean().reset_index()
            agg = agg.rename(columns={col: "Érték"})

        agg["Metrika"] = label
        frames.append(agg[["Team", "Érték", "Metrika"]])

    if not frames:
        fig = go.Figure()
        fig.add_annotation(
            text="Nincs elég adat",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
        )
        fig.update_layout(height=450, title=title)
        return fig

    agg_long = pd.concat(frames, ignore_index=True)

    # Csapatok sorrendje: a fő metrika (első) szerint csökkenő
    first_metric = list(metrics.keys())[0]
    team_order = (
        agg_long[agg_long["Metrika"] == first_metric]
        .sort_values("Érték", ascending=False)["Team"]
        .tolist()
    )

    fig = px.bar(
        agg_long,
        x="Team",
        y="Érték",
        color="Metrika",
        barmode="group",
        category_orders={
            "Team": team_order,
            "Metrika": list(metrics.keys()),
        },
        title=title,
        labels={"Team": "Csapat", "Érték": y_axis_title, "Metrika": "Metrika"},
    )

    fig.update_layout(
        height=450,
        xaxis_tickangle=-45,
        margin=dict(l=50, r=20, t=60, b=100),
        legend_title_text="",
        yaxis=dict(rangemode="tozero", title=y_axis_title),
    )

    return fig


def create_team_compare(df: pd.DataFrame) -> pn.Column:
    if df.empty:
        return pn.Column(
            pn.pane.Markdown("### 🏆 Csapat-összehasonlítás"),
            pn.pane.Markdown("_Nincs elég adat a megjelenítéshez._"),
        )

    fig_percent = _create_grouped_chart(
        df,
        PERCENT_METRICS,
        title="Százalékos metrikák",
        y_axis_title="Érték (%)",
        fmt=".1f",
    )

    fig_rate = _create_grouped_chart(
        df,
        RATE_METRICS,
        title="Mutatók (meccsenként)",
        y_axis_title="Érték (meccsenként)",
        fmt=".2f",
    )

    return pn.Column(
        pn.pane.Markdown("### 🏆 Csapat-összehasonlítás"),
        pn.pane.Markdown(
            "_Bal: százalékos metrikák (0-100). "
            "Jobb: meccsenkénti mutatók (0-10). "
            "Az azonos skálájú metrikák egy diagramon vannak, "
            "így elkerüljük a megtévesztő eltérő skálákat._"
        ),
        pn.Row(
            pn.pane.Plotly(fig_percent, config={"responsive": True}),
            pn.pane.Plotly(fig_rate, config={"responsive": True}),
        ),
    )