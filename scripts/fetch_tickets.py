import argparse
from pathlib import Path

from glpi_api import get_tickets
from data_pipeline import process_raw, save_json


def fetch_and_save(
    output: Path = Path("mock/sample_data.json"),
    status: str | None = None,
    limit: int = 100,
) -> None:
    """Fetch tickets from GLPI and save them to a JSON file."""
    tickets = get_tickets(status=status, limit=limit)
    df = process_raw(tickets)
    save_json(df, str(output))


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch tickets from GLPI API")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("mock/sample_data.json"),
        help="Path to save JSON data",
    )
    parser.add_argument("--status", help="Filter by status")
    parser.add_argument(
        "--limit", type=int, default=100, help="Maximum results"
    )
    args = parser.parse_args()

    fetch_and_save(output=args.output, status=args.status, limit=args.limit)
    print(f"✔ Saved tickets to {args.output}")


if __name__ == "__main__":
    main()
