import pandas as pd

from backend.services.metrics_service import calculate_dataframe_metrics


def test_calculate_metrics_empty_df():
    df = pd.DataFrame()
    assert calculate_dataframe_metrics(df) == {"total": 0, "opened": 0, "closed": 0}


def test_calculate_metrics_counts():
    df = pd.DataFrame({"status": ["new", "closed", "solved", "pending"]})
    result = calculate_dataframe_metrics(df)
    assert result == {"total": 4, "opened": 2, "closed": 2}
