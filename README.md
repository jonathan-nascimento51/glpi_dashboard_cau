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

## Running the Dash app

Ensure there is a ticket dump in `mock/sample_data.json` or a file of your choice, then run:

```bash
python main.py
```

The app will be available at <http://127.0.0.1:8050>.

## Worker API

`worker_api.py` provides a lightweight FastAPI service that exposes the same
ticket data for other applications. It can read from the JSON dump or fetch
directly from GLPI when the `--use-api` flag is supplied.

Example using the dump:

```bash
python worker_api.py
```

Fetch live data instead:

```bash
python worker_api.py --use-api
```

The service exposes three endpoints:

- `/tickets` – full list of tickets in JSON format.
- `/metrics` – summary with `total`, `opened` and `closed` counts.
- `/graphql` – GraphQL API providing the same information.

## Environment variables

Some scripts require a few variables set in a `.env` file. Copy `.env.example` and fill in your API credentials:

```bash
GLPI_URL=http://seu-glpi-url/api
APP_TOKEN=your_app_token_here
USER_TOKEN=your_user_token_here
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

