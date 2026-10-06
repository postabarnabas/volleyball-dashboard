from __future__ import annotations

import panel as pn
import plotly.graph_objects as go
import pandas as pd


# A radar dimenziói: megjelenített név -> DataFrame oszlopnév
RADAR_DIMS = {
    "Pont/szett": "PointsPerSet",
    "Ász/szett": "AcesPerSet",
    "Sánc/szett": "BlocksPerSet",
    "Támadás %": "Attack%",
    "Fogadás %": "PositiveReceive%",
    "Break pontok": "BreakPoints",
}


def _normalize(series: pd.Series) -> pd.Series:
    """0-1 közé normalizál egy pandas Series-t.

    Ha minden érték ugyanaz, akkor 0-t ad vissza (nincs értelme skálázni).
    """
    series = pd.to_numeric(series, errors="coerce")
    mn, mx = series.min(), series.max()
    if pd.isna(mn) or pd.isna(mx) or mx == mn:
        return series * 0
    return (series - mn) / (mx - mn)


def create_radar(df: pd.DataFrame) -> pn.Column:
    """Két játékos radar chartja, 6 dimenzióban.

    Args:
        df: A data_loader-ből származó DataFrame.

    Returns:
        Egy Panel Column, ami a radar chartot és a dropdownokat tartalmazza.
    """
    # Normalizált értékek
    norm_df = df.copy()
    for label, col in RADAR_DIMS.items():
        if col in norm_df.columns:
            norm_df[label] = _normalize(norm_df[col])
        else:
            norm_df[label] = 0.0

    # Csak azok a játékosok, akiknek van legalább 1 szettje
    norm_df = norm_df[norm_df["Sets"] > 0].copy()
    players = sorted(norm_df["Player"].dropna().unique().tolist())

    if len(players) < 2:
        return pn.Column(
            pn.pane.Markdown("### 🕸️ Játékos-profil"),
            pn.pane.Markdown("_Nincs elég játékos az összehasonlításhoz._"),
        )

    # Alapértelmezett: az első két játékos
    player1 = pn.widgets.Select(
        name="Játékos 1",
        options=players,
        value=players[0],
        width=250,
    )
    player2 = pn.widgets.Select(
        name="Játékos 2",
        options=players,
        value=players[1],
        width=250,
    )

    @pn.depends(player1, player2)
    def update(p1: str, p2: str):
        fig = go.Figure()

        for player in [p1, p2]:
            row = norm_df[norm_df["Player"] == player]
            if row.empty:
                continue
            row = row.iloc[0]
            values = [row[label] for label in RADAR_DIMS]
            # Bezárjuk a kört (első érték megismétlése)
            values_closed = values + [values[0]]
            labels_closed = list(RADAR_DIMS.keys()) + [list(RADAR_DIMS.keys())[0]]

            fig.add_trace(
                go.Scatterpolar(
                    r=values_closed,
                    theta=labels_closed,
                    fill="toself",
                    name=player,
                )
            )

        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1],
                )
            ),
            showlegend=True,
            height=500,
            margin=dict(l=60, r=60, t=60, b=40),
            title="Játékos-profil (normalizált)",
        )
        return fig

    return pn.Column(
        pn.pane.Markdown("### 🕸️ Játékos-profil"),
        pn.Row(player1, player2),
        pn.pane.Plotly(
            pn.bind(update, player1, player2),
            config={"responsive": True},
        ),
    )