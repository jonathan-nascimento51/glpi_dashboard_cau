# Testing Guide

The test suite relies on several optional libraries (such as **Playwright**) and expects coverage to be enabled by default. Install **all** runtime and development dependencies before invoking pytest. Base tools live in `requirements-dev.txt`, while packages specific to the end-to-end tests reside in `requirements-full-tests.txt` (or `pip install -e '.[full-tests]'`):

```bash
pip install -r requirements-dev.txt -r requirements-full-tests.txt  # generated via pip-compile
# or: pip install -e '.[full-tests]'
pip install -e .
```

After installing the packages, run the following to make the browsers available:

```bash
playwright install

Running a subset of tests can cause failures because `pytest.ini` enforces 85% coverage:

```ini
[pytest]
addopts = --cov=./ --cov-report=term-missing --cov-fail-under=85 -m "not e2e"
```

To execute individual tests locally you may disable coverage with `--no-cov` or override `addopts` in your environment:

```bash
pytest tests/test_worker_api.py::test_health_glpi --no-cov
# or
PYTEST_ADDOPTS="" pytest tests/test_worker_api.py
```

### Troubleshooting missing modules

`ModuleNotFoundError` typically means development dependencies were not installed. Common cases are:

- `aiohttp` required by the async GLPI client
- `pydantic>=2` for data models
- `playwright` for end-to-end tests

Ensure both requirement files are installed and that your virtual environment is active.
Missing any of these packages will cause import errors during test collection.
The backend tests expect environment variables like `GLPI_BASE_URL` to be set.
Create a `.env` file or export minimal values (e.g. `GLPI_BASE_URL=http://example.com/apirest.php`) before running `pytest`.
