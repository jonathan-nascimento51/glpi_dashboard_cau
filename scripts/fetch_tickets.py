import json
import logging
import os  # Importamos o módulo 'os' para ler as variáveis de ambiente
from pathlib import Path
from dotenv import load_dotenv

# Importa o cliente da API do seu projeto
from glpi_dashboard.services.glpi_api_client import GlpiApiClient

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Configuração básica de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fetch_raw_data():
    """
    Função de diagnóstico para buscar dados brutos da API do GLPI e
    salvá-los diretamente em um arquivo, sem processamento.
    """
    logger.info("Iniciando o script de diagnóstico CORRIGIDO...")

    # --- CORREÇÃO APLICADA AQUI ---
    # Carregamos as credenciais do ambiente para variáveis
    glpi_url = os.getenv("GLPI_BASE_URL")
    app_token = os.getenv("GLPI_APP_TOKEN")
    user_token = os.getenv("GLPI_USER_TOKEN")

    # Verificamos se as variáveis foram carregadas
    if not all([glpi_url, app_token, user_token]):
        logger.error(
            "ERRO: Uma ou mais variáveis de ambiente "
            "(GLPI_BASE_URL, GLPI_APP_TOKEN, GLPI_USER_TOKEN) "
            "não foram encontradas. Por favor, verifique seu arquivo .env."
        )
        return

    # Type assertions for static type checkers
    assert glpi_url is not None
    assert app_token is not None
    assert user_token is not None

    try:
        with GlpiApiClient(
            base_url=glpi_url, app_token=app_token, user_token=user_token
        ) as client:
            logger.info(
                "Cliente da API inicializado corretamente. Buscando chamados..."
            )

            params = {
                "is_deleted": 0,
                "sort": "date_mod",
                "order": "desc",
                "range": "0-200",
            }

            raw_tickets = client.get_all("Ticket", **params)
            logger.info(
                f"Busca concluída. {len(raw_tickets)} chamados recebidos do GLPI."
            )

            output_filename = "raw_tickets_output.json"
            with open(output_filename, "w", encoding="utf-8") as f:
                json.dump(raw_tickets, f, indent=2, ensure_ascii=False)

            logger.info(f"Dados brutos salvos com sucesso em '{output_filename}'")

    except Exception as e:
        logger.error(
            f"Ocorreu um erro durante a execução do script de diagnóstico: {e}",
            exc_info=True,
        )


async def fetch_and_save(output):
    """
    Função assíncrona para buscar dados e salvar em um arquivo.
    Substitua o conteúdo desta função pela lógica de busca de dados necessária.
    """
    glpi_url = os.getenv("GLPI_BASE_URL")
    app_token = os.getenv("GLPI_APP_TOKEN")
    user_token = os.getenv("GLPI_USER_TOKEN")

    if not all([glpi_url, app_token, user_token]):
        logger.error(
            "ERRO: Uma ou mais variáveis de ambiente "
            "(GLPI_BASE_URL, GLPI_APP_TOKEN, "
            "GLPI_USER_TOKEN) não foram encontradas. "
            "Por favor, verifique seu arquivo .env."
        )
        glpi_url = glpi_url or "http://localhost"
        app_token = app_token or "dummy"
        user_token = user_token or "dummy"

    assert glpi_url is not None
    assert app_token is not None
    assert user_token is not None

    try:
        with GlpiApiClient(
            base_url=glpi_url, app_token=app_token, user_token=user_token
        ) as client:
            params = {
                "is_deleted": 0,
                "sort": "date_mod",
                "order": "desc",
                "range": "0-200",
            }
            raw_tickets = client.get_all("Ticket", **params)

            # Guarantee each ticket has "id" and "status"
            for i, ticket in enumerate(raw_tickets):
                if not isinstance(ticket, dict):
                    raw_tickets[i] = {"id": 0, "status": ""}
                else:
                    if "id" not in ticket:
                        ticket["id"] = 0
                    if "status" not in ticket:
                        ticket["status"] = ""

            out_path = Path(output)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            with out_path.open("w", encoding="utf-8") as f:
                json.dump(raw_tickets, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(
            f"Ocorreu um erro durante a execução do fetch_and_save: {e}",
            exc_info=True,
        )


if __name__ == "__main__":
    fetch_raw_data()
