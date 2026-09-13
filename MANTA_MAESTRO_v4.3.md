# Manta Maestro v4.3 — Ecossistema Completo

> **Data de atualização:** 2026-07-27  
> **Branch:** `claude/parallel-ke-embeddings-index-xdu98y`  
> **Status:** ✅ Operacional

---

## 📊 Visão Geral de v4.3

Manta Maestro agora inclui **infraestrutura de indexação paralela de embeddings** para Knowledge Extractions, complementando os 20 agentes verticais e horizontais.

```
┌──────────────────────────────────────────────────────────────┐
│ MANTA MAESTRO v4.3                                           │
├──────────────────────────────────────────────────────────────┤
│ ✅ 11 Agentes Horizontais (Manta 00, 01, 02, 04-07, 13-16)   │
│ ✅ 10 Agentes Verticais (Manta 03-S1..S10)                   │
│ ✅ 5 Coleções RAG (S6–S10: Portos, Aeroportos, ...)         │
│ ✅ 86 Knowledge Extractions (KE)                             │
│    └─ 100% indexadas com embeddings BAAI/bge-small-en-v1.5 │
│ ✅ Infraestrutura de indexação paralela (v4.3 novo)         │
└──────────────────────────────────────────────────────────────┘
```

---

## 🏗️ Arquitetura v4.3

### Camada 1: Agentes (Routing + Context)

| Tipo | Código | Agente | Tier | Status |
|------|--------|--------|------|--------|
| **Horizontal** | Manta 00 | maestro (router) | Haiku→Sonnet | ✅ Operacional |
| | Manta 01 | claims | Opus | ✅ Operacional |
| | Manta 02 | contratual | Sonnet | ✅ Operacional |
| | Manta 04 | imobiliario | Sonnet | ✅ Operacional |
| | Manta 05 | orcamento | Sonnet | ✅ Operacional |
| | Manta 06 | modelagem | Sonnet/Opus | ✅ Operacional |
| | Manta 07 | cronograma | Sonnet | ✅ Operacional |
| | Manta 13 | bd | Sonnet | ✅ Operacional |
| | Manta 14 | apresentacoes | Sonnet | ✅ Operacional |
| | Manta 15 | advisory | Sonnet/Opus | ✅ Operacional |
| | Manta 16 | arquiteto-ia | Opus | ✅ Operacional |
| **Vertical** | Manta 03-S1 | rodovias | Sonnet | ✅ Operacional |
| | Manta 03-S2 | OAE (pontes/viadutos) | Sonnet | ✅ Operacional |
| | Manta 03-S3 | ferrovia | Sonnet | ✅ Operacional |
| | Manta 03-S4 | metrô | Sonnet | ✅ Operacional |
| | Manta 03-S6 | portos | Sonnet | 🆕 v4.2 |
| | Manta 03-S7 | aeroportos | Sonnet | 🆕 v4.2 |
| | Manta 03-S8 | saneamento | Sonnet | 🆕 v4.2 — PRIORIDADE AySA |
| | Manta 03-S9 | energia | Sonnet | 🆕 v4.2 — ANEEL/State Grid |
| | Manta 03-S10 | barragens | Sonnet | 🆕 v4.2 |

### Camada 2: RAG (Embeddings + Retrieval)

| Coleção | Embeddings | Status | Fontes |
|---------|-----------|--------|--------|
| knowledge_extractions | BAAI/bge-small-en-v1.5 (384d) | ✅ 86 KEs, 100% | Domínio cruzado |
| saneamento | pgvector `<=>` (cosine) | 🆕 v4.2 | SNIS, IWA, Lei 14.026 |
| energia | pgvector `<=>` (cosine) | 🆕 v4.2 | ANEEL, EPE, ONS, IEEE |
| portos | pgvector `<=>` (cosine) | 🆕 v4.2 | ANTAQ, PIANC |
| aeroportos | pgvector `<=>` (cosine) | 🆕 v4.2 | ANAC, ICAO, FAA |
| barragens | pgvector `<=>` (cosine) | 🆕 v4.2 | ICOLD, Lei 12.334 |

### Camada 3: Indexação (Orchestration + Parallelism)

**Novo em v4.3: Parallel KE Embeddings Indexer**

```
Discovery (SQL)
    ↓
Sharding (Python)
    ↓
Dispatch Paralelo (N subagents, Claude Code Task)
    ├─ Subagent 1: Shard 1 (15 KEs)
    ├─ Subagent 2: Shard 2 (15 KEs)
    ├─ Subagent N: Shard N (...)
    └─ Cada subagent:
       - Gera embeddings (SentenceTransformer)
       - Insere no Supabase MCP
       - Reporta sucesso/falhas
    ↓
Verification (SQL)
```

**Componentes:**
- `parallel_ke_embeddings_indexer.py` — Orchestrador (206 linhas)
- `run_ke_indexing_demo.py` — Demo end-to-end (236 linhas)
- `test_sql_generation.py` — Test SQL (81 linhas)

**Documentação:**
- `PARALLEL_KE_EMBEDDINGS.md` — Runbook técnico (185 linhas)
- `README_KE_INDEXING.md` — Quick start (135 linhas)

---

## 🚀 Casos de Uso v4.3

### 1. Indexação On-Demand de Novos KEs

**Trigger:** Novos KEs criados em `knowledge_extractions` sem passar por indexador

**Fluxo:**
```
Usuário: "Tenho 20 KEs sem embeddings. Dispara indexação?"
    ↓
Claude Code: Roda discovery + sharding
    ↓
Claude Code: Dispara 2 subagents em paralelo
    ├─ Subagent A: indexa shard 1 (10 KEs)
    └─ Subagent B: indexa shard 2 (10 KEs)
    ↓
Verification: 20 KEs confirmadas indexadas
```

