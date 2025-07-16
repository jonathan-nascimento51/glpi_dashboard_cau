# Guia de Migração Incremental para Microsserviços

| Fase | Passos-Chave | Métricas SMART |
| --- | --- | --- |

| 1. Identificação | - Monitorar churn de código em módulos

- Avaliar tempo médio de build e deploy
- Mapear bugs recorrentes | - Módulo com >30% de linhas modificadas a cada release
- Build >15 min ou deploy >10 min
- 5 bugs no trimestre no mesmo módulo |

| 2. Extração | - Criar repositório e pipeline independentes

- Implementar testes de integração
- Definir contrato de API |
- Serviço extraído com cobertura de testes >85%
- Pipeline de CI executando em <5 min |

| 3. Estrangulamento |

- Redirecionar chamadas do monólito para o novo serviço via API Gateway
- Usar Event-Carried State Transfer quando necessário |
- Percentual de tráfego encaminhado ao serviço atinge 100% em até 3 sprints
- Latência adicional <10% comparado ao monólito |

| 4. Depreciação |

- Remover código antigo do monólito
- Atualizar documentação e rotinas de monitoramento |
- Código legado removido em <2 sprints
- Redução de tempo de deploy do monólito em 30% |

O processo segue a ordem de identificar gargalos, extrair serviço bem testado, redirecionar gradualmente as chamadas (Strangler Fig Pattern) e finalmente remover o código redundante. Monitorar métricas de churn, tempo de build/deploy e ocorrências de bugs ajuda a decidir quando e o que extrair.
