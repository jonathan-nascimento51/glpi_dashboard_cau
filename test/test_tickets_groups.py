import importlib

def test_import_cli_groups():
    module = importlib.import_module("glpi_dashboard.cli.tickets_groups")
    assert module is not None
