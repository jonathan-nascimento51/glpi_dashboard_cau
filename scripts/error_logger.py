#!/usr/bin/env python
"""Save error messages to a JSON log file."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

STACK_RE = re.compile(r'File "(?P<file>.+?)", line (?P<line>\d+)')


def read_error_text(arg_text: str | None) -> str:
    """Return the error text from stdin or argument."""
    if not sys.stdin.isatty():
        return sys.stdin.read()
    if arg_text is not None:
        return arg_text
    return ""


def extract_metadata(text: str, agent: str | None) -> dict[str, object]:
    """Extract file, line and language information from the error text."""
    match = STACK_RE.search(text)
    file_path = match.group("file") if match else None
    line = int(match.group("line")) if match else None
    language = None
    if file_path:
        _, ext = os.path.splitext(file_path)
        if ext:
            language = ext.lstrip(".")
    return {
        "timestamp": f"{datetime.now(timezone.utc).isoformat()}Z",
        "stack": text.strip(),
        "file": file_path,
        "line": line,
        "language": language,
        "agent": agent,
    }


def append_log(entry: dict[str, object], log_path: Path) -> None:
    """Append an entry to the JSON log file."""
    log_path.parent.mkdir(exist_ok=True)
    data: list[dict[str, object]] = []
    if log_path.exists():
        with log_path.open("r", encoding="utf-8") as fh:
            loaded = json.load(fh)
        data = loaded
    data.append(entry)
    with log_path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  some_command 2>&1 | %(prog)s
  %(prog)s --text "My custom error message"
""",
    )
    parser.add_argument("--text", help="Error text. If omitted, read from stdin")
    parser.add_argument("--agent", help="Originating agent", default=None)
    parser.add_argument(
        "--logfile",
        default="logs/errors_log.json",
        help="Log file path",
    )
    args = parser.parse_args()

    text = read_error_text(args.text)
    if not text:
        parser.error("No error text provided via stdin or --text")

    entry = extract_metadata(text, agent=args.agent)
    append_log(entry, Path(args.logfile))
    print(f"\u2714 Logged error to {args.logfile}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
