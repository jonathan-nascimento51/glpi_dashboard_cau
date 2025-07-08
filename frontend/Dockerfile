FROM node:20-slim
RUN npm install -g npm@latest
ENV NPM_CONFIG_CACHE=/root/.npm

WORKDIR /app

# 1) Copia package.json + lockfile
COPY package.json package-lock.json* ./

# 2) Copia o .npmrc renomeado
COPY .npmrc ./

# 2) Usa npm install em vez de ci para garantir optionalDependencies
ARG INSTALL_DEV_DEPS=false
# Se INSTALL_DEV_DEPS for true, instala dependências de desenvolvimento
# Caso contrário, instala apenas as dependências de produção
RUN --mount=type=cache,target=/root/.npm \
    if [ "$INSTALL_DEV_DEPS" = "true" ]; then \
      npm install; \
    else \
      npm install --omit=dev; \
    fi
RUN npm rebuild esbuild --update-binary
RUN npm rebuild lightningcss --update-binary

# 4) Copia o restante do código e executa build/dev
COPY . .
EXPOSE 3000
CMD ["npm", "run", "dev"]
