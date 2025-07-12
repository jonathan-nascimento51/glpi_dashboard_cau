import subprocess
import time
from collections.abc import Generator

import pytest

from playwright.sync_api import expect, sync_playwright


pytest.importorskip("playwright.sync_api")


COMPOSE_CMD = ["docker", "compose"]


@pytest.fixture(scope="session", autouse=True)
def compose_up() -> Generator[None, None, None]:
    subprocess.run(COMPOSE_CMD + ["up", "-d"], check=True)
    # give services time to start
    time.sleep(10)
    yield
    subprocess.run(COMPOSE_CMD + ["down"], check=True)


@pytest.mark.e2e
def test_ticket_stats_page() -> None:
    """End-to-end test for the Ticket Statistics page."""

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page()
        page.goto("http://localhost:5173")

        expect(page.get_by_role("heading", name="Ticket Statistics")).to_be_visible()
        # Three stats cards should be rendered once data loads
        expect(page.locator("[data-testid='stats-value']")).to_have_count(3)

        browser.close()
