# GLPI Dashboard CAU

![Coverage](https://img.shields.io/badge/coverage-90%25-brightgreen.svg)
[![Security](https://snyk.io/test/github/jonathan-nascimento51/glpi_dashboard_cau/badge.svg)](https://snyk.io/test/github/jonathan-nascimento51/glpi_dashboard_cau)
[![Draft v0.1](https://img.shields.io/badge/DRAFT-v0.1-informational)](docs/vision.md)

This project provides a minimal dashboard to visualize service desk tickets from GLPI using a live connection to the REST API.

## Purpose

The goal is to inspect backlog, ticket status and productivity metrics without a live GLPI connection. Data is fetched via the API and normalized into JSON that the Dash app loads on startup.

## Getting Started

Install dependencies and prepare the environment:

You can run `./setup.sh` to install the main requirements in one step or
execute the commands below manually.

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt -r requirements-dev.txt
pip install -e .  # install package locally (packages live under src/)
pre-commit install  # sets up hooks for black, ruff, isort and mypy
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
- Node or Docker are **not** required for development

Set the connection details in `.env` using the keys `DB_*` and `REDIS_*`.

## Architecture

```
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
[AGENTS.md](AGENTS.md).
Instructions for running the React front-end—including npm scripts and required environment variables—are available in
[docs/frontend_architecture.md](docs/frontend_architecture.md). That document also covers how the front-end communicates with the worker API via `VITE_API_URL` and how to run the Jest and Playwright test suites.

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
```

This project also uses the `rich-click` library for colored CLI output. It is included in `requirements.txt`.

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

The service exposes four endpoints:

- `/tickets` – full list of tickets in JSON format.
- `/metrics` – summary with `total`, `opened` and `closed` counts.
- `/graphql/` – GraphQL API providing the same information.
- `/cache/stats` – returns cache hit/miss metrics.

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

Open `.env` and set the required values:

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
- `LANGCHAIN_TRACING_V2` – set to `true` to enable LangSmith tracing
- `LANGCHAIN_API_KEY` – API key used by LangSmith when tracing
- `LANGCHAIN_PROJECT` – optional project name for tracing sessions
- _Note_: IP filtering is not built into the worker API. Use your
  network configuration or a reverse proxy if access needs to be
  restricted.

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
`DB_USER`, `DB_PASSWORD` and all GLPI credentials have non-empty values. You can
create the file using:

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

After configuring the environment file you can optionally download a JSON dump of tickets:

```bash
python scripts/fetch_tickets.py --output tickets_dump.json
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
Running `docker-compose up` will build the image, initialize the database and start all services:

```bash
docker-compose up
```

This exposes the worker API on port `8000` and the dashboard on port `8080`.

## Tests and linting

Execute the unit tests with coverage:

```bash
pip install -r requirements.txt -r requirements-dev.txt
pytest --cov=./
pre-commit run --all-files
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
with:

```bash
npm run analyze
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
For long-term planning refer to
[roadmap_2025_2026.md](roadmap_2025_2026.md).

