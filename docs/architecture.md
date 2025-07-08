# Visão de Arquitetura

Este documento descreve as principais visões da arquitetura do **GLPI Dashboard CAU** utilizando a stack oficial baseada em **Python (FastAPI/Dash)**, `httpx`/`asyncio`, **Pandas** e **Redis**. As seções abaixo seguem o modelo 4+1 de Kruchten.

## 1. Visão Lógica

A aplicação é dividida em dois microsserviços principais:

- **Dash App**: interface web construída com Dash que apresenta gráficos e tabelas em tempo real.
- **Worker API**: serviço FastAPI responsável por coletar dados do GLPI, armazenar em Redis/PostgreSQL e expor endpoints REST/GraphQL.

```text
@startuml
actor Usuario
Usuario --> Dash
Dash --> Worker
Worker --> Redis
Worker --> "Banco de Dados"
Worker --> "GLPI REST API"
@enduml
```

## 2. Visão de Implementação

O repositório é organizado em pacotes Python com responsabilidade clara:

- `glpi_dashboard/` contém o código de domínio (cache, serviços e utilidades).
- `api/` expõe rotas FastAPI usadas pelo worker.
- `dashboard/` abriga o layout e callbacks do Dash.
- `etl/` reúne scripts de ingestão e normalização usando Pandas.

Esses módulos trocam dados através de objetos tipados e utilizam `httpx` com `asyncio` para chamadas não bloqueantes.

```text
@startuml
package "glpi_dashboard" {
  [services]
  [data]
  [cache]
}
package api {
  [worker_api]
}
package dashboard {
  [dashboard.layout]
}
[worker_api] --> [services]
[dashboard.layout] --> [cache]
[services] --> [data]
@enduml
```

## 3. Visão de Processo

Em tempo de execução, o worker executa tarefas assíncronas que obtêm dados do GLPI e atualizam o cache. A aplicação Dash lê esse cache periodicamente para renderizar indicadores. O fluxo típico é:

1. Usuário acessa o Dash e solicita métricas.
2. Dash consulta o Worker via HTTP.
3. Worker verifica Redis; se necessário, chama a API do GLPI usando `httpx`.
4. Os resultados são transformados em `pandas.DataFrame` e armazenados.
5. Dash exibe os dados atualizados ao usuário.

## 4. Visão de Implantação

A solução é distribuída em contêineres Docker orquestrados via `docker compose`:

- `dash`: executa o servidor Dash em Gunicorn/Uvicorn.
- `worker`: serviço FastAPI para integrações e cálculos.
- `redis`: cache de acesso rápido para dados de tickets.
- `db` (opcional): armazena históricos e metadados adicionais.

```text
@startuml
node dash
node worker
database Redis
database DB
cloud "GLPI" as glpi

user -- dash
Dash --> worker
worker --> Redis
worker --> DB
worker --> glpi
@enduml
```

## 5. Visão de Cenários

Um cenário comum envolve a visualização de backlog de chamados em tempo real:

1. O usuário abre o painel e solicita o gráfico de SLA.
2. Dash dispara uma requisição ao endpoint `/metrics/sla` do Worker.
3. O Worker consulta o cache Redis; se estiver expirado, faz `GET` na API do GLPI.
4. Os dados são normalizados com Pandas e gravados no cache.
5. Dash recebe os resultados e atualiza as figuras na tela.

```text
@startuml
actor Usuario
Usuario -> Dash : abrir painel
Dash -> Worker : GET /metrics/sla
Worker -> Redis : consultar
Redis --> Worker : hit/miss
Worker -> "GLPI API" : GET /Ticket
Worker --> Redis : salvar
Worker --> Dash : JSON c/ SLA
Dash --> Usuario : exibe gráfico
@enduml
```

Estas visões fornecem um panorama completo da arquitetura e do fluxo de dados, facilitando futuras evoluções e integrações.

## 6. Fluxo orientado a eventos

A replicação das tabelas do GLPI via Debezium gera eventos `TicketCreated` e
`TicketUpdated` que são publicados em um broker (Kafka ou RabbitMQ). O módulo
`events/consumer.py` assina esse fluxo e aplica cada alteração ao modelo de
leitura mantido no Redis. Dessa forma, as métricas são atualizadas
incrementalmente conforme os tickets mudam sem depender de consultas
periódicas.

Outros serviços podem consumir o mesmo stream para compor relatórios ou acionar
webhooks, bastando criar um consumidor para o mesmo tópico. O formato de evento
é simples:

```json
{
  "type": "TicketCreated",
  "payload": { "id": 123, "status": 1, "priority": 3 }
}
```

Esses eventos são processados em ordem e os agregados de cache são recalculados
apenas com os registros afetados.
