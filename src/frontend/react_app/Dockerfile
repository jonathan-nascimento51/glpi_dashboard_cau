# # Use imagem oficial com navegador e deps
# FROM mcr.microsoft.com/playwright:v1.44.1-jammy

# WORKDIR /app
# ENV NPM_CONFIG_CACHE=/root/.npm

# # Instalar dependências com cache
# COPY package.json package-lock.json* ./
# # COPY .npmrc ./
# RUN npm install --omit=dev --legacy-peer-deps
# RUN npm rebuild esbuild --update-binary
# RUN npm rebuild lightningcss --update-binary

# # Copiar código restante e iniciar servidor dev
# COPY . .

# # COPY scripts/healthchecks/healthcheck-webapp.sh /usr/local/bin/healthcheck.sh
# # RUN chmod +x /usr/local/bin/healthcheck.sh
# EXPOSE 3000
# # HEALTHCHECK \
# #   --interval=30s \
# #   --timeout=5s \
# #   --start-period=45s \
# #   --retries=3 \
# #   CMD ["healthcheck.sh"]
# CMD ["npm", "run", "dev"]

ARG INSTALL_DEV_DEPS="false"
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json* ./
RUN if [ "$INSTALL_DEV_DEPS" = "true" ]; then npm install --legacy-peer-deps; else npm install --omit=dev --legacy-peer-deps; fi
COPY . .

# Só roda build se for produção
ARG INSTALL_DEV_DEPS="false"
RUN if [ "$INSTALL_DEV_DEPS" = "false" ]; then npm run build; fi

# Produção: serve build estático com nginx
FROM nginx:alpine AS prod
COPY --from=builder /app/build /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

# Desenvolvimento: roda Vite (npm run dev)
FROM node:20-alpine AS dev
WORKDIR /app
COPY --from=builder /app /app
EXPOSE 5173
CMD ["npm", "run", "dev"]
