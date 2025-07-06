#!/bin/bash
set -euo pipefail

# Controle de instalação de Playwright/Chromium
# Defina SKIP_PLAYWRIGHT=true para pular a instalação (ex: em builds Docker)
SKIP_PLAYWRIGHT=${SKIP_PLAYWRIGHT:-true}

echo ">>> INICIANDO CONFIGURAÇÃO COMPLETA DO AMBIENTE <<<"

echo ">>> (1/6) Instalando dependências do sistema para o Playwright..."
sudo apt-get update -y
sudo apt-get install -y \
    libnss3 libnspr4 libatk1.0-0t64 libatk-bridge2.0-0t64 libcups2t64 \
    libdbus-1-3 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 \
    libgbm1 libpango-1.0-0 libcairo2 libasound2t64 libatspi2.0-0t64 libgtk-3-0t64 \
    libx11-xcb1 libxshmfence1 xvfb fonts-liberation libxslt1.1 libwoff1 \
    libharfbuzz-icu0 libvpx9 libavif16 libwebpdemux2 libenchant-2-2 libsecret-1-0 \
    libhyphen0 libgles2 libgstreamer1.0-0 gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good gstreamer1.0-libav

VENV_DIR=".venv"
if [ ! -d "$VENV_DIR" ]; then
  echo ">>> (2/6) Criando ambiente virtual em $VENV_DIR..."
  python3 -m venv "$VENV_DIR"
fi

echo ">>> (3/6) Ativando o ambiente virtual..."
# shellcheck disable=SC1090
source "$VENV_DIR/bin/activate"

echo ">>> (4/6) Atualizando o pip e instalando dependências Python..."
pip install --upgrade pip
pip install -r requirements.txt -r requirements-dev.txt
pip install -e .

echo ">>> (5/6) Instalando ganchos de pre-commit..."
if command -v pre-commit >/dev/null 2>&1; then
  pre-commit install
else
  echo "⚠️ pre-commit não encontrado. Instalando..."
  pip install pre-commit && pre-commit install
fi

echo ">>> (6/6) Instalando Docker..."
sudo apt-get install -y ca-certificates curl gnupg lsb-release
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update -y
curl -fsSL https://get.docker.com | sudo sh

# sudo usermod -aG docker "${USER:-$(whoami)}"  # Desnecessário no Codex

# Instalação opcional do Playwright/Chromium
if [ "$SKIP_PLAYWRIGHT" = "false" ]; then
  echo ">>> Instalando o browser Chromium para o Playwright..."
  npx playwright install --with-deps chromium < /dev/null \
    && echo "✅ Chromium instalado." \
    || { echo "❌ Falha na instalação do Chromium"; exit 1; }
else
  echo "⚠️ SKIP_PLAYWRIGHT=true — pulando instalação do Chromium."
fi

echo "✅ Etapas concluídas com sucesso:"
echo "  - Dependências do sistema instaladas"
echo "  - Ambiente virtual criado e ativado"
echo "  - Dependências Python instaladas"
echo "  - Ganchos de pre-commit configurados"
echo "  - Docker instalado"
echo "  - Chromium instalado (se aplicável)"