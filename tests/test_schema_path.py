import os
import sys

from glpi_dashboard.data.database import SCHEMA_FILE  # noqa: E402

sys.path.insert(
    0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "src")
)  # noqa: E402


def test_schema_file_exists() -> None:
    assert SCHEMA_FILE.exists(), f"{SCHEMA_FILE} does not exist"
