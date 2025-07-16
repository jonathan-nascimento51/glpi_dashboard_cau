# Testing Guide

The test suite relies on several optional libraries and expects coverage to be enabled by default. Install all runtime and development dependencies **before** invoking pytest:

```bash
pip install -r requirements.txt -r requirements-dev.txt
pip install -e .
```

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

`ModuleNotFoundError` typically means dependencies were not installed. Common cases are:

- `aiohttp` required by the async GLPI client
- `pydantic>=2` for data models

Ensure both requirement files are installed and that your virtual environment is active.
