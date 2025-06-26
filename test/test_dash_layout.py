import importlib

def test_import_dash_layout():
    module = importlib.import_module("dash_layout")
    assert module is not None
