# Gemini Prompt Examples – GLPI Data & UX 🌟

## Visão geral

Use estes prompts no **Gemini Advanced** para gerar insights semânticos, detecção de riscos e sugestões de UX.

---

### 1️⃣ Analisar Schema JSON

```text
Segue estrutura bruta de ticket do GLPI:
<COLE JSON>
Quais campos redundantes podem ser descartados? Gere um resumo dos tipos de dado e proponha um schema mínimo.
```

### 2️⃣ Regras de Validação

```text
Com base no schema mínimo, defina regras de validação (type, range, not null).
Produza código Pydantic que implemente essas regras.
```

### 3️⃣ Stress‑test Pipeline

```text
Gere 50 exemplos de ticket que quebrem as regras de validação anteriores (campos nulos, tipos errados, datas futuras).
```

### 4️⃣ UX Review do Dash

```text
Este é o layout atual (captura em Markdown).
Sugira melhorias rápidas de legibilidade e cores considerando acessibilidade WCAG AA.
```

### 5️⃣ Análise de Riscos Técnicos

```text
Liste riscos de dependência externa, credenciais vazadas, e falhas de rede.
Para cada risco, proponha mitigação.
```
