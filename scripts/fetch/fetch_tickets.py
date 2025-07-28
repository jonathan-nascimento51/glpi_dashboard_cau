import json
import os
import sys
from typing import Any

import requests
from dotenv import load_dotenv

# # Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

glpi_url = "http://cau.ppiratini.intra.rs.gov.br/glpi"
app_token = os.getenv("GLPI_APP_TOKEN")
user_token = os.getenv("GLPI_USER_TOKEN")
OUTPUT_FILE_PATH = "resources/data/tickets_master.json"

# IDs dos campos que queremos investigar
fields_to_validate = ["8", "95", "83"]

# --- Funções de Suporte (Robustas e com Tratamento de Erros) ---


def get_session_token(glpi_url: str, app_token: str, user_token: str) -> str:
    """Obtém um session_token para as próximas requisições."""
    headers: dict[str, Any] = {
        "Content-Type": "application/json",
        "Authorization": f"user_token {user_token}",
        "App-Token": app_token,
    }
    try:
        r = requests.get(
            f"{glpi_url}/apirest.php/initSession",
            headers=headers,
            timeout=10,
        )
        r.raise_for_status()
        print("Sessão iniciada com sucesso.")
        return r.json()["session_token"]
    except requests.exceptions.RequestException as e:
        print(
            "Erro Crítico: Não foi possível iniciar a sessão com o GLPI. "
            f"Detalhes: {e}",
            file=sys.stderr,
        )
        sys.exit(1)


def get_search_options_map(
    glpi_url: str, session_token: str, app_token: str, item_type: str = "Ticket"
) -> dict[int, str]:
    """
    Busca as opções de busca da API e cria um dicionário mapeando o ID
    (inteiro) para o nome amigável do campo (para nosso diagnóstico).
    """
    headers: dict[str, str] = {"Session-Token": session_token, "App-Token": app_token}
    url = f"{glpi_url}/apirest.php/listSearchOptions/{item_type}"
    try:
        return _extracted_from_get_search_options_map_11(url, headers)
    except (requests.exceptions.RequestException, KeyError) as e:
        print(
            f"Erro Crítico: Não foi possível obter ou processar"
            f" as opções de busca da API. "
            f"Detalhes: {e}",
            file=sys.stderr,
        )
        sys.exit(1)


def _extracted_from_get_search_options_map_11(
    url: str, headers: dict[str, str]
) -> dict[int, str]:
    r = requests.get(url, headers=headers, timeout=10)
    r.raise_for_status()
    options = r.json()

    # CORRIGIDO: mapeia corretamente as chaves do dict
    id_to_name_map: dict[int, str] = {
        int(k): v["name"]
        for k, v in options.items()
        if k.isdigit() and isinstance(v, dict) and "name" in v
    }

    print(
        f"Mapa de campos dinâmicos carregado."
        f" {len(id_to_name_map)} campos encontrados."
    )

    print("\n--- Diagnóstico dos Campos com Valor `null` ---")
    for field_id_str in fields_to_validate:
        field_id_int = int(field_id_str)
        if field_id_int in id_to_name_map:
            print(f"  -> O Campo ID '{field_id_str}' corresponde a:")
            print(f"    -> '{id_to_name_map[field_id_int]}'")
        else:
            print(
                f"  -> Alerta: O Campo ID '{field_id_str}' "
                f"não foi encontrado nas opções de busca da API."
            )
    print("--------------------------------------------\n")

    return id_to_name_map


