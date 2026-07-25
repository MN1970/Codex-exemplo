# Maestro Parallel Routing Test — Relatório

**Data:** 2026-07-25 10:12:30

**Total de testes:** 15
**Sucesso:** 13 / 15
**Taxa de acerto:** 86%

## Latência

- **Mínima:** 200.9ms
- **Máxima:** 201.0ms
- **Média:** 200.9ms

## Distribuição por Setor

| Setor | Corretos | Total | Taxa |

|-------|----------|-------|------|

| S01 | 2 | 2 | 100% |

| S02 | 2 | 2 | 100% |

| S03 | 2 | 2 | 100% |

| S04 | 2 | 2 | 100% |

| S06 | 2 | 2 | 100% |

| S07 | 0 | 2 | 0% |

| S08 | 2 | 2 | 100% |

| S09 | 1 | 1 | 100% |


## Falhas de Routing

| ID | Esperado | Roteado | Prompt |

|-------|----------|---------|--------|

| T11 | S07 | UNKNOWN | RBAC 154: qual é a categoria de pista de... |

| T12 | S07 | S06 | TPS: dimensões mínimas de terminal de pa... |


## Detalhes Completos

| ID | Esperado | Roteado | Latência | Status |

|-------|----------|---------|----------|--------|

| T01 | S01 | S01 | 200.9ms | ✅ |

| T02 | S01 | S01 | 200.9ms | ✅ |

| T03 | S02 | S02 | 200.9ms | ✅ |

| T04 | S02 | S02 | 200.9ms | ✅ |

| T05 | S03 | S03 | 200.9ms | ✅ |

| T06 | S03 | S03 | 200.9ms | ✅ |

| T07 | S04 | S04 | 200.9ms | ✅ |

| T08 | S04 | S04 | 200.9ms | ✅ |

| T09 | S06 | S06 | 200.9ms | ✅ |

| T10 | S06 | S06 | 200.9ms | ✅ |

| T11 | S07 | UNKNOWN | 200.9ms | ❌ |

| T12 | S07 | S06 | 200.9ms | ❌ |

| T13 | S08 | S08 | 201.0ms | ✅ |

| T14 | S08 | S08 | 201.0ms | ✅ |

| T15 | S09 | S09 | 201.0ms | ✅ |
