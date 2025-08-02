import logging
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from examples import demo_resilient_client

# Marca todos os testes neste módulo como assíncronos
pytestmark = pytest.mark.asyncio


async def test_main_success(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
):
    """
    Testa a função main em um cenário de sucesso.
    """
    # Arrange
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {"full_name": "openai/gpt-3"}
    # raise_for_status() não deve fazer nada em caso de sucesso
    mock_response.raise_for_status.return_value = None

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response

    # Mock do context manager do ResilientClient para retornar nosso client mockado
    mock_resilient_client_cm = MagicMock()
    mock_resilient_client_cm.__aenter__.return_value = mock_client
    mock_resilient_client_cm.__aexit__.return_value = None

    monkeypatch.setattr(
        demo_resilient_client, "ResilientClient", lambda: mock_resilient_client_cm
    )
    caplog.set_level(logging.INFO)

    # Act
    await demo_resilient_client.main()

    # Assert
    mock_client.get.assert_called_once_with(demo_resilient_client.API_URL)
    assert "Inicializando ResilientClient..." in caplog.text
    assert f"Requisitando dados de {demo_resilient_client.API_URL}" in caplog.text
    assert "Requisição bem-sucedida com status: 200" in caplog.text
    assert "Nome completo do repositório: openai/gpt-3" in caplog.text


async def test_main_http_error(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
):
    """
    Testa a função main quando ocorre um HTTPStatusError.
    """
    # Arrange
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 404
    mock_response.text = "Not Found"
    mock_response.request = MagicMock()
    mock_response.request.url = demo_resilient_client.API_URL
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Not Found", request=mock_response.request, response=mock_response
    )

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response

    mock_resilient_client_cm = MagicMock()
    mock_resilient_client_cm.__aenter__.return_value = mock_client
    mock_resilient_client_cm.__aexit__.return_value = None

    monkeypatch.setattr(
        demo_resilient_client, "ResilientClient", lambda: mock_resilient_client_cm
    )
    caplog.set_level(logging.ERROR)

    # Act
    await demo_resilient_client.main()

    # Assert
    assert "Ocorreu um erro HTTP: 404 - Not Found" in caplog.text


async def test_main_request_error(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
):
    """
    Testa a função main quando ocorre um RequestError.
    """
    # Arrange
    request = MagicMock(spec=httpx.Request)
    request.url = demo_resilient_client.API_URL
    error = httpx.RequestError("Network error", request=request)

    mock_client = AsyncMock()
    mock_client.get.side_effect = error

    mock_resilient_client_cm = MagicMock()
    mock_resilient_client_cm.__aenter__.return_value = mock_client
    mock_resilient_client_cm.__aexit__.return_value = None

    monkeypatch.setattr(
        demo_resilient_client, "ResilientClient", lambda: mock_resilient_client_cm
    )
    caplog.set_level(logging.ERROR)

    # Act
    await demo_resilient_client.main()

    # Assert
    assert f"Ocorreu um erro durante a requisição para {request.url}: " in caplog.text
    assert f"{error}" in caplog.text
