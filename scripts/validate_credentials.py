"""Check GLPI credentials before running the stack."""

from __future__ import annotations

import argparse
import asyncio
import base64
import os
import sys

import aiohttp
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

# Windows event loop fix for aiodns
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


def get_auth_header() -> dict[str, str]:
    """Build the correct Authorization header."""
    if GLPI_USER_TOKEN:
        return {"Authorization": f"user_token {GLPI_USER_TOKEN}"}
    if GLPI_USERNAME and GLPI_PASSWORD:
        # Basic Auth
        credentials = f"{GLPI_USERNAME}:{GLPI_PASSWORD}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        return {"Authorization": f"Basic {encoded_credentials}"}
    raise ValueError(
        "Nenhuma credencial (user_token ou username/password) foi fornecida."
    )


async def _check() -> None:
    """Perform a direct API call to check credentials and connectivity."""
    if USE_MOCK_DATA:
        print("⚠️  Modo offline ativado (USE_MOCK_DATA=True). Health check ignorado.")
        return

    http_proxy = os.getenv("HTTP_PROXY") or os.getenv("http_proxy")
    https_proxy = os.getenv("HTTPS_PROXY") or os.getenv("https_proxy")

    if http_proxy or https_proxy:
        print("ℹ️  Proxy detectado nas variáveis de ambiente:")
        if http_proxy:
            print(f"   - HTTP_PROXY: {http_proxy}")
        if https_proxy:
            print(f"   - HTTPS_PROXY: {https_proxy}")
        print(
            "   Se a conexão falhar, verifique se o proxy está correto ou desative-o.\n"
        )

    headers = {
        "App-Token": GLPI_APP_TOKEN.strip(),
        "Content-Type": "application/json",
        **get_auth_header(),
    }

    url = f"{GLPI_BASE_URL.rstrip('/')}/initSession"
    timeout = aiohttp.ClientTimeout(total=CLIENT_TIMEOUT_SECONDS)

    proxy = https_proxy or http_proxy

    try:
        async with aiohttp.ClientSession(timeout=timeout, trust_env=True) as session:
            async with session.get(
                url, headers=headers, ssl=VERIFY_SSL, proxy=proxy
            ) as response:
                if response.status == 200:
                    # Success, we can even get the session token if needed
                    data = await response.json()
                    session_token = data.get("session_token")
                    if not session_token:
                        print(
                            "❌ Falha ao autenticar: Resposta, mas sem session_token."
                        )
                        return  # Early exit on authentication failure
                    print(
                        "✅ Conexão com GLPI bem-sucedida! "
                        f"(Token: ...{session_token[-4:]})"
                    )
                else:
                    # Failure, print status and body for debugging
                    body = await response.text()
                    print(f"❌ Falha na autenticação (HTTP {response.status}):")
                    print(body)

    except aiohttp.ClientConnectorError as exc:
        print(
            f"❌ Falha de Conexão de Rede: Não foi possível conectar a {GLPI_BASE_URL}."
        )
        print(f"   Detalhe: {exc}")
        print(
            "\n   👉 Verifique se a VPN ou se há um firewall bloqueando o acesso."
        )  # fmt: skip
    except asyncio.TimeoutError:
        print(
            f"❌ Falha de Conexão: A requisição para {GLPI_BASE_URL} expirou (timeout)."
        )
    except Exception as exc:
        print(f"❌ Ocorreu um erro inesperado: {exc}")


def main() -> None:
    """Validate credentials and print result."""
    parser = argparse.ArgumentParser(description="Check GLPI credentials")
    # The debug flag is no longer needed as we print details on failure.
    parser.parse_args()

    load_dotenv()
    # No try/except block needed here as _check handles its own errors.
    asyncio.run(_check())


if __name__ == "__main__":  # pragma: no cover - manual run
    main()
