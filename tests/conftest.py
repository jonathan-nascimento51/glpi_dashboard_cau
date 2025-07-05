import pytest
from tests.test_glpi_session import (
    base_url,
    app_token,
    username,
    password,
    mock_client_session,
    mock_response,
)


@pytest.fixture(name="_base_url")
def fixture_base_url(base_url: str) -> str:
    return base_url


@pytest.fixture(name="_app_token")
def fixture_app_token(app_token: str) -> str:
    return app_token


@pytest.fixture(name="_username")
def fixture_username(username: str) -> str:
    return username


@pytest.fixture(name="_password")
def fixture_password(password: str) -> str:
    return password


@pytest.fixture(name="_mock_client_session")
def fixture_mock_client_session(mock_client_session):
    return mock_client_session


@pytest.fixture(name="_mock_response")
def fixture_mock_response(mock_response):
    return mock_response
