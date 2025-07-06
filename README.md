# GLPI Dashboard CAU

![Coverage](https://img.shields.io/badge/coverage-80%25-brightgreen.svg)
[![Security](https://snyk.io/test/github/jonathan-nascimento51/glpi_dashboard_cau/badge.svg)](https://snyk.io/test/github/jonathan-nascimento51/glpi_dashboard_cau)
[![Draft v0.1](https://img.shields.io/badge/DRAFT-v0.1-informational)](docs/vision.md)

This project provides a minimal dashboard to visualize service desk tickets from GLPI using a live connection to the REST API.

## Purpose

The goal is to inspect backlog, ticket status and productivity metrics without a live GLPI connection. Data is fetched via the API and normalized into JSON that the Dash app loads on startup.

## Getting Started

Install dependencies and prepare the environment:

You can run `./setup.sh` to install all dependencies, set up the editable package
and enable pre-commit hooks in one step or execute the commands below manually.

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt -r requirements-dev.txt
pip install -e .  # install package locally (packages live under src/)
pre-commit install  # sets up hooks for black, ruff, isort and mypy
# Ruff version pinned to 0.12.2 is included in requirements-dev.txt
# Reinstall dev dependencies before running pre-commit if your environment is outdated
```

Create a `.env` file from the template and set PostgreSQL/Redis credentials:

```bash
python scripts/setup_env.py  # copies .env.example
```

Initialize the database:

```bash
PYTHONPATH=$(pwd) python scripts/init_db.py --drop-all
```

Run the dashboard:

```bash
python main.py
```

Open <http://127.0.0.1:8050> in your browser.

## Dependencies

- Python 3.10+
- PostgreSQL and Redis instances running locally (or update the `.env` file)
- Node.js is required to run the React frontend locally.
  Docker remains an optional alternative for running the entire stack.

Set the connection details in `.env` using the keys `DB_*` and `REDIS_*`.

## Configuration

Store credentials in a local `.env` file or load them from a vault service.
Sensitive variables like `GLPI_*` should **never** be committed to the
repository. The project expects these values in your environment before running
any scripts.

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
[AGENTS.md](AGENTS.md). A walkthrough of the `langgraph_workflow.py` module is
available in [docs/langgraph_workflow.md](docs/langgraph_workflow.md).
Instructions for running the React front-end—including npm scripts and required environment variables—are available in
[docs/frontend_architecture.md](docs/frontend_architecture.md). That document also covers how the front-end communicates with the worker API via `NEXT_PUBLIC_API_BASE_URL` and how to run the Jest and Playwright test suites.
Create the environment file with `cp frontend/.env.example frontend/.env` before running the dashboard. Execute all npm commands from inside the `frontend` directory, e.g. `cd frontend && npm run dev`, or launch Docker.

## Main modules

- **`glpi_session.py`** – asynchronous client for the GLPI REST API used by the worker and ETL modules. This file replaces the former `glpi_api.py` referenced in early docs.
- **`data_pipeline.py`** – normalizes raw ticket data into a `pandas.DataFrame` and exports JSON.
- **`dash_layout.py`** – defines tables and charts for the Dash UI.
- **`main.py`** – starts the Dash server.
- **`scripts/`** – helper utilities like `filters.py`, `hash_data.py`, `log_exec.py`.

## Installation

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt -r requirements-dev.txt
pre-commit install  # sets up hooks for black, ruff, isort and mypy
# Ruff version pinned to 0.12.2 is included in requirements-dev.txt
# Reinstall dev dependencies before running pre-commit if your environment is outdated
```

This project also uses the `rich-click` library for colored CLI output. It is included in `requirements.txt`.

## Installing Dependencies Behind a Proxy or Offline

If your machine needs a proxy to reach PyPI, export the proxy variables before
invoking `pip`:

```bash
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=$HTTP_PROXY
pip install -r requirements.txt -r requirements-dev.txt
```

On a machine with internet access you can pre-download the wheels needed by the
project:

```bash
./scripts/download_wheels.sh [target-dir]
```

The script stores wheels under `./wheels` by default. Copy this directory to the
offline machine and install everything without contacting PyPI:

```bash
pip install --no-index --find-links=/path/to/wheels -r requirements.txt -r requirements-dev.txt
```

More setup tips—including offline usage with mock data—are documented in
[docs/glpi_tokens_guide.md](docs/glpi_tokens_guide.md).

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

## Running the Dash app

Start the dashboard pointing to your GLPI instance:

```bash
python main.py
```

The Dash server uses gzip compression via `flask-compress` and loads data lazily on first render.

Use the `/ping` endpoint for health checks; it returns `OK` when the server is running.

Profile startup time with:

```bash
python scripts/profile_dash.py
```

The app will be available at <http://127.0.0.1:8050>.

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
For additional troubleshooting steps in Portuguese, see
[docs/solucoes_problemas.md](docs/solucoes_problemas.md).
Specific guidance for erros `400 Bad Request` ao iniciar a sessão GLPI via Docker
está disponível em
[docs/troubleshooting_400_bad_request.md](docs/troubleshooting_400_bad_request.md).
Detalhes completos do endpoint `initSession` encontram-se em
[docs/init_session_api.md](docs/init_session_api.md).

## Running the Worker API

`worker.py` provides a lightweight FastAPI service that exposes ticket data for other applications. It always retrieves information from the GLPI API.

Run the service:

```bash
python worker.py
```

The service exposes several endpoints:

- `/tickets` – full list of tickets in JSON format.
- `/tickets/stream` – Server‑Sent Events (SSE) stream of progress followed by the JSON payload.
- `/metrics` – summary with `total`, `opened` and `closed` counts.
- `/metrics/aggregated` – cached counts grouped by status and technician.
- `/chamados/por-data` – aggregated tickets per creation date (cached in Redis for **1 hour**).
- `/chamados/por-dia` – totals for calendar heatmaps (cached in Redis for **24 hours**).
- `/graphql/` – GraphQL API providing the same information.
- `/cache/stats` – returns cache hit/miss metrics.
- `/health/glpi` – quick check that the worker can reach the GLPI API.

Make sure the service is running with `python worker.py` and that your
front-end points to it via `NEXT_PUBLIC_API_BASE_URL` in `frontend/.env`.
Create the environment file with `cp frontend/.env.example frontend/.env` before starting the front-end.
Run npm scripts from inside the `frontend` directory (`cd frontend && npm run dev`) or launch Docker.

Vite loads environment variables that start with `NEXT_PUBLIC_` thanks to `envPrefix` in `frontend/vite.config.ts`. Imports that begin with `@/` resolve to the `src` directory so paths stay short.
Copy `frontend/.env.example` to `frontend/.env` if the file doesn't exist and
adjust the URL as needed.

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

## Collecting ticket/group assignments

Use the helper CLI to dump assignments into a Parquet dataset:

```bash
python -m cli.tickets_groups --since 2025-06-01 --until 2025-06-30 \
    --outfile datasets/tickets_groups.parquet
```

Adjust the dates and destination file as needed. The command prints the resulting path after completion.

## Environment variables

Some scripts require a few variables set in a `.env` file. Copy the template and fill in your credentials:

```bash
python scripts/setup_env.py  # copies .env.example to .env
```

Open `.env` and set the required values.
*Important:* all variable names must be **uppercase**, otherwise the Pydantic loader will ignore them.

Example snippet:

```bash
# Database credentials
DB_NAME=glpi_dashboard
DB_USER=user
DB_PASSWORD=password

# Mapped automatically to the Postgres container
POSTGRES_DB=$DB_NAME
POSTGRES_USER=$DB_USER
POSTGRES_PASSWORD=$DB_PASSWORD
```

- `GLPI_BASE_URL` – base URL of the GLPI API (e.g. `https://glpi.company.com/apirest.php`).
  Using HTTPS is recommended for deployments.
- `GLPI_APP_TOKEN` – your application token
- `GLPI_USERNAME` / `GLPI_PASSWORD` – login credentials (optional if using a user token)
- `GLPI_USER_TOKEN` – API token for a specific user (optional)
- `KNOWLEDGE_BASE_FILE` – path to the JSON dump used by the dashboard and API
- `DB_HOST` – PostgreSQL host
- `DB_PORT` – PostgreSQL port
- `DB_NAME` – database name
- `DB_USER` – database username
- `DB_PASSWORD` – database password
- `REDIS_HOST` – Redis host
- `REDIS_PORT` – Redis port
- `REDIS_DB` – Redis database number
- `REDIS_TTL_SECONDS` – TTL for cached responses in seconds
- `LOG_LEVEL` – logging verbosity for backend and worker services (default `INFO`)
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

### Activating LangSmith tracing

Add the following variables to `.env` to record traces in your LangSmith
dashboard:

```bash
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=<your_langsmith_key>
LANGCHAIN_PROJECT=glpi-dashboard
```

With these set, the application will automatically initialize LangSmith when
importing `glpi_dashboard`.

Before running Docker make sure this `.env` file exists and that `DB_NAME`,
`DB_USER`, `DB_PASSWORD` and all GLPI credentials have non-empty values. The
compose files map these settings to `POSTGRES_DB`, `POSTGRES_USER` and
`POSTGRES_PASSWORD`. You can create the file using:

```bash
python scripts/setup_env.py
```

The Docker services rely on these settings to connect to the database and the
GLPI API.

You can verify that your credentials work before launching the stack:

```bash
python scripts/validate_credentials.py
```

If the connection succeeds you will see `✅ Conexão com GLPI bem-sucedida!`.

After configuring the environment file you can optionally generate a full JSON
dump of tickets. The repository only ships with a small sanitized sample under
`data/raw_tickets_sample.json` for quick tests.

```bash
python scripts/fetch_tickets.py --output data/tickets_dump.json
```

## Database setup

Run migrations to create the PostgreSQL tables defined in the `schema.sql` file located at the project root:

```bash
make init-db
```

Pass `--drop-all` to recreate everything from scratch.

The script can also be invoked directly:

```bash
PYTHONPATH=$(pwd) python scripts/init_db.py --drop-all
```

For a MySQL-specific walkthrough, see [docs/first_use_mysql.md](docs/first_use_mysql.md) which lists all required environment variables and setup steps.

## Docker deployment

You can run the entire stack with Docker. The compose file includes
`postgres`, `redis`, an `initdb` service, a FastAPI **worker** and the Dash dashboard.
Running `docker compose up` will build the image, initialize the database and start all services using `docker-compose.yml`:

```bash
docker compose up
```

Before launching the compose stack make sure the root environment file exists.
Create one from the template if needed:

```bash
cp .env.example .env
```

If the file is missing the backend falls back to `REDIS_HOST=localhost` which
prevents communication with the `redis` container.

When using Docker Compose the Redis host should be `redis`. Set `REDIS_HOST`,
`REDIS_URL` and `CACHE_REDIS_HOST` accordingly in your environment or `.env`
file.

For local development you can use `docker-compose-dev.yml`, which mounts your source files with hot reload:

```bash
docker-compose -f docker-compose-dev.yml up --build
```

The development compose file also sets Prometheus to `--log.level=warn` so only
warnings and errors appear in the logs. Adjust the command in
`docker-compose-dev.yml` if you need more verbose Prometheus output.

The backend Dockerfile allows skipping Playwright browser installation using the
`INSTALL_PLAYWRIGHT` build argument. This is set to `false` in
`docker-compose-dev.yml` to speed up development builds. Enable it only when you
need browser automation.

The frontend image takes advantage of BuildKit caching to speed up subsequent `npm ci` runs. Ensure BuildKit is enabled by setting `DOCKER_BUILDKIT=1`.

This exposes the worker API on port `8000` and the dashboard on port `5173`.

## Network

If the host has limited internet access you can pre-download all Python
dependencies using the helper script:

```bash
./scripts/download_wheels.sh [target-dir]
```

The wheels are saved under `./wheels` by default. Transfer the directory to the
offline machine and install using:

```bash
pip install --no-index --find-links=wheels -r requirements.txt -r requirements-dev.txt
```

## Tests and linting

Execute the unit tests with coverage:

Alternatively you can run `make test` to install dependencies and execute the
suite in one step.

```bash
pip install -r requirements.txt -r requirements-dev.txt
pip install -e .  # ensure local package is discoverable during tests
# install aiohttp explicitly if using a custom environment
pip install aiohttp
# the core suite relies on `aiohttp` and `pandas`
# `make test` runs the same setup; running `pytest` directly requires these
# dependencies to be installed beforehand
# optional extras for e2e and container tests
pip install testcontainers playwright
# browser tests require Chrome/Chromedriver
# install via `apt-get install chromium-driver` or `npx playwright install`
# skip them with `pytest -k 'not test_dashboard_flows'` if the driver is missing
pytest --cov=./
pre-commit run --all-files
```

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

### Bug prompt generation

After running the tests and lint checks you can gather the current warnings and
create a debugging prompt for other LLMs:

```bash
python scripts/generate_bug_prompt.py --output bug_prompt.md
```

## Front-end performance

The Next.js dashboard targets a Largest Contentful Paint (LCP) below **2.5&nbsp;seconds**.
Builds fail if any JavaScript bundle exceeds **250&nbsp;kB**. Run the analyzer
from the `frontend` directory with:

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
cd frontend && npm run perf:profile
```

## CI

Continuous integration runs on GitHub Actions using `.github/workflows/ci.yml`.
It installs dependencies using `./setup.sh`, initializes the database and
executes pre-commit hooks and the test suite for Python 3.10 and 3.12.

## Architecture Decision Records

All ADRs live in [`docs/adr`](docs/adr). Create new records with
`./scripts/adr-new "Título"` which fills in the MADR template automatically.

## License

This project is released under the [MIT License](LICENSE).

For CI/CD governance guidelines, see [docs/governanca_tecnica_prompt.md](docs/governanca_tecnica_prompt.md).
Guidance on connecting the API to Copilot Studio is available in
[docs/copilot_integration.md](docs/copilot_integration.md).
For common asyncio patterns and deployment notes see
[docs/asyncio_scenarios.md](docs/asyncio_scenarios.md).
For a complete developer usage guide see
[docs/developer_usage.md](docs/developer_usage.md).
