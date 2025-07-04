#!/bin/bash
# Simple helper to set up the Python environment inside Codex or locally.
# It installs all dependencies, installs the package in editable mode and
# configures pre-commit hooks so that formatting and tests run automatically.
# HTTP_PROXY=""
# HTTPS_PROXY=""

set -e

python -m pip install --upgrade pip
pip install -r requirements.txt -r requirements-dev.txt
pip install -e .
pre-commit install
npx playwright install --with-deps