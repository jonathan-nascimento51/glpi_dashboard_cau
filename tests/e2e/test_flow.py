import subprocess
import time
from collections.abc import Generator

import pytest

pytest.importorskip("playwright.sync_api")
from playwright.sync_api import sync_playwright

COMPOSE_FILE = "docker-compose-dev.yml"


@pytest.fixture(scope="session", autouse=True)
def compose_up() -> Generator[None, None, None]:
    subprocess.run(["docker", "compose", "-f", COMPOSE_FILE, "up", "-d"], check=True)
    # give services time to start
    time.sleep(10)
    yield
    subprocess.run(["docker", "compose", "-f", COMPOSE_FILE, "down"], check=True)


@pytest.mark.e2e
def test_full_checkout_flow() -> None:
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page()
        page.goto("http://localhost:5173")
        page.fill("input[name=email]", "demo@example.com")
        page.fill("input[name=password]", "secret")
        page.click("text=Login")
        page.click("text=Add to cart")
        page.click("text=Checkout")
        assert page.url.endswith("/confirmation")
        browser.close()
