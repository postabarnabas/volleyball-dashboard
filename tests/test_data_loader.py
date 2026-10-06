from src.data_loader import load_data


def test_load_data_returns_clean_player_dataframe():
    df = load_data()

    required = {
        "Surname",
        "Name",
        "Team",
        "Player",
        "Pontok",
        "Szettek",
        "Pont/szett",
    }

    missing = required - set(df.columns)
    assert not missing, f"Missing expected columns: {sorted(missing)}"
    assert len(df) > 0
    assert df["Player"].str.contains(" ").any()
    assert df["Pont/szett"].notna().any()
