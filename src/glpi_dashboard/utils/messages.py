from __future__ import annotations

import re


_CONTROL_CHARS_RE = re.compile(r"[\x00-\x1f\x7f]")


def sanitize_message(message: str, max_length: int = 200) -> str:
    """Return message without control chars and limited to ``max_length``."""
    cleaned = _CONTROL_CHARS_RE.sub("", message)
    return cleaned[:max_length]
