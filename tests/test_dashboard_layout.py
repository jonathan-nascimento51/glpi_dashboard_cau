import shutil
import subprocess

import dash_bootstrap_components as dbc
import pandas as pd
import pytest
from dash import Dash

from frontend.layout.layout import build_layout

_chromedriver = shutil.which("chromedriver")
try:
    _chrome_ok = (
        _chromedriver is not None
        and subprocess.run(
            [_chromedriver, "--version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        ).returncode
        == 0
    )
except OSError:
    _chrome_ok = False


@pytest.mark.skipif(not _chrome_ok, reason="chromedriver not installed")
def test_build_layout_contains_dropdown(dash_duo):
    """build_layout should render dropdown with options from df."""
    df = pd.DataFrame({"status": ["New", "Solved"]})
    app = Dash(__name__)
    app.layout = build_layout(df)

    dash_duo.start_server(app)

    dropdown = dash_duo.find_element("#status-filter")
    options = dropdown.find_elements("tag name", "option")
    labels = [o.text for o in options]
    values = [o.get_attribute("value") for o in options]

    assert labels == ["All", "New", "Solved"]
    assert values == ["", "New", "Solved"]


def test_build_layout_none_returns_alert():
    alert = build_layout(None)
    assert isinstance(alert, dbc.Alert)
    assert "Erro na conexão" in alert.children
