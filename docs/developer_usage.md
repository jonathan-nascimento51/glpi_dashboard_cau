# Guia Completo de Uso para Desenvolvedores

Este documento resume todos os componentes do projeto **GLPI Dashboard CAU**, explicando como executá-los, testá-los e estender suas funcionalidades.

## Visão Geral

A aplicação coleta dados do GLPI via REST API, normaliza resultados em PostgreSQL/Redis e disponibiliza um painel interativo em Dash. Há também um serviço `worker.py` que expõe endpoints REST e GraphQL.

Principais módulos do projeto:

| Arquivo | Função |
| ------- | ------ |
| `src/backend/infrastructure/glpi/glpi_session.py` | Cliente assíncrono para autenticação e chamadas à API GLPI |
| `src/backend/application/glpi_api_client.py` | Interface de alto nível que usa `GLPISession` para obter tickets completos |
| `src/backend/infrastructure/glpi/normalization.py` | Normaliza tickets em `pandas.DataFrame` e gera JSON |
| `src/frontend/layout/layout.py` | Layout e callbacks do dashboard em Dash |
| `src/backend/services/worker_api.py` | Lógica de cache e métricas usadas pelo `worker.py` |
| `shared/config/settings.py` | Carrega variáveis de ambiente (GLPI, DB, Redis) |
| `src/frontend/react_app/` | Projeto Next.js que consome o worker API |

Os módulos da Anti-Corruption Layer residem em `src/backend/adapters`. Importe-os diretamente desse pacote. O antigo `glpi_adapter.py` foi removido durante a refatoração.

Scripts utilitários residem em `scripts/` organizados por categoria, como `setup/init_db.py`, `fetch/fetch_tickets.py` e `etl/filters.py`.

## Configuração

1. **Instalar dependências**:

   ```bash
   python -m pip install --upgrade pip
   pip install --no-cache-dir --upgrade -r requirements.txt -r requirements-dev.txt
   pip install -e .  # importa pacotes da pasta src
   pip install opentelemetry-instrumentation-fastapi opentelemetry-instrumentation-logging
   pre-commit install
   ```

2. **Criar `.env`**:

   ```bash
   python scripts/setup/setup_env.py
   ```

   Ajuste tokens GLPI, credenciais de banco e host do Redis.
   Carregue essas variáveis em seus scripts com `python-dotenv`:

   ```python
   from dotenv import load_dotenv
   load_dotenv()
   ```

3. **Inicializar banco**:

   ```bash
   make init-db
   ```

## Executando o Dashboard

Inicie o servidor Dash com:

```bash
python dashboard_app.py
```

A interface ficará disponível em <http://127.0.0.1:8050>. Use o endpoint `/ping` para verificação de saúde.

## Executando o Worker API

O serviço FastAPI roda com:

```bash
python worker.py
```

Endpoints relevantes:

- `/v1/tickets` – lista completa de chamados
 - A resposta inclui os campos `priority` e `requester` em formato textual.
- `/v1/metrics/summary` – contagem de abertos/fechados
- `/v1/graphql/` – versão GraphQL
- `/v1/cache/stats` – estatísticas de cache

Exemplo de retorno:

```json
[
  {
    "id": 7,
    "title": "Falha no proxy",
    "status": "Closed",
    "priority": "Medium",
    "requester": "Alice"
  }
]
```

## Utilizando o ETL

Para gerar um dump de tickets em JSON ou Parquet:

```bash
python scripts/fetch/fetch_tickets.py --output data/tickets.json
python -m cli.tickets_groups --since 2025-06-01 --until 2025-06-30 --outfile grupos.parquet
```

Consulte `src/backend/infrastructure/glpi/normalization.py` para transformar os dados em DataFrame.

## Atualizando a Knowledge Base

O worker lê o arquivo definido em `KNOWLEDGE_BASE_FILE` para servir erros
conhecidos. Por padrão o caminho é `docs/knowledge_base_errors.md`.

1. Edite esse arquivo adicionando novas entradas em Markdown.
2. Se mover o arquivo, ajuste `KNOWLEDGE_BASE_FILE` no `.env` ou
   `.env.example`.
3. Reinicie o `worker.py` para que o conteúdo seja recarregado.

É possível consultar o material via endpoint `GET /v1/knowledge-base`.

## Testes e Lint

Execute toda a suíte de testes com cobertura:

```bash
make test
```

