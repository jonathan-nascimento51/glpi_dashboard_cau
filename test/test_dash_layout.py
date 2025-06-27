import importlib


def test_import_dash_layout():
    module = importlib.import_module("glpi_dashboard.dashboard.layout")
    assert module is not None
