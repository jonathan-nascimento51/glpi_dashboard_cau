#!/bin/bash
set -e
export REQUESTS_CA_BUNDLE=$(python -m certifi)
apt-get update && apt-get install -y build-essential
pip install -r requirements.txt -r requirements-dev.txt
pre-commit install
