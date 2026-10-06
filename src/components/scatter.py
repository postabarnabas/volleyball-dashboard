from __future__ import annotations

import pandas as pd
import plotly.express as px


def render_scatter(df: pd.DataFrame, x_metric: str = "Pontok", y_metric: str = "BP"):
    fig = px.scatter(
        df,
        x=x_metric,
        y=y_metric,
        color="Team",
        hover_name="Player",
        size="Szettek",
        title="Player performance comparison",
        labels={
            "Pontok": "Points",
            "BP": "Blocking points",
            "Szettek": "Sets",
        },
    )
    fig.update_layout(template="plotly_white", legend=dict(itemsizing="constant"))
    return fig
