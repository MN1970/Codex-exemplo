# SKILL: sicro-similaridade
**Versão:** v1.0 | **Status:** Production-Ready | **Tipo:** Integração Orçamentária

---

## Overview

Skill de busca e completação automática de itens SICRO com matching híbrido (BM25 + TF-IDF) e enriquecimento contextual multi-dimensional. Processa planilhas de quantitativo e retorna SICRO validado com score de confiança, composição de preço e histórico comparativo.

**Caso de uso principal:** Completar orçamentos incompletos ou mal codificados em segundos com confiança > 75%.

---

## Entrada

| Campo | Tipo | Obrigatório | Exemplo |
|-------|------|-------------|---------|
| planilha_quantitativo | xlsx/csv | ✅ | `orcamento-obra-x.xlsx` |
| uf | string | ✅ | `"SP"`, `"RJ"`, `"MG"` |
| periodo | string | ✅ | `"07-2026"` (MM-AAAA) |
| modo_granularidade | enum | ❌ | `"basico"` \| `"composto"` \| `"auto"` (default: auto) |
| threshold_confianca | float | ❌ | `0.75` (default) |
| usar_historico_manta | bool | ❌ | `true` (default) |
| usar_benchmark_sinapi | bool | ❌ | `true` (default) |
| resolver_obsolescencia | bool | ❌ | `true` (default) |

---

## Saída

### Excel Final (padrão Manta)

Colunas:
- `codigo_sicro` — código vigente (ex: 73.456.001)
- `descricao` — descrição SICRO oficial
- `unidade` — UN, M, M², M³, etc. (validada)
- `custo_m` — Material (R$/UN)
- `custo_mo` — Mão-de-obra (R$/UN)
- `custo_eq` — Equipamento (R$/UN)
- `custo_total` — M + MO + EQ
- `similaridade_pct` — % (0-100)
- `score_confianca` — 0-100 (banda de decisão incluída)
- `banda_decisao` — `auto_aceita` | `revisar` | `rejeitar`
- `top3_alternativas` — [cod1, cod2, cod3]
- `flag_divergencia_preco` — true/false (cliente vs SICRO)
- `flag_obsolescencia` — true/false + código migrado
- `media_ponderada` — R$ (agregado)

### JSON Estruturado

```json
{
  "items": [
    {
      "entrada": {
        "descricao_original": "...",
        "unidade_original": "..."
      },
      "resultado": {
        "codigo_sicro": "73.456.001",
        "descricao": "...",
        "unidade": "M",
        "custos": {
          "material": 100.00,
          "mao_obra": 50.00,
          "equipamento": 10.00,
          "total": 160.00
        },
        "scores": {
          "similaridade": 0.92,
          "confianca": 87,
          "banda": "auto_aceita"
        },
        "alternativas": [
          { "codigo": "73.456.002", "score": 0.88 },
          { "codigo": "73.456.003", "score": 0.85 }
        ],
        "flags": {
          "divergencia_preco": false,
          "obsolescencia": false,
          "incompatibilidade_unidade": false
        }
      }
    }
  ],
  "auditoria": {
    "timestamp": "2026-07-27T14:30:00Z",
    "uf": "SP",
    "periodo": "07-2026",
    "total_itens_processados": 150,
    "total_items_confianca_alta": 145,
    "media_score_confianca": 0.82,
    "trilha_log": "..."
  }
}
```

---

## Arquitetura (5 Camadas)

### L1: Pré-processamento
- Validação de entrada (UF, período)
- Normalização de unidades (conversão M³ → M, etc)
- Classificação: item básico vs composto

### L2: Indexação Híbrida
- BM25 (léxico) + TF-IDF (vetorial)
- Índice SICRO segmentado por UF e mês
- Fallback em clusters técnicos

### L3: Enriquecimento
- Prior histórico Manta (80 mil projetos)
- Benchmark SINAPI
- Normas técnicas (NBR, DNIT, ICAO, etc)
- Detecção de obsolescência + de-para

### L4: Composição & Score
- M/MO/EQ por UF/período
- RelevanceRanker: calibra BM25 + TF-IDF + priors em 0-100%
- 3 bandas de decisão

### L5: Orquestração
- Pipeline determinístico end-to-end
- Geração Excel + JSON
- Integração com aluci-guard (auditoria)

---

## Performance

| Métrica | Target |
|---------|--------|
| Latência | 180ms (mediana) |
| Throughput | 55 itens/seg |
| Taxa de sucesso confiança > 75% | 92% |
| Taxa de falso-positivo | < 3% |

---

## Integração com Agentes Manta

- **agente-infraestrutura (S1-S4):** Rodovias, OAE, Ferrovia, Metrô
- **agente-saneamento (S8):** Completação de ETA/ETE
- **agente-energia (S9):** LT, subestações, usinas
- **manta-orcamento (Manta 05):** Orçamento master

---

## Aliases

```bash
/buscar-sicro
/completar-orcamento
/validar-sicro
/comparar-sicro
/sicro-similaridade
```

---

## Histórico

- **v1.0** (2026-07-27) — Launch com 16 agentes Sonnet orquestrados. BM25+TF-IDF híbrido. Supabase pgvector (BAAI/bge-small-en-v1.5).
