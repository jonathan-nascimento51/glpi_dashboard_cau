import pandas as pd
import plotly.graph_objs as go
import pytest
from dash import html
from frontend.components.components import _status_fig, compute_ticket_stats

pytest.importorskip("pandas")


def test_status_fig_bar_counts() -> None:
    df = pd.DataFrame({"status": ["new", "closed", "closed", "new", "closed"]})
    fig = _status_fig(df)
    assert isinstance(fig, go.Figure)

    bars = dict(zip(fig.data[0].x, fig.data[0].y))
    assert bars == {"new": 2, "closed": 3}


def test_compute_ticket_stats_totals() -> None:
    df = pd.DataFrame({"status": ["new", "closed", "closed"]})
    stats = compute_ticket_stats(df)
    assert len(stats) == 3
    assert all(isinstance(div, html.Div) for div in stats)

    texts = [div.children for div in stats]
    assert texts[0] == "Total: 3"
    assert texts[1] == "Abertos: 1"
    assert texts[2] == "Fechados: 2"
