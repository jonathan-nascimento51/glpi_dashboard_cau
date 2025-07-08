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
[`utils/redis_client.py`](../src/glpi_dashboard/utils/redis_client.py). Caso esteja
usando outro cliente ou script, troque para a versão assíncrona ou remova o
`await` das chamadas.

## 9. Erro "FATAL: role 'user' does not exist"

A falha indica que o usuário especificado pela aplicação não foi criado no
PostgreSQL. Certifique-se de que as variáveis abaixo estejam presentes e com o
mesmo valor no `.env`:

```bash
DB_USER=user
DB_PASSWORD=password
POSTGRES_USER=$DB_USER
POSTGRES_PASSWORD=$DB_PASSWORD
```

Se o contêiner do banco tiver iniciado anteriormente com valores diferentes,
elimine o volume antigo e recrie tudo:

```bash
docker compose down -v
docker compose -f docker-compose-dev.yml up --build
make init-db
```

Após esses passos o backend conseguirá autenticar normalmente no PostgreSQL.
