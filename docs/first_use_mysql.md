# Guia de Primeiros Passos

Este documento descreve como preparar o ambiente e executar o dashboard GLPI
utilizando um banco de dados **MySQL** para armazenar os dados processados.
Todas as operações são realizadas online, consumindo diretamente a API do GLPI.

## 1. Pré‑requisitos

 - Python 3.10\u20133.12
- MySQL Server (local ou remoto)
- Acesso aos tokens da API GLPI (quando em modo online)

Certifique‑se de ter um usuário com permissões de criação de banco de dados.

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt -r requirements-dev.txt
pip install -e .  # install package locally (packages live under src/)
pip install opentelemetry-instrumentation-fastapi opentelemetry-instrumentation-logging
pre-commit install
```

## 2. Configuração do banco de dados MySQL

Crie um banco vazio e um usuário dedicado para a aplicação. Exemplo em um
terminal MySQL:

```sql
CREATE DATABASE glpi_dashboard CHARACTER SET utf8mb4;
CREATE USER 'dashboard'@'%' IDENTIFIED BY 'senhaSegura';
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER ON glpi_dashboard.* TO 'dashboard'@'%';
FLUSH PRIVILEGES;
```

Use esta conta restrita apenas para a aplicação. Para tarefas administrativas
(como migração ou manutenção do banco), utilize uma conta separada com
privilégios mais amplos.

Anote o host, porta e credenciais, pois serão usados no arquivo `.env`.

## 3. Variáveis de ambiente

Copie o modelo de configuração e preencha com seus dados:

```bash
python scripts/setup/setup_env.py  # gera o arquivo .env a partir de .env.example
```

Edite `.env` definindo:

```text
GLPI_BASE_URL=https://glpi.exemplo.com/apirest.php
GLPI_APP_TOKEN=token_da_aplicacao
GLPI_USER_TOKEN=token_de_usuario       # opcional
GLPI_USERNAME=usuario_glpi             # opcional se usar GLPI_USER_TOKEN
GLPI_PASSWORD=senha_glpi               # opcional se usar GLPI_USER_TOKEN

DB_HOST=localhost
DB_PORT=3306
DB_NAME=glpi_dashboard
DB_USER=dashboard
DB_PASSWORD=senhaSegura
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_TTL_SECONDS=3600
CODEGPT_PLUS_API_KEY=<seu_token>  # opcional

Para detalhes completos sobre cada variável, consulte a seção "Environment variables" do README.md.


```

## 4. Inicialização do esquema de banco

Após configurar o `.env`, execute a criação das tabelas:

```bash
PYTHONPATH=$(pwd) python scripts/setup/init_db.py --drop-all
```

O script lê o arquivo `schema.sql` localizado na raiz do projeto e cria as tabelas necessárias em seu servidor MySQL.

## 5. Execução do aplicativo

Execute a aplicação conectando diretamente na API GLPI:

```bash
python dashboard_app.py
```

O aplicativo utilizará as credenciais GLPI definidas no `.env` e registrará eventuais falhas de autenticação no console.

## 6. Verificação

Após o comando iniciar, abra `http://127.0.0.1:8050` no navegador. Você deverá
ver o dashboard carregado com os tickets. Caso tenha usado o modo online, verifique
os logs para confirmar que a conexão com a API ocorreu com sucesso.

## 7. Ambiente remoto

Para hospedar em um servidor, replique as etapas acima (instalação de Python,
MySQL e configuração do `.env`). Utilize um serviço como `systemd` ou `supervisor`
para manter o processo ativo e configure variáveis de ambiente no shell do
usuário que irá executar a aplicação.

```bash
# exemplo com systemd
sudo systemctl start glpi-dashboard.service
```

Mantenha os tokens e credenciais em local seguro, limitando as permissões do
arquivo `.env`.

---

Com esses passos você terá o dashboard rodando com persistência em MySQL e consumindo dados em tempo real da API GLPI.
