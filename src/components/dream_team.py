from __future__ import annotations

import pandas as pd


def build_dream_team(df: pd.DataFrame, max_players: int = 6) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["Player", "Team", "Pontok", "BP", "S #", "A #", "B #"])

    weighted = df.copy()
    weighted["dream_score"] = (
        weighted["Pontok"].fillna(0) * 1.0
        + weighted["BP"].fillna(0) * 1.5
        + weighted["S #"].fillna(0) * 1.8
        + weighted["A #"].fillna(0) * 1.2
        + weighted["B #"].fillna(0) * 1.6
    )
    return (
        weighted.sort_values("dream_score", ascending=False)
        .head(max_players)[["Player", "Team", "Pontok", "BP", "S #", "A #", "B #", "dream_score"]]
        .reset_index(drop=True)
    )
