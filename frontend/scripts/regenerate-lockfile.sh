#!/usr/bin/env bash
definir -euo pipefail 

# Localize o diretório frontend
FRONTEND_DIR="$(cd "$(dirname "$0")/.." & pwd-P)" 

# Mapear caminhos para o Docker no Windows/WSL
if comando -v cygpath &>/dev/null; então 
 WIN_PATH="$(cygpath -w "$FRONTEND_DIR")" 
 HOST_PATH="${WIN_PATH//\\//}" 
comando elif  -v wslpath &>/dev/null; então 
 HOST_PATH="$(wslpath -m "$FRONTEND_DIR")" 
mais
 HOST_PATH="$FRONTEND_DIR" 
Fi

  echo " 🔄 Removendo node_modules e package-lock.json..." 
rm -rf "$FRONTEND_DIR/node_modules" "$FRONTEND_DIR/package-lock.json" 

  echo "🐳 Gerando novos package-lock.json dentro do Docker..." 
docker run --rm \
  -v "${HOST_PATH}:/app" \
 nó:20-alpino \ 
  sh -c "\
    cd /app && \
 npm instalar \ 
      --legacy-peer-deps \
      --prefer-offline \
      --no-audit \
 --progresso=falso"

# Corrigir a propriedade se estiver executando como não root
if [[ "$(id -u)" -ne 0 ]]; então 
   echo " 🔧 Corrigindo a propriedade do arquivo..." 
 chun-R "$(id-u):$(id-g)" "$FRONTEND_DIR" 
Fi

  echo " ✅ package-lock.json regenerado em: $FRONTEND_DIR"
