from __future__ import annotations

import plotly.express as px

OTHER_LABEL = "Többi csapat"
OTHER_COLOR = "#C9CDD3"


def team_color_map(teams) -> dict[str, str]:
    """Stabil csapat -> szín megfeleltetés az egész dashboardhoz."""
    palette = px.colors.qualitative.Dark24
    return {team: palette[i % len(palette)] for i, team in enumerate(sorted(set(teams)))}