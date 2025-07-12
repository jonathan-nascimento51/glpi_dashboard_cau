#!/bin/bash
# Run lint and tests via pre-commit
# Exit immediately if a command exits with a non-zero status.
# Treat unset variables as an error.
# The return value of a pipeline is the status of the last command to exit with a non-zero status.
set -euo pipefail

pre-commit run --color always --show-diff-on-failure
