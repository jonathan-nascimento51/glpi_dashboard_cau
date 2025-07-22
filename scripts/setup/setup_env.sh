#!/bin/bash
set -euo pipefail

# --- Configuração e Funções Auxiliares ---

# Cores para logs
readonly C_RESET='\033[0m'
readonly C_RED='\033[0;31m'
readonly C_GREEN='\033[0;32m'
readonly C_YELLOW='\033[0;33m'
readonly C_BLUE='\033[0;34m'

# Funções de log
info() { echo -e "${C_BLUE}INFO: $1${C_RESET}"; }
warn() { echo -e "${C_YELLOW}WARN: $1${C_RESET}"; }
error() { echo -e "${C_RED}ERROR: $1${C_RESET}" >&2; }
success() { echo -e "${C_GREEN}✅ $1${C_RESET}"; }

# Verifica se o script está sendo executado como root
if [ "$EUID" -ne 0 ]; then
  error "Este script precisa ser executado com sudo. Use: sudo ./setup.sh"
  exit 1
fi

cleanup() {
  info "Executando limpeza..."
  if [ -f "$PROXY_FILE" ]; then
    info "Removendo configuração de proxy temporária..."
    if sudo -n true 2>/dev/null; then
      sudo rm -f "$PROXY_FILE"
      success "Arquivo de proxy removido com sucesso."
    else
      warn "sudo requer senha. Pulei a remoção de $PROXY_FILE"
    fi
    npm config delete proxy >/dev/null 2>&1 || true
    npm config delete https-proxy >/dev/null 2>&1 || true
  fi
}

check_os() {
  # Abort early on non-Linux systems
  local os_type
  os_type="${OSTYPE:-$(uname -s)}"
  case "$os_type" in
    linux*|Linux*) ;;
    *)
      error "Este script de setup suporta apenas Linux. Siga os passos manuais em docs/run_local.md"
      exit 1
      ;;
  esac
}

check_command() {
  command -v "$1" >/dev/null 2>&1 || { error "Comando '$1' não encontrado. Por favor, instale-o."; exit 1; }
}

# Variáveis de ambiente com valores padrão
SKIP_PLAYWRIGHT=${SKIP_PLAYWRIGHT:-true}
OFFLINE_INSTALL=${OFFLINE_INSTALL:-false}
INSECURE_TLS=${INSECURE_TLS:-false}
PROXY_FILE=/etc/apt/apt.conf.d/01proxy

# Local cache for Playwright browsers (override via PLAYWRIGHT_BROWSERS_PATH)
PLAYWRIGHT_CACHE_DIR="${PLAYWRIGHT_BROWSERS_PATH:-$HOME/.cache/ms-playwright}"
export PLAYWRIGHT_BROWSERS_PATH="$PLAYWRIGHT_CACHE_DIR"
mkdir -p "$PLAYWRIGHT_CACHE_DIR"

setup_system_dependencies() {
  info "(1/7) Verificando acesso à internet..."
  if curl -Is https://pypi.org/simple --max-time 5 >/dev/null 2>&1; then
    success "Conexão com a internet detectada"
  else
    warn "Sem acesso à internet. Configure HTTP_PROXY/HTTPS_PROXY ou use ./wheels para instalação offline"
  fi

  if [ -n "${HTTP_PROXY:-}" ]; then
    info "Configurando proxy para apt e npm..."
    echo "Acquire::http::Proxy \"${HTTP_PROXY}\";" | sudo tee "$PROXY_FILE" >/dev/null
    echo "Acquire::https::Proxy \"${HTTPS_PROXY:-$HTTP_PROXY}\";" | sudo tee -a "$PROXY_FILE" >/dev/null
    npm config set proxy "${HTTP_PROXY}"
    npm config set https-proxy "${HTTPS_PROXY:-$HTTP_PROXY}"
  fi

  # Determina o pacote ALSA correto para a distribuição
  local alsa_package="libasound2"
  if apt-cache show libasound2t64 >/dev/null 2>&1; then
    info "Distribuição usa 'libasound2t64'."
    alsa_package="libasound2t64"
  else
    info "Distribuição usa 'libasound2'."
  fi

  info "(2/7) Instalando dependências do sistema para o Playwright..."
  sudo apt-get update -y
  sudo apt-get install -y --no-install-recommends \
      curl ca-certificates libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2 \
      libdbus-1-3 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 \
      libgbm1 libpango-1.0-0 libcairo2 "${alsa_package}" libatspi2.0-0 libgtk-3-0 \
      libx11-xcb1 libxshmfence1 xvfb fonts-liberation libxslt1.1 libwoff1 \
      libharfbuzz-icu0 libwebpdemux2 libenchant-2-2 libsecret-1-0 \
      libhyphen0 libgles2 libgstreamer1.0-0 gstreamer1.0-plugins-base \
      gstreamer1.0-plugins-good gstreamer1.0-libav unzip
}

