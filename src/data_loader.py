from __future__ import annotations

from pathlib import Path
import pandas as pd

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "hvf_stats.xls"

# --- Globális szűrők ---
MIN_GAMES = 5
MIN_SETS = 8


def load_data() -> pd.DataFrame:
    """Load and clean the HVF statistics sheet.
    Csak a nyers adatokat tölti be, kiszűri a globális minimumot,
    és létrehozza a teljes nevet.
    """
    df = pd.read_excel(DATA_PATH, sheet_name=0, header=1)

    if df.empty:
        raise ValueError(f"The file {DATA_PATH} is empty or malformed.")

    # --- Csak a szükséges oszlopok kiválasztása ---
    keep_columns = {
        0: "Surname",
        1: "Name",
        2: "Team",
        3: "Games",
        4: "Sets",
        5: "Points",
        6: "BreakPoints",
        7: "Wins-Losses",
        8: "ServeErrors",      # S =
        9: "S !", 10: "S /", 11: "S -", 12: "S +",
        13: "Aces",            # S #
        14: "R=",              # R =
        15: "R!",              # R !
        16: "R/",              # R /
        17: "R-",              # R -
        18: "R+",              # R +
        19: "R#",              # R #
        21: "PerfectReceive%", # Kiv.%
        22: "A=",              # A =
        23: "A!",              # A !
        24: "A/",              # A /
        25: "A-",              # A -
        26: "A+",              # A +
        27: "A#",              # A #
        28: "Attack%",         # Tám%
        29: "B=",              # B =
        34: "Blocks",          # B #

    }

    df = df.iloc[:, list(keep_columns.keys())].copy()
    df.columns = list(keep_columns.values())

    # --- Sorok tisztítása ---
    df = df.dropna(subset=["Surname"]).copy()
    df = df[~df["Surname"].astype(str).str.contains("Sorted", case=False, na=False)].copy()

    # --- Számos oszlopok konvertálása ---
    numeric_cols = [
        "Games", "Sets", "Points", "BreakPoints", "Wins-Losses",
        "ServeErrors", "S !", "S /", "S -", "S +", "Aces", # ÚJ SOR "Aces",
        "R=", "R!", "R/", "R-", "R+", "R#",
        "A=", "A!", "A/", "A-", "A+", "A#",
        "Blocks", "B="
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        
    # ÚJ SOR: Összes nyitás kiszámítása
    df["ServeTotal"] = (
        df["ServeErrors"].fillna(0) + df["S !"].fillna(0) + df["S /"].fillna(0) +
        df["S -"].fillna(0) + df["S +"].fillna(0) + df["Aces"].fillna(0)
    )

    # --- Százalékos oszlopok (csak a % jel levágása) ---
    for col in ["PerfectReceive%", "Attack%"]:
        series = df[col].astype(str).str.replace("%", "", regex=False)
        series = series.str.replace(",", ".", regex=False)
        series = series.replace({".": pd.NA, "nan": pd.NA, "": pd.NA})
        df[col] = pd.to_numeric(series, errors="coerce")

    # --- Globális szűrés (csak meccs és szett alapján!) ---
    before = len(df)
    df = df[(df["Games"] > MIN_GAMES) & (df["Sets"] >= MIN_SETS)].copy()
    after = len(df)
    print(f"[data_loader] Szűrés: {before} -> {after} játékos "
          f"(Games > {MIN_GAMES}, Sets >= {MIN_SETS})")

    # --- Teljes név ---
    df["Player"] = (
        df["Surname"].astype(str).str.strip()
        + " "
        + df["Name"].astype(str).str.strip()
    )
    df["Player"] = df["Player"].str.replace(r"\s+", " ", regex=True).str.strip()
    df["AttackErrorPG"] = df["A="] / df["Games"].replace(0, pd.NA)
    df["ServeErrorPG"] = df["ServeErrors"] / df["Games"].replace(0, pd.NA)
    df["ReceiveErrorPG"] = df["R="] / df["Games"].replace(0, pd.NA)
    df["BlockErrorPG"] = df["B="] / df["Games"].replace(0, pd.NA)


        # --- Térkép adatok (Városok és koordináták) ---
    team_locations = {
        "FINO KAPOSVÁR": ("Kaposvár", 46.3594, 17.7968),
        "Vegyész RC Kazincbarcika": ("Kazincbarcika", 48.2500, 20.6333),
        "Máv Előre Foxconn": ("Székesfehérvár", 47.1910, 18.4108),
        "TFSE": ("Budapest", 47.4888, 19.0268),
        "MAFC": ("Budapest", 47.6181, 19.1903),
        "PRESTIGE FITNESS PSE": ("Budapest", 47.4693, 19.1293),
        "DEAC": ("Debrecen", 47.5316, 21.6273),
        "MEAFC-Peka Bau": ("Miskolc", 48.1035, 20.7784),
        "SWISSTEN DÁG KSE": ("Dág", 47.6667, 18.7333),
        "VIDUX-SZEGEDI RSE": ("Szeged", 46.2530, 20.1414),
        "Kecskeméti RC": ("Kecskemét", 46.9062, 19.6913),
        "Szolnoki RK-SC SI": ("Szolnok", 47.1747, 20.1764),
        "DKSE": ("Dunaújváros", 46.9619, 18.9355),
    }

    # Új oszlopok létrehozása
    df["City"] = df["Team"].map(lambda t: team_locations.get(t, ("Ismeretlen", 0, 0))[0])
    df["Lat"] = df["Team"].map(lambda t: team_locations.get(t, ("Ismeretlen", 0, 0))[1])
    df["Lon"] = df["Team"].map(lambda t: team_locations.get(t, ("Ismeretlen", 0, 0))[2])

    return df


# A filter_by_metric egyelőre üres, mert most csak a nyers adatot nézzük
def filter_by_metric(df: pd.DataFrame, metric: str) -> pd.DataFrame:
    return df


if __name__ == "__main__":
    frame = load_data()
    print()
    print(frame.head().to_string(index=False))
    print()
    print("Shape:", frame.shape)
    print()
    print("Columns:", frame.columns.tolist())