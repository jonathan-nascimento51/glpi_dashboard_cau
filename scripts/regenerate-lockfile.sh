#!/usr/bin/env bash
set -euo pipefail

# 1) Encontra a raiz do projeto
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd -P)"

# 2) Mapeia para o formato Windows que o Docker Desktop reconhece
if command -v cygpath &>/dev/null; then
  WIN_PATH="$(cygpath -w "$PROJECT_DIR")"
  HOST_PATH="${WIN_PATH//\\//}"
elif command -v wslpath &>/dev/null; then
  HOST_PATH="$(wslpath -m "$PROJECT_DIR")"
else
  HOST_PATH="$PROJECT_DIR"
fi

echo "🔄 Limpando node_modules e package-lock.json…"
rm -rf "$PROJECT_DIR/node_modules" "$PROJECT_DIR/package-lock.json"

echo "🐳 Gerando novo package-lock.json no container Linux…"
docker run --rm \
  -v "${HOST_PATH}:/app" \
  node:20-alpine \
  sh -c "\
    cd /app && \
    npm install \
      --legacy-peer-deps \
      --prefer-offline \
      --no-audit \
      --progress=false"

# 3) Ajusta dono dos arquivos no host (Linux/macOS)
if [[ "$(id -u)" -ne 0 ]]; then
  echo "🔧 Ajustando dono dos arquivos gerados…"
  chown -R "$(id -u):$(id -g)" "$PROJECT_DIR"
fi

echo "✅ package-lock.json regenerado em: $PROJECT_DIR"
