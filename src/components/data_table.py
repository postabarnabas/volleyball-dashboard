from __future__ import annotations

import panel as pn
import pandas as pd


def create_data_table(df: pd.DataFrame) -> pn.Column:
    """Interaktív, szűrhető és rendezhető adattábla a játékosokról."""
    
    # Kiválasztjuk, hogy mely oszlopok legyenek benne a táblázatban
    # (A túl hosszú listát elkerüljük, csak a lényegesebbeket)
    columns_to_show = [
        "Player", "Team", "Games", "Sets", "Points",
        "PointsPerGame", "AcesPerGame", "BlocksPerGame", 
        "Attack%", "PerfectReceive%"
    ]
    
    # Ha valamelyik oszlop hiányzik (pl. mert még nem futott a data_loader),
    # akkor csak azokat tartjuk meg, amik léteznek.
    existing_columns = [col for col in columns_to_show if col in df.columns]
    
    table_df = df[existing_columns].copy()
    
    # Oszlopnevek átnevezése a szép megjelenéshez
    rename_dict = {
        "Player": "Játékos",
        "Team": "Csapat",
        "Games": "Meccsek",
        "Sets": "Szettek",
        "Points": "Össz. Pont",
        "PointsPerGame": "Pont/meccs",
        "AcesPerGame": "Ász/meccs",
        "BlocksPerGame": "Sánc/meccs",
        "Attack%": "Támadás %",
        "PerfectReceive%": "Tökéletes fogadás %"
    }
    table_df = table_df.rename(columns={k: v for k, v in rename_dict.items() if k in table_df.columns})

    # Kerekítés a szebb megjelenéshez
    for col in ["Pont/meccs", "Ász/meccs", "Sánc/meccs"]:
        if col in table_df.columns:
            table_df[col] = table_df[col].round(2)

    # Szűrő widget (Csapatválasztó)
    teams = ["Összes csapat"] + sorted(df["Team"].dropna().unique().tolist())
    team_filter = pn.widgets.Select(
        name="Csapat szűrő", 
        options=teams, 
        value="Összes csapat",
        width=250
    )

    # A táblázat létrehozása (Tabulator)
    tabulator = pn.widgets.Tabulator(
        table_df,
        pagination="local",
        page_size=15, # Egyszerre 15 sort mutat, a többi lapozható
        sizing_mode="stretch_width",
        theme="simple",
        show_index=False,
        header_align="center",
        text_align="center",
    )

    # A szűrő és a táblázat összekapcsolása
    @pn.depends(team_filter, watch=True)
    def update_table(selected_team):
        if selected_team == "Összes csapat":
            tabulator.value = table_df
        else:
            filtered_df = table_df[table_df["Csapat"] == selected_team]
            tabulator.value = filtered_df

    return pn.Column(
        pn.pane.Markdown("### 📋 Adattábla"),
        pn.pane.Markdown(
            "_A szezon összes releváns játékosa. Az oszlopok fejléceire kattintva "
            "rendezhető a táblázat, a mezőkben pedig kereshető._"
        ),
        pn.Row(team_filter),
        tabulator,
    )