import sys
import importlib.util
import json
from pathlib import Path
from langgraph.graph import StateGraph
from typing import TypedDict, Optional

# Carregamento externo dos templates
TEMPLATE_PATH = Path("prompt_template.json")
if not TEMPLATE_PATH.exists():
    raise FileNotFoundError(f"Arquivo de templates não encontrado: {TEMPLATE_PATH}")

with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
    PROMPT_TEMPLATES = json.load(f)


def verificar_ambiente():
    pacotes = ["langgraph"]
    erros = []
    for pacote in pacotes:
        if importlib.util.find_spec(pacote) is None:
            erros.append(pacote)
    if erros:
        print("[Erro] Pacotes ausentes:", ", ".join(erros))
        print("Use: pip install " + " ".join(erros))
        sys.exit(1)
    else:
        print("[OK] Ambiente verificado com sucesso.")


def gerar_prompt(tipo, meta, contexto):
    if tipo not in PROMPT_TEMPLATES:
        raise ValueError("Tipo de prompt não suportado.")
    return PROMPT_TEMPLATES[tipo].format(meta=meta, contexto=contexto)


# Define o estado compartilhado do agente
class PromptState(TypedDict, total=False):
    tipo: str
    meta: str
    contexto: str
    prompt: Optional[str]
    next_node: Optional[str]


def supervisor(state):
    print("[Supervisor] Recebendo solicitação de geração de prompt...")
    return {"next_node": "builder"}


def builder(state):
    tipo = state.get("tipo")
    meta = state.get("meta")
    contexto = state.get("contexto")
    prompt = gerar_prompt(tipo, meta, contexto)
    print("\n[Prompt Gerado]\n")
    print(prompt)
    return {"prompt": prompt, "next_node": None}


# Construção do fluxo LangGraph
workflow = StateGraph(PromptState)
workflow.add_node("supervisor", supervisor)
workflow.add_node("builder", builder)
workflow.set_entry_point("supervisor")
workflow.add_edge("supervisor", "builder")
app = workflow.compile()

if __name__ == "__main__":
    verificar_ambiente()
    # Exemplo de entrada de teste
    initial_state = PromptState(
        {
            "tipo": "validacao_arquitetura",
            "meta": (
                "Auditar se o fluxo Supervisor → Workers "
                "está implementado corretamente"
            ),
            "contexto": (
                "O fluxo possui nó supervisor que roteia com base em mensagens "
                "e registra next_agent no estado."
            ),
        }
    )

    app.invoke(initial_state)
