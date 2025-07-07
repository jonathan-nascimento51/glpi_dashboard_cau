FROM node:20-alpine

ENV NPM_CONFIG_CACHE=/root/.npm

WORKDIR /app

# 1) Copia package.json + lockfile
COPY package.json package-lock.json* ./

# 2) Copia o .npmrc renomeado
COPY .npmrc ./

# 3) Instala dependências usando as flags do .npmrc
RUN --mount=type=cache,target=/root/.npm \
    npm ci --omit=dev   # ou --production

# 4) Copia o restante do código e executa build/dev
COPY . .
EXPOSE 3000
CMD ["npm", "run", "dev"]
