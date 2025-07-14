#!/bin/bash
set -euo pipefail

# Abort early on non-Linux systems
OS_TYPE="${OSTYPE:-$(uname -s)}"
case "$OS_TYPE" in
  linux*|Linux*) ;;
  *)
    echo "This setup script only supports Linux. Follow the manual steps in docs/run_local.md" >&2
    exit 1
    ;;
esac

SKIP_PLAYWRIGHT=${SKIP_PLAYWRIGHT:-true}
OFFLINE_INSTALL=${OFFLINE_INSTALL:-false}
PROXY_FILE=/etc/apt/apt.conf.d/01proxy

# Local cache for Playwright browsers (override via PLAYWRIGHT_BROWSERS_PATH)
PLAYWRIGHT_CACHE_DIR="${PLAYWRIGHT_BROWSERS_PATH:-$HOME/.cache/ms-playwright}"
export PLAYWRIGHT_BROWSERS_PATH="$PLAYWRIGHT_CACHE_DIR"
mkdir -p "$PLAYWRIGHT_CACHE_DIR"

echo ">>> Verificando acesso à internet..."
if curl -Is https://pypi.org/simple --max-time 5 >/dev/null 2>&1; then
  echo "✅ Conexão com a internet detectada"
else
  echo "⚠️ Sem acesso à internet. Configure HTTP_PROXY/HTTPS_PROXY ou use ./wheels para instalação offline"
fi

if [ -n "${HTTP_PROXY:-}" ]; then
  echo "Acquire::http::Proxy \"${HTTP_PROXY}\";" | sudo tee "$PROXY_FILE" >/dev/null
  echo "Acquire::https::Proxy \"${HTTPS_PROXY:-$HTTP_PROXY}\";" | sudo tee -a "$PROXY_FILE" >/dev/null
  echo "Proxy configurado em $PROXY_FILE"
  echo "Configurando proxy para npm..."
  npm config set proxy "${HTTP_PROXY}"
  npm config set https-proxy "${HTTPS_PROXY:-$HTTP_PROXY}"
fi

echo ">>> (1/6) Instalando dependências do sistema para o Playwright..."
sudo apt-get update -y
sudo apt-get install -y \
    curl ca-certificates libnss3 libnspr4 libatk1.0-0t64 libatk-bridge2.0-0t64 libcups2t64 \
    libdbus-1-3 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 \
    libgbm1 libpango-1.0-0 libcairo2 libasound2t64 libatspi2.0-0t64 libgtk-3-0t64 \
    libx11-xcb1 libxshmfence1 xvfb fonts-liberation libxslt1.1 libwoff1 \
    libharfbuzz-icu0 libvpx9 libavif16 libwebpdemux2 libenchant-2-2 libsecret-1-0 \
    libhyphen0 libgles2 libgstreamer1.0-0 gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good gstreamer1.0-libav unzip

VENV_DIR=".venv"
if [ ! -d "$VENV_DIR" ]; then
  echo ">>> (2/6) Criando ambiente virtual em $VENV_DIR..."
  python3 -m venv "$VENV_DIR"
fi

echo ">>> (3/6) Ativando o ambiente virtual..."
# shellcheck disable=SC1090
source "$VENV_DIR/bin/activate"

echo ">>> (4/6) Atualizando pip e instalando dependências Python..."
export PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1
pip install --upgrade pip
if [ "$OFFLINE_INSTALL" = "true" ]; then
  WHEEL_DIR=${WHEELS_DIR:-./wheels}
  pip install --no-index --find-links="$WHEEL_DIR" -r requirements.txt -r requirements-dev.txt
else
  pip install -r requirements.txt -r requirements-dev.txt
fi
pip install -e . pytest pytest-cov aiohttp
unset PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD

echo ">>> (5/6) Instalando ganchos de pre-commit..."
if command -v pre-commit >/dev/null 2>&1; then
  pre-commit install
else
  echo "⚠️ pre-commit não encontrado. Instalando..."
  pip install pre-commit && pre-commit install
fi

# Instalação opcional do Playwright/Chromium
if [ "$SKIP_PLAYWRIGHT" = "false" ]; then
  echo ">>> Instalando o browser Chromium para o Playwright..."
  export NODE_TLS_REJECT_UNAUTHORIZED=0 # Cuidado: desativa a verificação de certificado TLS

  npm install @playwright/test
  npx playwright@1.54.0 install --with-deps chromium < /dev/null || {
    echo "⚠️ Playwright falhou. Tentando download manual via curl..."
    curl -L https://playwright.azureedge.net/builds/chromium/1181/chromium-linux.zip -o chromium.zip \
      && unzip -q chromium.zip -d "$PLAYWRIGHT_CACHE_DIR" \
      && rm -f chromium.zip \
      && echo "✅ Chromium extraído manualmente em $PLAYWRIGHT_CACHE_DIR"
  }
  CHROME_PATH="$(find "$PLAYWRIGHT_CACHE_DIR" -type f -path '*chrome-linux/chrome' -print -quit 2>/dev/null || true)"
  if [ -x "$CHROME_PATH" ]; then
    echo "✅ Browser encontrado em $CHROME_PATH"
  else
    echo "❌ Browser não encontrado após instalação." >&2
    exit 1
  fi
else
  echo "⚠️ SKIP_PLAYWRIGHT=true — pulando instalação do Chromium."
fi

echo "✅ Etapas concluídas com sucesso!"
