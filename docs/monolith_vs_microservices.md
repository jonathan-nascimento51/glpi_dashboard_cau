# Análise Monólito vs Microsserviços

| Fator | Monólito (1-5) | Justificativa | Microsserviços (1-5) | Justificativa |
| --- | --- | --- | --- | --- |
| Limites de módulo | 2 | Módulos pouco isolados; mudanças em uma área afetam todo o sistema. | 4 | Serviços independentes possibilitam delimitar regras e domínios mais claramente. |
| Implantação | 2 | Requer deploy completo para cada atualização. | 5 | Cada serviço pode ser implantado isoladamente, reduzindo risco e tempo de parada. |
| Escalabilidade | 3 | Escala a aplicação inteira; custo alto para crescer apenas partes específicas. | 5 | Escalabilidade fina — apenas os serviços mais demandados recebem mais recursos. |
| Diversidade tecnológica | 2 | Normalmente restrito a uma stack única, limitando experimentação. | 5 | Permite escolher a melhor tecnologia para cada serviço (ex.: Node.js para API, Python para processamento). |
| Complexidade operacional | 3 | Configuração e monitoramento simplificados, mas risco de gargalos em módulos críticos. | 2 | Necessita orquestração (containers, discovery, tracing), elevando esforço operacional. |
| Lei de Conway | 3 | Organização tende a se alinhar à estrutura monolítica; alterações de times ou processos demandam muito esforço. | 4 | Estrutura em serviços facilita mapear times a funcionalidades, reduzindo dependências cruzadas. |

**Recomendação**: Iniciar com monólito é indicado se a equipe e o escopo ainda são pequenos, permitindo maior velocidade de entrega e menor sobrecarga operacional. Conforme a aplicação crescer e pontos específicos demandarem escalabilidade ou ciclos de deploy mais frequentes, considere extrair gradualmente módulos para microsserviços (ex.: autenticação ou processamento intensivo). Avalie constantemente o custo de comunicação e a maturidade da equipe em DevOps antes de avançar.
