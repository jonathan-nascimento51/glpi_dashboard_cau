"""Offline Dash app using JSON dump."""

import json
from pathlib import Path

import pandas as pd
from dash import Dash

from data_pipeline import process_raw
from dash_layout import build_layout


DATA_FILE = Path("mock/sample_data.json")


def load_data(path: Path = DATA_FILE) -> pd.DataFrame:
    """Load and process ticket data from JSON."""
    with path.open() as f:
        raw = json.load(f)
    return process_raw(raw)


def create_app(df: pd.DataFrame) -> Dash:
    """Create Dash application."""
    app = Dash(__name__)
    app.layout = build_layout(df)
    return app


if __name__ == "__main__":
    df = load_data()
    app = create_app(df)
    app.run_server(debug=True)
