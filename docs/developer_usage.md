# Guia Completo de Uso para Desenvolvedores

Este documento resume todos os componentes do projeto **GLPI Dashboard CAU**, explicando como executá-los, testá-los e estender suas funcionalidades.

## Visão Geral

A aplicação coleta dados do GLPI via REST API, normaliza resultados em PostgreSQL/Redis e disponibiliza um painel interativo em Dash. Há também um serviço `worker.py` que expõe endpoints REST e GraphQL.

Principais módulos em `src/glpi_dashboard`:

| Arquivo | Função |
| ------- | ------ |
| `glpi_session.py` | Cliente assíncrono para autenticação e chamadas à API GLPI |
| `data_pipeline.py` | Normaliza tickets em `pandas.DataFrame` e gera JSON |
| `dash_layout.py` | Layout e callbacks do dashboard em Dash |
| `services/worker_api.py` | Lógica de cache e métricas usadas pelo `worker.py` |
| `config/settings.py` | Carrega variáveis de ambiente (GLPI, DB, Redis) |

Scripts utilitários residem em `scripts/` (ex.: `init_db.py`, `fetch_tickets.py`, `validate_credentials_test.py`).

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
python scripts/fetch_tickets.py --output tickets.json
python -m cli.tickets_groups --since 2025-06-01 --until 2025-06-30 --outfile grupos.parquet
```

Consulte `data_pipeline.py` para transformar os dados em DataFrame.

## Testes e Lint

Execute toda a suíte de testes com cobertura:

```bash
make test
```

Rodar apenas lint:

```bash
black --check .
flake8 .
```

## Docker

A execução completa pode ser feita via Compose:

```bash
docker-compose up
```

Isso sobe PostgreSQL, Redis, `initdb`, o `worker` e o dashboard em portas 8000 e 8080.

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
