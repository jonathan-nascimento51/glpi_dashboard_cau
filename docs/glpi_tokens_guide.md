
# Guia Avançado – Configuração & Execução do **GLPI Dashboard**

> **Revisão:** 2025-07-02  

Este documento conduz da clonagem do repositório ao monitoramento em produção.  
**Todas as capturas abaixo** são meramente ilustrativas; substitua pelos _prints_ do seu ambiente caso deseje documentação interna.

---

## 1 ▪️ Clonar o projeto

```bash
git clone https://github.com/<seu-usuario>/glpi-dashboard.git
cd glpi-dashboard
```

---

## 2 ▪️ Criar ambiente Python

```bash
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
# .venv\Scripts\Activate.ps1   # Windows PowerShell
pip install -r requirements.txt -r requirements-dev.txt
pip install -e .  # install package locally (packages live under src/)
pip install opentelemetry-instrumentation-fastapi opentelemetry-instrumentation-logging
```

---

## 3 ▪️ Gerar `.env`

```bash
python scripts/setup/setup_env.py          # copia .env.example → .env
```

Edite as variáveis de conexão:

```env
GLPI_BASE_URL="https://glpi.company.com/apirest.php"
GLPI_APP_TOKEN="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
GLPI_USER_TOKEN="yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy"
```

---

## 4 ▪️ Obter tokens GLPI

| Tipo de token | Onde obter | Captura |
|---------------|------------|---------|
| **Aplicação** (`GLPI_APP_TOKEN`) | *Setup → General → API_ | ![Menu Setup → General](docs/images/app_token_menu.png) |
| **Usuário** (`GLPI_USER_TOKEN`)  | _Perfil → Preferences → API* | ![Preferences → API](docs/images/user_token_pref.png) |

> **Dica:** salve os prints‑screen acima na pasta `docs/images/` para que os caminhos funcionem.  

---

## 5 ▪️ Validar credenciais

```bash
python scripts/validate_credentials.py
```

- **✅ Sucesso** → prossiga  
- **❌ Falha** → revise IP permitido ou tokens

---

## 6 ▪️ Subir stack Docker

```bash
docker compose up -d --build
```

O comando `docker compose` exige o plugin Docker Compose v2. Instale o pacote
`docker-compose-plugin` ou atualize seu Docker Engine caso ele não esteja
disponível.

Ao finalizar, execute:

```bash
docker compose ps --format "table {.Name} {.State} {.Health}"
```

Todos os serviços devem aparecer como **running / healthy**.

---

## 7 ▪️ Acessar o dashboard

- **API worker:** <http://localhost:8000/metrics>  
- **Dashboard (Dash/Plotly):** <http://localhost:8080>

Caso a API esteja indisponível ou tokens inválidos, o front‑end exibe um alerta amigável:

![Alerta de falha de conexão](docs/images/dashboard_alert.png)

---

## 8 ▪️ Modo offline (dados *mock_)

```bash
export USE_MOCK_DATA=true          # Linux/macOS
python dashboard_app.py
```

O backend irá ler `tests/resources/mock_tickets.json`.

---

## 9 ▪️ Testes & lint

```bash
pip install -r requirements.txt -r requirements-dev.txt
pip install opentelemetry-instrumentation-fastapi opentelemetry-instrumentation-logging
pytest --cov=./
pre-commit run --all-files
```

Cobertura mínima de 85 % garantida no CI (GitHub Actions).

---

## 10 ▪️ Monitoramento de produção

O contêiner **worker** possui `HEALTHCHECK` interno que executa `curl -I` no
endpoint `/health/glpi` (método **HEAD**). A rota `GET` continua disponível para
verificações manuais. Use:

```bash
docker events --filter 'event=health_status' --since 30m
```

para acompanhar oscilações em tempo real.

---

### Checklist rápido

| ✔ | Passo | Comando |
|---|-------|---------|
|   | Clonar repo | `git clone …` |
|   | Gerar `.env` | `python scripts/setup/setup_env.py` |
|   | Definir tokens | editar `.env` |
|   | Validar API | `python scripts/validate_credentials.py` |
|   | `docker compose up` | iniciar stack |
|   | Dashboard ok | abrir <http://localhost:5173> |

---

> **Nota final:** este guia usa capturas em `docs/images/…`. Se preferir imagens externas, basta substituir pelo link completo.

---

## 11 ▪️ Gerar tokens da API GLPI *(Referência rápida)_

> Os passos abaixo produzem **GLPI_APP_TOKEN** e **GLPI_USER_TOKEN** — obrigatórios no `.env`.

### 11.1 Token da aplicação (`GLPI_APP_TOKEN`)

1. Entre no GLPI com conta **admin**  
2. Navegue: **Setup → General → aba API**  
3. Marque **Enable REST API = Yes**  
4. Copie o valor de **API access token**

![Setup → General](https://tic.gal/wp-content/uploads/2019/07/1-enable-api-1.png)
![Aba API](https://tic.gal/wp-content/uploads/2019/07/1-enable-api.png)

### 11.2 Token do usuário (`GLPI_USER_TOKEN`)

1. Logado como o usuário que fará as consultas  
2. Clique no avatar (canto superior‑direito) → **Preferences**  
3. Abra a aba **API** e, se preciso, clique _Generate token_  
4. Copie **API token**

![Preferences → API](https://tic.gal/wp-content/uploads/2019/07/3-user-generate-api-token.png)

### 11.3 Atualizar `.env`

```env
GLPI_APP_TOKEN="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
GLPI_USER_TOKEN="yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy"
```

Pronto: o dashboard agora autentica corretamente na API.
