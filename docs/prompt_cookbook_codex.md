# Codex Prompt Cookbook – GLPI Dashboard 📚

## Como usar

1. Abra uma sessão **Codex** (ChatGPT code‑interpreter).
2. Copie o bloco *PROMPT* desejado para o chat.
3. Revise o diff sugerido; aceite ou ajuste; faça commit.
4. Repita para cada arquivo.

---

### 1️⃣ Gerar **glpi_session.py**

```text
Você é um engenheiro Python sênior.
Crie **glpi_session.py** com:
- login() que cria sessão e retorna um objeto Session pronto.
- get_tickets(status=None, limit=100, session=None) → List[dict]
- Uso de python‑dotenv para ler GLPI_BASE_URL, GLPI_APP_TOKEN, GLPI_USER_TOKEN
- Tratamento de erros HTTP com raise_for_status()
- Type hints e docstrings.
```

### 2️⃣ Gerar **backend/utils/pipeline.py**

```text
Você é um especialista em ETL.
Crie backend/utils/pipeline.py com:
- process_raw(data: List[dict]) -> pandas.DataFrame
- Campos obrigatórios: id, status, group, date_creation, assigned_to, requester
- Converta datas para datetime, preencha NaN com None
```

### 3️⃣ Gerar **dashboard/layout.py**

```text
Você é front‑end Dash.
Crie dashboard/layout.py contendo a função build_layout(df) que devolve um objeto html.Div com:
- H1 título
- 3 contadores (total, abertos, fechados)
- Gráfico de barras tickets por status
- DataTable com id, name, status, technician
Sem CSS avançado.
```

### 4️⃣ Atualizar **requirements.txt**

```text
Adicione/atualize:
dash>=2.17
pandas>=2.2
requests>=2.32
python-dotenv>=1.0
pre-commit>=3.7
```

### 5️⃣ Script **.devcontainer/setup.sh**

```bash
Gere setup.sh:
- apt-get update && install build-essential
- pip install -r requirements.txt -r requirements-dev.txt
- pre-commit install
```

### 6️⃣ Criar testes **tests/test_glpi_session.py**

```text
Use pytest e requests-mock.
Teste que get_tickets() retorna lista não vazia e lança HTTPError em 500.
```

### 7️⃣ Refatorar depois

```text
Reescreva backend.utils.pipeline.process_raw para aceitar DataFrame e Series.
Garanta 100% coverage nos testes.
```

### 8️⃣ Mensagens de commit (Conventional Commits)

```text
feat(api): add glpi_session with session support
fix(api): handle 401 unauthorized
docs(readme): add local setup guide
```
