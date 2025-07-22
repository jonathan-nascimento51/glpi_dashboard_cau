# Stage 1: Build da aplicação React
FROM node:20.19.0-alpine AS builder

WORKDIR /app
ENV NPM_CONFIG_CACHE=/root/.npm

# Argumento de build para a URL da API, que será injetado no build estático.
ARG NEXT_PUBLIC_API_BASE_URL
ENV NEXT_PUBLIC_API_BASE_URL=$NEXT_PUBLIC_API_BASE_URL

# Copia os arquivos de dependência e instala
COPY src/frontend/react_app/package.json src/frontend/react_app/package-lock.json* ./
RUN npm install --legacy-peer-deps

# Copia o restante do código-fonte do frontend
COPY src/frontend/react_app/ ./

# Executa o build da aplicação para produção
RUN npm run build

# Stage 2: Ambiente de desenvolvimento
FROM node:20.19.0-alpine AS dev

WORKDIR /app
ENV NPM_CONFIG_CACHE=/root/.npm

# Copia os arquivos de dependência e instala
COPY src/frontend/react_app/package.json src/frontend/react_app/package-lock.json* ./
RUN npm install --legacy-peer-deps

# Copia o restante do código-fonte do frontend
COPY src/frontend/react_app/ ./

# Comando para iniciar o ambiente de desenvolvimento
CMD ["npm", "run", "dev"]

# Stage 3: Cria a imagem final com Nginx para produção
FROM nginx:1.25-alpine AS prod

# Instala curl para o healthcheck
RUN apk add --no-cache curl

# Copia os arquivos estáticos gerados no stage de build
COPY --from=builder /app/dist /usr/share/nginx/html

# Copia a configuração customizada do Nginx para lidar com SPA
COPY ./src/frontend/react_app/nginx.conf /etc/nginx/conf.d/default.conf

# Expõe a porta 80, que é a porta padrão do Nginx
EXPOSE 80

# Healthcheck para verificar se o Nginx está respondendo
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost/ || exit 1

# Comando para iniciar o Nginx em modo foreground
CMD ["nginx", "-g", "daemon off;"]
