from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from dash import html


def _status_fig(df: pd.DataFrame) -> go.Figure:
    counts = df.groupby("status").size().reset_index(name="count")
    return px.bar(counts, x="status", y="count")


def compute_ticket_stats(df: pd.DataFrame) -> list[html.Div]:
    """Return aggregated ticket statistics as ready-to-render divs."""
    total = len(df)
    closed = df[df["status"].str.lower() == "closed"].shape[0]
    opened = total - closed
    return [
        html.Div(f"Total: {total}"),
        html.Div(f"Abertos: {opened}"),
        html.Div(f"Fechados: {closed}"),
    ]
