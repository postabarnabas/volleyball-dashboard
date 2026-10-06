from __future__ import annotations

from pathlib import Path
import pandas as pd

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "hvf_stats.xls"


def load_data() -> pd.DataFrame:    
    df = pd.read_excel(DATA_PATH, sheet_name=0, header=1)

    if df.empty:
        raise ValueError(f"The file {DATA_PATH} is empty or malformed.")

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
        13: "Aces",            # S #
        14: "ReceiveErrors",   # R =
        20: "PositiveReceive%",  # +és#%
        21: "PerfectReceive%",   # Kiv.%
        22: "AttackErrors",    # A =
        24: "AttackBlocked",   # A /
        28: "Attack%",         # Tám%
        34: "Blocks",          # B #
    }

    df = df.iloc[:, list(keep_columns.keys())].copy()
    df.columns = list(keep_columns.values())

    df = df.dropna(subset=["Surname"]).copy()
    df = df[~df["Surname"].astype(str).str.contains("Sorted", case=False, na=False)].copy()

    numeric_cols = [
        "Games", "Sets", "Points", "BreakPoints", "Wins-Losses",
        "ServeErrors", "Aces", "ReceiveErrors",
        "AttackErrors", "AttackBlocked", "Blocks",
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    for col in ["PositiveReceive%", "PerfectReceive%", "Attack%"]:
        series = df[col].astype(str).str.replace("%", "", regex=False)
        series = series.str.replace(",", ".", regex=False)
        series = series.replace({".": pd.NA, "nan": pd.NA, "": pd.NA})
        df[col] = pd.to_numeric(series, errors="coerce")

    df["Player"] = (
        df["Surname"].astype(str).str.strip()
        + " "
        + df["Name"].astype(str).str.strip()
    )
    df["Player"] = df["Player"].str.replace(r"\s+", " ", regex=True).str.strip()

    df["PointsPerSet"] = df["Points"] / df["Sets"].replace(0, pd.NA)
    df["AcesPerSet"] = df["Aces"] / df["Sets"].replace(0, pd.NA)
    df["BlocksPerSet"] = df["Blocks"] / df["Sets"].replace(0, pd.NA)

    return df


if __name__ == "__main__":
    frame = load_data()
    print(frame.head().to_string(index=False))
    print()
    print("Shape:", frame.shape)
    print()
    print("Columns:", frame.columns.tolist())