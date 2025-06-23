"""Compute SHA‑256 hash of a JSON file and write <file>.sha256."""


import argparse
import hashlib
import pathlib
import sys


def sha256sum(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate SHA‑256 for JSON dump.")
    parser.add_argument("json_file", type=pathlib.Path, help="Path to JSON file")
    args = parser.parse_args()

    if not args.json_file.exists():
        sys.exit(f"File not found: {args.json_file}")

    digest = sha256sum(args.json_file)
    sha_file = args.json_file.with_suffix(args.json_file.suffix + ".sha256")
    sha_file.write_text(digest)
    print(f"✔ Hash written to {sha_file}")


if __name__ == "__main__":
    main()
