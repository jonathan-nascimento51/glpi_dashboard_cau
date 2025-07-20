# Instruções para o GitHub Copilot

Este é um projeto full-stack com um backend em Python (FastAPI) e um frontend em React (TypeScript), projetado para ser executado com Docker Compose.

## Práticas Gerais e Arquitetura

- **Gerenciamento de Versões**: As versões do Node.js e Python são gerenciadas pelo **`mise`** (via arquivo `.tool-versions`). Sempre use `mise` para instalar e ativar as versões corretas.
- **Execução do Projeto**: A forma principal de executar a aplicação é com **`docker-compose up`**.
- **Scripts**: Utilize os comandos definidos no `Makefile` para tarefas comuns (ex: `make setup`, `make test`, `make lint`).
- **Mensagens de Commit**: Siga o padrão **Conventional Commits** (ex: `feat:`, `fix:`, `docs:`, `refactor:`).
- **Variáveis de Ambiente**: As configurações são gerenciadas através de arquivos `.env`, a partir do `.env.example`.

## Backend (Python)

- **Framework**: Use **FastAPI** para criar endpoints da API, seguindo as melhores práticas para código `async`.
- **Modelagem de Dados**: Use **Pydantic** para definir modelos de dados, validação e configurações.
- **Sincronização de Tipos (Backend -> Frontend)**: Modelos Pydantic que precisam ser expostos ao frontend devem ser definidos em `src/backend/models/ts_models.py`. Após qualquer alteração, execute `make gen-types` para atualizar as interfaces TypeScript correspondentes.
- **Banco de Dados**: O projeto utiliza **PostgreSQL**.
- **Modelagem de Dados**: Use **Pydantic** para definir modelos de dados, validação e configurações.
- **Requisições HTTP**: Para chamadas a APIs externas (como a do GLPI), utilize a biblioteca `aiohttp` de forma assíncrona.
- **Estilo de Código**: O código Python segue estritamente os formatadores **`black`**, **`isort`** e o linter **`ruff`**, aplicados via `pre-commit`.
- **Testes**: Escreva testes unitários e de integração usando **`pytest`**. Utilize fixtures para setup e mocks (`unittest.mock`) para isolar dependências.

## Frontend (React + TypeScript)

- **Build Tool**: O ambiente de desenvolvimento e build é gerenciado pelo **`vite`**.
- **Requisições à API**: Gerencie o estado do servidor e as chamadas à API com **`@tanstack/react-query`** (usando os hooks `useQuery` e `useMutation`). Não utilize `axios` ou `fetch` diretamente nos componentes.
- **Gerenciamento de Estado Global**: Para estado global do lado do cliente, utilize **`zustand`**.
- **Componentes e Estilo**: Crie componentes funcionais com Hooks. A estilização é feita com **Tailwind CSS**.
- **Gráficos**: Para visualização de dados, utilize a biblioteca **`recharts`**.
- **Testes**: Escreva testes unitários e de componentes com **`jest`** e **`@testing-library/react`**.
