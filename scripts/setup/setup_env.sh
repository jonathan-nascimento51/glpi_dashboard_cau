#!/bin/bash
set -euo pipefail

# Se você tiver um arquivo com os certificados corporativos:
export REQUESTS_CA_BUNDLE=$(python -m certifi)
export NODE_EXTRA_CA_CERTS=$(python -m certifi)

# Caso necessário, você pode desabilitar temporariamente a verificação de certificados (não recomendado para produção)
export PYTHONHTTPSVERIFY=0

if [ "$(id -u)" -eq 0 ] && [ -n "${SUDO_USER-}" ]; then
    echo -e "\033[0;31mERROR: Este script não deve ser executado com 'sudo'. Ele solicitará a senha quando necessário.\033[0m" >&2
    echo -e "\033[0;31mPor favor, execute como o seu usuário normal: ./scripts/setup/setup_env.sh\033[0m" >&2
    exit 1
fi

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

# Variáveis globais
PROXY_FILE=/etc/apt/apt.conf.d/01proxy

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

setup_system_dependencies() {
    # Variáveis de ambiente com valores padrão
    SKIP_PLAYWRIGHT=${SKIP_PLAYWRIGHT:-true}
    OFFLINE_INSTALL=${OFFLINE_INSTALL:-false}
    INSECURE_TLS=${INSECURE_TLS:-false}

    # Local cache for Playwright browsers (override via PLAYWRIGHT_BROWSERS_PATH)
    PLAYWRIGHT_CACHE_DIR="${PLAYWRIGHT_BROWSERS_PATH:-$HOME/.cache/ms-playwright}"
    export PLAYWRIGHT_BROWSERS_PATH="$PLAYWRIGHT_CACHE_DIR"
    mkdir -p "$PLAYWRIGHT_CACHE_DIR"

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

    # Determina o pacote ALSA correto para a distribuição, usando um método mais robusto.
    local alsa_package="libasound2"
    # Em sistemas como Ubuntu 24.04 (Noble), pacotes foram renomeados com o sufixo 't64'.
    # Verificamos a versão do SO para usar o nome de pacote correto.
    if command -v lsb_release >/dev/null 2>&1 && [ "$(lsb_release -cs)" = "noble" ]; then
        info "Ubuntu Noble detectado. Usando 'libasound2t64'."
        alsa_package="libasound2t64"
    elif apt-cache show libasound2t64 >/dev/null 2>&1; then
        # Fallback para o método anterior caso lsb_release não funcione ou não seja Noble
        info "Distribuição usa 'libasound2t64' (detectado via apt-cache)."
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
        curl https://mise.run | sh

        # Adiciona o mise ao PATH da sessão atual para que possa ser encontrado
        export PATH="$HOME/.local/bin:$PATH"
    fi
    # Ativa o mise para a sessão atual do script, garantindo que o PATH seja modificado
    # para usar as versões de ferramentas corretas (node, python, etc.).
    eval "$(mise activate bash)"
    warn "Mise foi instalado/ativado. Para uso permanente, reinicie seu shell ou execute 'source ~/.bashrc'."

    info "Confiando no arquivo de configuração do mise para evitar prompts interativos..."
    mise trust

    mise install

    # Silencia o aviso de depreciação sobre arquivos de versão idiomáticos
    mise settings set idiomatic_version_file_enable_tools node
}

setup_python_env() {
    info "(4/7) Configurando ambiente Python..."
    eval "$(mise activate bash)" # Garante que o python do mise está no PATH

    local venv_dir=".venv"
    if [ ! -d "$venv_dir" ]; then
        info "Criando ambiente virtual em $venv_dir..."
        python -m venv "$venv_dir"
    fi

    info "Ativando o ambiente virtual..."
    # shellcheck disable=SC1091
    source "$venv_dir/bin/activate"

    info "Atualizando pip e instalando dependências Python..."
    export PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1
    pip install --upgrade pip
    if [ "$OFFLINE_INSTALL" = "true" ]; then
        local wheel_dir
        wheel_dir=${WHEELS_DIR:-./wheels}
        pip install --no-index --find-links="$wheel_dir" -r requirements.txt -r requirements-dev.txt
    else
        pip install --trusted-host github.com -r requirements.txt -r requirements-dev.txt
        pip install -e .[dev]
    fi
    unset PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD

    # Corrige permissões do venv e egg-info se foram criados com sudo
    local owner_user="${SUDO_USER:-$(whoami)}"
    if [ -d "$venv_dir" ] && [ "$(stat -c '%U' "$venv_dir")" = "root" ]; then
        warn "O diretório .venv e/ou .egg-info pertencem ao root. Corrigindo permissões..."
        # O glob `src/*.egg-info` pode não expandir se não houver correspondência, então usamos find
        sudo chown -R "$owner_user":"$(id -g "$owner_user")" "$venv_dir"
        find src -maxdepth 1 -type d -name "*.egg-info" -exec sudo chown -R "$owner_user":"$(id -g "$owner_user")" {} +
    fi
}

setup_node_env() {
    info "(5/7) Instalando dependências do frontend..."
    eval "$(mise activate bash)" # Garante que o node/npm do mise está no PATH

    local frontend_dir="src/frontend/react_app"
    local node_modules_dir="$frontend_dir/node_modules"

    # Corrige problemas de permissão se node_modules foi criado com sudo
    if [ -d "$node_modules_dir" ]; then
        if [ "$(stat -c '%U' "$node_modules_dir")" = "root" ]; then
            warn "O diretório node_modules pertence ao root. Corrigindo permissões..."
            sudo chown -R "${SUDO_USER:-$(whoami)}":"$(id -g "${SUDO_USER:-$(whoami)}")" "$frontend_dir"
        fi
    fi

    (
        cd "$frontend_dir"
        info "Instalando dependências do package.json..."
        npm install --legacy-peer-deps
        info "Garantindo que as definições de tipo do React estão instaladas..."
        npm install --save-dev @types/react @types/react-dom
    )
}

setup_git_hooks() {
    info "(6/7) Instalando ganchos de pre-commit..."
    if command -v pre-commit >/dev/null 2>&1; then
        pre-commit install
    else
        warn "pre-commit não encontrado. Instalando..."
        pip install pre-commit && pre-commit install
    fi
}

setup_playwright() {
    if [ "$SKIP_PLAYWRIGHT" = "false" ]; then
        info "(7/7) Instalando o browser Chromium para o Playwright..."
        if [ "$INSECURE_TLS" = "true" ]; then
            export NODE_TLS_REJECT_UNAUTHORIZED=0 # Cuidado: desativa a verificação de certificado TLS
        fi

        info "Instalando dependências do Playwright via npm..."
        (cd src/frontend/react_app && npm install @playwright/test)
        info "Instalando o browser Chromium para o Playwright..."
        (cd src/frontend/react_app && npx playwright install --with-deps chromium < /dev/null) || {
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
