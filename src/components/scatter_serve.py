from __future__ import annotations

import pandas as pd
import panel as pn
import plotly.express as px

from src.theme import OTHER_COLOR, OTHER_LABEL, team_color_map

ALL_TEAMS = "Összes csapat"


def create_scatter_serve(df: pd.DataFrame) -> pn.Column:
    """Rontott nyitás % vs. ász % scatter (a pontok mérete az összes nyitás)."""

    base_df = df[df["ServeTotal"] > 0].copy()

    if base_df.empty:
                return pn.Column(
            pn.pane.Markdown("<h1 style='text-align: center;'>Nyitás: kockázat vs. hatékonyság</h1>", sizing_mode="stretch_width"),
            pn.pane.Markdown("_Nincs elég adat a megjelenítéshez._"),
        )

    # Százalékok a nyers darabszámokból (a forrásban nincs ilyen oszlop)
    base_df["ServeError%"] = base_df["ServeErrors"] / base_df["ServeTotal"] * 100
    base_df["Ace%"] = base_df["Aces"] / base_df["ServeTotal"] * 100

    team_colors = team_color_map(df["Team"].dropna().unique())
    team_order = sorted(team_colors)

    # --- Widgetek ---
    min_serves = pn.widgets.IntSlider(
        name="Min. nyitások száma", start=10, end=200, step=10, value=30, width=250
    )
    team_select = pn.widgets.Select(
        name="Csapat kiemelése",
        options=[ALL_TEAMS] + team_order,
        value=ALL_TEAMS,
        width=250,
    )

    def _view(min_s: int, team: str):
        plot_df = base_df[base_df["ServeTotal"] >= min_s].copy()

        if plot_df.empty:
            return pn.pane.Markdown(
                "_Ezzel a küszöbbel nincs játékos – csökkentsd a minimumot._"
            )

        # Kiemelés: a kiválasztott csapat színes, a többi szürke
        plot_df["Szín"] = plot_df["Team"]
        if team != ALL_TEAMS:
            plot_df["Szín"] = plot_df["Team"].where(plot_df["Team"] == team, OTHER_LABEL)

        fig = px.scatter(
            plot_df,
            x="ServeError%",
            y="Ace%",
            size="ServeTotal",
            size_max=26,
            color="Szín",
            color_discrete_map={**team_colors, OTHER_LABEL: OTHER_COLOR},
            category_orders={"Szín": [OTHER_LABEL] + team_order},  # szürke hátul
            hover_name="Player",
            hover_data={
                "Team": True,
                "ServeTotal": True,
                "ServeErrors": True,
                "Aces": True,
                "ServeError%": ":.1f",
                "Ace%": ":.1f",
                "Szín": False,
            },
            labels={
                "ServeError%": "Rontott nyitás %",
                "Ace%": "Ász %",
                "ServeTotal": "Összes nyitás",
                "ServeErrors": "Rontott nyitások",
                "Aces": "Ászok",
                "Team": "Csapat",
                "Szín": "Csapat",
            },
            title="Nyitás: kockázat vs. hatékonyság",
            template="plotly_white",
        )

        # Mediánvonalak: negyedekre bontják a diagramot
        med_x = plot_df["ServeError%"].median()
        med_y = plot_df["Ace%"].median()
        fig.add_vline(
            x=med_x, line_dash="dot", line_color="gray",
            annotation_text=f"medián: {med_x:.1f}%", annotation_position="top",
        )
        fig.add_hline(
            y=med_y, line_dash="dot", line_color="gray",
            annotation_text=f"medián: {med_y:.1f}%", annotation_position="right",
        )

        # Sarokfeliratok az olvasáshoz
        corner = dict(xref="paper", yref="paper", showarrow=False,
                      font=dict(size=11, color="gray"))
        fig.add_annotation(x=0.01, y=0.99, xanchor="left", yanchor="top",
                           text="kevés hiba, sok ász", **corner)
        fig.add_annotation(x=0.99, y=0.01, xanchor="right", yanchor="bottom",
                           text="sok hiba, kevés ász", **corner)

        fig.update_xaxes(ticksuffix="%")
        fig.update_yaxes(ticksuffix="%")
        fig.update_layout(
            height=520,
            legend_title_text="Csapat",
            legend=dict(orientation="h", y=-0.2),
            margin=dict(l=40, r=20, t=60, b=40),
        )

        caption = pn.pane.Markdown(
            f"_Megjelenítve: **{len(plot_df)}** játékos a {len(df)}-ból "
            f"(min. {min_s} nyitás). A százalékok az összes nyitásra vonatkoznak. "
            "A buborék mérete az összes nyitások száma "
            "A szaggatott vonalak a megjelenített játékosok "
            "mediánját jelölik._"
        )
        return pn.Column(
            caption,
            pn.pane.Plotly(fig, config={"responsive": True}),
        )

    return pn.Column(
        pn.pane.Markdown("<h1 style='text-align: center;'>Nyitás: kockázat vs. hatékonyság</h1>", sizing_mode="stretch_width"),
        pn.Row(min_serves, team_select),
        pn.bind(_view, min_serves, team_select),
    )