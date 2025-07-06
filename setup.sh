#!/bin/bash
# Script final e autônomo para configurar o ambiente de desenvolvimento.
# Instala dependências de sistema, cria um venv, instala pacotes Python
# e baixa os browsers do Playwright de forma não-interativa.

# Para o script se houver algum erro
set -e

echo ">>> INICIANDO CONFIGURAÇÃO COMPLETA DO AMBIENTE <<<"

# --- 1. INSTALAÇÃO DE DEPENDÊNCIAS DO SISTEMA (CRÍTICO) ---
# O Playwright precisa destas bibliotecas para rodar os navegadores.
# O `-y` responde 'sim' para todas as perguntas do apt-get.
#
# ** VERSÃO ATUALIZADA para Ubuntu 24.04 (Noble) com pacotes 't64' **
#
echo ">>> (1/5) Instalando dependências do sistema para o Playwright..."
sudo apt-get update
sudo apt-get install -y \
    libnss3 \
    libnspr4 \
    libatk1.0-0t64 \
    libatk-bridge2.0-0t64 \
    libcups2t64 \
    libdbus-1-3 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2t64 \
    libatspi2.0-0t64 \
    libgtk-3-0t64 \
    libx11-xcb1 \
    libxshmfence1 \
    xvfb \
    fonts-liberation \
    libxslt1.1 \
    libwoff1 \
    libharfbuzz-icu0 \
    libvpx9 \
    libavif16 \
    libwebpdemux2 \
    libenchant-2-2 \
    libsecret-1-0 \
    libhyphen0 \
    libgles2 \
    libgstreamer1.0-0 \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    gstreamer1.0-libav

# --- 2. GERENCIAMENTO DO AMBIENTE VIRTUAL ---
VENV_DIR=".venv"

if [ ! -d "$VENV_DIR" ]; then
  echo ">>> (2/5) Criando ambiente virtual em $VENV_DIR..."
  python3 -m venv $VENV_DIR
fi

echo ">>> (2/5) Ativando o ambiente virtual..."
source $VENV_DIR/bin/activate

# --- 3. INSTALAÇÃO DAS DEPENDÊNCIAS PYTHON ---
echo ">>> (3/5) Atualizando o pip..."
pip install --upgrade pip

echo ">>> (3/5) Instalando dependências de produção e desenvolvimento..."
pip install -r requirements.txt -r requirements-dev.txt

echo ">>> (3/5) Instalando o pacote glpi-dashboard-cau em modo de edição..."
pip install -e .

# --- 4. CONFIGURAÇÃO DE FERRAMENTAS DE DESENVOLVIMENTO ---
echo ">>> (4/5) Instalando ganchos de pre-commit..."
pre-commit install
