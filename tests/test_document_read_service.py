from pathlib import Path

import pytest

from backend.services.document_service import read_file


def test_read_file_success(tmp_path):
    p = tmp_path / "kb.txt"
    p.write_text("hello")
    assert read_file(p) == "hello"


def test_read_file_not_found(tmp_path):
    p = tmp_path / "missing.txt"
    with pytest.raises(FileNotFoundError):
        read_file(p)


def test_read_file_permission_error(monkeypatch, tmp_path):
    p = tmp_path / "secret.txt"
    p.write_text("data")

    def fail(*args, **kwargs):
        raise PermissionError

    monkeypatch.setattr(Path, "open", lambda *a, **k: fail())
    with pytest.raises(PermissionError):
        read_file(p)
