import importlib


def test_load_data_mock(monkeypatch):
    monkeypatch.setenv("USE_MOCK_DATA", "true")
    import backend.core.settings as settings

    importlib.reload(settings)
    import dashboard_app as main

    importlib.reload(main)

    df = main.load_data()
    assert df is not None
    assert not df.empty
