# Título

Supervisor Pattern em LangGraph: Modularização de Fluxos Multi-Agente

## Introdução

O padrão *Supervisor* organiza agentes de LLM em fluxos controlados por estados. Ao desacoplar papéis e etapas, o arquiteto mantém visibilidade detalhada do percurso e possibilita a escalabilidade por adição de novos nós.

## Vantagens

- **Isolamento de responsabilidades**: cada agente executa uma função única, o que facilita a depuração.
- **Rastreabilidade**: os estados do LangGraph registram contexto e ações, permitindo auditoria completa dos diálogos.
- **Escalabilidade**: novos comportamentos podem ser inseridos como nós especializados, sem alterar a lógica principal.

## Código

```python
from langgraph import Graph, Node
from agents import Planner, Coder, Reviewer

# Define nós especializados
planner = Node(Planner())
coder = Node(Coder())
reviewer = Node(Reviewer())

# Cria grafo Supervisor
workflow = Graph()
workflow.add_nodes([planner, coder, reviewer])
workflow.add_edge(planner, coder)
workflow.add_edge(coder, reviewer)

if __name__ == "__main__":
    workflow.run({"spec": "Adicionar endpoint para métricas"})
```

## Tabela de Boas Práticas

| Categoria | Prática Recomendada | Descrição Funcional |
|-----------|--------------------|---------------------|
| Serialização de estado | Persistir snapshots de contexto em estruturas imutáveis | Permite replay determinístico e simplifica testes |
| Segurança de loops | Definir contador de ciclos ou TTL para cada fluxo | Evita loops infinitos e controla consumo de tokens |
| Visualização de fluxo | Executar `print_ascii()` após configurar o grafo | Inspeciona a topologia e valida dependências |

## Conclusão

O Supervisor pattern em LangGraph simplifica a orquestração de múltiplos agentes de IA. Com estados bem definidos e acoplamento mínimo entre nós, a solução se torna robusta para aplicações corporativas que exigem rastreabilidade e fácil manutenção.
Para padronizar os nomes de nós e chaves, consulte [naming_conventions_langgraph.md](naming_conventions_langgraph.md).

## Quando aplicar o padrão

Empregue o Supervisor pattern sempre que for necessário direcionar dinamicamente a execução para agentes especializados ou recuperar de falhas sem interromper o fluxo principal. Ele se mostra útil em pipelines que exigem auditabilidade de cada passo e na expansão de comportamentos por meio de novos nós.

### Exemplo completo

O módulo [`langgraph_workflow.py`](src/glpi_dashboard/services/langgraph_workflow.py) demonstra o padrão em ação. Compile e execute o grafo com o comando abaixo:

```bash
PYTHONPATH=src python - <<'PY'
from glpi_dashboard.services.langgraph_workflow import build_workflow
wf = build_workflow().compile()
state = {"messages": ["fetch"], "next_agent": "", "iteration_count": 0}
print(wf.invoke(state)["messages"][-1])
PY
```

Esse trecho utiliza o Supervisor para decidir qual nó executa em seguida e retorna `fetched tickets` quando a chamada à API é concluída com sucesso.