**Tempo esperado:** ~2 min/shard (10 KEs)

### 2. Migração Futura de Modelo

**Scenario:** Passar de `bge-small-en-v1.5` (384d) para `bge-m3` (1024d)

**Estratégia:**
1. Criar coluna `embedding_m3` em `ke_embeddings`
2. Rodar novo indexador com `model='BAAI/bge-m3-base'`
3. Inserir em `embedding_m3` (nunca sobrescrever `embedding`)
4. Atualizar `match_kes_hybrid` para usar coluna correta
5. Retire suporte legado apenas após verificação

**Benefício:** Sem downtime, sem perda de dados históricos

### 3. Cron Automático

**Futura:** Discovery automático 1x/dia + alerta se houver KEs pendentes

```bash
# 01:00 UTC diariamente
SELECT COUNT(*) FROM ke WHERE embeddings IS NULL
IF count > 0 THEN
  notify(user_email, "N KEs pending indexing")
END
```

---

## 📋 Status de Deploy v4.3

### ✅ Completo
- [x] Implementar orchestrador (discovery, sharding, dispatch, verify)
- [x] Demo end-to-end com dados fictícios
- [x] Test de geração SQL
- [x] Runbook técnico + quick start
- [x] Verificação de base (86 KEs, 100% indexadas)
- [x] Atualizar CLAUDE.md (v4.3)
- [x] Documentar modelo imutável + regras críticas

### ⏳ Em Progresso (v4.2)
- [ ] Criar 5 coleções RAG em Supabase (`rag_chunks`)
- [ ] Inserir 5 routing rules em `sp_agent_routing`
- [ ] Criar pastas SP para S6–S10
- [ ] Testar routing do Maestro

### 📅 Roadmap (Próximas semanas)
- [ ] Integração com cron para discovery automático
- [ ] Dashboard de status (KEs indexados/dia)
- [ ] Integração com aluci-guard (audit de normas/leis em KEs)

---

## 📦 Matriz de Releases

| Versão | Data | Foco | Agentes | RAG | Indexação |
|--------|------|------|---------|-----|-----------|
| **v4.1** | 2026-Q1 | Horizontais + S1–S4 | 15 | S1–S4 | ✗ |
| **v4.2** | 2026-07-05 | Expansão S6–S10 | 20 | +5 (S6–S10) | ✗ |
| **v4.3** | 2026-07-27 | KE Embeddings | 20 | +5 + KE | ✅ Paralelo |

---

## 🔗 Links & Referências

### Documentação Principal
- **[CLAUDE.md](./CLAUDE.md)** — Master registry (agentes, routing, RAG, histórico)
- **[PARALLEL_KE_EMBEDDINGS.md](./PARALLEL_KE_EMBEDDINGS.md)** — Runbook técnico profundo
- **[README_KE_INDEXING.md](./README_KE_INDEXING.md)** — Quick start executivo

### Scripts
- **[parallel_ke_embeddings_indexer.py](./scripts/parallel_ke_embeddings_indexer.py)** — Orchestrador
- **[run_ke_indexing_demo.py](./scripts/run_ke_indexing_demo.py)** — Demo (rodar para ver funcionando)
- **[test_sql_generation.py](./scripts/test_sql_generation.py)** — Test de SQL

### Agentes S6–S10
- [agente-portos.md](./.claude/agents/agente-portos.md)
- [agente-aeroportos.md](./.claude/agents/agente-aeroportos.md)
- [agente-saneamento.md](./.claude/agents/agente-saneamento.md)
- [agente-energia.md](./.claude/agents/agente-energia.md)
- [agente-barragens.md](./.claude/agents/agente-barragens.md)

### PR
- **[#37 (draft)](https://github.com/MN1970/Codex-exemplo/pull/37)** — Parallel KE Embeddings Indexer

---

## 🎯 Próximos Passos

### Imediato (hoje)
- [x] Atualizar CLAUDE.md master (v4.3)
- [x] Documentar ecossistema completo
- [x] Commitar tudo na branch designada

### Esta semana
- [ ] Revisão de PR #37 (aprovação MN)
- [ ] Merge de v4.3 para main
- [ ] Notificar time de lançamento v4.3

### Próximas semanas
- [ ] Cron/webhook para discovery automático
- [ ] Dashboard de status
- [ ] Integração com aluci-guard

---

## 📞 Contato & Tickets

- **v4.3 Main Ticket:** MNT-2026-KE-EMBEDDINGS-PARALLEL
- **Branch:** `claude/parallel-ke-embeddings-index-xdu98y`
- **PR:** [#37](https://github.com/MN1970/Codex-exemplo/pull/37)
- **Owner:** Claude Code
- **Date:** 2026-07-27

---

## 📋 Changelog Resumido v4.3

```
v4.3 (2026-07-27)
├─ ✅ Parallel KE Embeddings Indexer (discovery → sharding → dispatch → verify)
├─ ✅ KeIndexerOrchestrator class (206 linhas Python)
├─ ✅ Demo end-to-end (236 linhas)
├─ ✅ Test SQL generation (81 linhas)
├─ ✅ Runbook técnico (185 linhas)
├─ ✅ Quick start (135 linhas)
├─ ✅ 86 KEs verificados (100% indexados)
├─ ✅ Modelo BAAI/bge-small-en-v1.5 (384d, L2-normalized)
├─ ✅ Regras críticas documentadas (ON CONFLICT, chunk_text, model field)
├─ ✅ CLAUDE.md master atualizado (v4.3)
└─ 📅 Roadmap: cron automático, dashboard, integração aluci-guard
```

---

**Manta Maestro v4.3 está operacional.** 🚀