def fetch_all_tickets(
    glpi_url: str, session_token: str, app_token: str
) -> list[dict[str, object]]:
    """Busca todos os chamados da API, solicitando todos os campos disponíveis."""
    headers: dict[str, str] = {"Session-Token": session_token, "App-Token": app_token}
    params: dict[str, str] = {
        "range": "0-99999",
        "is_deleted": "false",
        "get_all_fields": "true",  # Parâmetro para tentar obter mais campos
    }
    url = f"{glpi_url}/apirest.php/Ticket"
    try:
        return _extracted_from_fetch_all_tickets_13(url, headers, params)
    except requests.exceptions.RequestException as e:
        print(
            f"Erro Crítico: Falha ao buscar a lista de chamados. Detalhes: {e}",
            file=sys.stderr,
        )
        # Check if 'r' (response object) was assigned before trying to access it
        if isinstance(e, requests.exceptions.HTTPError):
            print(f"Resposta do servidor: {e.response.text}", file=sys.stderr)
        sys.exit(1)


def _extracted_from_fetch_all_tickets_13(
    url: str, headers: dict[str, str], params: dict[str, Any]
) -> list[dict[str, Any]]:
    print("Buscando todos os chamados com todos os campos...")
    r = requests.get(url, headers=headers, params=params, timeout=180)
    r.raise_for_status()
    tickets = r.json()
    print(f"Busca concluída. {len(tickets)} chamados recebidos.")
    return tickets


def save_data_to_json(data: Any, file_path: str) -> None:
    """Salva os dados em um arquivo JSON, seguindo a arquitetura do projeto."""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Dados mestre salvos com sucesso em: {file_path}")
    except IOError as e:
        print(
            "Erro Crítico:" f"Não foi possível salvar o arquivo JSON. Detalhes: {e}",
            file=sys.stderr,
        )
        sys.exit(1)


# --- Execução Principal ---
if __name__ == "__main__":
    print("--- Iniciando Script de Coleta e Diagnóstico de Chamados GLPI ---")
    try:
        if not all([glpi_url, app_token, user_token]):
            raise ValueError(
                "Variáveis de ambiente GLPI_BASE_URL, GLPI_APP_TOKEN ou GLPI_USER_TOKEN"
                " não estão definidas."
            )

        # Garantir que as variáveis não são None para o type checker
        assert glpi_url is not None
        assert app_token is not None
        assert user_token is not None

        session_token = get_session_token(glpi_url, app_token, user_token)
        search_map = get_search_options_map(glpi_url, session_token, app_token)
        if all_tickets := fetch_all_tickets(glpi_url, session_token, app_token):
            save_data_to_json(all_tickets, OUTPUT_FILE_PATH)
        else:
            print("Nenhum chamado foi retornado pela API.")
        print("--- Script concluído com sucesso! ---")
    except ValueError as e:
        print(f"Erro de configuração: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}", file=sys.stderr)
        sys.exit(1)

# import asyncio
# import json
# import logging
# import os  # Importamos o módulo 'os' para ler as variáveis de ambiente
# import sys
# from pathlib import Path
# from typing import Any

# from dotenv import load_dotenv

# # Importa o cliente da API do seu projeto
# from backend.infrastructure.glpi.glpi_session import Credentials, GLPISession
# from shared.utils.logging import init_logging

# # Carrega as variáveis de ambiente do arquivo .env
# load_dotenv()

# # Configuração básica de logging
# init_logging(logging.INFO)
# logger = logging.getLogger(__name__)

# if sys.platform.startswith("win"):
#     # WindowsSelectorEventLoopPolicy is only
#     # available on Windows and in some Python versions.
#     # Import it explicitly and use getattr for type checker compatibility.
#     policy = getattr(asyncio, "WindowsSelectorEventLoopPolicy", None)
#     if policy is not None:
#         asyncio.set_event_loop_policy(policy())


# def fetch_raw_data():
#     """
#     Função de diagnóstico para buscar dados brutos da API do GLPI e
#     salvá-los diretamente em um arquivo, sem processamento.
#     """
#     logger.info("Iniciando o script de diagnóstico CORRIGIDO...")

#     # --- CORREÇÃO APLICADA AQUI ---
#     # Carregamos as credenciais do ambiente para variáveis
#     glpi_url = os.getenv("GLPI_BASE_URL")
#     app_token = os.getenv("GLPI_APP_TOKEN")
#     user_token = os.getenv("GLPI_USER_TOKEN")

