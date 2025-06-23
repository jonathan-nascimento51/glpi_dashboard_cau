# GLPI Dashboard – Plano MVP e Scripts Auxiliares

> **Versão:** 2025‑06‑23  
> **Autor:** Jonathan (pirata) – suporte ChatGPT

---

## 1 Objetivo

Entregar um **dashboard mínimo viável (MVP)** que:

1. Consome a API GLPI somente dentro da rede corporativa para gerar um *dump* JSON.
2. Permite evoluir interface e lógica **offline** usando esse dump.
3. Disponibiliza scripts automáticos para verificação de integridade (hash), logging de execuções e filtros de dados.
4. Inclui CI/CD simples com execução em ambiente *mock*.

---

## 2 Estrutura do Repositório

```text
glpi_dashboard/
├── .env.example
├── requirements.txt
├── glpi_api.py
├── data_pipeline.py
├── dash_layout.py
├── main.py
├── scripts/
│   ├── hash_data.py
│   ├── log_exec.py
│   └── filters.py
├── mock/
│   ├── sample_data.json
│   └── dev_schema_example.json
├── tests/
│   └── test_filters.py
├── .github/
│   └── workflows/
│       └── ci_mock.yml
└── README.md
```

---

## 3 Roadmap de Etapas

| Fase                     | Ambiente | Entregáveis-chave                            |
|--------------------------|----------|----------------------------------------------|
| **1. Backend (API)**     | Intra    | `glpi_api.py`, `data_pipeline.py`, `hash_data.py` |
| **2. Frontend Offline**  | Externo  | `dash_layout.py`, `main.py`, `mock/*.json`   |
| **3. Refino & Deploy**   | Ambos    | CSS, refresh automático, `ci_mock.yml`       |

---

## 4 Scripts Automáticos

### 4.1 `scripts/hash_data.py`
Calcula SHA‑256 do dump JSON e grava em `<arquivo>.sha256`.

### 4.2 `scripts/log_exec.py`
Registra execuções em `log.jsonl` com metadados (`time`, `user`, `source`).

### 4.3 `scripts/filters.py`
Funções de filtragem sobre `pandas.DataFrame`:
- `by_status(df, status)`
- `by_group(df, group)`
- `by_technician(df, tech)`

---

## 5 Workflow CI/CD – `ci_mock.yml`

1. Dispara em `push` e `pull_request`.
2. Matrix Python `3.10` e `3.12`.
3. Passos:
   - Checkout
   - Instala dependências
   - Lint (`black`, `flake8`)
   - Testes unitários (`pytest`) usando `mock/sample_data.json`.

---

## 6 Uso Rápido

```bash
# Gerar hash
python scripts/hash_data.py mock/sample_data.json

# Registrar execução
python scripts/log_exec.py --source mock/sample_data.json --user pirata

# Executar filtros no Python
python - <<'PY'
from scripts import filters
import json, pandas as pd
df = pd.DataFrame(json.load(open("mock/sample_data.json")))
print(filters.by_status(df, "new").head())
PY
```

---

### 🚀 Bom trabalho e bons commits!
