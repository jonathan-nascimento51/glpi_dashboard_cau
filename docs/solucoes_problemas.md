# Soluções para Problemas Comuns

Este documento reúne estratégias para lidar com falhas de inicialização, inconsistências nos dados retornados pela API GLPI e cuidados ao executar o dashboard em ambientes de produção ou desenvolvimento. Siga as recomendações abaixo para melhorar a robustez do projeto **glpi_dashboard_cau**.

## 1. Tratamento de Campos Inesperados ou Faltantes

- Utilize `dict.get("campo", valor_padrao)` ao acessar chaves do JSON.
- Prefira modelos de dados tolerantes (ex.: `pydantic.BaseModel` com campos opcionais).
- Inicialize o layout do Dash com placeholders e carregue dados nos callbacks.
- Envolva a etapa de obtenção de dados em `try/except` e registre falhas no log.

## 2. Sanitização de DataFrames

- Defina um esquema flexível com **Pandera** ou reindexe manualmente o DataFrame.
- Preencha colunas faltantes com `fill_value=np.nan` e descarte colunas extras.
- Converta tipos usando `pd.to_numeric(..., errors="coerce")` e limpe valores nulos.

## 3. Configurações de Saúde do Serviço Dash

- Adicione um endpoint simples de health check via `@app.server.route("/ping")`.
- O retorno deve ser `"OK", 200`, permitindo sondagens de disponibilidade.
- Desative o reloader em produção (`app.run_server(use_reloader=False)`).
- Utilize monitoramento externo (Docker `HEALTHCHECK` ou probes do Kubernetes).

## 4. Conflitos de Porta no WSL2

- Caso a porta 8050 esteja em uso por `wslrelay.exe`, execute `wsl --shutdown` no Windows.
- Atualize o WSL2 para a versão mais recente sempre que possível.
- Em último caso, altere a porta do Dash (`app.run_server(port=8051)`).

## 5. Exibição Amigável de Erros no Browser

- Capture exceções nos callbacks e retorne um `html.Div` ou `dcc.Graph` com mensagem de erro.
- Use `dcc.Loading` para indicar carregamento e `dash.no_update` quando apropriado.
- Para gráficos vazios, crie uma figura com anotação "Dados não disponíveis".

## 6. Melhores Práticas de Deploy

- Execute a aplicação com **Gunicorn**: `gunicorn -w 4 -b 0.0.0.0:8050 main:create_app`.
- Coloque o **Nginx** como proxy reverso e responsável por TLS.
- Considere empacotar tudo em Docker para facilitar o deploy.

## 7. Logs e Estratégias de Fallback

- Configure o módulo `logging` para gravar em arquivo rotativo (`RotatingFileHandler`).
- Unifique logs do Flask e do Gunicorn quando aplicável.
- Verifique `df.empty` antes de gerar gráficos e use cache local para último DataFrame válido.

Esses tópicos complementam o guia [docs/error_map.md](docs/error_map.md) com soluções voltadas a dados inconsistentes e ajustes de ambiente. Consulte-os sempre que encontrar instabilidades no dashboard.

## 8. Erro "object bool can't be used in 'await' expression"

Esse problema indica que o cliente Redis foi criado de forma **síncrona** (`redis.Redis`),
mas a chamada foi feita com `await`. Certifique‑se de importar `redis.asyncio` e
instanciar `redis.asyncio.Redis` como mostrado em
[`utils/redis_client.py`](../src/backend/utils/redis_client.py). Caso esteja
usando outro cliente ou script, troque para a versão assíncrona ou remova o
`await` das chamadas.

## 9. Erro "FATAL: role 'user' does not exist"

O usuário e o banco de dados definidos em `DB_USER` e `DB_NAME` são criados
automaticamente na primeira execução do contêiner. O script
[`docker/db-init/01-init-db.sh`](../docker/db-init/01-init-db.sh) é copiado para
o diretório `/docker-entrypoint-initdb.d/` e executado pelo PostgreSQL,
garantindo as permissões necessárias. Esse script também cria as roles de
aplicação e executa qualquer SQL estático presente em
`docker/db-init/00-extensions.sql`.

Se o volume do banco foi criado com credenciais incorretas, remova-o antes de
iniciar novamente:

```bash
docker compose down -v  # remove o volume com a configuração errada
docker compose up --build
make init-db
```

Após recriar o volume o backend deverá autenticar normalmente no PostgreSQL.

## 10. Erro "ReferenceError: require is not defined in ES module scope"

Ao executar scripts Node.js com `"type": "module"` no `package.json`, o runtime trata todos os arquivos `.js` como módulos ESM. Caso o código ainda use `require()` ou variáveis como `__dirname`, o Node exibirá o erro acima.

**Soluções**

1. **Migrar para ESM**: troque `require()` por `import` e crie `__dirname` usando:

   ```js
   import { fileURLToPath } from 'node:url'
   import path from 'node:path'
   const __filename = fileURLToPath(import.meta.url)
   const __dirname = path.dirname(__filename)
   ```

2. **Manter CommonJS**: renomeie o arquivo para `.cjs` e ajuste os comandos npm.

Consulte [docs/adr/0006-esm-adoption.md](adr/0006-esm-adoption.md) para entender a política de ESM no projeto.

## 11. Avisos e Deprecações do npm

Quando rodar `npm install` ou `npm ci` podem aparecer avisos ligados a proxy e pacotes depreciados. A seguir algumas orientações para eliminá-los.

### 11.1 Unknown env config 'http-proxy'

Esse aviso ocorre porque variáveis como `HTTP_PROXY` e `HTTPS_PROXY` não correspondem mais às chaves de configuração do npm. Remova-as do `.npmrc` e, se necessário, configure o proxy com `npm config set proxy <url>`.

Se o proxy estiver desativado, limpe as variáveis antes de executar o setup:

```bash
unset HTTP_PROXY HTTPS_PROXY
```

Também verifique se não restaram entradas de proxy no `.npmrc`, conforme explicado acima.

### 11.2 NODE_TLS_REJECT_UNAUTHORIZED=0

Desativar a verificação de certificados TLS torna as conexões inseguras. Em vez disso, exporte `NODE_EXTRA_CA_CERTS` apontando para o certificado desejado ou utilize certificados válidos.

### 11.3 Pacotes depreciados

Mensagens de deprecated indicam que uma dependência não é mais mantida. Atualize as versões diretas no `package.json` e utilize `overrides` para forçar versões mais novas em dependências transitivas. Priorize `rimraf@^4`, `glob@^9` e substitua `lodash.get` por optional chaining (`obj?.a?.b`).

### 11.4 TypeError: `crypto.hash` is not a function

Ao utilizar o **Vite 7** com versões antigas do Node.js pode surgir o erro `TypeError: crypto.hash is not a function`. Essa função foi incorporada recentemente e só está disponível a partir do Node **20.19** ou **22.12.0**.

Certifique‑se de instalar uma dessas versões e ativá‑la com o `nvm`:

```bash
nvm install 22.12.0   # ou "nvm install 20.19.0"
nvm use 22.12.0
```

Após atualizar o Node, remova a pasta `node_modules` e reinstale as dependências para garantir que o build do Vite seja executado corretamente.
