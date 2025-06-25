"""Simple Dash layout for ticket overview."""

from __future__ import annotations

import pandas as pd
from dash import dash_table, dcc, html
import plotly.express as px


def build_layout(df: pd.DataFrame) -> html.Div:
    """Build dashboard layout."""
    total = len(df)
    closed = df[df["status"].str.lower() == "closed"].shape[0]
    opened = total - closed

    status_counts = df.groupby("status").size().reset_index(name="count")
    fig = px.bar(status_counts, x="status", y="count")

    table = dash_table.DataTable(
        id="ticket-table",
        data=df[["id", "name", "status", "assigned_to"]].to_dict("records"),
        columns=[
            {"name": c, "id": c}
            for c in ["id", "name", "status", "assigned_to"]
        ],
        page_size=10,
    )

    return html.Div(
        [
            html.H1("GLPI Dashboard"),
            html.Div(
                [
                    html.Div(f"Total: {total}"),
                    html.Div(f"Abertos: {opened}"),
                    html.Div(f"Fechados: {closed}"),
                ]
            ),
            dcc.Graph(figure=fig),
            table,
        ]
    )
