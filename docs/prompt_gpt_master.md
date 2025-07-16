# GPT‑4 Pro Master Prompt – Orquestração do Projeto 🧠

Copie o bloco abaixo inteiro no GPT‑4 (navegação ativa) para obter um **plano macro**:

---

```text
Contexto:
- Projeto: Dashboard GLPI que consome API interna.
- Ambiente: Repositório git github.com/<org>/glpi_dashboard
- Dependências principais: Dash, pandas, requests.

Tarefas:
1. Liste todos os riscos técnicos e operacionais (segurança, escalabilidade, dados).
2. Gere um blueprint de CI/CD (GitHub Actions) que:
   - Instala dependências
   - Roda pytest
   - Envia cobertura para Codecov
3. Modele um roadmap de 3 sprints (MVP, Refino, Deploy)
4. Proponha uma arquitetura multi‑agente (Codex = geração de código, Gemini = validação semântica, GPT = planejamento) incluindo fluxograma.

Formato da resposta:
## Riscos
Tabela | Mitigação
## CI/CD YAML
```yaml
# ...
```

## Roadmap

Bullet list

## Fluxograma

Mermaid diagram

---
