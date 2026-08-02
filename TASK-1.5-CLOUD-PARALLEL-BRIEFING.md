# 🚨 TASK 1.5 PARALLEL EXECUTION — CLOUD TEAM

**Status**: 🔴 **DEVOPS NO-SHOW** — reassigned to Cloud team for parallel execution  
**Priority**: 🔴 **MÁXIMA CRITICIDADE — BLOQUEADOR DO CAMINHO CRÍTICO**  
**Timestamp**: 2026-08-01 (T+1h after DevOps briefing went unanswered)  
**Owner**: Cloud team (Task 1.4 reassignment)  
**Deadline**: 2026-08-05 18:00 UTC (3 dias, imóvel)

---

## 📌 SITUAÇÃO

DevOps has not initiated work on Task 1.5 (S12/S13 operationalization) after 1+ hour since briefing dispatch. To keep Phase 1 critical path moving, **Cloud team is taking over the execution in parallel** with their current Task 1.4 (G012 investigation).

**Why Cloud team is best positioned**:
- Already accessing project `ogxxgvgtulrbbppshjie` (principal Supabase) for G012 audit
- Already have SQL execution capability via MCP Supabase tools
- SharePoint access already confirmed for investigation
- No additional tooling/access needed
- 1.5 execution **complements** 1.4 (consolidation investigation → actual consolidation setup)

---

## 🎯 TASK 1.5 EXECUTION CHECKLIST (CLOUD TEAM)

### Part 1: RAG Collections (Supabase `manta_rag_chunks`)

**Collection 1: `og:` — Óleo & Gás**
- [ ] Create collection in `rag_collections` table:
  - `name`: "óleo-gás"
  - `prefix`: "og:"
  - `description`: "Óleo & Gás — downstream + midstream (ANP, API, ASME, NFPA, HAZOP)"
  - `source`: "ANP, API 650/653, ASME B31.3/4/8, NFPA 30, HAZOP"
- [ ] Insert 20–30 chunks into `manta_rag_chunks`:
  - Embedding: **1024-dimensional bge-m3** (confirmed from audit)
  - Sources: ANP normas, API 650 (tanks), ASME B31 (pipelines), NFPA 30 (flammable), HAZOP methodology
  - Example chunks:
    - "API 650: Design, fabrication and installation of vertical welded steel tanks for oil storage"
    - "ASME B31.3: Process Piping — design, materials, fabrication, assembly, testing, inspection, operation"
    - "NFPA 30: Flammable and combustible liquids code — storage, handling, use"
    - "ANP Resolução 14/2007: Especificações de derivados de petróleo"
    - "HAZOP — Hazard and Operability Study methodology for pipeline and terminal design"
  - Metadata: `agent_id: "03-S12"`, `segment: "S12"`, `active: true`, `vector_dimension: 1024`

**Collection 2: `edi:` — Edificações**
- [ ] Create collection in `rag_collections` table:
  - `name`: "edificações"
  - `prefix`: "edi:"
  - `description`: "Edificações — residencial, comercial, hospitalar, data center (NBR 15575, LEED, BIM)"
  - `source`: "NBR 15575, LEED, BIM normas"
- [ ] Insert 20–30 chunks into `manta_rag_chunks`:
  - Embedding: **1024-dimensional bge-m3** (same embedder as all collections)
  - Sources: NBR 15575 (performance), LEED criteria, BIM standards, structural design
  - Example chunks:
    - "NBR 15575: Desempenho de edificações habitacionais — requisitos técnicos"
    - "LEED v4.1: Leadership in Energy and Environmental Design — sustainability criteria"
    - "BIM ISO 19650 — Building Information Modelling — information management"
    - "NBR 6118: Design of concrete structures — structural design"
    - "NBR 7187: Design of concrete structures for bridges — loads and combinations"
  - Metadata: `agent_id: "03-S13"`, `segment: "S13"`, `active: true`, `vector_dimension: 1024`

**Reference**: Both collections follow same schema as S6–S10 collections (audited in `docs/SUPABASE-PROJECT-AUDIT.md`):
```sql
-- Schema reference from manta_rag_chunks:
id, collection_id, document_id, chunk_index, text, vector, metadata, created_at, updated_at
```

---

### Part 2: Routing Keywords (Supabase `maestro_routing_keywords`)

**S12 Keywords — Óleo & Gás**:
- [ ] Insert 10+ keywords into `maestro_routing_keywords`:
  - Keywords: `petróleo`, `óleo e gás`, `gasoduto`, `oleoduto`, `dutovia`, `refinaria`, `ANP`, `tancagem`, `API 650`, `ASME B31`, `NFPA 30`, `HAZOP`, `terminal de combustíveis`, `GLP`, `distribuidora`
  - Weight: `0.8–0.9` (high confidence, same as S6–S10)
  - Agent: `03-S12` (agente-oleo-gas)
  - Active: `true`

**S13 Keywords — Edificações**:
- [ ] Insert 10+ keywords into `maestro_routing_keywords`:
  - Keywords: `edificação`, `torre residencial`, `comercial`, `galpão`, `warehouse`, `data center`, `hospital`, `universidade`, `MCMV`, `NBR 15575`, `LEED`, `BIM`, `estrutura`, `fundação`
  - Weight: `0.8–0.9` (high confidence, same as S6–S10)
  - Agent: `03-S13` (agente-edificacoes)
  - Active: `true`

