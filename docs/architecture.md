Visão de Arquitetura (Plano de Melhoria)
Este documento descreve as principais visões da arquitetura do GLPI Dashboard CAU. Esta versão foi atualizada para refletir a estrutura de pastas refatorada e ideal do projeto, que visa a máxima organização e clareza.

1. Visão Lógica
A arquitetura lógica da aplicação permanece a mesma, dividida em componentes com responsabilidades claras:

Worker API (FastAPI): O backend responsável pela coleta, processamento e exposição dos dados do GLPI.

Dashboard App (Dash): A interface de análise interna, construída em Python com Dash.

Frontend App (React): A interface principal para o usuário, rica e interativa, construída com React/TypeScript.

Plaintext

@startuml
actor Usuario as User
participant "Frontend (React)" as ReactApp
participant "Dashboard (Dash)" as DashApp
participant "Worker (FastAPI)" as Worker
database "Redis" as Redis
database "PostgreSQL" as DB
cloud "GLPI REST API" as GLPI

User --> ReactApp
User --> DashApp
ReactApp --> Worker
DashApp --> Worker
Worker --> Redis
Worker --> DB
Worker --> GLPI
@enduml

2. Visão de Implementação (Estrutura Atual)
O repositório mantém uma separação de responsabilidades sob o diretório `src/`, que concentra todo o código Python do projeto.

src/backend/: Módulos, serviços e rotas do Worker API (FastAPI), incluindo a integração com o GLPI.

src/frontend/: Módulos da aplicação Dash, incluindo layouts e callbacks.

src/shared/: Modelos Pydantic, DTOs e utilitários compartilhados entre os diferentes componentes Python.

src/glpi_tools/: Ferramentas de linha de comando.

src/frontend/react_app/: Diretório dedicado exclusivamente à aplicação principal em React/TypeScript/Vite. Ele é autocontido, com suas próprias dependências e scripts.

documentation/: (Refatorado) Pasta central para toda a documentação do projeto. Arquivos como ARCHITECTURE.md, README.md (exceto o principal), ADRs e outros guias serão movidos para cá.

scripts/: (Refatorado) Centralizará todos os scripts utilitários (.py, .sh, .js) que auxiliam em tarefas de desenvolvimento e automação.

docker/: (Refatorado) Conterá arquivos de configuração auxiliares do Docker, como docker-compose.override.yml e docker-compose.prod.yml, além de scripts de inicialização de contêineres.

Raiz do Projeto: A raiz será mantida o mais limpa possível, contendo apenas arquivos essenciais para a inicialização e configuração do projeto:

Configuração Docker: docker-compose.yml, Dockerfile.

Configuração do Projeto: pyproject.toml, package.json, requirements.txt.

CI/CD e Qualidade: .github/, .gitignore, .pre-commit-config.yaml.

Documentação Essencial: README.md.

Plaintext

@startuml
package "src (Python)" as src {
  [backend]
  [frontend]
  [shared]
}

package "frontend (React/TS)" as fe {
  [components]
  [hooks]
}

package "documentation" as docs
package "scripts"
package "docker"

fe ..> [backend] : HTTP
[frontend] ..> [backend] : (Uso interno de dados)
[backend] -> [shared]
@enduml
1. Visão de Processo
O fluxo de execução não se altera. O Worker continua sendo a peça central que processa os dados, e as aplicações frontend (React e Dash) consomem esses dados via API.

1. Visão de Implantação
A estratégia de implantação com contêineres Docker permanece a mesma, sendo beneficiada pela organização dos arquivos que simplifica a construção das imagens.

1. Visão de Cenários
Os cenários de uso continuam idênticos, uma vez que a refatoração da estrutura de arquivos não afeta a funcionalidade externa da aplicação.

1. Fluxo orientado a eventos
A lógica de consumo de eventos continuará a mesma, porém o arquivo responsável será realocado para seguir a nova estrutura. O consumidor estará em `src/backend/events_consumer.py` (caminho atualizado).

Esta versão do documento serve como o "plano diretor" para a refatoração, garantindo que todos os envolvidos tenham uma visão clara da estrutura organizada que queremos alcançar.