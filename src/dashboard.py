from __future__ import annotations

import sys
from pathlib import Path

# --- A projekt gyökere a sys.path-hoz ---
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import panel as pn

from src.components.data_table import create_data_table
from src.components.map import create_map
from src.components.radar import MIN_ATTEMPTS, create_radar
from src.components.scatter import create_scatter
from src.components.scatter_serve import create_scatter_serve
from src.components.team_compare import create_team_compare
from src.data_loader import MIN_GAMES, MIN_SETS, load_data

AUTHOR = "Posta Barnabás"
REPO_URL = "https://github.com/postabarnabas/volleyball-dashboard"
ACCENT = "#1F3A5F"

# A komponensekben használt feliratok (ezek alapján találjuk meg a legördülőket)
ALL_TEAMS = "Összes csapat"
TEAM_SELECT_NAMES = {"Csapat kiemelése", "Csapat szűrő"}
METRIC_SELECT_NAME = "Mutató"

pn.extension("plotly", "tabulator", sizing_mode="stretch_width")

df = load_data()
teams = sorted(df["Team"].dropna().unique())
n_players = len(df)
n_teams = len(teams)

# --- Komponensek (változatlanul, a saját legördülőikkel) ---
team_compare = create_team_compare(df)
team_map = create_map(df)
scatter = create_scatter(df)
scatter_serve = create_scatter_serve(df)
radar = create_radar(df)
data_table = create_data_table(df)


# ============================================================
#  Közös vezérlők: a komponensek módosítása nélkül
# ============================================================
def find_widgets(obj, cls, names=None) -> list:
    """Rekurzívan megkeresi a komponensekben lévő widgeteket."""
    found = []
    if isinstance(obj, cls) and (names is None or obj.name in names):
        found.append(obj)
    children = getattr(obj, "objects", None)
    if isinstance(children, (list, tuple)):
        for child in children:
            found.extend(find_widgets(child, cls, names))
    return found


def sync(a, b) -> None:
    """Két widget értéke kétirányban követi egymást."""

    def forward(event):
        if b.value != event.new:
            try:
                b.value = event.new
            except ValueError:
                pass

    def backward(event):
        if a.value != event.new:
            try:
                a.value = event.new
            except ValueError:
                pass

    a.param.watch(forward, "value")
    b.param.watch(backward, "value")
    try:
        b.value = a.value
    except ValueError:
        pass


# --- Közös csapatválasztó: az összes komponens csapat-legördülőjét vezérli ---
team_select = pn.widgets.Select(
    name="Csapat kiemelése", options=[ALL_TEAMS] + teams, value=ALL_TEAMS, width=250
)
team_inner = []
for component in (team_map, team_compare, scatter, scatter_serve, data_table):
    team_inner += find_widgets(component, pn.widgets.Select, TEAM_SELECT_NAMES)
for widget in team_inner:
    sync(team_select, widget)

# --- A csapat-összehasonlító mutatóválasztójának tükre a vezérlősávban ---
metric_select = None
metric_inner = find_widgets(team_compare, pn.widgets.Select, {METRIC_SELECT_NAME})
if metric_inner:
    metric_select = pn.widgets.Select(
        name="Csapat-mutató",
        options=metric_inner[0].options,
        value=metric_inner[0].value,
        width=280,
    )
    sync(metric_select, metric_inner[0])

print(
    f"[dashboard] Összekötött csapatválasztók: {len(team_inner)}, "
    f"mutatóválasztó: {'igen' if metric_select is not None else 'nem található'}"
)

reset_button = pn.widgets.Button(
    name="Összes csapat", button_type="primary", align=("start", "end")
)


def _reset(_event):
    team_select.value = ALL_TEAMS


reset_button.on_click(_reset)

controls = pn.Row(
    team_select,
    reset_button,
    pn.pane.Markdown(
        "_A csapatválasztó egyszerre állítja a térképet, a csapat-összehasonlítót, "
        "a pontdiagramokat és a táblázatot; a térképen a jelölőre kattintva is "
        "választhatsz. A játékos-profil független._",
        margin=(25, 10, 0, 20),
    ),
    styles={
        "position": "sticky",
        "top": "0",
        "z-index": "1000",
        "background": "white",
        "padding": "10px 15px",
        "border-bottom": "1px solid #d0d7de",
    },
    sizing_mode="stretch_width",
)


# --- Segédfüggvények az elrendezéshez ---
def gap(height: int = 50) -> pn.Spacer:
    """Függőleges térköz (mindig új példány)."""
    return pn.Spacer(height=height)


def section(title: str, text: str = "") -> pn.pane.Markdown:
    """Szekciófejléc vékony aláhúzással."""
    body = f"## {title}" + (f"\n\n_{text}_" if text else "")
    return pn.pane.Markdown(
        body,
        margin=(10, 10, 10, 10),
        styles={"border-bottom": f"2px solid {ACCENT}", "padding-bottom": "6px"},
    )


