# Manta Maestro v5.0 — Agent Registry & Orchestration

**Registro mestre e especificação operacional dos agentes IA da Manta Associados.**

---

## O que é Manta Maestro v5.0?

Uma plataforma escalável de **20 agentes IA** (11 horizontais + 9 verticais S1–S10) sustentada por **8 pilares arquiteturais**:

1. **Routing Determinístico** — Maestro (R1) roteia prompts com 90%+ confiança
2. **Qualidade Vertical** — 5 novos agentes (S6–S10: Portos, Aeroportos, Saneamento, Energia, Barragens)
3. **Ciclo de Vida** — 8 fases: estudo prévio → encerramento
4. **RAG Híbrido** — BM25 + embedding + reranker em <50ms
5. **Tiering Automático** — Haiku/Sonnet/Opus via complexity score
6. **Observabilidade** — Run tracking imutável, custos, latência
7. **Orquestração Async** — APScheduler: reindex diário, feedback, limpeza
8. **Versionamento de Skills** — Checksums MD5, rollback automático, grace period 30d

---

## Arquivos Principais

### Documentação

| Arquivo | Propósito |
|---------|-----------|
| **CLAUDE.md** | Master registry: 20 agentes, 8 pilares, R1–R10, RAG, deploy checklist |
| **VERSIONS.json** | Checksums de todos 20 skills v5.0 + 9 RAG collections |
| **docs/ARQUITETURA-v5.0.md** | Detalhe dos 8 pilares (P1–P8) |
| **docs/DEPLOYMENT-GUIDE.md** | Step-by-step deploy (8 fases, 48h → go-live) |
| **docs/ROUTING-REFERENCE.md** | Especificação completa R1 (3-stage pipeline, keywords) |
| **DEPLOY-CHECKLIST.md** | Quick reference checklist (imprimir e marcar) |
| **docs/PORTAL-BACKEND-PLANO.md** | Plano de arquitetura do backend do Portal IA (MNT-2026-ARQ-0001) — proposta |

### Scripts

| Script | Função |
|--------|--------|
| **scripts/healthcheck.py** | Valida checksums, RAG, CLAUDE.md, settings.json |
| **scripts/rag-reindex.py** | Reindexação RAG diária (APScheduler trigger) |
| **scripts/tiering-audit.py** | Auditoria R7 (formula complexity score) |

---

## Começar

### 1. Ler (15 min)
- Cabeçalho + 8 pilares em **CLAUDE.md**
- **docs/ARQUITETURA-v5.0.md**

### 2. Validar (5 min)
```bash
python3 scripts/healthcheck.py
```

### 3. Deploy (4–6h)
Siga **DEPLOY-CHECKLIST.md** (8 fases)

---

## Performance Targets

| Métrica | Target | v4.2 | Improvement |
|---------|--------|------|------------|
| Routing latency | <500ms | ~800ms | 37% faster |
| RAG query | <50ms | ~200ms | 75% faster |
| Cost/run | $0.05–$0.08 | $0.12 | 40% cheaper |
| Latency p95 | <5s | ~8s | 37% faster |

---

**Manta Maestro v5.0 — Ready for deployment**

*Generated: 2026-07-25*
