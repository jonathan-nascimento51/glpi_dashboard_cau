#!/usr/bin/env bash
# Configure GitHub access using the GitHub CLI (gh).
# This script installs gh if missing and authenticates using $GITHUB_TOKEN.
set -euo pipefail

if ! command -v gh >/dev/null 2>&1; then
  echo ">>> Installing GitHub CLI..."
  type -p curl >/dev/null || (sudo apt-get update -y && sudo apt-get install -y curl)
  curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
  sudo chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg
  echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list >/dev/null
  sudo apt-get update -y
  sudo apt-get install -y gh
fi

if [ -z "${GITHUB_TOKEN:-}" ]; then
  cat <<EOM
⚠️  GITHUB_TOKEN not set.
Create a personal access token with repo permissions and run:
  export GITHUB_TOKEN=<token>
  bash scripts/setup_github_access.sh
EOM
  exit 1
fi

echo ">>> Authenticating GitHub CLI..."
echo "$GITHUB_TOKEN" | gh auth login --with-token

echo ">>> Marking repository as safe..."
git config --global --add safe.directory "$(pwd)"

echo "✅ GitHub access configured."
