# GLPI Dashboard CAU

![Coverage](coverage.svg)
[![Security](https://snyk.io/test/github/jonathan-nascimento51/glpi_dashboard_cau/badge.svg)](https://snyk.io/test/github/jonathan-nascimento51/glpi_dashboard_cau)
[![Draft v0.1](https://img.shields.io/badge/DRAFT-v0.1-informational)](docs/vision.md)

This project provides a minimal dashboard to visualize service desk tickets from GLPI using a live connection to the REST API.

## Purpose

The goal is to inspect backlog, ticket status and productivity metrics without a live GLPI connection. Data is fetched via the API and normalized into JSON that the Dash app loads on startup.
Additional sample scripts and demonstration modules reside in [`examples/`](examples/).
Pattern modules such as `song_serializer.py` and `sort_strategy.py` live in [`examples/patterns/`](examples/patterns/) and are provided for educational purposes only.

## Development Setup

Follow these steps to prepare a local environment. A condensed walkthrough is
available in [docs/install_quickstart.md](docs/install_quickstart.md).

**Note:** The React frontend now lives under the canonical path
`src/frontend/react_app` (the former `frontend/` symlink was removed).
Always run npm commands from this directory and update any custom scripts
or volume mounts accordingly.

See [docs/DEV_SETUP.md](docs/DEV_SETUP.md#stabilizing-react-hook-dependencies)
for tips on stabilizing React hook dependencies with `useMemo` and `useCallback`.

Run `scripts/setup/setup_env.sh` (or `make setup`) to create the `.venv` directory,
install packages from `requirements.txt` and the development set defined in
`pyproject.toml` (compiled into `requirements-dev.txt`) and enable `pre-commit`
hooks automatically. Optional extras can be added later with
`./scripts/install_dev_extras.sh`. These packages include browsers and
instrumentation required for the full test suite. If you prefer to install
packages manually, remember to run `pre-commit install` afterward.

**Note:** `setup_env.sh` only supports Linux. The script checks your OS at start
and exits with status 1 when run on macOS or Windows, directing you to the
manual steps in [docs/run_local.md](docs/run_local.md).

```bash
bash scripts/setup/setup_env.sh
```
Run `mise trust` once after cloning to silence warnings about the `.mise.toml`
configuration.

If a `wheels/` directory is available run the script with `OFFLINE_INSTALL=true`
to avoid contacting PyPI:

```bash
bash scripts/setup/setup_env.sh OFFLINE_INSTALL=true
```

Use `python scripts/download_wheels.py` on a machine with internet access to
prefetch these wheels.

The script installs `pre-commit` and all Python dependencies in one go. You may
still run the manual commands below if you need finer control:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt -r requirements-dev.txt  # generated via pip-compile
# includes dev tools like pytest-cov used by the CI coverage step
pip install -e .
pre-commit install
cd src/frontend/react_app && npm ci
# installs Node dev dependencies such as dotenv for the React tests
# remove any stale compiled JS that might shadow the TypeScript sources
find src/frontend/react_app/src -name '*.js' -delete
```

See [docs/testing.md](docs/testing.md) for tips on running individual tests and
for common import errors.

The `pip install` steps above must be run before executing any tests so that
the local package and its development dependencies are available.

Run `make diagnose` to verify the Codex environment. The helper script
`scripts/diagnostics/diagnose_codex.py` prints useful metadata for troubleshooting.

Runtime packages come from `requirements.txt`; development and testing tools are defined in `pyproject.toml` and compiled into `requirements-dev.txt`.

Create a `.env` file from the template and fill in your GLPI and database
credentials. PostgreSQL is used by default but you can point the application to
MySQL by setting values like:

```bash
DB_HOST=localhost
DB_PORT=3306
DB_NAME=glpi_dashboard
DB_USER=dashboard
DB_PASSWORD=senhaSegura
```

Generate the template with:

```bash
python scripts/setup/setup_env.py  # copies .env.example
```

Initialize the database:

```bash
PYTHONPATH=src python scripts/setup/init_db.py --drop-all
```

Start the backend API (required by the dashboard):

```bash
python worker.py
```

Run the dashboard:

```bash
python dashboard_app.py
```

Open <http://127.0.0.1:8050> in your browser (or set `DASH_PORT` to change the port).

The Dash callbacks expose connection status via a notification container:

```python
from dashboard_app import load_data
from frontend.callbacks.callbacks import register_callbacks

register_callbacks(app, load_data)
```

To launch the entire stack with Docker use:

```bash
docker compose up
```

This starts PostgreSQL, Redis, the FastAPI worker and the Dash app. Access the dashboard at `http://localhost:5174` when the build finishes.

## Dependencies

- Python 3.10\u20133.12
- PostgreSQL and Redis instances running locally (or update the `.env` file)
- Node.js >=20.19.0 is required to run the React frontend locally. The required
  version is stored in the `.nvmrc` file at the repository root. This version is
  picked up automatically by [mise](https://github.com/jdx/mise) thanks to the
This version is picked up automatically by [mise](https://github.com/jdx/mise) thanks to the
  `.mise.toml` configuration. If you use `mise`, run `mise trust` once after cloning to trust the project's configuration.

Alternatively, if you prefer to use [nvm](https://github.com/nvm-sh/nvm), you can install the version with:

  ```bash
  nvm install
  nvm use 20.19.0
  ```

  Docker remains an optional alternative for running the entire stack if the
  required Node version cannot be installed.
- The React dashboard fetches data with [`@tanstack/react-query`](https://tanstack.com/query) for
  caching and background updates.

Set the connection details in `.env` using the keys `DB_*` and `REDIS_*`.

## Configuration

Store credentials in a local `.env` file or load them from a vault service.
Sensitive variables like `GLPI_*` should **never** be committed to the
repository. The project expects these values in your environment before running
any scripts.

For production you can mount database credentials as Docker secrets and expose
them via `DB_USER_FILE` and `DB_PASSWORD_FILE`:

```bash
echo "appuser" | docker secret create db_user -
echo "s3cr3t" | docker secret create db_password -
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## Architecture

```plaintext
         +---------+      +-------------+
         |  GLPI   +----->+  Worker API |
         +---------+      +-------------+
                |                |
                v                v
         +-----------+     +-----------+
         | PostgreSQL |     |  Redis    |
         +-----------+     +-----------+
```

The dashboard reads data produced by the worker and stored in PostgreSQL. More details on the multi-agent workflow can be found in
[AGENTS.md](AGENTS.md). Structural file moves are logged in [docs/REFACTOR_LOG.md](docs/REFACTOR_LOG.md). A walkthrough of the `langgraph_workflow.py` module is
available in [docs/langgraph_workflow.md](docs/langgraph_workflow.md).
Instructions for running the React front-end—including npm scripts and required environment variables—are available in
[docs/frontend_architecture.md](docs/frontend_architecture.md). That document also covers how the front-end communicates with the worker API via `NEXT_PUBLIC_API_BASE_URL` and how to run the Jest and Playwright test suites.
Create the environment file with `cp src/frontend/react_app/.env.example src/frontend/react_app/.env` before running the dashboard. Docker Compose automatically loads `.env` when present. Execute all npm commands from inside the `src/frontend/react_app` directory, e.g. `cd src/frontend/react_app && npm run dev`, or launch Docker.

When running via Docker, the front-end container reaches the backend using the
service name `backend`. The `.env` file already sets
`NEXT_PUBLIC_API_BASE_URL=http://backend:8000` so requests between containers
resolve correctly. Browsers on the host can still hit the API on
`http://localhost:8000` thanks to the published port. If you see
`net::ERR_NAME_NOT_RESOLVED` errors in the browser console, edit
`src/frontend/react_app/.env` and set `NEXT_PUBLIC_API_BASE_URL` to
`http://localhost:8000` or add `backend` to your `/etc/hosts` file.

### Multi-agent pipeline (A1–A9)

The project automates code generation via a nine-stage prompt flow. The sequence
is executed as `A1 ▶ A2 ▶ A3 ▶ A4‑6 ▶ A7 ▶ A8 ▶ A9` where:

- **A1 – Meta-Prompt Builder** defines the subtasks and expected artifacts.
- **A2 – Intérprete de Requisitos** extracts the technical requirements.
- **A3 – Decompositor Estratégico** splits the prompt into logical sections.
- **A4 – Gerador de Bloco: Identidade & Objetivo** sets the persona and goal.
- **A5 – Gerador de Bloco: Instruções & Regras** writes the detailed rules.
- **A6 – Gerador de Bloco: Contexto & Variáveis** supplies API data and defaults.
- **A7 – Gerador de Bloco: Exemplo & Saída Esperada** creates a few-shot sample.
- **A8 – Compositor de Prompt Final** joins all blocks into one prompt.
- **A9 – Validador & Justificativa** reviews the final result for coherence.

See [docs/AGENTS.md](docs/AGENTS.md) for the full prompt templates.
Structural changes made during these steps are summarized in [docs/REFACTOR_LOG.md](docs/REFACTOR_LOG.md). The five-block format (Identity, Instructions, Context, Examples, Question) is outlined in [docs/PROMPT_BUILDER.md](docs/PROMPT_BUILDER.md).

### Node.js ESM conventions

`package.json` declares `"type": "module"`, so all `.js` files use ES Module syntax by default. Configuration files that still rely on `module.exports` have been renamed with the `.cjs` extension. When adding new scripts or configs prefer ESM (`import`/`export`) and only use `.cjs` for legacy CommonJS code.
If a script still depends on `require()`, rename it with the `.cjs` extension or rewrite it using `import`. When migrating, use `fileURLToPath(import.meta.url)` to recreate `__dirname`.

## Main modules

- **`src/backend/infrastructure/glpi/glpi_session.py`** – asynchronous client for the GLPI REST API used by the worker and ETL modules. This file replaces the former `glpi_api.py` referenced in early docs.
- **`src/backend/utils/pipeline.py`** – normalizes raw ticket data into a `pandas.DataFrame` and exports JSON.
- **`src/frontend/layout/layout.py`** – defines tables and charts for the Dash UI.
- **`glpi_tools/__main__.py`** – exposes the CLI commands such as `list-fields`.
- **`src/backend/adapters/mapping_service.py`** – obtém e cacheia IDs de campos
  do GLPI. O `GlpiApiClient` usa esse mapa para preencher `forcedisplay`
  dinamicamente.
- **`dashboard_app.py`** – starts the Dash server.
- **`worker.py`** – primary backend entry point used by Docker and CI to launch the FastAPI service.
- **`scripts/`** – helper utilities grouped under `setup/`, `fetch/`, `etl/`, `diagnostics/` and `refactor/` (e.g. `setup/init_db.py`, `fetch/fetch_tickets.py`, `diagnostics/diagnose_codex.py`).

### Quick usage examples

Run the worker API and dashboard locally:

```bash
python worker.py &
python dashboard_app.py &
```

Launch the React frontend in another terminal:

```bash
cd src/frontend/react_app && npm run dev
```

Inspect available CLI commands:

```bash
python -m glpi_tools --help
```

Query a list of fields for a GLPI item:

```bash
python -m glpi_tools list-fields Ticket
```

Count ticket statuses for multiple levels:

```bash
python -m glpi_tools count-by-level N1 N2
```

### Generating components and modules

Use [Plop](https://plopjs.com) to scaffold new React components or Dash modules.
Run the following command from the project root and follow the prompts:

```bash
npm run generate
```

Files are created under `src/frontend/react_app/src/components/` for React and
under `src/frontend/modules/` for Dash.

### Running tests

**Important:** Install packages from **both** `requirements.txt` and
`requirements-dev.txt` before running `pytest` or invoking `make test`.
The `requirements-dev.txt` file contains extras such as `dash[testing]`,
`playwright`, `fakeredis`, `testcontainers` and `pact-python` which are needed
for the full suite. Install them with:

```bash
pip install -r requirements-dev.txt --break-system-packages
```

**Note:** The `--break-system-packages` flag is used here to bypass Python's external package management protection. This is necessary in some environments where system-level packages need to be updated directly. However, this approach can interfere with system packages and is not recommended for general use. To avoid potential issues, consider using a virtual environment as described below.

Alternatively use `pip install -e '.[dev]'` to install all development extras.

### Using a Virtual Environment

To safely manage dependencies, set up a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt

## Installing Dependencies Behind a Proxy or Offline

If your machine needs a proxy to reach PyPI, export the proxy variables before
invoking `pip`. The `scripts/setup/setup_env.sh` script automatically configures `apt` when
`HTTP_PROXY` is defined and can work offline by setting `OFFLINE_INSTALL=true`:

```bash
export HTTP_PROXY=http://proxy.company.com:8080␊
export HTTPS_PROXY=$HTTP_PROXY
```

Run the installation commands from the [Development Setup](#development-setup) section to install the dependencies through the proxy.

On a machine with internet access you can pre-download the wheels needed by the
project:

```bash
./scripts/download_wheels.sh [target-dir]
```

The script stores wheels under `./wheels` by default. Copy this directory to the
offline machine and install everything without contacting PyPI:

```bash
pip install --no-index --find-links=/path/to/wheels -r requirements.txt -r requirements-dev.txt  # generated via pip-compile

Then run the setup script with `OFFLINE_INSTALL=true bash scripts/setup/setup_env.sh` to skip online downloads.

More setup tips—including offline usage with mock data—are documented in
[docs/glpi_tokens_guide.md](docs/glpi_tokens_guide.md).  See also
[docs/dev_performance_guide.md](docs/dev_performance_guide.md) for
strategies to pre-build Docker images and cache Python wheels.

## Instalação em rede restrita

Caso o ambiente tenha acesso limitado à internet ou exija proxy corporativo,
defina as variáveis `HTTP_PROXY` e `HTTPS_PROXY` antes de executar o `pip`:

```bash
export HTTP_PROXY=http://proxy.empresa.com:8080
export HTTPS_PROXY=$HTTP_PROXY
```

Em uma máquina com conexão liberada faça o download dos pacotes necessários:

```bash
pip download -r requirements.txt -d wheels/
```

Transfira o diretório `wheels/` para o destino e instale sem consultar o PyPI:

```bash
pip install --no-index --find-links=wheels/ -r requirements.txt
```

O front-end já executa `npm ci --prefer-offline`, reutilizando o cache de
dependências sempre que possível.

## GitHub access

Repositórios privados ou actions personalizadas exigem autenticação. Defina
`GITHUB_TOKEN` no arquivo `.env` (ou exporte a variável) e execute o script de
configuração do GitHub CLI:

```bash
export GITHUB_TOKEN=<token com permissao repo>
bash scripts/setup/setup_github_access.sh
```

O utilitário instala o `gh` caso esteja ausente e armazena as credenciais para o
usuário atual.

## Docker offline

Se o host não puder acessar o **Docker Hub**, é possível salvar previamente as
imagens usadas pelo `docker-compose.yml`:

```bash
./scripts/save_docker_images.sh --file docker-compose.yml --output images.tar
```

Copie `images.tar` para a máquina de destino e carregue com `docker load -i`.
Assim a stack sobe mesmo sem internet ou com registro interno.

## Running the Dash app

Start the dashboard pointing to your GLPI instance:

```bash
python dashboard_app.py
```

The entry point initializes structured logging via:

```python
from backend.utils.logging import init_logging
init_logging()
```

Set `APP_ENV=production` to force JSON logs and disable traceback diagnostics.
Use any other value for colorful developer output.

The Dash server uses gzip compression via `flask-compress` and loads data lazily on first render.

Use the `/ping` endpoint for health checks; it returns `OK` when the server is running.

Profile startup time with:

```bash
python scripts/profile_dash.py
```

The app will be available at <http://127.0.0.1:8050> by default; set `DASH_PORT` if you need a different port.

For an OS-specific walkthrough including virtual environment commands, see
[docs/run_local.md](docs/run_local.md).

### Browser latency benchmark

The dashboard previously filtered tickets on the server, leading to ~500 ms
round-trips per change. After migrating the filter to a
`dash_clientside_callback` and rendering the scatter plot with
`go.Scattergl`, the same interaction completes in roughly 50 ms as measured
in Chrome DevTools (Network → Timings).

If you encounter issues during the first run, consult
[docs/error_map.md](docs/error_map.md) for troubleshooting tips.
For additional troubleshooting steps in Portuguese, see␊
[docs/solucoes_problemas.md](docs/solucoes_problemas.md). Esse arquivo também
traz orientações para resolver avisos e pacotes depreciados do npm.
Orientações específicas para erros `400 Bad Request` ao iniciar a sessão GLPI via Docker
estão disponíveis em
[docs/troubleshooting_400_bad_request.md](docs/troubleshooting_400_bad_request.md).
Detalhes completos do endpoint `initSession` encontram-se em
[docs/init_session_api.md](docs/init_session_api.md).
Siga o passo a passo em [docs/fix_no_tickets.md](docs/fix_no_tickets.md) caso o
dashboard exiba "Nenhum chamado encontrado" mesmo com dados disponíveis.

## Running the Worker API

`worker.py` provides a lightweight FastAPI service that exposes ticket data for other applications. It always retrieves information from the GLPI API.

Run the service:

```bash
python worker.py
```

Call `init_logging()` early in the main function to capture logs:

```python
from fastapi import FastAPI
from backend.utils.logging import init_logging
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

init_logging()
app = FastAPI(...)
FastAPIInstrumentor().instrument_app(app)
```

The API uses **ORJSONResponse** for fast serialization. Heavy aggregations are
pre-computed by an ARQ worker. Start it separately with:

```bash
PYTHONPATH=src python src/backend/application/metrics_worker.py
```

Alternatively you can use the module form:

```bash
python -m backend.application.metrics_worker
```

When the FastAPI service starts it primes the Redis cache by calling
`load_tickets()`. This fills the `chamados_por_data`,
`metrics_aggregated`, `metrics_levels` and `metrics:overview` keys so
endpoints are responsive immediately.

- The service exposes several endpoints:

 - `/tickets` – full list of tickets in JSON format. The payload includes the
   ticket `priority` label and the `requester` name when available.
- `/tickets/stream` – Server‑Sent Events (SSE) stream of progress followed by the JSON payload.
- `/metrics` – summary with `total`, `opened` and `closed` counts.
- `/metrics/aggregated` – counts grouped by status and technician, pre-computed by the worker.
- `/metrics/aggregated` – dictionary with `open_tickets`,
  `tickets_closed_this_month` and `status_distribution`.
- `/metrics/levels/<level>` – same fields as `/metrics/aggregated` but scoped
  to a single support level.
- `/metrics/levels` – mapping of levels to status counts stored in the
  `metrics_levels` cache.
- `/chamados/por-data` – tickets per creation date, refreshed every 10 minutes.
- `/chamados/por-dia` – totals for calendar heatmaps, refreshed every 10 minutes.
- `/graphql/` – GraphQL API providing the same information.
- `/cache/stats` – returns cache hit/miss metrics.
- `/health` – quick check that the worker can reach the GLPI API.

Example `/metrics/aggregated` payload:

```json
{
  "open_tickets": {"N1": 5},
  "tickets_closed_this_month": {"N1": 2},
  "status_distribution": {"new": 3, "closed": 2}
}
```

The `/metrics/levels/N1` endpoint yields the same fields scoped to the
requested level. `/metrics/levels` returns a dictionary of levels mapped
to status counts.

Example ticket payload:

```json
[
  {
    "id": 42,
    "title": "Network issue",
    "status": "New",
    "priority": "High",
    "requester": "Maria"
  }
]
```

### Offline fallback

If the GLPI API is unavailable the worker automatically serves data from
`tests/resources/mock_tickets.json`. Set `USE_MOCK_DATA=true` in the environment to force
this behaviour. Responses include the header `X-Warning: using mock data` when
the fallback is active.

Make sure the service is running with `python worker.py` and that your
front-end points to it via `NEXT_PUBLIC_API_BASE_URL` in
`src/frontend/react_app/.env`.

Docker Compose now mounts `src/frontend/react_app/.env.example` directly in the
frontend service. Copy this file to `.env` only when running the React app
outside the containers. Run npm scripts from inside the
`src/frontend/react_app` directory (`cd src/frontend/react_app && npm run dev`)
or launch Docker.

Vite loads environment variables that start with `NEXT_PUBLIC_` thanks to
`envPrefix` in `src/frontend/react_app/vite.config.ts`. Imports that begin with
`@/` resolve to the `src` directory so paths stay short.

### Generating TypeScript interfaces

Run the following command to sync the frontend types with the backend models:

```bash
make gen-types
```

This converts the Pydantic models in `backend.domain.ts_models` into TypeScript definitions under `src/frontend/react_app/src/types/api.ts`.

Example GraphQL query to retrieve ticket data:

```graphql
query GetTickets {
  tickets {
    id
    name
    status
    user {
      name
    }
  }
}
```

### Generating architecture docs

Rebuild `ARCHITECTURE.md` from the ADR source with:

```bash
python scripts/generate_arch_docs.py
```

The file is version controlled and CI will fail if it is out of sync.

## Collecting ticket/group assignments

Use the helper CLI to dump assignments into a Parquet dataset:

```bash
python -m cli.tickets_groups --since 2025-06-01 --until 2025-06-30 \
    --outfile datasets/tickets_groups.parquet
```

Adjust the dates and destination file as needed. The command prints the resulting path after completion.

## LangGraph workflow demo

To experiment with the supervisor pattern in isolation compile the graph and invoke it manually:

```bash
PYTHONPATH=src python - <<'PY'
import asyncio
from backend.application.langgraph_workflow import build_workflow

async def main():
    wf = build_workflow().compile()
    state = {"messages": ["fetch"], "next_agent": "", "iteration_count": 0}
    result = await wf.ainvoke(state)
    print(result["messages"][-1])

asyncio.run(main())
PY
```

## Environment variables

Some scripts require a few variables set in a `.env` file. Copy the template and fill in your credentials:

```bash
python scripts/setup/setup_env.py  # copies .env.example to .env
```

Open `.env` and set the required values.
*Important:* all variable names must be **uppercase**, otherwise the Pydantic loader will ignore them.

Example snippet:

```bash
# Database credentials
DB_NAME=glpi_dashboard
DB_USER=user  # non-privileged application user
DB_PASSWORD=password

# Mapped automatically to the Postgres container
POSTGRES_DB=$DB_NAME
POSTGRES_USER=postgres  # superuser inside the container
POSTGRES_PASSWORD=postgres
```

When you run `docker compose up` the initialization script
`docker/db-init/01-init-db.sh` automatically creates the application user and
database if they do not exist. The script reads `DB_USER`, `DB_PASSWORD` and
`DB_NAME` (or their `_FILE` variants) from the environment. Customize these
variables in your `.env` file before launching the stack. Static statements
such as extensions can be placed in `docker/db-init/00-extensions.sql` which the
container also executes on first startup.

- `GLPI_BASE_URL` – base URL of the GLPI API (e.g. `https://glpi.company.com/apirest.php`).
  Using HTTPS is recommended for deployments.
- `GLPI_APP_TOKEN` – your application token
- `GLPI_USERNAME` / `GLPI_PASSWORD` – login credentials (optional if using a user token)
- `GLPI_USER_TOKEN` – API token for a specific user (optional)
- The service validates these tokens on startup and will exit with an error if they
  are missing or malformed. Log output masks any value matching the token pattern.
- Tokens are expected to be hexadecimal strings at least 40 characters long.
- `DASHBOARD_API_TOKEN` – optional token required in the `X-API-Token` header when
  accessing the worker API
- You may also provide secrets via file-based variants such as
  `GLPI_APP_TOKEN_FILE` and `GLPI_USER_TOKEN_FILE`. Set each variable with
  the path to a Docker/Kubernetes secret file and the client will read the
  token from that location.
- `VERIFY_SSL` – set to `false` to ignore invalid TLS certificates
- `CLIENT_TIMEOUT_SECONDS` – HTTP client timeout in seconds
- `KNOWLEDGE_BASE_FILE` – caminho para o arquivo Markdown com erros
  conhecidos utilizado pelo worker (padrão `docs/knowledge_base_errors.md`)
- `DB_HOST` – PostgreSQL host
- `DB_PORT` – PostgreSQL port
- `HOST_DB_PORT` – host port bound to the PostgreSQL container (default `5432`)
- `DB_NAME` – database name
- `DB_USER` – database username
- `DB_PASSWORD` – database password
- `REDIS_HOST` – Redis host
- `REDIS_PORT` – Redis port
- `REDIS_DB` – Redis database number
- `REDIS_TTL_SECONDS` – TTL for cached responses in seconds
- `CACHE_TYPE` – choose `redis` (default) or `simple` for in-memory caching
- `LOG_LEVEL` – logging verbosity for backend and worker services (default `INFO`)
- `APP_ENV` – set to `production` for JSON logs without backtraces
- `API_CORS_ALLOW_ORIGINS` – comma-separated list of trusted origins when `APP_ENV=production`
- `API_CORS_ALLOW_METHODS` – comma-separated HTTP methods allowed in production (default `GET,HEAD,OPTIONS`)
- `LANGCHAIN_TRACING_V2` – set to `true` to enable LangSmith tracing
- `LANGCHAIN_API_KEY` – API key used by LangSmith when tracing
- `LANGCHAIN_PROJECT` – optional project name for tracing sessions
- *Note*: IP filtering is not built into the worker API. Use your
  network configuration or a reverse proxy if access needs to be
  restricted. If your company enforces outbound proxies, define
  `HTTP_PROXY` and `HTTPS_PROXY` as shown in `.env.example`.

When these variables are present the package will automatically
initialize LangSmith and record traces for your runs. The project name
defaults to `default` if `LANGCHAIN_PROJECT` is unset.

### Database roles

The initialization script `docker/db-init/01-init-db.sh` creates a
least-privilege setup:

- `migration_user` – owner of schema migrations. Tables created by this role
  automatically grant permissions to the application roles.
- `app_readwrite` – allows standard CRUD access. This role is granted to
  `DB_USER` so the application can read and write normally.
- `app_readonly` – read-only access for future analytics or reporting tasks.

### Activating LangSmith tracing

Add the following variables to `.env` to record traces in your LangSmith
dashboard:

```bash
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=<your_langsmith_key>
LANGCHAIN_PROJECT=glpi-dashboard
```

With these set, the application will automatically initialize LangSmith when
importing `backend`.

Before running Docker make sure this `.env` file exists and that `DB_NAME`,
`DB_USER`, `DB_PASSWORD` and all GLPI credentials have non-empty values. The
compose files map these settings to `POSTGRES_DB`, `POSTGRES_USER` and
`POSTGRES_PASSWORD`. You can create the file using:

```bash
python scripts/setup/setup_env.py
```

The Docker services rely on these settings to connect to the database and the
GLPI API.
Run `npm run check-env` to verify that all mandatory variables are present
before building or launching the stack. The PostgreSQL container reads `DB_NAME`,
`DB_USER` and `DB_PASSWORD` from `.env` and the initialization script runs
automatically on the first `docker compose up`. If the container fails to start
remove any existing volume with `docker compose down -v` and recreate the stack.

You can verify that your credentials work before launching the stack:

```bash
python scripts/validate_credentials.py
```

If the connection succeeds you will see `✅ Conexão com GLPI bem-sucedida!`.
If you receive `❌ Falha de Conexão de Rede` the host may be unreachable.
Check that your VPN is active and no firewall rules block access to the
configured `GLPI_BASE_URL`.

After configuring the environment file you can optionally generate a full JSON
dump of tickets. The repository only ships with a small sanitized sample under
`resources/data/raw_tickets_sample.json` for quick tests.

```bash
python scripts/fetch/fetch_tickets.py --output data/tickets_dump.json
```

## Database setup

Run migrations to create the PostgreSQL tables defined in `resources/db/schema.sql`:

```bash
make init-db
```

Pass `--drop-all` to recreate everything from scratch.

The script can also be invoked directly:

```bash
PYTHONPATH=src python scripts/setup/init_db.py --drop-all
```

## Docker deployment

You can run the entire stack with Docker. The compose file includes
`postgres`, `redis`, a FastAPI **worker** and the Dash dashboard. The database
service mounts initialization scripts from `docker/db-init` which create the
non-privileged user and database on first startup. These scripts run only once
because the PostgreSQL data is persisted in a volume. If you modify any file in
`docker/db-init` you must recreate the volume with `docker compose down -v`
before restarting the stack.
The examples below rely on the Docker Compose plugin (`docker compose`).
Install the `docker-compose-plugin` package or upgrade to Docker Engine 20.10+
if the command is unavailable.

### Development

Running `docker compose up` loads `docker-compose.override.yml` automatically and
mounts the source directories for hot reload:

```bash
docker compose up
```

Before launching the compose stack make sure the root environment file exists.
Create one from the template if needed:

```bash
cp .env.example .env
```

Docker Compose loads `.env` automatically when it exists.

PostgreSQL binds to port `${HOST_DB_PORT:-5432}` on the host. Change
`HOST_DB_PORT` in `.env` if this port is already taken or if you prefer a
different mapping.

If the file is missing the backend falls back to `REDIS_HOST=redis` so the
services can communicate with the bundled `redis` container.

When using Docker Compose the Redis host should be `redis`. Set `REDIS_HOST`,
`REDIS_URL` and `CACHE_REDIS_HOST` accordingly in your environment or `.env`
file.

### Production

Combine the base file with `docker-compose.prod.yml`:

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

The override file also sets Prometheus to `--log.level=warn` so only warnings
and errors appear in the logs. Adjust the command in
`docker-compose.override.yml` if you need more verbose Prometheus output.

The Dockerfile at `docker/backend_service/Dockerfile` allows skipping Playwright browser installation using the
`INSTALL_PLAYWRIGHT` build argument. This is set to `false` in
`docker-compose.override.yml` to speed up development builds. Enable it only when you
need browser automation.

The frontend image takes advantage of BuildKit caching to speed up subsequent `npm ci` runs. Ensure BuildKit is enabled by setting `DOCKER_BUILDKIT=1`.

This exposes the worker API on port `8000` and the dashboard on port `5174`.
Open `http://localhost:5174` in your browser once the containers are ready.

## Configuration Management

Docker Compose loads variables from the `.env` file at the repository root.
Each `${VAR}` reference in the compose files is replaced with the value defined
in this file. The same variables are injected into the containers using the
`env_file` directive so the services see identical settings at runtime.

Environment variables follow the standard precedence order:

1. Values passed on the command line with `-e` or `--env-file`
2. Entries under the `environment:` section of a service
3. Keys loaded from `env_file`
4. Defaults baked into the Docker image

For production deployments store secrets like tokens and passwords in Docker
secrets (or an external manager) instead of committing them to the `.env` file.

## Network

If the host has limited internet access you can pre-download all Python
dependencies using the helper script:

```bash
./scripts/download_wheels.sh [target-dir]
```

The wheels are saved under `./wheels` by default. Transfer the directory to the
offline machine and install using:

```bash
pip install --no-index --find-links=wheels -r requirements.txt -r requirements-dev.txt  # generated via pip-compile
```

## Tests and linting

Execute the unit tests with coverage. The `pytest.ini` configuration applies
`--cov=./ --cov-report=term-missing --cov-fail-under=85` by default. If
`pytest-cov` is not installed or you want to skip coverage checks run
`pytest -p no:cov` or override `PYTEST_ADDOPTS` when invoking the command. Note
that running only a subset of tests may fail because the `addopts` line in
`pytest.ini` enforces coverage. Use `--no-cov` or clear `PYTEST_ADDOPTS` when
invoking individual files. See [docs/testing.md](docs/testing.md) for details.
Before running `pytest` or `make test` you **must** install all dependencies and the local package in editable mode using the commands shown in the setup section.

Running `scripts/setup/setup_env.sh` performs the same installation automatically and configures
pre-commit hooks. If you use the Makefile run `make setup` once to prepare the
virtual environment before calling `make test`. After the environment is ready
you can run `make test` to execute the suite in one step or invoke `pytest`
directly.

For quick local tests you may copy `.env.example` to `.env` if the file is
missing:

```bash
cp .env.example .env
```

You may also install only the optional development extras with:

```bash
./scripts/install_dev_extras.sh
```

This reads the `[project.optional-dependencies].dev` list from `pyproject.toml`
and installs each package via `pip`.

Browser-based tests such as `test_dashboard_flows` rely on Chrome and
Chromedriver. If these are unavailable you can skip them with:

```bash
pytest -k 'not test_dashboard_flows'
```

Lint checks can be run manually:

```bash
black --check .
flake8 .
```

Node-based tests and linting require local packages as well. Navigate to
`src/frontend/react_app` and run `npm ci` before executing `npm test` or
`npm run lint`. This installs dev dependencies like `dotenv` used by the Jest
suite.

### Bug prompt generation

After checking the tests and lints you can consolidate the failures into a
prompt for GPT‑4 or Gemini:

1. Ensure the environment is set up and run
   `pre-commit run --all-files && pytest`.
2. Generate the prompt with:

   ```bash
   python scripts/generate_bug_prompt.py --output bug_prompt.md
   ```

3. Open `bug_prompt.md` and copy its contents into the LLM chat to request
   bug‑fix suggestions.

The output location defaults to `prompts/bug_prompt.md` as configured in
`src/prompt_config.py`. The file is temporary and ignored by version control.

### Prompt settings

`PromptConfig` centralizes options used by automation scripts.
It defines the directory where prompts are stored, the default models
(`gpt-4o` for Codex and `gemini-1.5-pro` for Gemini) and caching paths.
It also exposes the locations of each `AGENTS.md` file and the
`A1 → A9` multi-agent sequence used throughout the project.

## Front-end performance

The Vite React dashboard targets a Largest Contentful Paint (LCP) below **2.5&nbsp;seconds**.
Builds fail if any JavaScript bundle exceeds **250&nbsp;kB**. Run the analyzer
from the `src/frontend/react_app` directory with:

```bash
npm run analyze
```

### Performance: List Virtualization

Very large ticket lists can hurt rendering performance if each row is mounted at
once. The `VirtualizedTicketTable` component automatically enables
`react-window` when the data set contains **100 rows or more**. For smaller lists
you may still use the component and tweak the threshold inside
`VirtualizedTicketTable.tsx`.

During unit tests the virtualization layer is mocked so snapshots remain stable.
`jest.setup.ts` registers the mock:

```ts
jest.mock('react-window', () => {
  const React = require('react')
  const MockedList = (props: any) => <div>{props.children}</div>
  return {
    FixedSizeList: MockedList,
    VariableSizeList: MockedList,
  }
}, { virtual: true })
```

Make sure your Jest configuration includes this setup file via
`setupFilesAfterEnv`.

### \ud83d\udd0d Monitoramento de Performance

O layout principal inclui um `React.Profiler` que registra a dura\u00e7\u00e3o de render no console durante o desenvolvimento. Quando `NODE_ENV` é `development`, a biblioteca `why-did-you-render` é carregada dinamicamente para apontar re-renderiza\u00e7\u00f5es desnecess\u00e1rias.

Em produ\u00e7\u00e3o, a fun\u00e7\u00e3o `reportWebVitals` envia as m\u00e9tricas **CLS**, **LCP**, **FCP** e **INP** para o Sentry. As builds de PR executam o workflow `performance.yml`, que roda o Lighthouse CI com os seguintes limites:

- LCP < 3\u00a0s
- TTI < 3.5\u00a0s
- Total-Byte-Weight < 250\u00a0kB

Gere flamegraphs locais com:

```bash
cd src/frontend/react_app && npm run perf:profile
```

## CI

Continuous integration runs on GitHub Actions using `.github/workflows/ci.yml`.
The workflow is split into three jobs:

1. **Lint** – installs dependencies via `scripts/setup/setup_env.sh`, checks Python code with
   `pre-commit` and runs `npm run lint` inside `src/frontend/react_app`.
2. **Test** – executed for Python 3.10, 3.11 and 3.12 through a matrix build.
   It runs `pytest` and the Jest suite for the React app.
3. **Build** – tagged commits trigger a Docker build that publishes the image to
   GHCR.

Tracing is enabled during tests thanks to
`opentelemetry-instrumentation-fastapi` and
`opentelemetry-instrumentation-logging`.

### Snyk setup

The CI workflow runs a Snyk vulnerability scan after the test jobs finish. Make
sure your network can reach `snyk.io` as described in
[docs/snyk_setup.md](docs/snyk_setup.md). You can validate connectivity with:

```bash
./scripts/check_snyk_access.sh


The workflow also runs `ast-grep` using rules under `rules/` to ensure
frontend modules never import database layers directly.

## Architecture Decision Records

All ADRs live in [`docs/adr`](docs/adr). Create new records with
`./scripts/adr-new "Título"` which fills in the MADR template automatically.

## Examples Directory

Code samples and pattern demos reside in [`examples/`](examples/). Demonstration modules such as `song_serializer.py` and `sort_strategy.py` live under [`examples/patterns`](examples/patterns/) and are intended solely for educational use.

The repository also contains a [`labs/`](labs/) folder for experimental work
that hasn't been fully adopted. See [`labs/prototypes/`](labs/prototypes/) for
isolated proofs of concept. Nothing inside `labs/` ships with production
builds.

### Running the Rope codemod

Refactor moves can be automated with `scripts/run_py_codemod.sh`. The wrapper
invokes Rope's `refactor_move.py` and rewrites imports for you. The
[Rope](https://github.com/python-rope/rope) library is part of the `dev` extras
defined in `pyproject.toml` and therefore included in `requirements-dev.txt`.
Running `make setup` (or installing the requirements manually) prepares
everything automatically.

```bash
./scripts/run_py_codemod.sh src/shared/utils/resilience/circuit_breaker.py src/backend/adapters/resilience/
```

See the
[Codemod Python (Rope) entry](docs/REFACTOR_LOG.md#codemod-python-rope)
for details on how this script was used during the structural refactor.

## License

This project is released under the [MIT License](LICENSE).

### CI/CD Pipeline

A GitHub Actions workflow (`cicd.yml`) runs linting with **ruff**, **black** and **isort**, executes the full pytest suite and builds a Docker image for pushes to `main` or version tags. The resulting image is published to GHCR and deployed through `scripts/deploy/deploy_production.sh`.
For CI/CD governance guidelines, see [docs/governanca_tecnica_prompt.md](docs/governanca_tecnica_prompt.md).
Guidance on connecting the API to Copilot Studio is available in
[docs/copilot_integration.md](docs/copilot_integration.md).
For common asyncio patterns and deployment notes see
[docs/asyncio_scenarios.md](docs/asyncio_scenarios.md).
For a complete developer usage guide see
[docs/developer_usage.md](docs/developer_usage.md).
