import importlib
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "src"))


def test_load_data_mock(monkeypatch):
    monkeypatch.setenv("USE_MOCK_DATA", "true")
    import src.glpi_dashboard.config.settings as settings
    importlib.reload(settings)
    import main
    importlib.reload(main)

    df = main.load_data()
    assert df is not None
    assert not df.empty
