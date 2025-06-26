# GLPI Dashboard CAU

![Coverage](https://img.shields.io/badge/coverage-90%25-brightgreen.svg)

This project provides a minimal dashboard to visualize service desk tickets from GLPI. Data can be retrieved from the GLPI REST API and stored locally in JSON for offline exploration with [Dash](https://dash.plotly.com/).

## Purpose

The goal is to inspect backlog, ticket status and productivity metrics without a live GLPI connection. Data is fetched via the API and normalized into JSON that the Dash app loads on startup.

## Getting Started

Install dependencies and prepare the environment:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt
pre-commit install
```

Create a `.env` file from the template and set PostgreSQL/Redis credentials:

```bash
python scripts/setup_env.py  # copies .env.example
```

Initialize the database then generate sample tickets:

```bash
python scripts/init_db.py --drop-all
python scripts/gen_mock_data.py --count 100 --null-rate 0.1
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

The dashboard reads data produced by the worker and stored in PostgreSQL or the
local `mock` JSON file. More details on the multi-agent workflow can be found in
[AGENTS.md](AGENTS.md).

## Main modules

- **`glpi_session.py`** – asynchronous client for the GLPI REST API used by the worker and ETL modules. This file replaces the former `glpi_api.py` referenced in early docs.
- **`data_pipeline.py`** – normalizes raw ticket data into a `pandas.DataFrame` and exports JSON.
- **`dash_layout.py`** – defines tables and charts for the Dash UI.
- **`main.py`** – starts the Dash server using data from `mock/`.
- **`scripts/`** – helper utilities like `filters.py`, `hash_data.py`, `log_exec.py`
  and the `gen_mock_data.py` generator.

## Installation

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt -r requirements-dev.txt
pre-commit install
```

This project also uses the `rich-click` library for colored CLI output. It is included in `requirements.txt`.

## Running the Dash app

Ensure there is a ticket dump in `mock/sample_data.json` or a file of your choice, then run:

```bash
python main.py  # uses mock data by default

# fetch live data instead
USE_MOCK=false python main.py
```

The Dash server uses gzip compression via `flask-compress` and loads data lazily on first render.

Profile startup time with:

```bash
python scripts/profile_dash.py
```

The app will be available at <http://127.0.0.1:8050>.

For an OS-specific walkthrough including virtual environment commands, see
[docs/run_local.md](docs/run_local.md).

## Running the Worker API

`worker_api.py` provides a lightweight FastAPI service that exposes the same ticket data for other applications. It can read from the JSON dump or fetch directly from GLPI when the `--use-api` flag is supplied.

Run with the sample JSON dump:

```bash
python worker_api.py            # uses mock/sample_data.json

# fetch live data instead
USE_MOCK=false python worker_api.py --use-api
```

Fetch live data instead:

```bash
python worker_api.py --use-api  # fetches from GLPI API
```

The service exposes four endpoints:

- `/tickets` – full list of tickets in JSON format.
- `/metrics` – summary with `total`, `opened` and `closed` counts.
- `/graphql/` – GraphQL API providing the same information.
- `/cache/stats` – returns cache hit/miss metrics.

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

- `GLPI_BASE_URL` – base URL of the GLPI API (e.g. `https://glpi.company.com/apirest.php`)
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

After configuring the environment file you can download tickets from GLPI:

```bash
python scripts/fetch_tickets.py --output mock/sample_data.json
```
Alternatively generate mock tickets offline:

```bash
python scripts/gen_mock_data.py --count 100 --null-rate 0.1
```


This JSON file can be used by both the Dash app and the worker API when running without the `--use-api` flag.

## Database setup

Run migrations to create the PostgreSQL tables defined in `schema.sql`:

```bash
make init-db
```

Pass `--drop-all` to recreate everything from scratch.

The script can also be invoked directly:

```bash
python scripts/init_db.py --drop-all
```

For a MySQL-specific walkthrough, see [docs/first_use_mysql.md](docs/first_use_mysql.md) which lists all required environment variables and setup steps.
<<<<<<< ours
=======

>>>>>>> theirs

## Docker deployment

You can run the entire stack with Docker. The compose file includes
`postgres`, `redis`, an `initdb` service, a FastAPI **worker** and the Dash dashboard.
Running `docker-compose up` will build the image, initialize the database and start all services:

```bash
docker-compose up
```

This exposes the worker API on port `8000` and the dashboard on port `8050`.

## Tests and linting

Execute the unit tests with coverage:

```bash
pip install -r requirements.txt -r requirements-dev.txt
pytest --cov=./
```

Lint checks can be run manually:

```bash
black --check .
flake8 .
```

## CI

Continuous integration runs on GitHub Actions using `.github/workflows/ci_mock.yml`.
It installs dependencies, initializes the database and executes pre-commit hooks
and the test suite for Python 3.10 and 3.12.

## License

This project is released under the [MIT License](LICENSE).

