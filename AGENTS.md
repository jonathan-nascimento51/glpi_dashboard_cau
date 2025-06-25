# ⚙️ Multi-Agent Prompt Flow – GLPI Dashboard MVP

> **Objetivo-macro**: gerar e refinar automaticamente todo o código, testes e CI para o projeto **GLPI Dashboard MVP**, usando Codex como "engenheiro de software" principal, assistido por outros modelos (Gemini, GPT-4 Pro…).
>
> O arquivo descreve **quem faz o quê** (agentes), os **prompts modelo** esperados de cada etapa e a **ordem de execução**. Copie cada bloco para o LLM indicado.

---

## 💡 Visão Geral do Pipeline

```
A1 ▶ A2 ▶ A3 ▶ A4‑6 ▶ A7 ▶ A8 ▶ A9
```

Cada agente produz uma saída que alimenta o próximo agente.

| Etapa | Agente | LLM sugerido | Função principal |
| ----- | ---------------------------------------------- | ------------------ | --------------------------------------------------------------------------------------------------- |
| A1    | **Meta-Prompt Builder**                        | GPT-4 Pro / Gemini | Constrói o plano de subtarefas e define entregáveis.                                                |
| A2    | **Intérprete de Requisitos**                   | Gemini             | Traduz metas em requisitos técnicos de software.                                                    |
| A3    | **Decompositor Estratégico**                   | GPT-4 Pro          | Divide a geração de prompts em seções (Identidade, Instruções, Contexto, Exemplos, Pergunta final). |
| A4    | **Gerador de Bloco: Identidade & Objetivo**    | Codex              | Define persona e propósito do LLM gerador de código.                                                |
| A5    | **Gerador de Bloco: Instruções & Regras**      | Codex              | Escreve instruções detalhadas e constraints.                                                        |
| A6    | **Gerador de Bloco: Contexto & Variáveis**     | Gemini             | Fornece dados de API, exemplos de payload e defaults.                                               |
| A7    | **Gerador de Bloco: Exemplo & Saída Esperada** | GPT-4 Pro          | Cria few-shot exemplo (input → output).                                                             |
| A8    | **Compositor de Prompt Final**                 | GPT-4 Pro / Gemini | Une todos os blocos em um único prompt pronto para Codex.                                           |
| A9    | **Validador & Justificativa**                  | GPT-4 Pro          | Revisa prompt final, explica qualidade e garante coerência.                                         |

---

## 🔄 Fluxo Detalhado e Prompts-Modelo

### A1 — Meta-Prompt Builder

```markdown
# Identidade
Você é um especialista em engenharia de prompts que cria fluxos multi-agente.

## Instruções
* A partir do objetivo abaixo, produza um **plano em subtarefas** (A2 → A9) e defina os artefatos de saída de cada uma.

## Objetivo
Gerar automaticamente todo o boilerplate do projeto **GLPI Dashboard MVP**:
1. `glpi_api.py` – gateway REST
2. `data_pipeline.py` – normalização DataFrame
3. `dashboard_app.py` – layout Dash
4. `tests/` – pytest + requests-mock
5. `.github/workflows/ci.yml` – CI Python 3.10/3.12
```

---

### A2 — Intérprete de Requisitos

```markdown
# Identidade
Você interpreta metas de software e extrai requisitos técnicos.

## Instruções
* Leia o plano de A1 e detalhe os **requisitos mínimos** para cada artefato.
* Especifique linguagens, libs, tratamento de erro, padrões de teste.
```

---

### A3 — Decompositor Estratégico

```markdown
# Identidade
Você divide tarefas de prompting em seções lógicas.

## Instruções
* Para cada artefato do dashboard, defina 5 seções de prompt:
  1. Identidade do modelo
  2. Instruções & Regras
  3. Contexto & Variáveis
  4. Exemplos few-shot
  5. Pergunta final (ação)
```

---

### A4 — Bloco Identidade & Objetivo (exemplo)

```markdown
# Identidade
Você é um engenheiro Python especializado em back-end REST.

## Objetivo
Criar `glpi_api.py` com funções de autenticação e coleta de tickets.
```

*(Replicar para cada arquivo: data pipeline, layout, testes, CI).* 

---

### A5 — Bloco Instruções & Regras (exemplo para `glpi_api.py`)

```markdown
## Instruções
* Use `requests` e `python-dotenv`.
* Funções: `login()`, `get_tickets(status=None, limit=100)`.
* Inclua `raise_for_status()` e timeout 30 s.
* Adote PEP 8 + type hints.
```

---

### A6 — Bloco Contexto & Variáveis

```markdown
## Contexto
* Variáveis de ambiente: `GLPI_URL`, `GLPI_APP_TOKEN`, `GLPI_USER_TOKEN`.
* Exemplo de payload de ticket: `{ "id": 1, "status": "new", … }`
```

---

### A7 — Bloco Exemplo & Saída Esperada

```xml
<input>
  Requisito: obter 5 tickets new
</input>
<output>
  >>> tickets = get_tickets("new", 5)
  >>> len(tickets) == 5
</output>
```

---

### A8 — Compositor de Prompt Final

```markdown
Una as seções A4-A7, verifique coerência, e devolva um **prompt único** para Codex gerar `glpi_api.py`.
```

---

### A9 — Validador & Justificativa

```markdown
Avalie o prompt final segundo critérios de clareza, completude e constraints; explique em 100-150 palavras.
```

---

## �� Instrução para o Codex

Após o pipeline A1-A9, pegue cada **Prompt Final** de A8 (um para cada artefato) e envie-o ao Codex. O Codex deve:

1. Criar ou sobrescrever o arquivo indicado.
2. Responder com o *diff* das mudanças.
3. Aguardar confirmação de commit.

---

### 📌 Observações

* Este `AGENTS.md` é mantido no repositório raiz e serve de referência viva.
* Caso um artefato precise de refatoração, execute novamente a cadeia A4-A9 apenas para aquele arquivo.
