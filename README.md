# 🏐 Férfi NBI Extraliga 2025/26 – Interaktív röplabda-dashboard

Interaktív adatvizualizációs dashboard a 2025/26-os férfi röplabda Extraliga játékos- és csapatstatisztikáiról.
Az **Adattudomány MSc** adatvizualizációs beadandójaként készült Python, Panel és Plotly segítségével.


## Tartalom

- [Mit tud a dashboard?](#mit-tud-a-dashboard)
- [Adatok](#adatok)
- [Telepítés és futtatás](#telepítés-és-futtatás)
- [Használat](#használat)
- [Projektstruktúra](#projektstruktúra)
- [Hogyan kerültük el a félrevezető ábrázolást?](#hogyan-kerültük-el-a-félrevezető-ábrázolást)
- [Korlátok](#korlátok)
- [Technológia](#technológia)
- [Szerző](#szerző)

## Mit tud a dashboard?

| Nézet | Diagramtípus | Interakció |
|---|---|---|
| **Térkép** | Térkép, fix méretű jelölők | Hover a csapat adataival (mérkőzések, szettek, játékoskeret, szerzett pont/szett, legjobb pontszerző); kattintás a jelölőre kiemeli a csapatot az egész dashboardon |
| **Csapat-összehasonlítás** | Vízszintes oszlopdiagram | Mutatóválasztó (támadás %, tökéletes fogadás %, ász/szett, sánc/szett, rontott nyitás/szett), a csapatok mindig a választott mutató szerint rendezettek, a bajnokság átlagát jelző vonallal |
| **Támadás vs. fogadás** | Pontdiagram (buborék) | Csapat kiemelése, hover, mediánvonalak |
| **Nyitás: kockázat vs. hatékonyság** | Pontdiagram (buborék) | Minimum-nyitásszám csúszka, csapat kiemelése, hover |
| **Játékos-profil** | Percentilis-radar + táblázat | Két tetszőleges játékos összehasonlítása, nyers értékekkel |
| **Adattábla** | Táblázat | Rendezés, csapatszűrés, névkeresés, oszlopon belüli sávok |
| **Módszertan** | Lenyitható kártya | Mutatók, a félrevezető ábrák elkerülése, korlátok |

Az oldal tetején lévő **közös vezérlősáv** (görgetéskor is látható) egyszerre állítja a csapatválasztót az összes nézeten:
a kiválasztott csapat színes, a többi szürke, a csapatszínek pedig minden diagramon azonosak.

## Adatok

- **Forrás:** HVF (Magyar Röplabda Szövetség) statisztikai export, Férfi NBI Extraliga 2025/26, játékosonkénti szezon-összesítés (`data/hvf_stats.xls`).
- **Szűrés:** a dashboard azokat a játékosokat mutatja, akik legalább 6 mérkőzésen és 8 szetten szerepeltek (181 játékos, 13 csapat).
- **Ami nincs az adatban:** mérkőzés-eredmények és tabella, játékposztok (szerepkör), idősor.
- **Csapatok helyszíne:** a térképhez a csapatok városának koordinátáit kézzel rögzítettük (`src/data_loader.py`).

## Telepítés és futtatás

Szükséges: **Python 3.10 vagy újabb**.

```bash
# 1. Virtuális környezet létrehozása
python -m venv .venv

# 2. Aktiválás
#   Windows (PowerShell):
.venv\Scripts\Activate.ps1
#   macOS / Linux:
source .venv/bin/activate

# 3. Függőségek telepítése
pip install -r requirements.txt

# 4. A dashboard indítása (a projekt gyökeréből)
panel serve src/dashboard.py --show
```

A dashboard ezután a böngészőben nyílik meg (alapértelmezés szerint a `http://localhost:5006/dashboard` címen).

> Az `.xls` fájl beolvasásához az `xlrd` csomag szükséges, ezt a `requirements.txt` tartalmazza.

### Egyes komponensek önálló megtekintése

A `tests/` mappában komponensenként egy előnézeti szkript található, amellyel egy diagram külön is megnyitható, például:

```bash
panel serve tests/test_radar.py --show
```

## Használat

1. **Csapatválasztó (felül):** válassz egy csapatot, és minden nézeten kiemelődik. Az „Összes csapat" gomb visszaállítja.
2. **Térkép:** a jelölőre kattintva is csapatot választhatsz, hover-rel pedig a csapat részletei jelennek meg.
3. **Csapat-összehasonlítás:** a „Mutató" legördülővel válthatsz a mutatók között.
4. **Nyitás-diagram:** a csúszkával növelheted a minimum-nyitásszámot, így a kis mintájú, zajos pontok eltűnnek.
5. **Játékos-profil:** válassz két játékost; a radar mellett a táblázat a nyers értékeket és a percentiliseket mutatja.
6. **Adattábla:** a fejlécre kattintva rendezhető, a névkeresővel szűrhető.

## Projektstruktúra

```
volleyball-dashboard/
├── data/
│   └── hvf_stats.xls            # a HVF statisztikai exportja
├── src/
│   ├── __init__.py
│   ├── dashboard.py             # elrendezés, közös vezérlősáv, módszertan
│   ├── data_loader.py           # beolvasás, tisztítás, csapatadatok, koordináták
│   ├── theme.py                 # közös csapatszínek, kiemelés, csapatválasztó
│   └── components/
│       ├── __init__.py
│       ├── data_table.py        # adattábla
│       ├── map.py               # térkép
│       ├── radar.py             # percentilis-radar
│       ├── scatter.py           # támadás vs. fogadás
│       ├── scatter_serve.py     # nyitás: kockázat vs. hatékonyság
│       └── team_compare.py      # csapat-összehasonlítás
├── tests/                       # komponensenkénti előnézeti szkriptek
├── requirements.txt
└── README.md
```

## Hogyan kerültük el a félrevezető ábrázolást?

A beadandóhoz megadott ellenpéldák tipikus hibáit tudatosan kerültük:

| Tipikus hiba | Amit tettünk |
|---|---|
| **Csonkolt tengely** | Az oszlopdiagram nullától indul; a pontdiagramok tengelyei százalékban feliratozottak, a mediánvonalak viszonyítási pontot adnak. |
| **Átlagok átlaga** | A csapatmutatók összesítettek (összes találat / összes kísérlet), nem a játékosok százalékainak átlaga. Ez a rangsort is megváltoztatta: a MEAFC fogadási mutatója az átlagolós változatban a lista alsó harmadában volt, az összesítettben a 3. helyen áll. |
| **Kis minták** | A nyitás-diagramon állítható minimum-nyitásszám van, a támadás–fogadás diagramon csak a nullánál nagyobb értékű játékosok szerepelnek, a játékos-profil legalább 30 kísérletes sokaságon számol. |
| **Torzító normalizálás (radar)** | A radar percentilis alapú, minden tengelyen kifelé = jobb (a hibák megfordítva); a nyers értékek táblázata mutatja a különbségek valódi nagyságát. A szaggatott kör a liga mediánja (50. percentilis). |
| **Nem összehasonlítható nevező** | A darabszám-alapú mutatókat szettre vetítjük meccs helyett, mert a hosszabb meccsek több szettet, így több ászt és blokkot jelentenek. |
| **Megtévesztő színek** | 13 csapat színe nem különböztethető meg biztonságosan, ezért a kiválasztott csapat színes, a többi szürke; a csapatszínek minden diagramon azonosak, egy szín sem ismétlődik. |
| **Terület-torzítás** | A térképen a jelölők mérete fix és nem hordoz jelentést. |
| **Egyéb** | Nincs 3D-diagram, kördiagram és kettős tengely; az egy diagramon szereplő értékek azonos mértékegységűek. |

## Korlátok

- Az adatok nem tartalmaznak játékposztot, ezért a játékosok összehasonlítása korlátozott.
- A mérkőzés- és szettszám a legtöbbet játszó játékos adatából becsült.
- Egyetlen szezon összesítése: nincs meccsszintű adat és idősor.
- A percentilis a sorrendet mutatja, a különbség nagyságát nem.

## Technológia

- [Python](https://www.python.org/), [pandas](https://pandas.pydata.org/)
- [Panel](https://panel.holoviz.org/) (HoloViz) – a dashboard és az interakciók
- [Plotly](https://plotly.com/python/) – a diagramok és a térkép

Mindkét könyvtár szerepel a [pyviz.org](https://pyviz.org/) eszközlistáján.

## Szerző

**Posta Barnabás** – Adattudomány MSc, adatvizualizációs projekt.