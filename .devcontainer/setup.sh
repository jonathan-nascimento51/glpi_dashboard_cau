#!/bin/bash
set -e
apt-get update && apt-get install -y build-essential
pip install -r requirements.txt
pre-commit install
