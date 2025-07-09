from src.backend.db.database import SCHEMA_FILE


def test_schema_file_exists() -> None:
    assert SCHEMA_FILE.exists(), f"{SCHEMA_FILE} does not exist"
