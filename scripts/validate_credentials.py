"""Check GLPI credentials before running the stack."""

from __future__ import annotations

import argparse
import asyncio
import os
import sys

import aiohttp
from aiohttp import BasicAuth, ClientResponse
from dotenv import load_dotenv

from backend.core.settings import (
    CLIENT_TIMEOUT_SECONDS,
    GLPI_APP_TOKEN,
    GLPI_BASE_URL,
    GLPI_PASSWORD,
    GLPI_USER_TOKEN,
    GLPI_USERNAME,
    USE_MOCK_DATA,
    VERIFY_SSL,
)
from backend.infrastructure.glpi.glpi_session import mask_proxy_url

# Windows event loop fix for aiodns
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())  # type: ignore


def get_auth_header() -> dict[str, str]:
    """Build the correct Authorization header."""
    if GLPI_USER_TOKEN:
        return {"Authorization": f"user_token {GLPI_USER_TOKEN}"}
    if GLPI_USERNAME and GLPI_PASSWORD:
        basic_auth = BasicAuth(GLPI_USERNAME, GLPI_PASSWORD)
        return {"Authorization": basic_auth.encode()}
    raise ValueError(
        "Nenhuma credencial (user_token ou username/password) foi fornecida."
    )


def _print_proxy_info(http_proxy: str | None, https_proxy: str | None) -> None:
    if http_proxy or https_proxy:
        print("INFO: Proxy detectado nas variáveis de ambiente:")
        if http_proxy:
            print(f"   - HTTP_PROXY: {mask_proxy_url(http_proxy)}")
        if https_proxy:
            print(f"   - HTTPS_PROXY: {mask_proxy_url(https_proxy)}")
        print(
            "   Se a conexão falhar, verifique se o proxy está correto ou desative-o.\n"
        )


async def _handle_response(response: ClientResponse) -> None:
    if response.status != 200:
        body: str = await response.text()
        print(f"❌ Falha na autenticação (HTTP {response.status}):")
        print(body)
        return

    try:
        data: dict[str, str] = await response.json()
    except Exception as parse_exc:
        print(f"❌ Erro ao processar resposta JSON: {parse_exc}")
        print(f"   Resposta bruta: {await response.text()}")
        return

    session_token = data.get("session_token")
    if not session_token:
        print("❌ Falha ao autenticar: Resposta válida, mas sem session_token.")
        return
    print("✅ Conexão com GLPI bem-sucedida! " f"(Token: ...{session_token[-4:]})")


def _handle_exception(exc: Exception) -> None:
    if isinstance(exc, aiohttp.InvalidURL):
        print(f"❌ Erro de Configuração: A URL do GLPI é inválida: {exc}")
        print(
            "   Por favor, verifique se a variável GLPI_BASE_URL está definida "
            "corretamente no seu arquivo .env."
        )
    elif isinstance(exc, aiohttp.ClientConnectorError):
        print(
            f"❌ Falha de Conexão de Rede: Não foi possível conectar a {GLPI_BASE_URL}."
        )
        print(f"   Detalhe: {exc}")
        print("\n   👉 Verifique se a VPN ou se há um firewall bloqueando o acesso.")
    elif isinstance(exc, asyncio.TimeoutError):
        print(
            f"❌ Falha de Conexão: A requisição para {GLPI_BASE_URL} expirou (timeout)."
        )
    else:
        print(f"❌ Ocorreu um erro inesperado: {exc}")


async def _check(disallowed_proxies: list[str]) -> None:
    """Perform a direct API call to check credentials and connectivity."""
    if USE_MOCK_DATA:
        print("⚠️  Modo offline ativado (USE_MOCK_DATA=True). Health check ignorado.")
        return

    http_proxy = os.getenv("HTTP_PROXY") or os.getenv("http_proxy")
    https_proxy = os.getenv("HTTPS_PROXY") or os.getenv("https_proxy")

    _print_proxy_info(http_proxy, https_proxy)

    headers = {
        "App-Token": GLPI_APP_TOKEN.strip(),
        "Content-Type": "application/json",
        **get_auth_header(),
    }

    url = f"{GLPI_BASE_URL.rstrip('/')}/initSession"
    timeout = aiohttp.ClientTimeout(total=CLIENT_TIMEOUT_SECONDS)

    proxy = https_proxy or http_proxy
    if proxy and any(domain in proxy for domain in disallowed_proxies):
        proxy = None

    try:
        async with aiohttp.ClientSession(timeout=timeout, trust_env=True) as session:
            async with session.get(
                url, headers=headers, ssl=VERIFY_SSL, proxy=proxy
            ) as response:
                await _handle_response(response)
    except Exception as exc:
        _handle_exception(exc)


def main() -> None:
    """Validate credentials and print result."""
    parser = argparse.ArgumentParser(description="Check GLPI credentials")
    parser.add_argument(
        "--disallowed-proxies",
        default=os.getenv("DISALLOWED_PROXIES", "proxymwg.ppiratini.intra.rs.gov.br"),
        help="Comma-separated list of proxy domains that should be ignored",
    )
    args = parser.parse_args()

    load_dotenv()
    disallowed = [d.strip() for d in args.disallowed_proxies.split(",") if d.strip()]
    # No try/except block needed here as _check handles its own errors.
    asyncio.run(_check(disallowed))


if __name__ == "__main__":  # pragma: no cover - manual run
    main()
