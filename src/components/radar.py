from __future__ import annotations

import numpy as np
import pandas as pd
import panel as pn
import plotly.graph_objects as go

MIN_ATTEMPTS = 30  # ennyi kísérlet alatt nem kerül be az adott elem percentilis-sokaságába

ATTACK_COLS = ["A=", "A!", "A/", "A-", "A+", "A#"]
RECEIVE_COLS = ["R=", "R!", "R/", "R-", "R+", "R#"]

# (felirat, oszlop, nagyobb_a_jobb, egység, a sokaságot szűrő mennyiség)
RADAR_METRICS = [
    ("Támadás % (kill)", "Attack%", True, "%", "AttackTotal"),
    ("Támadási hiba %", "AttackError%", False, "%", "AttackTotal"),
    ("Ász %", "Ace%", True, "%", "ServeTotal"),
    ("Rontott nyitás %", "ServeError%", False, "%", "ServeTotal"),
    ("Tökéletes fogadás %", "PerfectReceive%", True, "%", "ReceiveTotal"),
    ("Fogadási hiba %", "ReceiveError%", False, "%", "ReceiveTotal"),
    # elöl játszók (legalább MIN_ATTEMPTS támadás) között hasonlítjuk
    ("Sánc / szett", "BlocksPerSet", True, "", "AttackTotal"),
]

PLAYER_STYLES = [
    ("#2E91E5", "rgba(46,145,229,0.25)"),
    ("#EB663B", "rgba(235,102,59,0.25)"),
]


def _prepare(df: pd.DataFrame) -> pd.DataFrame:
    """Arányok és percentilisek (kifelé = jobb) minden tengelyen."""
    d = df.copy().reset_index(drop=True)

    d["AttackTotal"] = d[ATTACK_COLS].fillna(0).sum(axis=1)
    d["ReceiveTotal"] = d[RECEIVE_COLS].fillna(0).sum(axis=1)

    d["AttackError%"] = d["A="] / d["AttackTotal"].replace(0, np.nan) * 100
    d["Ace%"] = d["Aces"] / d["ServeTotal"].replace(0, np.nan) * 100
    d["ServeError%"] = d["ServeErrors"] / d["ServeTotal"].replace(0, np.nan) * 100
    d["ReceiveError%"] = d["R="] / d["ReceiveTotal"].replace(0, np.nan) * 100
    d["BlocksPerSet"] = d["Blocks"] / d["Sets"].replace(0, np.nan)

    for label, col, higher, _unit, base in RADAR_METRICS:
        eligible = d[base] >= MIN_ATTEMPTS
        values = d[col].where(eligible)
        ranks = values.rank(pct=True) if higher else (-values).rank(pct=True)
        d[f"pct::{label}"] = ranks * 100  # 100 = a legjobb

    return d


def _fmt(value: float, unit: str) -> str:
    return f"{value:.1f}{unit}" if unit == "%" else f"{value:.2f}{unit}"


def _create_radar_figure(rows: list[pd.Series]) -> go.Figure:
    labels = [m[0] for m in RADAR_METRICS]
    theta = labels + [labels[0]]

    fig = go.Figure()

    # Referencia: mediánszint (50. percentilis)
    fig.add_trace(
        go.Scatterpolar(
            r=[50] * len(theta),
            theta=theta,
            mode="lines",
            line=dict(color="gray", dash="dot", width=1),
            name="Mediánszint (50.)",
            hoverinfo="skip",
        )
    )

    for (line_color, fill_color), row in zip(PLAYER_STYLES, rows):
        r = [row[f"pct::{label}"] for label in labels]
        raw = [_fmt(row[col], unit) for _l, col, _h, unit, _b in RADAR_METRICS]
        fig.add_trace(
            go.Scatterpolar(
                r=r + [r[0]],
                theta=theta,
                customdata=raw + [raw[0]],
                mode="lines+markers",
                fill="toself",
                fillcolor=fill_color,
                line=dict(color=line_color, width=2),
                marker=dict(size=6),
                name=f"{row['Player']} ({row['Team']})",
                hovertemplate=(
                    "<b>%{theta}</b><br>Érték: %{customdata}"
                    "<br>Percentilis: %{r:.0f}<extra>" + row["Player"] + "</extra>"
                ),
            )
        )

    fig.update_layout(
        polar=dict(
            radialaxis=dict(range=[0, 100], tickvals=[25, 50, 75, 100], tickfont=dict(size=10)),
            angularaxis=dict(rotation=90, direction="clockwise"),
        ),
        showlegend=True,
        legend=dict(orientation="h", y=-0.1),
        height=520,
        margin=dict(l=70, r=70, t=40, b=60),
        template="plotly_white",
    )
    return fig


