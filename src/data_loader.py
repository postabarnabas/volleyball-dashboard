from __future__ import annotations
from pathlib import Path
import pandas as pd

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "hvf_stats.xls"

def _clean_column_name(column_name: object) -> str:
    value = str(column_name).strip()
    value = value.replace("Sorted ascSorted desc", "")
    value = value.replace("Sorted desc", "")
    value = value.replace("Sorted", "")
    value = value.replace(" asc", "")
    value = value.replace(" desc", "")
    value = value.strip()
    return value

def load_data() -> pd.DataFrame:
    """Load and clean the HVF statistics sheet."""
    df = pd.read_excel(DATA_PATH, sheet_name=0, header=1)

    if df.empty:
        raise ValueError(f"The file {DATA_PATH} is empty or malformed.")

    df = df.rename(columns={
        df.columns[0]: "Surname",
        df.columns[1]: "Name",
        df.columns[2]: "Team",
        df.columns[3]: "Game played",
        df.columns[4]: "Sets played",
        df.columns[5]: "Points",
        df.columns[6]: "BP",
        df.columns[7]: "GY-V",
        df.columns[8]: "Missed serve",
        df.columns[13]: "Ace",
        df.columns[14]: "Receiving Error",
        df.columns[20]: "Positive receiving %",
        df.columns[21]: "Perfect receiving %",
        df.columns[22]: "Attack Error",
        df.columns[24]: "Attack blocked",
        df.columns[28]: 'Attack %',
        df.columns[34]: 'Block'
    })



    df.columns = [_clean_column_name(column) for column in df.columns]
    df = df.dropna(subset=["Surname"]).copy()
    df = df[~df["Surname"].astype(str).str.contains("Sorted", case=False, na=False)].copy()
    df = df.replace(".", pd.NA)

    numeric_cols = [
        "Game played", "Sets played", "Points", "BP", "GY-V",
        "S =", "S !", "S /", "S -", "S +", "S #",
        "R =", "R !", "R /", "R -", "R +", "R #",
        "A =", "A !", "A /", "A -", "A +", "A #",
        "B =", "B !", "B /", "B -", "B +", "B #",
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    for col in ["+és#%", "Kiv.%", "Tám%"]:
        if col in df.columns:
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


    return df


if __name__ == "__main__":
    frame = load_data()
    print(frame.head().to_string(index=False))
    print(frame.shape)
    print(frame.columns.tolist())
