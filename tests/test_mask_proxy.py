import pytest

from backend.infrastructure.glpi.glpi_session import mask_proxy_url


@pytest.mark.parametrize(
    "url,expected",
    [
        (
            "http://user:secret@proxy.example.com:8080",
            "http://user:***@proxy.example.com:8080",
        ),
        ("http://proxy.example.com:8080", "http://proxy.example.com:8080"),
        (None, None),
    ],
)
def test_mask_proxy_url(url, expected):
    assert mask_proxy_url(url) == expected
