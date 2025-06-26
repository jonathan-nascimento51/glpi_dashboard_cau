import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))  # noqa: E402

<<<<<<< ours
<<<<<<< ours
<<<<<<< ours
from scripts.gen_mock_data import generate_tickets, paginate
=======
from scripts.gen_mock_data import generate_tickets, paginate  # noqa: E402
>>>>>>> theirs
=======
from scripts.gen_mock_data import generate_tickets, paginate  # noqa: E402
>>>>>>> theirs
=======
from scripts.gen_mock_data import generate_tickets, paginate  # noqa: E402
>>>>>>> theirs


def test_generate_count():
    tickets = generate_tickets(5)
    assert len(tickets) == 5
    assert all("id" in t for t in tickets)


def test_null_fields():
    tickets = generate_tickets(5, null_rate=1.0)
    assert any(t.get("assigned_to") is None for t in tickets)


def test_error_injection():
    tickets = generate_tickets(5, error_rate=1.0)
    assert any("id" not in t or "status" not in t for t in tickets)


def test_pagination():
    tickets = generate_tickets(75)
    pages = paginate(tickets, page_size=50)
    assert len(pages) == 2
    assert sum(len(p["tickets"]) for p in pages) == 75
