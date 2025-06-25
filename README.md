# GLPI Dashboard CAU

This project provides a minimal dashboard to visualize service desk tickets from GLPI. Data can be retrieved from the GLPI REST API and stored locally in JSON for offline exploration with [Dash](https://dash.plotly.com/).

## Purpose

The goal is to inspect backlog, ticket status and productivity metrics without a live GLPI connection. Data is fetched via the API and normalized into JSON that the Dash app loads on startup.

## Main modules

- **`glpi_api.py`** – wrapper for the GLPI REST API that handles authentication and ticket retrieval.
- **`data_pipeline.py`** – normalizes raw ticket data into a `pandas.DataFrame` and exports JSON.
- **`dash_layout.py`** – defines tables and charts for the Dash UI.
- **`main.py`** – starts the Dash server using data from `mock/`.
- **`scripts/`** – helper utilities like `filters.py`, `hash_data.py` and `log_exec.py`.

## Installation

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
pre-commit install
```

This project also uses the `rich-click` library for colored CLI output. It is included in `requirements.txt`.

## Running the Dash app

Ensure there is a ticket dump in `mock/sample_data.json` or a file of your choice, then run:

```bash
python main.py
```

The app will be available at <http://127.0.0.1:8050>.

## Running the Worker API

`worker_api.py` provides a lightweight FastAPI service that exposes the same ticket data for other applications. It can read from the JSON dump or fetch directly from GLPI when the `--use-api` flag is supplied.

Run with the sample JSON dump:

```bash
python worker_api.py            # uses mock/sample_data.json
```

Fetch live data instead:

```bash
python worker_api.py --use-api  # fetches from GLPI API
```

The service exposes three endpoints:

- `/tickets` – full list of tickets in JSON format.
- `/metrics` – summary with `total`, `opened` and `closed` counts.
- `/graphql/` – GraphQL API providing the same information.

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

Open `.env` and set `GLPI_URL`, `GLPI_APP_TOKEN` and `GLPI_USER_TOKEN`. The template also defines `KNOWLEDGE_BASE_FILE` pointing to the JSON dump used by the dashboard and API.

After configuring the environment file you can download tickets from GLPI:

```bash
python scripts/fetch_tickets.py --output mock/sample_data.json
```

This JSON file can be used by both the Dash app and the worker API when running without the `--use-api` flag.

## Docker deployment

Build the image and run the worker API:

```bash
docker build -t glpi-dashboard .
docker run --env-file .env -p 8000:8000 glpi-dashboard
```

Use `docker-compose` for convenience:

```bash
docker-compose up
```

## Tests and linting

Execute the unit tests with:

```bash
pytest
```

Lint checks can be run manually:

```bash
black --check .
flake8 .
```

## License

This project is released under the [MIT License](LICENSE).

