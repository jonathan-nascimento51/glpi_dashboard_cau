"""Append run metadata to log.jsonl for simple audit."""

import argparse
import json
import os
import uuid
from datetime import datetime


def main() -> None:
    parser = argparse.ArgumentParser(description="Log execution details.")
    parser.add_argument(
        "--source",
        required=True,
        help="Source JSON file used",
    )
    parser.add_argument(
        "--user",
        default=os.getenv("USER", "unknown"),
        help="Executor",
    )
    parser.add_argument(
        "--logfile",
        default="log.jsonl",
        help="Log output file",
    )
    args = parser.parse_args()

    entry = {
        "id": str(uuid.uuid4()),
        "time": datetime.utcnow().isoformat() + "Z",
        "source": args.source,
        "user": args.user,
    }

    with open(args.logfile, "a") as f:
        f.write(json.dumps(entry) + "\n")
    print(f"✔ Logged execution to {args.logfile}")


if __name__ == "__main__":
    main()