#     # Verificamos se as variáveis foram carregadas
#     if not all([glpi_url, app_token, user_token]):
#         logger.error(
#             "ERRO: Uma ou mais variáveis de ambiente "
#             "(GLPI_BASE_URL, GLPI_APP_TOKEN, GLPI_USER_TOKEN) "
#             "não foram encontradas. Por favor, verifique seu arquivo .env."
#         )
#         return

#     # Type assertions for static type checkers
#     assert glpi_url is not None
#     assert app_token is not None
#     assert user_token is not None

#     async def _run() -> None:
#         creds = Credentials(app_token=app_token, user_token=user_token)
#         async with GLPISession(glpi_url, creds) as client:
#             await _save_raw_tickets(client)

#     try:
#         asyncio.run(_run())
#     except Exception as e:
#         logger.error(
#             f"Ocorreu um erro durante a execução do script de diagnóstico: {e}",
#             exc_info=True,
#         )


# async def _save_raw_tickets(client: GLPISession) -> None:
#     logger.info("Cliente da API inicializado corretamente. Buscando chamados...")

#     params: dict[str, Any] = {
#         "is_deleted": 0,
#         "sort": "date_mod",
#         "order": "desc",
#         "range": "0-200",
#     }

#     raw_tickets = await client.get_all("Ticket", **params)
#     logger.info(f"Busca concluída. {len(raw_tickets)} chamados recebidos do GLPI.")

#     output_filename = "resources/data/raw_tickets_sample.json"
#     with open(output_filename, "w", encoding="utf-8") as f:
#         json.dump(raw_tickets, f, indent=2, ensure_ascii=False)

#     logger.info(f"Dados brutos salvos com sucesso em '{output_filename}'")


# async def fetch_and_save(output: str) -> None:
#     """
#     Função assíncrona para buscar dados e salvar em um arquivo.
#     Substitua o conteúdo desta função pela lógica de busca de dados necessária.
#     """
#     glpi_url = os.getenv("GLPI_BASE_URL")
#     app_token = os.getenv("GLPI_APP_TOKEN")
#     user_token = os.getenv("GLPI_USER_TOKEN")

#     if not all([glpi_url, app_token, user_token]):
#         logger.error(
#             "ERRO: Uma ou mais variáveis de ambiente "
#             "(GLPI_BASE_URL, GLPI_APP_TOKEN, "
#             "GLPI_USER_TOKEN) não foram encontradas. "
#             "Por favor, verifique seu arquivo .env."
#         )
#         glpi_url = glpi_url or "http://localhost"
#         app_token = app_token or "dummy"
#         user_token = user_token or "dummy"

#     assert glpi_url is not None
#     assert app_token is not None
#     assert user_token is not None

#     try:
#         creds = Credentials(app_token=app_token, user_token=user_token)
#         async with GLPISession(glpi_url, creds) as client:
#             params: dict[str, Any] = {
#                 "is_deleted": 0,
#                 "sort": "date_mod",
#                 "order": "desc",
#                 "range": "0-200",
#             }
#             raw_tickets = await client.get_all("Ticket", **params)

#             # Guarantee each ticket has "id" and "status"
#             for ticket in raw_tickets:
#                 if "id" not in ticket:
#                     ticket["id"] = 0
#                 elif "status" not in ticket:
#                     ticket["status"] = ""

#             out_path = Path(output)
#             out_path.parent.mkdir(parents=True, exist_ok=True)
#             with out_path.open("w", encoding="utf-8") as f:
#                 json.dump(raw_tickets, f, indent=2, ensure_ascii=False)
#     except Exception as e:
#         logger.error(
#             f"Ocorreu um erro durante a execução do fetch_and_save: {e}",
#             exc_info=True,
#         )


# if __name__ == "__main__":
#     fetch_raw_data()
