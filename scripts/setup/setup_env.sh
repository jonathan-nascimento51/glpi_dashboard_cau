#!/bin/bash
set -euo pipefail
trap 'error "Erro na linha $LINENO. Comando: $BASH_COMMAND"' ERR

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

# Determina o usuário original que invocou o sudo e seu diretório home
readonly OWNER_USER="${SUDO_USER:-$(whoami)}"
readonly OWNER_HOME="/home/${OWNER_USER}"
readonly MISE_PATH="${OWNER_HOME}/.local/bin/mise"

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
    sudo -u "$OWNER_USER" npm config delete proxy >/dev/null 2>&1 || true
    sudo -u "$OWNER_USER" npm config delete https-proxy >/dev/null 2>&1 || true
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
PLAYWRIGHT_CACHE_DIR="${PLAYWRIGHT_BROWSERS_PATH:-${OWNER_HOME}/.cache/ms-playwright}"
export PLAYWRIGHT_BROWSERS_PATH="$PLAYWRIGHT_CACHE_DIR"
sudo -u "$OWNER_USER" mkdir -p "$PLAYWRIGHT_CACHE_DIR"

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
    sudo -u "$OWNER_USER" npm config set proxy "${HTTP_PROXY}"
    sudo -u "$OWNER_USER" npm config set https-proxy "${HTTPS_PROXY:-$HTTP_PROXY}"
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

  if ! command -v mise &> /dev/null; then
    if [ ! -f "$MISE_PATH" ]; then
      warn "Comando 'mise' não encontrado. Instalando para o usuário $OWNER_USER..."
      sudo -u "$OWNER_USER" curl https://mise.run | sudo -u "$OWNER_USER" sh
    fi
    # Adiciona mise ao PATH da sessão atual do script
    export PATH="${OWNER_HOME}/.local/bin:$PATH"
  fi

  # Verifica se mise foi instalado corretamente
  if ! command -v mise &> /dev/null; then
    error "Falha na instalação ou ativação do mise. Verifique o PATH."
    exit 1
  fi

  info "Instalando ferramentas definidas no .tool-versions..."
  sudo -u "$OWNER_USER" "$MISE_PATH" install
  info "Confiando na configuração do mise para este projeto..."
  sudo -u "$OWNER_USER" "$MISE_PATH" trust --yes .
}

setup_python_env() {
  info "(4/7) Configurando ambiente Python..."
  eval "$("$MISE_PATH" activate bash)"

  local venv_dir=".venv"
  # Remover venv existente para garantir um ambiente limpo
  if [ -d "$venv_dir" ]; then
    info "Removendo ambiente virtual antigo para garantir um estado limpo..."
    rm -rf "$venv_dir"
  fi

  # Remove .egg-info directories from previous failed runs to prevent permission errors
  info "Limpando metadados de pacotes antigos (.egg-info)..."
  rm -rf src/*.egg-info

  info "Criando novo ambiente virtual em $venv_dir como usuário $OWNER_USER..."
  sudo -u "$OWNER_USER" python3 -m venv "$venv_dir"

  info "Atualizando pip e instalando dependências Python como usuário $OWNER_USER..."
  export PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1

  # Executa os comandos pip como o usuário proprietário, usando o pip do venv
  local pip_cmd="${venv_dir}/bin/pip"
  sudo -u "$OWNER_USER" "$pip_cmd" install --upgrade pip
  if [ "$OFFLINE_INSTALL" = "true" ]; then
    local wheel_dir=${WHEELS_DIR:-./wheels}
    info "Instalando dependências de produção e desenvolvimento do cache local..."
    sudo -u "$OWNER_USER" "$pip_cmd" install --no-index --find-links="$wheel_dir" -r requirements.txt -r requirements-dev.txt -e .[dev]
  else
    info "Instalando dependências de produção e desenvolvimento..."
    # Instala dependências de produção, de desenvolvimento (incluindo pre-commit) e o pacote local em modo editável.
    sudo -u "$OWNER_USER" "$pip_cmd" install -r requirements.txt -r requirements-dev.txt -e .[dev]
  fi
  unset PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD
}

setup_node_env() {
    info "(5/7) Instalando dependências do frontend..."
    eval "$("$MISE_PATH" activate bash)"

    local frontend_dir="src/frontend/react_app"

    if [ ! -d "$frontend_dir" ]; then
        error "Diretório $frontend_dir não encontrado!"
        exit 1
    fi

    # Remove node_modules to ensure a clean install and prevent permission issues
    if [ -d "$frontend_dir/node_modules" ]; then
        info "Removendo node_modules antigo para garantir um estado limpo..."
        rm -rf "$frontend_dir/node_modules"
    fi

    info "Executando 'npm install' como usuário $OWNER_USER..."
    (cd "$frontend_dir" && sudo -u "$OWNER_USER" "$MISE_PATH" exec -- npm install --legacy-peer-deps)
}

setup_git_hooks() {
  info "(6/7) Instalando ganchos de pre-commit..."
  local venv_pre_commit=".venv/bin/pre-commit"
  if [ ! -f "$venv_pre_commit" ]; then
    error "pre-commit não encontrado em .venv/bin/. A instalação do Python falhou?"
    exit 1
  fi
  sudo -u "$OWNER_USER" "$venv_pre_commit" install
}

setup_playwright() {
  if [ "$SKIP_PLAYWRIGHT" = "false" ]; then
    info "(7/7) Instalando o browser Chromium para o Playwright..."
    if [ "$INSECURE_TLS" = "true" ]; then
      export NODE_TLS_REJECT_UNAUTHORIZED=0 # Cuidado: desativa a verificação de certificado TLS
    fi

    info "Instalando dependências do Playwright via npm..."
    (cd src/frontend/react_app && sudo -u "$OWNER_USER" "$MISE_PATH" exec -- npm install @playwright/test)
    info "Instalando o browser Chromium para o Playwright..."
    (cd src/frontend/react_app && sudo -u "$OWNER_USER" "$MISE_PATH" exec -- npx playwright install --with-deps chromium < /dev/null) || {
      warn "Playwright falhou. Tentando download manual via curl..."
      sudo -u "$OWNER_USER" curl -L https://playwright.azureedge.net/builds/chromium/1181/chromium-linux.zip -o chromium.zip \
        && sudo -u "$OWNER_USER" unzip -q chromium.zip -d "$PLAYWRIGHT_CACHE_DIR" \
        && sudo -u "$OWNER_USER" rm -f chromium.zip \
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
