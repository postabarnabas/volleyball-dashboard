from __future__ import annotations

import pandas as pd
import panel as pn

ALL_TEAMS = "Összes csapat"

# adatoszlop -> megjelenített név
COLUMNS = {
    "Player": "Játékos",
    "Team": "Csapat",
    "Games": "Meccsek",
    "Sets": "Szettek",
    "Points": "Pontok",
    "Aces": "Ászok",
    "Blocks": "Pontblokk",
    "Attack%": "Támadás %",
    "PerfectReceive%": "Tökéletes fogadás %",
}

# Sávos megjelenítés: a számok mögött az oszlop maximumához viszonyított arány
BAR_COLUMNS = ["Pontok", "Ászok", "Pontblokk"]
BAR_COLOR = "#BCD7F0"


def _filter(table: pd.DataFrame, team: str, query: str) -> pd.DataFrame:
    """Csapat és névkereső szűrés."""
    out = table
    if team != ALL_TEAMS:
        out = out[out["Csapat"] == team]
    if query and query.strip():
        out = out[
            out["Játékos"].str.contains(query.strip(), case=False, na=False, regex=False)
        ]
    return out


def create_data_table(df: pd.DataFrame) -> pn.Column:
    """Interaktív, szűrhető, rendezhető adattábla a játékosokról."""

    table_df = df[list(COLUMNS)].rename(columns=COLUMNS).copy()

    if table_df.empty:
        return pn.Column(
            pn.pane.Markdown("<h1 style='text-align: center;'>Adattábla</h1>", sizing_mode="stretch_width"),
            pn.pane.Markdown("_Nincs elég adat a megjelenítéshez._"),
        )

    # --- Widgetek ---
    team_filter = pn.widgets.Select(
        name="Csapat szűrő",
        options=[ALL_TEAMS] + sorted(df["Team"].dropna().unique().tolist()),
        value=ALL_TEAMS,
        width=250,
    )
    search = pn.widgets.TextInput(
        name="Játékos keresése", placeholder="pl. Pavliuk", width=250
    )

    # --- Igazítás: nevek balra, számok középre ---
    align = {col: "center" for col in table_df.columns}
    align.update({"Játékos": "left", "Csapat": "left"})

    # --- Sávok a mennyiségi oszlopokban ---
    formatters = {
        col: {
            "type": "progress",
            "max": float(table_df[col].max()),
            "color": BAR_COLOR,
            "legend": True,
        }
        for col in BAR_COLUMNS
    }

    tabulator = pn.widgets.Tabulator(
        table_df,
        disabled=True,                 # az adatok nem szerkeszthetők
        pagination="local",
        page_size=15,
        sizing_mode="stretch_width",
        theme="simple",
        show_index=False,
        header_align=align,
        text_align=align,
        formatters=formatters,
        widths={"Játékos": 220, "Csapat": 200},
        sorters=[{"field": "Pontok", "dir": "desc"}],
    )

    # Csapat + név szűrés: beépített szűrő, a rendezés és a lapozás megmarad
    tabulator.add_filter(
        pn.bind(_filter, team=team_filter, query=search.param.value_input)
    )

    def _count(team: str, query: str):
        n = len(_filter(table_df, team, query))
        return pn.pane.Markdown(f"Találatok: **{n}** / {len(table_df)} játékos")

    return pn.Column(
        pn.pane.Markdown("<h1 style='text-align: center;'>Adattábla</h1>", sizing_mode="stretch_width"),
        pn.pane.Markdown(
            "_A szezon releváns játékosai (legalább 6 meccs és 8 szett). A fejlécre "
            "kattintva rendezhető, a csapatválasztóval és a névkeresővel szűrhető. "
            "A Pontok, Ászok és Pontblokk oszlopokban a sáv az oszlop legnagyobb "
            "értékéhez viszonyít. "
            "Az üres cella azt jelenti, hogy "
            "nincs adat (pl. a játékos nem támad vagy nem fogad)._"
        ),
        pn.Row(team_filter, search, pn.bind(_count, team_filter, search.param.value_input)),
        tabulator,
    )