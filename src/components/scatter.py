from __future__ import annotations

import pandas as pd
import panel as pn
import plotly.express as px

from src.theme import OTHER_COLOR, OTHER_LABEL, team_color_map

ALL_TEAMS = "Összes csapat"


def create_scatter(df: pd.DataFrame) -> pn.Column:
    """Támadás% vs. tökéletes fogadás% scatter (csak ha mindkét érték > 0)."""

    # Csak azok, akiknek mindkét értéke megvan ÉS nagyobb nullánál
    # (a NaN > 0 kifejezés False, így a hiányzók is kiesnek)
    plot_base = df[(df["Attack%"] > 0) & (df["PerfectReceive%"] > 0)].copy()

    if plot_base.empty:
        return pn.Column(
            pn.pane.Markdown("<h1 style='text-align: center;'>Támadás vs. Fogadás</h1>", sizing_mode="stretch_width"),
            pn.pane.Markdown("_Nincs elég adat a megjelenítéshez._"),
        )

    team_colors = team_color_map(df["Team"].dropna().unique())
    team_order = sorted(team_colors)

    # --- Widget: csapat kiemelése ---
    team_select = pn.widgets.Select(
        name="Csapat kiemelése",
        options=[ALL_TEAMS] + team_order,
        value=ALL_TEAMS,
        width=250,
    )

    def _view(team: str):
        plot_df = plot_base.copy()

        # Kiemelés: a kiválasztott csapat színes, a többi szürke
        plot_df["Szín"] = plot_df["Team"]
        if team != ALL_TEAMS:
            plot_df["Szín"] = plot_df["Team"].where(plot_df["Team"] == team, OTHER_LABEL)

        fig = px.scatter(
            plot_df,
            x="Attack%",
            y="PerfectReceive%",
            size="Points",
            size_max=26,
            color="Szín",
            color_discrete_map={**team_colors, OTHER_LABEL: OTHER_COLOR},
            category_orders={"Szín": [OTHER_LABEL] + team_order},  # szürke hátul
            hover_name="Player",
            hover_data={
                "Team": True,
                "Points": True,
                "Sets": True,
                "Attack%": ":.0f",
                "PerfectReceive%": ":.0f",
                "Szín": False,
            },
            labels={
                "Attack%": "Támadás %",
                "PerfectReceive%": "Tökéletes fogadás %",
                "Points": "Pontok",
                "Sets": "Szettek",
                "Team": "Csapat",
                "Szín": "Csapat",
            },
            title="Támadás % vs. tökéletes fogadás %",
            template="plotly_white",
        )

        # Mediánvonalak: negyedekre bontják a diagramot
        med_x = plot_df["Attack%"].median()
        med_y = plot_df["PerfectReceive%"].median()
        fig.add_vline(
            x=med_x, line_dash="dot", line_color="gray",
            annotation_text=f"medián: {med_x:.0f}%", annotation_position="top",
        )
        fig.add_hline(
            y=med_y, line_dash="dot", line_color="gray",
            annotation_text=f"medián: {med_y:.0f}%", annotation_position="right",
        )

        fig.update_xaxes(ticksuffix="%")
        fig.update_yaxes(ticksuffix="%")
        fig.update_layout(
            height=520,
            legend_title_text="Csapat",
            legend=dict(orientation="h", y=-0.2),
            margin=dict(l=40, r=20, t=60, b=40),
        )

        caption = pn.pane.Markdown(
            f"_Megjelenítve: **{len(plot_df)}** játékos a {len(df)}-ból. "
            "Csak azok szerepelnek, akiknek a támadás % és a tökéletes fogadás % "
            "is megvan és nagyobb nullánál. A buborék mérete a szerzett pontok számával arányos. "
            "A szaggatott vonalak a megjelenített játékosok mediánját jelölik._"
        )
        return pn.Column(
            caption,
            pn.pane.Plotly(fig, config={"responsive": True}),
        )

    return pn.Column(
        pn.pane.Markdown("<h1 style='text-align: center;'>Támadás vs. Fogadás</h1>", sizing_mode="stretch_width"),
        pn.Row(team_select),
        pn.bind(_view, team_select),
    )