# --- Fejléc ---
header = pn.pane.Markdown(
    f"""
# 🏐 Férfi NBI Extraliga 2025/26 – Interaktív Dashboard
**Adatforrás:** HVF Férfi NBI Extraliga 2025/26 | **Készítette:** {AUTHOR}
""",
    sizing_mode="stretch_width",
    margin=(10, 10, 0, 10),
)


# --- Módszertan és korlátok (lenyitható) ---
methodology = pn.pane.Markdown(
    f"""
## Adatok

- **Forrás:** HVF statisztikai export, Férfi NBI Extraliga 2025/26, játékosonkénti szezon-összesítés.
- **Szűrés:** a dashboard azokat a játékosokat mutatja, akik legalább {MIN_GAMES} mérkőzésen és {MIN_SETS} szetten szerepeltek: {n_players} játékos, {n_teams} csapat.
- **Ami nincs a fájlban:** mérkőzés-eredmények és tabella, játékosposztok.

## Mutatók

- **Támadás %:** kill szerzett pont támadásból / összes támadás. Nem azonos a hivatalos „hatékonysággal", ami a hibákat is levonja.
- **Tökéletes fogadás %:** tökéletes fogadás száma / összes fogadás száma.
- **Ász % és rontott nyitás %:** az összes nyitásra vetítve. **Hiba %:** hiba / az adott elem összes kísérlete.
- **Csapatmutatók:** összesített arány (összes találat / összes kísérlet), a darabszám-alapúak szettre vetítve.
- **Percentilis (Játékos-profil):** a liga hány százalékánál jobb a játékos az adott elemben.

## Hogyan kerültük el a félrevezető ábrázolást?

A feladathoz adott ellenpéldák tipikus hibáit tudatosan kerültük:

1. **Csonkolt tengely:** az oszlopdiagram nullától indul; a pontdiagramok tengelyei százalékban feliratozottak, a mediánvonalak viszonyítási pontot adnak.
2. **Átlagok átlaga:** a csapatmutatók összesítettek, nem a játékosok százalékainak átlaga.
3. **Kis minták:** a nyitás-diagramon állítható minimum-nyitásszám van, a támadás–fogadás diagramon csak a nullánál nagyobb értékű játékosok szerepelnek, a játékos-profil legalább {MIN_ATTEMPTS} kísérletes sokaságon számol.
4. **Mérőszám-választás:** meccs helyett szettre vetítünk, mert a hosszabb meccsek több szettet, így automatikusan több ászt és blokkot jelentenek.
5. **Színek:** 13 csapat színe nem különböztethető meg biztonságosan, ezért a kiválasztott csapat színes, a többi szürke; a csapatszínek minden diagramon azonosak, egy szín sem ismétlődik.
6. **Radar:** minden tengely percentilis, kifelé = jobb (a hibák megfordítva), referenciaként a mediánszinttel; a nyers értékek táblázata mutatja a különbségek valódi nagyságát.
7. **Térkép:** a jelölők mérete fix és nem hordoz jelentést, így a terület nem torzít.

## Korlátok

- A fájl nem tartalmaz játékposztot, ezért a játékosok összehasonlítása korlátozott (pl. liberó és feladó).
- A mérkőzés- és szettszám a legtöbbet játszó játékos adatából becsült.
- A percentilis a sorrendet mutatja, a különbség nagyságát nem.
- A térkép a csapatok városát jelöli, nem a pontos pályát egy csapat kivételével.

## Technológia

Python, pandas, [Panel](https://panel.holoviz.org/) (HoloViz) és Plotly. Forráskód: [{REPO_URL}]({REPO_URL})
""",
    sizing_mode="stretch_width",
)

methodology_card = pn.Card(
    methodology,
    title="Módszertan, mutatók és korlátok (kattints a kinyitáshoz)",
    collapsed=True,
    sizing_mode="stretch_width",
    margin=(10, 10, 10, 10),
)

# --- Lábléc ---
footer = pn.pane.Markdown(
    f"""
---
**Technológiák:** Python, Panel, Plotly, pandas | **Adat:** [HVF Férfi NBI Extraliga 2025/26](https://hvf-web.dataproject.com/Statistics_AllPlayers.aspx?ID=56&PID=63) | **Készítette:** {AUTHOR}
""",
    sizing_mode="stretch_width",
)

# --- Elrendezés ---
dashboard = pn.Column(
    header,
    controls,
    gap(20),
    team_map,
    gap(70),
    team_compare,
    gap(90),
    # ---- Játékosok ----
    section(
        "Játékosok",
        "Támadás, fogadás és nyitás pontdiagramokon, két játékos részletes profilja.",
    ),
    gap(10),
    pn.Row(scatter, pn.Spacer(width=50), scatter_serve),
    gap(70),
    pn.Column(radar, max_width=1100, align="center", sizing_mode="stretch_width"),
    gap(70),
    data_table,
    gap(60),
    methodology_card,
    gap(30),
    footer,
    sizing_mode="stretch_width",
    margin=(0, 40, 40, 40),
)

# --- Servable ---
dashboard.servable()