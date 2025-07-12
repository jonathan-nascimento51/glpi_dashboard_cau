#!/usr/bin/env python
"""Generate ARCHITECTURE.md from ADR-0007 table."""
from __future__ import annotations

import re
from pathlib import Path

ADR_PATH = Path("docs/adr/0007-refined-project-structure.md")
OUT_PATH = Path("ARCHITECTURE.md")

TABLE_RE = re.compile(r"^\|\s*`(?P<path>.+?)`\s*\|\s*(?P<purpose>.+?)\s*\|")


def parse_table(text: str) -> list[tuple[str, str]]:
    """Extract (path, purpose) entries from a markdown table."""
    entries: list[tuple[str, str]] = []
    in_table = False
    for line in text.splitlines():
        if line.strip().startswith("| path"):
            in_table = True
            continue
        if in_table:
            if not line.strip().startswith("|"):
                break
            match = TABLE_RE.match(line)
            if match:
                entries.append((match.group("path"), match.group("purpose")))
    return entries


def build_mermaid(entries: list[tuple[str, str]]) -> str:
    """Return a mermaid diagram listing the directories."""
    lines = ["graph TD"]
    for path, _ in entries:
        label = path.strip("/") or "/"
        lines.append(f"    root --> {label}['{label}']")
    return "\n".join(lines)


def generate_doc(entries: list[tuple[str, str]]) -> str:
    """Create the ARCHITECTURE.md content."""
    lines = [
        "# Project Architecture",
        "",
        "This file is generated from [docs/adr/0007-refined-project-structure.md](docs/adr/0007-refined-project-structure.md).",
        "",
        "## Directory Overview",
        "",
        "| Path | Purpose |",
        "| ---- | ------- |",
    ]
    for path, purpose in entries:
        lines.append(f"| `{path}` | {purpose} |")
    lines.append("")
    lines.append("```mermaid")
    lines.append(build_mermaid(entries))
    lines.append("```")
    lines.append("")
    lines.append(
        "For component relations see [docs/architecture.md](docs/architecture.md)."
    )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    text = ADR_PATH.read_text(encoding="utf-8")
    entries = parse_table(text)
    if not entries:
        raise SystemExit("No table found in ADR file")
    OUT_PATH.write_text(generate_doc(entries), encoding="utf-8")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
