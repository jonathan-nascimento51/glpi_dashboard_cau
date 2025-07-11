import pytest

pytest.importorskip("pandas")
import pandas as pd

from frontend.components.components import compute_ticket_stats
from glpi_dashboard.acl.normalization import sanitize_status_column


def test_sanitize_status_column():
    df = pd.DataFrame({"status": ["Closed", None, 404, "OPEN", float("nan")]})
    sanitized = sanitize_status_column(df)
    assert sanitized["status"].tolist() == ["closed", "", "404", "open", ""]


def test_compute_ticket_stats_handles_invalid_status():
    df = pd.DataFrame({"status": ["Closed", "closed", None, 404, "OPEN", float("nan")]})
    stats = compute_ticket_stats(df)
    texts = [div.children for div in stats]
    assert "Total: 6" in texts[0]
    assert "Abertos: 4" in texts[1]
    assert "Fechados: 2" in texts[2]
