# RAG Optimization Benchmark — Executive Summary

**Data:** 39-query benchmark (Recall@1: 69.23%, Recall@3: 84.62%, Contaminação: 20.51%)  
**Status:** Below threshold — immediate action required  
**Root Cause:** 4 orthogonal issues in embedding + domain filtering

---

## Key Findings

### Contaminador Principal: S10 (Barragens)
- Representa 3 das 8 contaminações cruzadas (37.5%)
- Termos estruturais genéricos ("terraplenagem", "fundação", "drenagem") capturados incorretamente
- Embedding model não discrimina contexto (rodovia ≠ barragem para "terraplenagem")

### Termos Ambíguos Críticos
| Termo | Domínios afetados | Problema |
|-------|------------------|----------|
| terraplenagem | S1, S2, S10 | Subleito (rodovia) vs. aterro (barragem) |
| estrutura/fundação | S2, S10 | Fundação de ponte vs. fundação de barragem |
| drenagem | S6, S10 | Drenagem superficial (porto) vs. profunda (barragem) |
| via permanente | S3, S4 | Ferrovia vs. metrô (muito similares) |

---

## Recommended Action Plan

### Phase 1: HOJE (1-2h) — Strategy 1
**Normalização de prefixos + anti-termos**
- Reduzir peso de `bar:` de 1.0 → 0.85
- Adicionar tabela `domain_anti_terms` com 10-15 pares exclusivos
- Modificar função de busca para penalizar cross-domain
- **Impacto esperado:** Recall@1 +5-8%, contaminação -30-40%

### Phase 2: ESTA SEMANA (4-6h) — Strategy 2
**Enriquecer corpus com contexto diferenciador**
- Criar 50-100 synthetic chunks por domínio
- Adicionar `context_tag` + `disambiguator` para termos ambíguos
- Validar com domain experts
- Re-rodar benchmark
- **Impacto esperado:** Recall@1 +8-12%, contaminação -50-70%

### Phase 3: FALLBACK (8-12h) — Strategy 3
**Trocar embedding model + semantic layer**
- Avaliar upgrade ada-002 → text-embedding-3-large
- Implementar semantic disambiguation pós-embedding
- Custo-benefício: ⚠️ Alto esforço, execute APENAS se Phase 1+2 insuficientes

---

## Target Metrics After Implementation

| Métrica | Atual | Após S1 | Após S1+S2 | Após S1+S2+S3 |
|---------|-------|---------|-----------|---------------|
| **Recall@1** | 69.23% | 74-77% | 77-82% | 82-88% |
| **Recall@3** | 84.62% | 87-88% | 88-90% | 90-92% |
| **Contaminação** | 20.51% | 12-14% | 6-10% | 2-5% |

---

## Success Criteria
- ✅ Recall@1 ≥ 70% (CRITICAL)
- ✅ Contaminação ≤ 5% (CRITICAL)
- ✅ Recall@3 ≥ 85%

Phase 1 alone should hit first threshold; Phase 1+2 should hit all three.

---

## Next Step
Execute Phase 1 implementation today, then re-run benchmark to validate improvements.
