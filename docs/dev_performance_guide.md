# Development Performance Guide

This document summarizes strategies to reduce the initial setup time when preparing a new development environment. The goal is to avoid the repeated cost of installing system packages and large dependencies every time a container is built from scratch.

## 1. Pre-built Base Image

Use the provided `Dockerfile` with the `INSTALL_PLAYWRIGHT` build argument set to `true` to produce a base image that already contains system dependencies, Python packages and Playwright browsers. Store this image in a registry accessible to the development team.

```bash
docker build --build-arg INSTALL_PLAYWRIGHT=true -t glpi-dashboard-base -f Dockerfile .
```

Publishing this base image allows subsequent `docker compose` runs to reuse the cached layers instead of repeating the installation process.

## 2. Cache Python Wheels

When network access is limited, download the project wheels once and reuse them:

```bash
./scripts/download_wheels.sh /tmp/wheels
```

Transfer the directory to the offline environment and install using:

```bash
pip install --no-index --find-links=/tmp/wheels -r requirements.txt -r requirements-dev.txt
```

## 3. Save Docker Images

The helper script `save_docker_images.sh` now accepts `--file` and `--output` arguments. Use it to export all images referenced by a compose file:

```bash
./scripts/save_docker_images.sh --file docker-compose.yml --output images.tar
```

Load the archive on an isolated machine with `docker load -i images.tar`.

## 4. Minimize `apt-get` Calls

Combine system package installations inside a single `RUN` layer within the Dockerfile. The current Dockerfile already consolidates packages to take advantage of build cache. Avoid repeating `apt-get update` in separate steps.

These practices help cut the environment setup time from minutes to seconds, especially when running in ephemeral CI/CD jobs or behind a corporate proxy.

## 5. Cache e Configuração Específicos da Aplicação

Use `pip install --no-cache-dir` para instalar dependências dentro do Docker. Isso permite reutilizar a camada do Docker, mas evita que arquivos temporários sejam gravados em `~/.cache/pip`.

Para builds reproduzíveis, mantenha um arquivo de lock com as versões exatas dos pacotes. Gere-o via `pip freeze` ou ferramentas como `pip-tools` e compartilhe-o no repositório.

### Gerenciando Navegadores Playwright

A imagem base criada com `INSTALL_PLAYWRIGHT=true` já embute o pacote Playwright e os navegadores padrão. Para futuras atualizações desses binários, configure o cache fora do contêiner.

Defina `PLAYWRIGHT_BROWSERS_PATH` apontando para um volume persistente ou diretório de cache do CI/CD. Dessa forma o download ocorre apenas na primeira execução, sendo reutilizado por todos os builds subsequentes.

Times que trabalham atrás de proxy podem definir `PLAYWRIGHT_DOWNLOAD_HOST` para um repositório interno (Artifactory ou Nexus), permitindo a obtenção dos navegadores sem acesso direto à internet.

### Cache Avançado em Ambientes de CI/CD

Plataformas como **GitLab CI/CD** (usando a chave `cache`), **GitHub Actions** (com a ação `actions/cache`) e outros provedores de CI/CD permitem persistir diretórios entre jobs. Configure o cache para armazenar:

- O caminho definido em `PLAYWRIGHT_BROWSERS_PATH`, evitando o download repetido dos binários do Playwright.
- Diretórios do APT como `/var/cache/apt` e `/var/lib/apt/lists`, reduzindo o tempo de `apt-get update`.

Use uma abordagem em camadas para obter melhores resultados:

1. **Camadas de imagem Docker** para dependências base e pacotes Python (`pip`).
2. **Caches de diretório do CI/CD** para artefatos externos, como os binários do Playwright.
3. **Proxies ou mirrors** para acelerar requisições de rede, por exemplo durante o `apt-get update`.

## Uma Estratégia Holística para um Ambiente Sub-Minuto

- A scheduled pipeline builds a base image with `--no-cache`, scans for vulnerabilities, tags the result, and pushes it to a private registry.
- The application pipeline uses this base image, restores the Playwright cache directory, builds the application image reusing Docker layers, and runs the job with `PLAYWRIGHT_BROWSERS_PATH` set.

By layering caches at the image and directory levels, the startup time drops from around 20 minutes to less than a minute.


### Exemplo de Dockerfile.base

A imagem base deve ser criada em um job agendado ou sempre que houver atualizacao de dependencias de sistema. Use `docker build --no-cache` para garantir que `apt-get update` traga patches de seguranca.

```Dockerfile
FROM ubuntu:22.04

# Pacotes essenciais e configuracao do Docker Engine
RUN --mount=type=cache,target=/var/cache/apt \
    apt-get update && apt-get install -y \
        ca-certificates \
        curl \
        gnupg \
        lsb-release \
        git \
        wget && \
    rm -rf /var/lib/apt/lists/* && \
    mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" > /etc/apt/sources.list.d/docker.list && \
    apt-get update && apt-get install -y docker-ce-cli docker-compose-plugin && \
    rm -rf /var/lib/apt/lists/*

# Node.js e Playwright
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g playwright && \
    playwright install --with-deps chromium
```
