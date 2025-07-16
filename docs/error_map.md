# Mapa de Erros Comuns

Este guia relaciona os principais problemas que podem ocorrer na primeira execucao do dashboard GLPI. Cada entrada indica o sintoma observado, a causa mais provavel, os passos para correcao e o comando/instrucao que pode ser repassado ao Codex para automatizar a solucao.

| Sintoma | Causa provavel | Passos para solucao | Instrucao para Codex |
| ------- | -------------- | ------------------ | -------------------- |
| `401 Unauthorized` ao chamar a API GLPI | `GLPI_APP_TOKEN` ou credenciais incorretas | Verifique as variaveis em `.env` e tente autenticar manualmente com `curl` | "Atualize .env com tokens validos e execute novamente `python dashboard_app.py`" |
| `400 Bad Request` com `ERROR_WRONG_APP_TOKEN_PARAMETER` | app-token invalido ou IP nao autorizado | Confirme o valor do token em `Configuração > Geral > API` e ajuste o intervalo de IP permitido | "Atualize `GLPI_APP_TOKEN` e verifique IPs autorizados" |
| Erro `pymysql.err.OperationalError` na inicializacao | Servico MySQL inativo ou credenciais invalidas | Teste a conexao via `mysql -h $DB_HOST -u $DB_USER -p` | "Substitua valores `DB_*` em `.env` e rode `PYTHONPATH=$(pwd) python scripts/setup/init_db.py`" |
| Mensagem "Arquivo JSON nao encontrado" | Caminho incorreto para o dump | Confirme a existencia do arquivo com `ls -l` | "Ajuste o caminho do dump gerado por `scripts/fetch/fetch_tickets.py`" |
| Dashboard nao inicia: porta 8050 em uso | Outro processo utilizando a porta | Liste processos com `lsof -i :8050` e finalize-os | "Matar processo na porta 8050 antes de executar o server" |
| `ModuleNotFoundError` ao rodar scripts | Dependencias ausentes ou ambiente virtual desativado | Ative o venv, rode `pip install -r requirements.txt -r requirements-dev.txt` e depois `pip install -e .` (pacotes estão em `src/`) | "Crie ou ative o venv e reinstale dependencias" |

Estas orientacoes sao complementares aos guias [run_local](run_local.md) e [first_use_mysql](first_use_mysql.md).
