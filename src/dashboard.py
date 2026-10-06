from __future__ import annotations

import streamlit as st

from components.dream_team import build_dream_team
from components.radar import render_radar
from components.scatter import render_scatter
from components.team_compare import summarize_by_team
from data_loader import load_data


@st.cache_data
def get_data():
    return load_data()


def main() -> None:
    st.set_page_config(page_title="Volleyball Dashboard", layout="wide")
    df = get_data()

    teams = sorted(df["Team"].dropna().unique())
    selected_teams = st.sidebar.multiselect("Teams", teams, default=teams[:5])

    if selected_teams:
        filtered = df[df["Team"].isin(selected_teams)].copy()
    else:
        filtered = df.copy()

    st.title("Volleyball Dashboard")

    metrics = [
        ("Players", len(filtered)),
        ("Teams", filtered["Team"].nunique()),
        ("Total points", int(filtered["Pontok"].fillna(0).sum())),
        ("Average points/set", round(float(filtered["Pont/szett"].mean()), 2) if filtered["Pont/szett"].notna().any() else 0),
    ]

    columns = st.columns(len(metrics))
    for col, (label, value) in zip(columns, metrics):
        col.metric(label, value)

    st.subheader("Player performance")
    scatter = render_scatter(filtered)
    st.plotly_chart(scatter, use_container_width=True)

    left_col, right_col = st.columns(2)
    with left_col:
        selected_player = st.selectbox("Player", filtered["Player"].sort_values().tolist())
        radar = render_radar(filtered, selected_player)
        st.plotly_chart(radar, use_container_width=True)

    with right_col:
        st.subheader("Dream team")
        st.dataframe(build_dream_team(filtered), use_container_width=True)

    st.subheader("Team comparison")
    team_summary = summarize_by_team(filtered)
    st.dataframe(team_summary, use_container_width=True)

    team_chart_data = team_summary.set_index("Team")[["avg_points", "avg_blocks"]]
    st.bar_chart(team_chart_data)


if __name__ == "__main__":
    main()
