from __future__ import annotations

import panel as pn
import plotly.graph_objects as go
import pandas as pd

# 4 hiba-alapú dimenzió (mind meccsenként)
RADAR_DIMS = {
    "Támadási hiba/meccs": "AttackErrorPG",
    "Rontott nyitás/meccs": "ServeErrorPG",
    "Kapott ász/meccs": "ReceiveErrorPG",
    "Sánchiba/meccs": "BlockErrorPG",
}


def _normalize(series: pd.Series) -> pd.Series:
    """0-1 közé normalizál."""
    series = pd.to_numeric(series, errors="coerce")
    mn, mx = series.min(), series.max()
    if pd.isna(mn) or pd.isna(mx) or mx == mn:
        return series * 0
    return (series - mn) / (mx - mn)


def _create_radar_figure(
    df: pd.DataFrame,
    title: str,
    p1: str,
    p2: str,
) -> go.Figure:
    """Egy radar diagram létrehozása a 4 dimenzióval."""
    fig = go.Figure()

    for player in [p1, p2]:
        row = df[df["Player"] == player]
        if row.empty:
            continue
        row = row.iloc[0]
        values = [row[label] for label in RADAR_DIMS]
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
        title=title,
    )
    return fig


def create_radar(df: pd.DataFrame) -> pn.Column:
    """Két játékos összehasonlítása egy 4 dimenziós (hiba) radaron."""
    
    # Itt már nem kell szűrnünk, mert a globális szűrés a data loaderben megtörtént.
    # Csak azokat vesszük, akiknek van minden hiba adata.
    plot_df = df.dropna(subset=list(RADAR_DIMS.values())).copy()

    if plot_df.empty:
        return pn.Column(
            pn.pane.Markdown("### 🕸️ Hiba-profil"),
            pn.pane.Markdown("_Nincs elég adat a megjelenítéshez._"),
        )

    # Normalizálás
    norm_df = plot_df.copy()
    for label, col in RADAR_DIMS.items():
        norm_df[label] = _normalize(norm_df[col])

    players = sorted(norm_df["Player"].dropna().unique().tolist())
    
    player1 = pn.widgets.Select(name="Játékos 1", options=players, value=players[0], width=250)
    player2 = pn.widgets.Select(name="Játékos 2", options=players, value=players[1], width=250)

    @pn.depends(player1, player2, watch=True)
    def update_radar(p1: str, p2: str):
        return pn.pane.Plotly(
            _create_radar_figure(norm_df, "Játékos hiba-profil (normalizált)", p1, p2), 
            config={"responsive": True}
        )

    return pn.Column(
        pn.pane.Markdown("### 🕸️ Játékos hiba-profil"),
        pn.pane.Markdown(
            "_A radar 4 dimenziója: Támadási hiba, Rontott nyitás, Kapott ász, Sánchiba (mind meccsenként). "
            "A kisebb érték a jobb, de a normalizálás miatt a nagyobb területű játékos többet hibázik._"
        ),
        pn.Row(player1, player2),
        update_radar,
    )