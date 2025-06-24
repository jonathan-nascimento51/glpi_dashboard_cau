import shutil
from pathlib import Path


def create_env(
    example: Path = Path(".env.example"), target: Path = Path(".env")
) -> None:
    """Create a local .env by copying from an example file if not present."""
    if target.exists():
        print(f"{target} already exists")
        return
    if not example.exists():
        raise FileNotFoundError(example)
    shutil.copy(example, target)
    print(f"Created {target} from {example}")


if __name__ == "__main__":
    create_env()
