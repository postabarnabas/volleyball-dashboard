from __future__ import annotations

import pandas as pd


def summarize_by_team(df: pd.DataFrame) -> pd.DataFrame:
    summary = (
        df.groupby("Team", dropna=False)
        .agg(
            players=("Player", "count"),
            total_points=("Pontok", "sum"),
            avg_points=("Pontok", "mean"),
            avg_blocks=("B #", "mean"),
            total_aces=("S #", "sum"),
        )
        .sort_values("total_points", ascending=False)
        .reset_index()
    )
    return summary