Before running the tests, **install the dependencies from both** `requirements.txt` **and** `requirements-dev.txt`, then install the project in editable mode so imports resolve correctly:

```bash
pip install -r requirements.txt -r requirements-dev.txt
pip install -e .
pip install aiohttp  # required for glpi_session tests
```

The `make test` target automatically installs these requirement files before running pytest.

Rodar apenas lint:

```bash
black --check .
flake8 .
```

## Docker

A execução completa pode ser feita via Compose:

```bash
docker compose up
```

Certifique-se de que o plugin Docker Compose esteja instalado; caso
`docker compose` não esteja disponível, instale o pacote `docker-compose-plugin`
ou atualize seu Docker Engine.

Isso sobe PostgreSQL, Redis, o `worker` e o dashboard em portas 8000 e 5174.

## Estrutura de Pastas

```plaintext
├── src/
│   ├── backend/   # serviços FastAPI e integrações GLPI
│   ├── frontend/  # layout do dashboard em Dash
│   ├── frontend/react_app/  # projeto React/Next.js
│   └── shared/    # modelos e utilidades comuns
├── examples/      # códigos de referência e testes
├── tests/         # suíte pytest
├── scripts/       # utilidades de linha de comando
├── data/          # dumps temporários
└── docs/          # documentação adicional
```

Para detalhes de arquitetura e troubleshooting, consulte também:

- `docs/run_local.md`
- `docs/error_map.md`
- `docs/revisao_arquitetural_glpi_dashboard.md`
- `docs/windows_dev_setup.md`

## React Query e hooks personalizados

A dashboard React emprega [@tanstack/react-query](https://tanstack.com/query)
para cache e sincronização em segundo plano.

### QueryClientProvider

O `QueryClient` é criado em `src/frontend/react_app/src/lib/queryClient.ts` e fornecido ao
`QueryClientProvider` dentro de `src/frontend/react_app/src/main.tsx`:

```tsx
import { QueryClientProvider } from '@tanstack/react-query'
import { queryClient } from '@/lib/queryClient'

root.render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>
  </React.StrictMode>,
)
```

Altere as opções padrão do `queryClient` nesse arquivo para ajustar
`staleTime` ou `cacheTime` conforme necessário.

### Padrão de uso do `useApiQuery`

O helper `useApiQuery` padroniza chamadas ao worker API. Ele recebe uma
`queryKey`, o `endpoint` e, opcionalmente, um objeto de opções do React Query:

```ts
const { data, isLoading } = useApiQuery(['tickets'], '/v1/tickets')
```

Se precisar passar opções criadas inline, serializá-las ou extraia-as para uma
constante para evitar re-renderizações extras.

Internamente a função usa o `fetch` nativo e monta a URL com
`NEXT_PUBLIC_API_BASE_URL`.

### Exemplos de novos hooks

Crie funções que reutilizem `useApiQuery` ou `useQuery` quando você precisar
de lógica adicional:

```ts
export function useUsuarios() {
  return useApiQuery(['usuarios'], '/usuarios')
}
```

Para atualizar dados manualmente, invoque
`queryClient.invalidateQueries(['usuarios'])` ou atualize o cache com
`queryClient.setQueryData`.

### Cache e estratégias de invalidação

O React Query segue a estratégia *stale-while-revalidate*: o cache é exibido
imediatamente enquanto uma nova solicitação é executada em segundo plano.
Defina `staleTime` para controlar quando os dados tornam-se obsoletos e use
`invalidateQueries` após operações de gravação. Também é possível definir
`refetchInterval` em hooks específicos para manter métricas em tempo real.

### Storybook

Para visualizar os componentes React de forma isolada, execute:

```bash
cd src/frontend/react_app
npm run storybook
```

Este comando abre a interface em <http://localhost:6006> (porta padrão, configurável). Utilize as histórias
para validar diferentes estados (carregando, erro, sucesso) antes de integrar
ao fluxo principal.

### Executando o Rope codemod

Refatorações estruturais podem ser automatizadas com `scripts/run_py_codemod.sh`. O script usa o `refactor_move.py` da biblioteca Rope para mover módulos e atualizar os imports automaticamente.

Antes de rodar o utilitário instale o Rope:

```bash
pip install rope
```

Execute o script informando o arquivo de origem e o diretório de destino:

```bash
./scripts/run_py_codemod.sh caminho/original.py pasta_destino/
```
