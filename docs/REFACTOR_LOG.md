## 🚚 Refatoração Estrutural – Mapeamento Inicial (Codex)

Data: 2025-07-09
Responsável: RefatorAgent (Codex)

Ações sugeridas:
Olá, sou seu Arquiteto Full-Stack de Automação & Métricas.

Mapeamento sugerido
src/api/__init__.py → src/backend/api/__init__.py — inicializa o pacote de rotas da API no backend.
src/etl/tickets_groups.py → src/backend/services/tickets_groups.py — script de ETL que consulta o GLPI, pertencendo à camada de serviços.
src/glpi_dashboard/acl/dto.py → src/backend/adapters/dto.py — define DTOs utilizados na integração com o GLPI (anti‑corrupção).
src/glpi_dashboard/acl/mapping_service.py → src/backend/adapters/mapping_service.py — serviço de mapeamento de IDs para nomes, usado como adaptador.
src/glpi_dashboard/acl/normalization.py → src/backend/adapters/normalization.py — normaliza dados vindos da API GLPI, parte do adaptador.
src/glpi_dashboard/acl/ticket_models.py → src/backend/models/ticket_models.py — modelos de domínio para tickets.
src/glpi_dashboard/cache.py → src/backend/utils/cache.py — configuração de cache Redis, utilidade compartilhada.
src/glpi_dashboard/cli/tickets_groups.py → src/backend/core/tickets_groups.py — comando CLI para acionar o ETL, mantido no núcleo do backend.
src/glpi_dashboard/config/settings.py → src/backend/core/settings.py — centraliza as configurações da aplicação.
src/glpi_dashboard/dashboard/callbacks.py → src/frontend/callbacks/callbacks.py — callbacks do Dash, parte do frontend.
src/glpi_dashboard/dashboard/components.py → src/frontend/components/components.py — componentes visuais reutilizáveis do dashboard.
src/glpi_dashboard/dashboard/layout.py → src/frontend/layout/layout.py — montagem do layout principal do frontend.
src/glpi_dashboard/data/database.py → src/backend/db/database.py — definição do modelo e acesso ao banco PostgreSQL.
src/glpi_dashboard/data/transform.py → src/backend/utils/transform.py — funções auxiliares de transformação de DataFrame.
src/glpi_dashboard/events/consumer.py → src/backend/services/events_consumer.py — consumo de eventos (Kafka) e atualização de métricas.
src/glpi_dashboard/glpi_adapter.py → src/backend/adapters/glpi_adapter.py — wrapper legado exportando a camada ACL.
src/glpi_dashboard/services/aggregated_metrics.py → src/backend/services/aggregated_metrics.py — cálculo e cache de métricas agregadas.
src/glpi_dashboard/services/langgraph_workflow.py → src/backend/services/langgraph_workflow.py — orquestração de workflow com LangGraph.
src/glpi_dashboard/services/worker_api.py → src/backend/api/worker_api.py — implementação da API FastAPI/GraphQL do worker.
src/glpi_dashboard/utils/redis_client.py → src/backend/utils/redis_client.py — cliente Redis assíncrono com métricas de cache.
src/patterns/resilience/retry_decorator.py → src/shared/resilience/retry_decorator.py — decorator genérico de retry, útil em qualquer módulo.
src/patterns/order_observer.py → src/shared/order_observer.py — exemplo de padrão observer, independente do backend.
Essas movimentações alinham cada módulo com responsabilidades semelhantes dentro da nova estrutura, separando claramente backend, frontend e utilidades compartilhadas.

## 🚚 Refatoração Estrutural Aplicada (auto_mover.py)
Data: 2025-07-09
Ferramenta: scripts/auto_mover.py
Descrição: Arquivos foram movidos de acordo com o mapeamento fornecido por Codex (RefatorAgent).
Status: ✅ Concluído com sucesso
Verificado via: ./init_refactor.sh + inspeção visual

## \ud83d\udcc6 Atualizacao 2025-07-09
- Executado `bash init_refactor.sh` para listar a nova estrutura de arquivos.
- Verificado que persistem pastas extras como `glpi_dashboard` e `etl`.
- Dependencias instaladas via `requirements.txt` e `requirements-dev.txt`.
- Testes executados com `pytest` mas falharam por erros de importacao.
- Necessario revisar modulos faltantes antes de prosseguir com a migracao.