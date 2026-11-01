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
        "Blocks",
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