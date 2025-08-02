import asyncio
import logging
import sys

import httpx

from examples.resilient_client import ResilientClient

# Configura o logging para exibir mensagens informativas
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)

API_URL = "https://api.github.com/repos/openai/gpt-3"


async def main():
    """
    Demonstra o uso do ResilientClient para fazer uma requisição a uma API pública,
    com tratamento de erros e logging adequados.
    """
    logger.info("Inicializando ResilientClient...")
    try:
        async with ResilientClient() as client:
            logger.info("Requisitando dados de %s", API_URL)
            resp = await client.get(API_URL)

            resp.raise_for_status()

            logger.info("Requisição bem-sucedida com status: %d", resp.status_code)
            data = resp.json()
            if full_name := data.get("full_name"):
                logger.info("Nome completo do repositório: %s", full_name)
            else:
                logger.warning("O campo 'full_name' não foi encontrado na resposta.")
    except httpx.HTTPStatusError as e:
        logger.error(
            "Ocorreu um erro HTTP: %s - %s", e.response.status_code, e.response.text
        )
    except httpx.RequestError as e:
        logger.error(
            "Ocorreu um erro durante a requisição para %s: %s", e.request.url, e
        )
    except Exception as e:
        logger.exception("Ocorreu um erro inesperado: %s", e)


if __name__ == "__main__":
    asyncio.run(main())