setup_mise() {
  info "(3/7) Instalando versões de ferramentas com mise..."
  if ! command -v mise >/dev/null 2>&1; then
    warn "Comando 'mise' não encontrado. Instalando..."
    local mise_script="/tmp/mise_install.sh"
    info "Baixando o script de instalação do mise..."
    sudo -u "${SUDO_USER:-$(whoami)}" curl -fsSL -o "$mise_script" https://mise.run
    if [ ! -f "$mise_script" ]; then
        error "Falha ao baixar o script de instalação do mise."
        exit 1
    fi
    info "Executando o script de instalação do mise..."
    sudo -u "${SUDO_USER:-$(whoami)}" sh "$mise_script"
    rm -f "$mise_script"
    # Adiciona o mise ao PATH da sessão atual para que possa ser encontrado
    export PATH="$HOME/.local/bin:$PATH"
  fi
  # Ativa o mise para a sessão atual do script, garantindo que o PATH seja modificado
  # para usar as versões de ferramentas corretas (node, python, etc.).
  eval "$(mise activate bash)"
  warn "Mise foi instalado/ativado. Para uso permanente, reinicie seu shell ou execute 'source ~/.bashrc'."

  sudo -u "${SUDO_USER:-$(whoami)}" mise install
  sudo -u "${SUDO_USER:-$(whoami)}" mise trust --yes .
  # Silencia o aviso de depreciação sobre arquivos de versão idiomáticos
  sudo -u "${SUDO_USER:-$(whoami)}" mise settings set idiomatic_version_file_enable_tools node
}

setup_python_env() {
  info "(4/7) Configurando ambiente Python..."
  eval "$(mise activate bash)" # Garante que o python do mise está no PATH

  local venv_dir=".venv"
  if [ ! -d "$venv_dir" ]; then
    info "Criando ambiente virtual em $venv_dir..."
    sudo -u "${SUDO_USER:-$(whoami)}" python -m venv "$venv_dir"
  fi

  info "Atualizando pip e instalando dependências Python..."
sudo -u "${SUDO_USER:-$(whoami)}" bash - <<EOF
source ".venv/bin/activate"
export PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1
pip install --upgrade pip
if [ "$OFFLINE_INSTALL" = "true" ]; then
  wheel_dir=${WHEELS_DIR:-./wheels}
  pip install --no-index --find-links="$wheel_dir" -r requirements.txt -r requirements-dev.txt
else
  pip install -r requirements.txt
  pip install -e .[dev]
fi
unset PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD
EOF

  # Permissões corretas pois comandos rodam como usuário
}

setup_node_env() {
    info "(5/7) Instalando dependências do frontend..."
    eval "$(mise activate bash)" # Garante que o node/npm do mise está no PATH

    local frontend_dir="src/frontend/react_app"
    local node_modules_dir="$frontend_dir/node_modules"

info "Instalando dependências do package.json..."
info "Garantindo que as definições de tipo do React estão instaladas..."
sudo -u "${SUDO_USER:-$(whoami)}" bash - <<EOF
cd "$frontend_dir"
npm install --legacy-peer-deps
npm install --save-dev @types/react @types/react-dom
EOF
}

setup_git_hooks() {
  info "(6/7) Instalando ganchos de pre-commit..."
  if command -v pre-commit >/dev/null 2>&1; then
    sudo -u "${SUDO_USER:-$(whoami)}" pre-commit install
  else
    warn "pre-commit não encontrado. Instalando..."
    sudo -u "${SUDO_USER:-$(whoami)}" pip install pre-commit && \
    sudo -u "${SUDO_USER:-$(whoami)}" pre-commit install
  fi
}

setup_playwright() {
  if [ "$SKIP_PLAYWRIGHT" = "false" ]; then
    info "(7/7) Instalando o browser Chromium para o Playwright..."
    if [ "$INSECURE_TLS" = "true" ]; then
      export NODE_TLS_REJECT_UNAUTHORIZED=0 # Cuidado: desativa a verificação de certificado TLS
    fi

    info "Instalando dependências do Playwright via npm..."
    sudo -u "${SUDO_USER:-$(whoami)}" bash -c 'cd src/frontend/react_app && npm install @playwright/test'
    info "Instalando o browser Chromium para o Playwright..."
    sudo -u "${SUDO_USER:-$(whoami)}" bash -c 'cd src/frontend/react_app && npx playwright install --with-deps chromium < /dev/null' || {
      warn "Playwright falhou. Tentando download manual via curl..."
      curl -L https://playwright.azureedge.net/builds/chromium/1181/chromium-linux.zip -o chromium.zip \
        && unzip -q chromium.zip -d "$PLAYWRIGHT_CACHE_DIR" \
        && rm -f chromium.zip \
        && success "Chromium baixado e extraído manualmente em $PLAYWRIGHT_CACHE_DIR"
    }
    local chrome_path
    chrome_path="$(find "$PLAYWRIGHT_CACHE_DIR" -type f -path '*chrome-linux/chrome' -print -quit 2>/dev/null || true)"
    if [ -x "$chrome_path" ]; then
      success "Browser encontrado em $chrome_path"
    else
      error "Browser não encontrado após instalação."
      exit 1
    fi
  else
    info "(7/7) SKIP_PLAYWRIGHT=true — pulando instalação do Chromium."
  fi
}

main() {
  trap cleanup EXIT

  check_os
  check_command "curl"
  check_command "sudo"

  setup_system_dependencies
  setup_mise
  setup_python_env
  setup_node_env
  setup_git_hooks
  setup_playwright

  success "Setup concluído com sucesso!"
  info "Para ativar o ambiente, execute: source .venv/bin/activate"
}

main "$@"