**Verification**: After insertion, `maestro_routing_keywords` should have 50+ total rows (9 existing + 20 new S12/S13).

---

### Part 3: SharePoint Folders

**Folder 1: `/03_Projetos/OleoGas/`**
- [ ] Create folder structure in SharePoint:
  ```
  /03_Projetos/OleoGas/
  ├── README.md (template below)
  ├── /01_Documentos (for PDFs, normas)
  ├── /02_Desenhos (for DWGs, P&IDs)
  ├── /03_Orçamentos (for cost estimates)
  ├── /04_Cronogramas (for schedules)
  └── /05_Claims (for dispute docs)
  ```
- [ ] README.md content:
  ```markdown
  # Óleo & Gás (S12) — Projetos
  
  Repositório compartilhado para projetos de óleo & gás (downstream + midstream).
  Roteiro: ANP, API 650/653, ASME B31, NFPA 30, HAZOP.
  
  **Agente**: Manta 03-S12 (agente-oleo-gas)
  **Mentor**: [Cloud team contact]
  ```

**Folder 2: `/03_Projetos/Edificacoes/`**
- [ ] Create folder structure in SharePoint:
  ```
  /03_Projetos/Edificacoes/
  ├── README.md (template below)
  ├── /01_Documentos (for PDFs, normas)
  ├── /02_Desenhos (for DWGs, BIM models)
  ├── /03_Orçamentos (for cost estimates)
  ├── /04_Cronogramas (for schedules)
  └── /05_Claims (for dispute docs)
  ```
- [ ] README.md content:
  ```markdown
  # Edificações (S13) — Projetos
  
  Repositório compartilhado para projetos de edificações (residencial, comercial, galpão, hospitalar, data center).
  Roteiro: NBR 15575, LEED, BIM.
  
  **Agente**: Manta 03-S13 (agente-edificacoes)
  **Mentor**: [Cloud team contact]
  ```

---

## 📋 DEFINITION OF DONE

Task 1.5 is complete when:

1. ✅ **S12 (Óleo & Gás) is routable by Maestro**
   - Collection `og:` exists with 20+ chunks (1024d embeddings)
   - 10+ keywords registered and active
   - SharePoint folder `/03_Projetos/OleoGas/` created with README
   - Test: Maestro can dispatch "ANP regulação de gasoduto" → `agente-oleo-gas`

2. ✅ **S13 (Edificações) is routable by Maestro**
   - Collection `edi:` exists with 20+ chunks (1024d embeddings)
   - 10+ keywords registered and active
   - SharePoint folder `/03_Projetos/Edificacoes/` created with README
   - Test: Maestro can dispatch "NBR 15575 desempenho habitacional" → `agente-edificacoes`

3. ✅ **SQL verification**
   - `SELECT COUNT(*) FROM rag_collections WHERE prefix IN ('og:', 'edi:')` → 2
   - `SELECT COUNT(*) FROM manta_rag_chunks WHERE collection_id IN (og, edi)` → 40+
   - `SELECT COUNT(*) FROM maestro_routing_keywords WHERE agent_id IN ('03-S12', '03-S13')` → 20+
   - Latency test: All queries execute in <500ms (Maestro router SLA)

4. ✅ **Production deployment**
   - All changes applied to principal Supabase project `ogxxgvgtulrbbppshjie`
   - No data loss, no query breaks, RLS policies unaffected
   - Both agents appear as "active, operacional" in `manta_agent_capabilities`

---

## 📅 TIMELINE — COMPRESSED (3 DAYS)

| Date | Phase | Checkpoint |
|------|-------|-----------|
| 08-01 (hoje) | Brief + Setup | SQL prepared, SharePoint access confirmed |
| 08-02 | Execute Supabase | RAG collections + keywords inserted in staging |
| 08-03 | Test + Validate | Latency <500ms, Maestro routing verified |
| 08-04 | Production | Deploy to ogxxgvgtulrbbppshjie, smoke tests prepared |
| 08-05 18:00 | ✅ DEADLINE | Task complete, ready for Task 1.6 (smoke tests) |

---

## 🔗 REFERENCES

- **Existing S6–S10 example**: `docs/SUPABASE-PROJECT-AUDIT.md` § "RAG Collections — 9 confirmadas"
- **Schema reference**: `docs/SUPABASE-PROJECT-AUDIT.md` § "Data audit — manta_rag_chunks structure"
- **Embedder confirmed**: 1024-dimensional bge-m3 (not 384d) — see column comment in production
- **Agents spec**: `.claude/agents/agente-oleo-gas.md`, `.claude/agents/agente-edificacoes.md`
- **SQL templates**: from `TASK-1.5-DEVOPS-BRIEFING.md` (adaptable for Cloud execution)

---

## ⚠️ BLOCKERS / RISKS

- **None identified** — Cloud team already has access + expertise from G012 investigation
- **Synergy**: executing Task 1.5 **during** Task 1.4 (G012 consolidation) means both Supabase projects can be reconciled in parallel

---

## 🎬 NEXT ACTION

**Cloud team**: Confirm receipt + start SQL preparation today.  
**MN**: Notify Cloud team lead of reassignment (this briefing link).  
**Timeline**: Standby for Cloud progress update at daily standup (17:00 UTC).

---

**Status**: ⏳ Awaiting Cloud team confirmation. Phase 1 critical path intact if Cloud executes in parallel.

