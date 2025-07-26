import argparse
import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def ensure_package_dirs(dest: Path) -> None:
    """Create directories for destination and add __init__.py for packages."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.suffix != ".py":
        return

    path = dest.parent
    while REPO_ROOT in path.parents or path == REPO_ROOT:
        init = path / "__init__.py"
        if not init.exists():
            init.touch()
        if path == REPO_ROOT:
            break
        path = path.parent


def git_mv(src: Path, dest: Path) -> None:
    subprocess.run(["git", "mv", str(src), str(dest)], check=True, cwd=REPO_ROOT)


def main() -> int:
    parser = argparse.ArgumentParser(description="Move files according to a map")
    parser.add_argument(
        "--map",
        default="scripts/refactor/file_map.json",
        help="Mapping JSON path",
    )
    args = parser.parse_args()

    mapping = json.loads(Path(args.map).read_text())

    for src_rel, dest_rel in mapping.items():
        src = REPO_ROOT / src_rel
        dest = REPO_ROOT / dest_rel
        if not src.exists():
            print(f"Skipping missing file: {src_rel}")
            continue
        ensure_package_dirs(dest)
        git_mv(src, dest)
        print(f"Moved {src_rel} -> {dest_rel}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
