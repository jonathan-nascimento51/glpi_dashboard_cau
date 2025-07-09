import importlib


def test_import_dash_layout():
    module = importlib.import_module("frontend.layout.layout")
    assert module is not None


def test_import_cli_groups():
    module = importlib.import_module("backend.services.tickets_groups")
    assert module is not None
