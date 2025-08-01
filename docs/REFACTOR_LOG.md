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
REMOVIDO: `src/backend/utils/cache.py` (substituído por `src/backend/utils/redis_client.py`).
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

## 📄 Atualizacao 2025-07-31

- Removido `src/backend/utils/cache.py` (substituído por `src/backend/utils/redis_client.py`) e o teste correspondente `tests/test_cache_initialization.py`.
 - Removido `src/shared/utils/resilience/example_api.py` por se tratar de exemplo obsoleto.

## 📄 Atualizacao 2025-08-01

- Movidos modelos para `src/backend/schemas/` e ajustados imports em todo o projeto.

## 📄 Atualizacao 2025-08-01

- Movido `src/shared/utils/resilience/resilient_client.py` (990 bytes) para `examples/resilient_client.py`.
- Movido `tests/test_resilient_client.py` (1612 bytes) para `examples/test_resilient_client.py`.
- Movido `scripts/demo_resilient_client.py` (353 bytes) para `examples/demo_resilient_client.py`.
