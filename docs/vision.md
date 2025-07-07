# Documento de Visao

![DRAFT v0.1](https://img.shields.io/badge/DRAFT-v0.1-informational)

## 1.1 Objetivo
O projeto **GLPI Dashboard CAU** tem como objetivo consolidar indicadores do service desk em uma interface única e responsiva. Os dados são coletados da API REST do GLPI, normalizados e armazenados em PostgreSQL para consulta rápida. Além do modo online, há suporte a operação *offline* por meio de arquivos JSON, permitindo evoluir o dashboard sem depender da instância oficial. A iniciativa reduz o trabalho manual de relatórios e fornece visão em tempo real sobre backlog, SLA e produtividade.

## 1.2 Stakeholders
- **Equipe de suporte (CAU)** – acompanha diariamente os chamados e planeja atividades.
- **Gestores de TI** – analisam SLA, backlog e produtividade para priorizações e alocação de recursos.
- **Time de desenvolvimento** – mantém as APIs, rotinas de ETL e o frontâ-end.
- **Infraestrutura** – garante a disponibilidade de banco de dados, Redis e GLPI.

## 1.3 Visao
A visão é oferecer uma plataforma leve que exponha métricas do GLPI por meio de uma API worker e de um frontâ-end interativo. O sistema opera tanto online—buscando tickets atuais—quanto offline com *dumps* JSON, incentivando experimentação sem impacto na produção. Modular e open source, o projeto deve ser fácil de implantar via Docker e prover KPIs claros como tempo médio de resolução e distribuição de chamados por grupo.

## 1.4 Requisitos Funcionais / Nao Funcionais
### Funcionais
1. Coletar tickets via API REST do GLPI com autenticação.
2. Normalizar e gravar informações em PostgreSQL.
3. Exibir SLA, backlog e produtividade em gráficos responsivos.
4. Disponibilizar endpoints REST e GraphQL para consulta.
5. Permitir modo offline lendo JSONs pré-gerados.

### Não Funcionais
1. Tempo de carregamento das métricas principais inferior a 1 s.
2. Código em Python 3.10–3.12 com testes automatizados e PEP 8.
3. Deploy simplificado via Docker Compose e variáveis de ambiente.
4. Cache de consultas em Redis com TTL configurável.
5. Suporte aos principais navegadores modernos.


