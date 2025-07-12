import pandas as pd
import pytest

from backend.adapters.normalization import sanitize_status_column
from frontend.components.components import compute_ticket_stats

pytest.importorskip("pandas")


def test_sanitize_status_column():
    df = pd.DataFrame({"status": ["Closed", None, 404, "OPEN", float("nan")]})
    sanitized = sanitize_status_column(df)
    assert sanitized["status"].tolist() == ["closed", "", "404", "open", ""]


def test_compute_ticket_stats_handles_invalid_status():
    df = pd.DataFrame({"status": ["Closed", "closed", None, 404, "OPEN", float("nan")]})
    stats = compute_ticket_stats(df)
    texts = [str(div.children) for div in stats]
    assert "Total: 6" == texts[0]
    assert "Abertos: 4" == texts[1]
    assert "Fechados: 2" == texts[2]
