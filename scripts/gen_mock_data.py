"""Generate synthetic GLPI tickets for offline testing.

Example:
<<<<<<< ours
<<<<<<< ours
    python scripts/gen_mock_data.py --count 50 --null-rate 0.1 --error-rate 0.05
=======
    python scripts/gen_mock_data.py --count 50 \
        --null-rate 0.1 --error-rate 0.05
>>>>>>> theirs
=======
    python scripts/gen_mock_data.py --count 50 \
        --null-rate 0.1 --error-rate 0.05
>>>>>>> theirs
"""

import argparse
import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any

STATUSES = ["new", "assigned", "in_progress", "closed"]
GROUPS = ["N1", "N2", "N3"]
USERS = ["alice", "bob", "carol", "dave"]
PRIORITIES = [0, 1, 5, 10]


def _maybe_null(value: Any, null_rate: float) -> Any:
    return None if random.random() < null_rate else value


<<<<<<< ours
<<<<<<< ours
def _generate_ticket(idx: int, null_rate: float, error_rate: float) -> Dict[str, Any]:
=======
=======
>>>>>>> theirs
def _generate_ticket(
    idx: int,
    null_rate: float,
    error_rate: float,
) -> Dict[str, Any]:
<<<<<<< ours
>>>>>>> theirs
=======
>>>>>>> theirs
    ticket = {
        "id": idx,
        "status": random.choice(STATUSES),
        "group": random.choice(GROUPS),
        "date_creation": (
            datetime.utcnow() - timedelta(days=random.randint(0, 30))
        ).isoformat(),
        "assigned_to": random.choice(USERS),
        "name": f"ticket-{idx}",
        "priority": random.choice(PRIORITIES),
<<<<<<< ours
<<<<<<< ours
        "watchers": [random.choice(USERS) for _ in range(random.randint(0, 2))],
=======
=======
>>>>>>> theirs
        # fmt: off
        "watchers": [
            random.choice(USERS)
            for _ in range(random.randint(0, 2))
        ],
        # fmt: on
<<<<<<< ours
>>>>>>> theirs
=======
>>>>>>> theirs
    }

    for key in ["assigned_to", "watchers", "priority"]:
        ticket[key] = _maybe_null(ticket[key], null_rate)

    if isinstance(ticket.get("watchers"), list) and random.random() < 0.3:
        ticket["watchers"] = []

    if random.random() < error_rate:
        ticket.pop(random.choice(list(ticket.keys())), None)

    return ticket


def generate_tickets(
    count: int, null_rate: float = 0.0, error_rate: float = 0.0
) -> List[Dict[str, Any]]:
    """Return a list of fake GLPI tickets."""
<<<<<<< ours
<<<<<<< ours
    return [_generate_ticket(i + 1, null_rate, error_rate) for i in range(count)]
=======
=======
>>>>>>> theirs
    # fmt: off
    return [
        _generate_ticket(i + 1, null_rate, error_rate)
        for i in range(count)
    ]
    # fmt: on
<<<<<<< ours
>>>>>>> theirs
=======
>>>>>>> theirs


def paginate(
    tickets: List[Dict[str, Any]], page_size: int = 50
) -> List[Dict[str, Any]]:
    """Return paginated structure for tickets."""
    pages = []
    for start in range(0, len(tickets), page_size):
        page = start // page_size + 1
        pages.append(
            {
                "page": page,
<<<<<<< ours
<<<<<<< ours
                "tickets": tickets[start : start + page_size],
=======
                "tickets": tickets[start : start + page_size],  # noqa: E203
>>>>>>> theirs
=======
                "tickets": tickets[start : start + page_size],  # noqa: E203
>>>>>>> theirs
            }
        )
    return pages


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate mock GLPI tickets")
<<<<<<< ours
<<<<<<< ours
    parser.add_argument("--count", type=int, default=100, help="Number of records")
=======
=======
>>>>>>> theirs
    parser.add_argument(
        "--count",
        type=int,
        default=100,
        help="Number of records",
    )
<<<<<<< ours
>>>>>>> theirs
=======
>>>>>>> theirs
    parser.add_argument(
        "--null-rate",
        type=float,
        default=0.0,
        help="Probability for null fields",
    )
    parser.add_argument(
        "--error-rate",
        type=float,
        default=0.0,
        help="Probability for missing fields",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("mock/sample_data.json"),
        help="Destination JSON file",
    )
    parser.add_argument(
        "--page-size",
        type=int,
        default=50,
        help="Page size for pagination metadata",
    )
    args = parser.parse_args()

    tickets = generate_tickets(args.count, args.null_rate, args.error_rate)
    data = {
        "data": tickets,
        "pages": paginate(tickets, args.page_size),
    }
    with args.output.open("w") as f:
        json.dump(data, f, indent=2)

    print(f"✔ Generated {args.count} tickets at {args.output}")


if __name__ == "__main__":
    main()
