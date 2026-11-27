from __future__ import annotations

import pandas as pd
import panel as pn
import plotly.express as px

from src.theme import OTHER_COLOR, OTHER_LABEL, team_color_map

ALL_TEAMS = "Összes csapat"


def _team_info(df: pd.DataFrame) -> pd.DataFrame:
    """Egy sor csapatonként: helyszín + hoveren mutatott adatok."""
    g = df.groupby("Team")
    top = df.loc[g["Points"].idxmax()].set_index("Team")

    info = pd.DataFrame({
        "City": g["City"].first(),
        "Lat": g["Lat"].first(),
        "Lon": g["Lon"].first(),
        "Games": g["TeamGames"].first(),
        "Sets": g["TeamSets"].first(),
        "PlayersUsed": g["PlayersUsed"].first(),   # szűrés előtti létszám
        "Regulars": g.size(),                      # szűrés utáni (rendszeres) létszám
        "PointsPerSet": g["Points"].sum() / g["TeamSets"].first(),
        "TopPlayer": top["Player"],
        "TopPoints": top["Points"],
    })
    return info.reset_index()


def create_map(df: pd.DataFrame) -> pn.Column:
    """Térkép a csapatok városaival: fix méretű jelölők, gazdag hover."""

    if df.empty:
        return pn.Column(
            pn.pane.Markdown("<h1 style='text-align: center;'>Csapatok földrajzi elhelyezkedése</h1>", sizing_mode="stretch_width"),
            pn.pane.Markdown("_Nincs elég adat a megjelenítéshez._"),
        )

    info = _team_info(df)
    team_colors = team_color_map(info["Team"])
    team_order = sorted(team_colors)

    team_select = pn.widgets.Select(
        name="Csapat kiemelése",
        options=[ALL_TEAMS] + team_order,
        value=ALL_TEAMS,
        width=250,
    )

    def _view(team: str):
        t = info.copy()
        t["Szín"] = t["Team"]
        if team != ALL_TEAMS:
            t["Szín"] = t["Team"].where(t["Team"] == team, OTHER_LABEL)

        fig = px.scatter_map(
            t,
            lat="Lat",
            lon="Lon",
            color="Szín",
            color_discrete_map={**team_colors, OTHER_LABEL: OTHER_COLOR},
            category_orders={"Szín": [OTHER_LABEL] + team_order},  # szürke hátul
            custom_data=[
                "Team", "City", "Games", "Sets", "PlayersUsed",
                "Regulars", "PointsPerSet", "TopPlayer", "TopPoints",
            ],
        )

        # Fix méretű jelölők: a méret nem hordoz jelentést
        fig.update_traces(
            marker=dict(size=27, opacity=0.9),
            hovertemplate=(
                "<b>%{customdata[0]}</b> (%{customdata[1]})<br>"
                "Mérkőzések: %{customdata[2]} · Szettek: %{customdata[3]}<br>"
                "Pályára lépett játékos: %{customdata[4]} "
                "(ebből rendszeres: %{customdata[5]})<br>"
                "Szerzett pont / szett: %{customdata[6]:.1f}<br>"
                "Legjobb pontszerző: %{customdata[7]} (%{customdata[8]:.0f} pont)"
                "<extra></extra>"
            ),
        )

        fig.update_layout(
            map_style="open-street-map",
            map_zoom=7,
            map_center={"lat": 47.1625, "lon": 19.5033},
            height=600,
            margin={"r": 0, "t": 10, "l": 0, "b": 0},
            legend_title_text="Csapat",
        )
        return pn.pane.Plotly(fig, config={"responsive": True})

    return pn.Column(
        pn.pane.Markdown("<h1 style='text-align: center;'>Csapatok földrajzi elhelyezkedése</h1>", sizing_mode="stretch_width"),
        pn.pane.Markdown(
            "_A jelölők mérete mindenhol azonos, és nem hordoz jelentést, a szín csak "
            "azonosít. Hover-rel látható a csapat "
            "kerete és teljesítménye. „Rendszeres” = legalább 8 mérkőzés és 5 szett._"
        ),
        pn.Row(team_select),
        pn.bind(_view, team_select),
    )