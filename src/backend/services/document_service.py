from __future__ import annotations

from pathlib import Path


def read_file(path: str | Path) -> str:
    """Return the text contents of ``path``.

    Errors are propagated so callers can translate them into HTTP responses.
    """
    file_path = Path(path)
    with file_path.open("r", encoding="utf-8") as fh:
        return fh.read()


__all__ = ["read_file"]
