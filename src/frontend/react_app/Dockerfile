# 🔧 Upgraded Node to satisfy Vite@7 engine requirements (≥20.19)
FROM node:20.19.0-alpine

WORKDIR /app
ENV NPM_CONFIG_CACHE=/root/.npm

# Instalar dependências com cache
COPY package.json package-lock.json* ./
# COPY .npmrc ./
 # Instala todas as dependências (incluindo dev para o servidor Vite)
 # e pula o download dos browsers do Playwright, que não são necessários no container.
RUN PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 npm install
RUN npm rebuild esbuild --update-binary
RUN npm rebuild lightningcss --update-binary

# Copiar código restante e iniciar servidor dev␊
COPY . .
# COPY scripts/healthchecks/healthcheck-webapp.sh /usr/local/bin/healthcheck.sh␊
# RUN chmod +x /usr/local/bin/healthcheck.sh
# EXPOSE 3000
# HEALTHCHECK \
#   --interval=30s \
#   --timeout=5s \
#   --start-period=45s \
#   --retries=3 \
#   CMD ["healthcheck.sh"]
CMD ["npm", "run", "dev"]
