#!/usr/bin/env python
"""Download wheel files for offline installation."""

from __future__ import annotations

import subprocess
from pathlib import Path

import click


@click.command()
@click.argument("directory", required=False, default="wheels")
def main(directory: str) -> None:
    """Download all dependencies into *directory*."""
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)

    cmd = [
        "pip",
        "download",
        "-r",
        "requirements.txt",
        "-r",
        "requirements-dev.txt",
        "-d",
        str(target),
    ]
    subprocess.run(cmd, check=True)

    click.echo(
        "Packages saved to %s\nInstall later with:\n"
        "pip install --no-index --find-links=%s "
        "-r requirements.txt -r requirements-dev.txt" % (target, target)
    )


if __name__ == "__main__":  # pragma: no cover
    main()
