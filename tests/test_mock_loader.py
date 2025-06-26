import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))  # noqa: E402

import pandas as pd  # noqa: E402
from mock_loader import load_mock_data  # noqa: E402
from config import USE_MOCK  # noqa: E402


def test_load_mock_data():
    df = load_mock_data("mock/sample_data.json")
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert set(["id", "status", "group"]).issubset(df.columns)


def test_use_mock_flag_type():
    assert isinstance(USE_MOCK, bool)