def _create_table(rows: list[pd.Series]) -> pd.DataFrame:
    data = {"Mutató": [m[0] for m in RADAR_METRICS]}
    for i, row in enumerate(rows, start=1):
        data[f"{i}. {row['Player']}"] = [
            f"{_fmt(row[col], unit)}  ({row[f'pct::{label}']:.0f}. percentilis)"
            for label, col, _h, unit, _b in RADAR_METRICS
        ]
    return pd.DataFrame(data)


def create_radar(df: pd.DataFrame) -> pn.Column:
    """Két játékos percentilis-profilja (kifelé = jobb) + nyers értékek."""

    d = _prepare(df)
    pct_cols = [f"pct::{m[0]}" for m in RADAR_METRICS]

    # Választható: akinek minden elemből van elég kísérlete
    eligible = d.dropna(subset=pct_cols).copy()

    if len(eligible) < 2:
        return pn.Column(
            pn.pane.Markdown("<h1 style='text-align: center;'>Játékos-profil</h1>", sizing_mode="stretch_width"),
            pn.pane.Markdown("_Nincs elég adat a megjelenítéshez._"),
        )

    eligible = eligible.sort_values("Player")
    options = {f"{r.Player} ({r.Team})": int(i) for i, r in eligible.iterrows()}

    # Alapérték: a legtöbb pontot szerző két játékos
    top2 = eligible.sort_values("Points", ascending=False).index[:2]

    player1 = pn.widgets.Select(name="Játékos 1", options=options, value=int(top2[0]), width=300)
    player2 = pn.widgets.Select(name="Játékos 2", options=options, value=int(top2[1]), width=300)

    def _view(i1: int, i2: int):
        rows = [eligible.loc[i1], eligible.loc[i2]]
        return pn.Column(
            pn.pane.Plotly(_create_radar_figure(rows), config={"responsive": True}),
            pn.pane.DataFrame(_create_table(rows), index=False, sizing_mode="stretch_width"),
        )

    return pn.Column(
        pn.pane.Markdown("<h1 style='text-align: center;'>Játékos-profil</h1>", sizing_mode="stretch_width"),
        pn.pane.Markdown(
            "_Minden tengely **percentilis**: azt mutatja, a liga játékosainak hány százalékánál "
            "jobb az adott elemben (100 = a legjobb, a szaggatott kör a mediánszint). "
            "A hibák tengelyei fordítva vannak számolva, így **minden tengelyen kifelé = jobb**. "
            f"A percentilis azok között készül, akiknek legalább {MIN_ATTEMPTS} kísérletük van az "
            "adott elemben (a sáncnál: legalább 30 támadás, vagyis elöl játszik). "
            f"Csak az a {len(eligible)} játékos választható, akinek mindhárom elemből van elég "
            "kísérlete, így a profil nem tartalmaz hiányzó tengelyt. "
            "A percentilis a sorrendet mutatja, a különbség nagyságát nem: ezt a hover és a "
            "táblázat nyers értékei adják._"
        ),
        pn.Row(player1, player2),
        pn.bind(_view, player1, player2),
    )