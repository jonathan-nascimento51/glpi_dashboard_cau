from __future__ import annotations

import pandas as pd
from dash import callback, Output, Input

from .components import _status_fig, compute_ticket_stats


def register_callbacks(app, df: pd.DataFrame) -> None:
    @callback(
        Output("ticket-table", "data"),
        Output("status-graph", "figure"),
        Output("stats", "children"),
        Input("init-load", "n_intervals"),
    )
    def load_data(_):
        fig = _status_fig(df)
        stats = compute_ticket_stats(df)
        return df.to_dict("records"), fig, stats
