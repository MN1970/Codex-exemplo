# Maestro Parallel Routing Test — Relatório

**Data:** 2026-07-25 10:12:45

**Total de testes:** 15
**Sucesso:** 14 / 15
**Taxa de acerto:** 93%

## Latência

- **Mínima:** 201.6ms
- **Máxima:** 201.8ms
- **Média:** 201.7ms

## Distribuição por Setor

| Setor | Corretos | Total | Taxa |

|-------|----------|-------|------|

| S01 | 2 | 2 | 100% |

| S02 | 2 | 2 | 100% |

| S03 | 2 | 2 | 100% |

| S04 | 2 | 2 | 100% |

| S06 | 2 | 2 | 100% |

| S07 | 1 | 2 | 50% |

| S08 | 2 | 2 | 100% |

| S09 | 1 | 1 | 100% |


## Falhas de Routing

| ID | Esperado | Roteado | Prompt |

|-------|----------|---------|--------|

| T12 | S07 | S06 | TPS: dimensões mínimas de terminal de pa... |


## Detalhes Completos

| ID | Esperado | Roteado | Latência | Status |

|-------|----------|---------|----------|--------|

| T01 | S01 | S01 | 201.6ms | ✅ |

| T02 | S01 | S01 | 201.6ms | ✅ |

| T03 | S02 | S02 | 201.6ms | ✅ |

| T04 | S02 | S02 | 201.7ms | ✅ |

| T05 | S03 | S03 | 201.7ms | ✅ |

| T06 | S03 | S03 | 201.7ms | ✅ |

| T07 | S04 | S04 | 201.7ms | ✅ |

| T08 | S04 | S04 | 201.7ms | ✅ |

| T09 | S06 | S06 | 201.7ms | ✅ |

| T10 | S06 | S06 | 201.8ms | ✅ |

| T11 | S07 | S07 | 201.8ms | ✅ |

| T12 | S07 | S06 | 201.8ms | ❌ |

| T13 | S08 | S08 | 201.8ms | ✅ |

| T14 | S08 | S08 | 201.8ms | ✅ |

| T15 | S09 | S09 | 201.8ms | ✅ |
