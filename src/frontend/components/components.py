from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from dash import html
from glpi_dashboard.utils import sanitize_status_column


def _status_fig(df: pd.DataFrame) -> go.Figure:
    counts = df.groupby("status").size().reset_index(name="count")
    return px.bar(counts, x="status", y="count")


def compute_ticket_stats(df: pd.DataFrame) -> list[html.Div]:
    """Return aggregated ticket statistics as ready-to-render divs."""
    clean = sanitize_status_column(df)
    total = len(clean)
    closed = clean[clean["status"] == "closed"].shape[0]
    opened = total - closed
    return [
        html.Div(f"Total: {total}"),
        html.Div(f"Abertos: {opened}"),
        html.Div(f"Fechados: {closed}"),
    ]
