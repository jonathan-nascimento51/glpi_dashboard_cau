#!/usr/bin/env python
"""Detect merge conflict markers in the project tree."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

MERGE_MARKERS = (
    "<<<<<<< ",
    "=======",
    ">>>>>>> ",
)


def scan_file(path: Path) -> list[int]:
    """Return line numbers containing merge markers."""
    lines = []
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as fh:
            for idx, line in enumerate(fh, 1):
                stripped = line.lstrip()
                # fmt: off
                if any(
                    stripped.startswith(marker)
                    for marker in MERGE_MARKERS
                ):
                    lines.append(idx)
                # fmt: on
    except Exception as exc:  # RESOLVIDO: robust file handling
        print(f"failed to read {path}: {exc}", file=sys.stderr)
    return lines


def scan_tree(root: Path) -> int:
    """Scan all files under *root* and report markers."""
    has_markers = False
    for path in root.rglob("*"):
        if path.is_file():
            if matches := scan_file(path):
                lines = ", ".join(str(n) for n in matches)
                print(f"{path}: conflict markers at lines {lines}")
                has_markers = True
    return 1 if has_markers else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Directory to scan (defaults to current working directory)",
    )
    args = parser.parse_args()
    return scan_tree(Path(args.directory))


if __name__ == "__main__":
    raise SystemExit(main())
