# Guia Completo de Uso para Desenvolvedores

Este documento resume todos os componentes do projeto **GLPI Dashboard CAU**, explicando como executá-los, testá-los e estender suas funcionalidades.

## Visão Geral

A aplicação coleta dados do GLPI via REST API, normaliza resultados em PostgreSQL/Redis e disponibiliza um painel interativo em Dash. Há também um serviço `worker.py` que expõe endpoints REST e GraphQL.

Principais módulos em `src/glpi_dashboard`:

| Arquivo | Função |
| ------- | ------ |
| `glpi_session.py` | Cliente assíncrono para autenticação e chamadas à API GLPI |
| `backend/utils/pipeline.py` | Normaliza tickets em `pandas.DataFrame` e gera JSON |
| `dashboard/layout.py` | Layout e callbacks do dashboard em Dash |
| `services/worker_api.py` | Lógica de cache e métricas usadas pelo `worker.py` |
| `config/settings.py` | Carrega variáveis de ambiente (GLPI, DB, Redis) |

Scripts utilitários residem em `scripts/` (ex.: `setup/init_db.py`, `fetch/fetch_tickets.py`, `validate_credentials_script.py`).

## Configuração

1. **Instalar dependências**:

   ```bash
   pip install -r requirements.txt -r requirements-dev.txt
   pip install -e .  # importa pacotes da pasta src
   pre-commit install
   ```

2. **Criar `.env`**:

   ```bash
   python scripts/setup_env.py
   ```

   Ajuste tokens GLPI, credenciais de banco e host do Redis.
   Carregue essas variáveis em seus scripts com `python-dotenv`:

   ```python
   from dotenv import load_dotenv
   load_dotenv()
   ```

3. **Inicializar banco**:

   ```bash
   make init-db
   ```

## Executando o Dashboard

Inicie o servidor Dash com:

```bash
python main.py
```

A interface ficará disponível em <http://127.0.0.1:8050>. Use o endpoint `/ping` para verificação de saúde.

## Executando o Worker API

O serviço FastAPI roda com:

```bash
python worker.py
```

Endpoints relevantes:

- `/tickets` – lista completa de chamados
- `/metrics` – contagem de abertos/fechados
- `/graphql/` – versão GraphQL
- `/cache/stats` – estatísticas de cache

## Utilizando o ETL

Para gerar um dump de tickets em JSON ou Parquet:

```bash
python scripts/fetch/fetch_tickets.py --output data/tickets.json
python -m cli.tickets_groups --since 2025-06-01 --until 2025-06-30 --outfile grupos.parquet
```

Consulte `backend/utils/pipeline.py` para transformar os dados em DataFrame.

## Atualizando a Knowledge Base

O worker lê o arquivo definido em `KNOWLEDGE_BASE_FILE` para servir erros
conhecidos. Por padrão o caminho é `docs/knowledge_base_errors.md`.

1. Edite esse arquivo adicionando novas entradas em Markdown.
2. Se mover o arquivo, ajuste `KNOWLEDGE_BASE_FILE` no `.env` ou
   `.env.example`.
3. Reinicie o `worker.py` para que o conteúdo seja recarregado.

É possível consultar o material via endpoint `GET /knowledge-base`.

## Testes e Lint

Execute toda a suíte de testes com cobertura:

```bash
make test
```

Before running the tests, **install the dependencies from both** `requirements.txt` **and** `requirements-dev.txt`, then install the project in editable mode so imports resolve correctly:

```bash
pip install -r requirements.txt -r requirements-dev.txt
pip install -e .
pip install aiohttp  # required for glpi_session tests
```

The `make test` target automatically installs these requirement files before running pytest.

Rodar apenas lint:

```bash
black --check .
flake8 .
```

## Docker

A execução completa pode ser feita via Compose:

```bash
docker compose up
```

Certifique-se de que o plugin Docker Compose esteja instalado; caso
`docker compose` não esteja disponível, instale o pacote `docker-compose-plugin`
ou atualize seu Docker Engine.

Isso sobe PostgreSQL, Redis, o `worker` e o dashboard em portas 8000 e 5173.

## Estrutura de Pastas

```plaintext
├── src/                 # código principal do pacote
│   └── glpi_dashboard/
├── tests/               # suíte pytest
├── scripts/             # utilidades de linha de comando
├── data/                # local para dumps e arquivos temporários
└── docs/                # documentação adicional
```

Para detalhes de arquitetura e troubleshooting, consulte também:

- `docs/run_local.md`
- `docs/error_map.md`
- `docs/revisao_arquitetural_glpi_dashboard.md`
- `docs/windows_dev_setup.md`
