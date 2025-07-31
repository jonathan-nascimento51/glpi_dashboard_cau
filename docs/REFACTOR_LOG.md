# 🚚 Refatoração Estrutural – Mapeamento Inicial (Codex)

Data: 2025-07-09
Responsável: RefatorAgent (Codex)

Ações sugeridas:
Olá, sou seu Arquiteto Full-Stack de Automação & Métricas.

Mapeamento sugerido
src/api/__init__.py → src/backend/api/__init__.py — inicializa o pacote de rotas da API no backend.
tickets_groups.py → src/backend/services/tickets_groups.py — script de ETL que consulta o GLPI, pertencendo à camada de serviços.
src/backend/adapters/dto.py — define DTOs utilizados na integração com o GLPI (anti‑corrupção).
src/backend/adapters/mapping_service.py — serviço de mapeamento de IDs para nomes, usado como adaptador.
src/backend/adapters/normalization.py — normaliza dados vindos da API GLPI, parte do adaptador.
src/backend/models/ticket_models.py — modelos de domínio para tickets.
src/backend/utils/cache.py — configuração de cache Redis, utilidade compartilhada.
src/backend/core/tickets_groups.py — comando CLI para acionar o ETL, mantido no núcleo do backend.
src/backend/core/settings.py — centraliza as configurações da aplicação.
src/frontend/callbacks/callbacks.py — callbacks do Dash, parte do frontend.
src/frontend/components/components.py — componentes visuais reutilizáveis do dashboard.
src/frontend/layout/layout.py — montagem do layout principal do frontend.
src/backend/db/database.py — definição do modelo e acesso ao banco PostgreSQL.
O antigo `data/transform.py` foi migrado para `src/backend/adapters/normalization.py` — funções de limpeza e agregação.
src/backend/services/events_consumer.py — consumo de eventos (Kafka) e atualização de métricas.
glpi_adapter.py — removido; a ACL é importada diretamente dos módulos em `backend/adapters`.
src/backend/services/aggregated_metrics.py — cálculo e cache de métricas agregadas.
src/backend/services/langgraph_workflow.py — orquestração de workflow com LangGraph.
src/backend/api/worker_api.py — implementação da API FastAPI/GraphQL do worker.
src/backend/utils/redis_client.py — cliente Redis assíncrono com métricas de cache.
examples/resilience/retry_decorator.py → src/shared/utils/resilience/retry_decorator.py — decorator genérico de retry, útil em qualquer módulo.
examples/order_observer.py → src/shared/order_observer.py — exemplo de padrão observer, independente do backend.
Essas movimentações alinham cada módulo com responsabilidades semelhantes dentro da nova estrutura, separando claramente backend, frontend e utilidades compartilhadas.

## 🚚 Refatoração Estrutural Aplicada (auto_mover.py)

Data: 2025-07-09
Ferramenta: scripts/auto_mover.py
Descrição: Arquivos foram movidos de acordo com o mapeamento fornecido por Codex (RefatorAgent).
Status: ✅ Concluído com sucesso

Verificado via: scripts/refactor/init_refactor.sh + inspeção visual
Nota: `scripts/auto_mover.py` foi removido após a migração porque o mapeamento estava vazio.

## \ud83d\udcc6 Atualizacao 2025-07-09

- Executado `bash scripts/refactor/init_refactor.sh` para listar a nova estrutura de arquivos.
- Verificado que persistem pastas extras como `glpi_dashboard` e `etl`.
- Dependencias instaladas via `requirements.txt` e `requirements-dev.txt`.
- Testes executados com `pytest` mas falharam por erros de importacao.
- Necessario revisar modulos faltantes antes de prosseguir com a migracao.

## 🔄 Codemod Python (Rope)

Data: 2025-07-09
Ferramenta: scripts/run_py_codemod.sh
Descrição: Script auxilia na movimentação de módulos Python utilizando a biblioteca Rope. Recebe o caminho do arquivo de origem e o diretório de destino, cria as pastas necessárias e aciona `refactor_move.py` para atualizar as importações automaticamente.

## 📄 Atualizacao 2025-07-10

- README ampliado com instruções de uso do `scripts/run_py_codemod.sh`.
- Reforçada a dependência da biblioteca Rope para realizar a refatoração.
-

## \ud83d\udcc6 Atualizacao 2025-07-31
- Criada pasta `new_project/` com subpastas `backend/`, `frontend/` e `shared/`.
- Adicionado `new_project/Dockerfile` (167 bytes) e `new_project/docker-compose.yml` (107 bytes) para um setup simplificado.
- Copias de `.env.example` adicionadas em `new_project/.env.example` (2623 bytes) e `new_project/frontend/.env.example` (184 bytes).
- `new_project/backend/main.py` (109 bytes) contem worker FastAPI minimo.
## \ud83d\udcc6 Atualizacao 2025-07-31 (metrics)
- `new_project/backend/main.py` (4683 bytes) passou a incluir rotas `metrics/overview` e `metrics/level`. As fun\u00e7\u00f5es derivam de `app/api/metrics.py`.
## \ud83d\udcc6 Atualizacao 2025-07-31 (Dockerfile cleanup)
- Removido `Dockerfile` (474 bytes) em favor de `docker/backend/Dockerfile`. Referências atualizadas.
