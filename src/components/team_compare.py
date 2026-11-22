from __future__ import annotations

import pandas as pd
import panel as pn
import plotly.express as px

from src.theme import OTHER_COLOR, OTHER_LABEL, team_color_map

ALL_TEAMS = "Összes csapat"

ATTACK_COLS = ["A=", "A!", "A/", "A-", "A+", "A#"]
RECEIVE_COLS = ["R=", "R!", "R/", "R-", "R+", "R#"]

# num / den: a team_table oszlopai; scale: 100 a százalékhoz
METRICS = {
    "Támadás %": dict(
        num="kills", den="attacks", scale=100, unit="%", higher_better=True,
        num_label="kill", den_label="támadás",
        desc="Csapat összes pontja / csapat összes támadásának száma.",
    ),
    "Tökéletes fogadás %": dict(
        num="perfect_rec", den="receptions", scale=100, unit="%", higher_better=True,
        num_label="tökéletes fogadás", den_label="fogadás",
        desc="Csapat összes tökéletes fogadása / csapat összes fogadásának száma.",
    ),
    "Ász / szett": dict(
        num="aces", den="sets", scale=1, unit="", higher_better=True,
        num_label="ász", den_label="szett",
        desc="Csapat összes ásza / csapat szettjeinek száma.",
    ),
    "Sánc (pontblokk) / szett": dict(
        num="blocks", den="sets", scale=1, unit="", higher_better=True,
        num_label="pontblokk", den_label="szett",
        desc="Csapat összes pontblokkja / csapat szettjeinek száma.",
    ),
    "Rontott nyitás / szett": dict(
        num="serve_errors", den="sets", scale=1, unit="", higher_better=False,
        num_label="rontott nyitás", den_label="szett",
        desc="Csapat összes rontott nyitása / csapat szettjeinek száma.",
    ),
}


def _team_table(df: pd.DataFrame) -> pd.DataFrame:
    """Csapatszintű összegek (súlyozott mutatókhoz: összeg / összeg)."""
    g = df.groupby("Team")
    return pd.DataFrame({
        # a csapat szettszáma ~ a legtöbbet játszó játékos szettjei
        "sets": g["Sets"].max(),
        "kills": g["A#"].sum(),
        "attacks": g[ATTACK_COLS].sum().sum(axis=1),
        "perfect_rec": g["R#"].sum(),
        "receptions": g[RECEIVE_COLS].sum().sum(axis=1),
        "aces": g["Aces"].sum(),
        "serve_errors": g["ServeErrors"].sum(),
        "blocks": g["Blocks"].sum(),
    })


def create_team_compare(df: pd.DataFrame) -> pn.Column:
    if df.empty:
        return pn.Column(
            pn.pane.Markdown("<h1 style='text-align: center;'>Csapat-összehasonlítás</h1>", sizing_mode="stretch_width"),
            pn.pane.Markdown("_Nincs elég adat a megjelenítéshez._"),
        )

    team_table = _team_table(df)
    team_colors = team_color_map(df["Team"].dropna().unique())

    metric_select = pn.widgets.Select(
        name="Mutató", options=list(METRICS), value=list(METRICS)[0], width=280
    )
    team_select = pn.widgets.Select(
        name="Csapat kiemelése",
        options=[ALL_TEAMS] + sorted(team_colors),
        value=ALL_TEAMS,
        width=250,
    )

    def _view(metric: str, team: str):
        m = METRICS[metric]
        t = team_table.copy()
        t["Érték"] = t[m["num"]] / t[m["den"]] * m["scale"]
        t["Num"] = t[m["num"]]
        t["Den"] = t[m["den"]]

        # Bajnokság összesített átlaga (súlyozott: összeg / összeg)
        league = t[m["num"]].sum() / t[m["den"]].sum() * m["scale"]

        t = t.reset_index().sort_values("Érték", ascending=not m["higher_better"])
        order = t["Team"].tolist()

        t["Szín"] = t["Team"]
        if team != ALL_TEAMS:
            t["Szín"] = t["Team"].where(t["Team"] == team, OTHER_LABEL)

        unit = m["unit"]
        title = metric + ("" if m["higher_better"] else " (kevesebb = jobb)")

        fig = px.bar(
            t,
            x="Érték",
            y="Team",
            orientation="h",
            color="Szín",
            color_discrete_map={**team_colors, OTHER_LABEL: OTHER_COLOR},
            category_orders={"Team": order},
            custom_data=["Num", "Den"],
            title=title,
            template="plotly_white",
        )
        fig.update_traces(
            texttemplate="%{x:.1f}" + unit,
            textposition="outside",
            hovertemplate=(
                "<b>%{y}</b><br>"
                + metric + ": %{x:.2f}" + unit + "<br>"
                + m["num_label"] + ": %{customdata[0]:.0f}<br>"
                + m["den_label"] + ": %{customdata[1]:.0f}"
                "<extra></extra>"
            ),
        )
        fig.add_vline(
            x=league, line_dash="dot", line_color="gray",
            annotation_text=f"bajnokság átlaga: {league:.1f}{unit}",
            annotation_position="top",
        )
        fig.update_xaxes(
            range=[0, t["Érték"].max() * 1.15], ticksuffix=unit, title=None
        )
        fig.update_yaxes(autorange="reversed", title=None)  # a legjobb felül
        fig.update_layout(
            height=520,
            showlegend=False,
            margin=dict(l=20, r=20, t=60, b=40),
        )

        caption = pn.pane.Markdown(
            f"_{m['desc']} A csapatok a legjobbtól a leggyengébbig vannak rendezve"
            f"{'' if m['higher_better'] else ' (itt a kevesebb a jobb)'}. "
            " A szaggatott vonal a bajnokság "
            "összesített átlaga. A szettszám a csapat legtöbbet játszó "
            "játékosának szettjeiből becsült._"
        )
        return pn.Column(
            caption,
            pn.pane.Plotly(fig, config={"responsive": True}),
        )

    return pn.Column(
        pn.pane.Markdown("<h1 style='text-align: center;'>Csapat-összehasonlítás</h1>", sizing_mode="stretch_width"),
        pn.Row(metric_select, team_select),
        pn.bind(_view, metric_select, team_select),
    )