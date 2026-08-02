# 🎯 PHASE 1 — PLANO DE AÇÃO FINAL

**Data**: 2026-08-01  
**Status**: ✅ **4 DECISÕES CAPTURADAS + 5 AGENTES SONNET COMPLETARAM ANÁLISE**  
**Próximo**: Executar 7 tarefas paralelas com timelines

---

## 📋 DECISÕES CONFIRMADAS (Q1-Q4)

| Q | Decisão | Timeline | Owner |
|---|---------|----------|-------|
| **Q1** | 384d → migrar AGORA (Fase 0) | 2026-08-01 (8h) | Cloud |
| **Q2** | SIM — S11 formalizar Fase 2 | 2026-08-15 (Fase 2) | DevOps |
| **Q3** | SIM mas ACELERAR RLS — 5d | 2026-08-01 a 08-05 | Security |
| **Q4** | VIVO — migrar projeto Supabase | 2026-08-08 a 08-21 (Fase 2) | Cloud |

---

## 🚀 TAREFAS PARALELAS — PLANO DETALHADO

### 1.1 — D1 Embedder Fase 0 (4h) ⚡ HOJE

**O quê**: Migrar embedder de 384-dimensional para 1024-dimensional

**Timeline**: 2026-08-01 06:00 a 14:00 UTC (8 horas máximo)

**Passos**:
1. (1h) Design migration strategy
   - Backup atual: exportar `manta_rag_chunks` com embeddings 384d
   - Estratégia: recompute ou reload?
   - Modelos: bge-m3 (multilingual) ou pasar bge-large-en-v1.5?
   
2. (3h) Executar migration
   - Atualizar coluna embedding (384 → 1024 dimensões)
   - Recompute embeddings via bge-m3 (Supabase Edge Functions ou local)
   - Validar: todos 204 chunks re-embedidos
   
3. (2h) Testing
   - RAG query test: embeddings antigos vs novos — ranking muda?
   - Latência: <500ms query? (pgvector distância 1024d é mais lenta?)
   - Acurácia: resultados melhoram conforme EMBEDDER-DECISION.md (+11-14%)?

4. (2h) Documentação
   - Resultado: 384d→1024d SIM/NÃO
   - Performance impact: latência delta
   - Checkpoint approval: Cloud confirma sucesso para QA/Security

**Owner**: Cloud  
**Success Criteria**: 0 errors, <500ms latency, all 204 chunks re-embedded  
**Blocker**: None (paralelo total)

---

### 1.2 — D3 RLS Hardening (5d COMPRESSED) 🔒 ACCELERATED

**O quê**: Implementar Row-Level Security em 3 tabelas críticas

**Tabelas**:
- `rag_collections` — Agent vê apenas collections do segmento dele
- `sp_agent_routing` — Agent vê apenas suas rotas de SharePoint
- `maestro_routing_keywords` — Admin only (public read, agent query via Maestro)

**Timeline Compressed** (Q3 decision): 2026-08-01 a 08-05 (5d ao invés de 8d)

**Dia 1 (08-01)**: Design RLS Policies
```sql
-- rag_collections: Admin unrestricted, Agent by collection_slug
CREATE POLICY "agent_sees_segment_rag"
  ON rag_collections FOR SELECT
  USING (
    auth.role() = 'admin'
    OR collection_slug LIKE CONCAT(auth.jwt() -> 'segmento', ':%')
  );

-- sp_agent_routing: Admin unrestricted, Agent by agent_id
CREATE POLICY "agent_sees_own_routing"
  ON sp_agent_routing FOR SELECT
  USING (
    auth.role() = 'admin'
    OR agent_id = auth.jwt() -> 'agent_id'
  );

-- maestro_routing_keywords: Admin only
CREATE POLICY "admin_keywords_only"
  ON maestro_routing_keywords FOR SELECT
  USING (auth.role() = 'admin');
```

**Dias 2-3 (08-02 a 08-03)**: Staging Testing
- Deploy em `manta-staging` (branch Supabase)
- Testes:
  - [ ] Admin user: pode ler todas as 3 tabelas?
  - [ ] Agent user (S8): pode ler apenas san:* da rag_collections?
  - [ ] Agent user (S9): pode ler apenas ene:* da rag_collections?
  - [ ] Anon user: é rejeitado (403)?
  - [ ] Query performance: <100ms mesmo com RLS?

**Dias 4-5 (08-04 a 08-05)**: Produção
- Deploy em `ogxxgvgtulrbbppshjie` (manta-maestro)
- Rollback plan: disable RLS se quebra
- Monitoring: erratas nos logs?

**Owner**: Security + Database  
**Success Criteria**: 0 test failures, 0 production errors, <100ms queries  
**Risk**: Compressed timeline = mais urgência, menos testing

---

### 1.3 — D5 DataDog APM Setup (3-4d) 📊 OBSERVABILITY

**O quê**: Setup observabilidade do Maestro em DataDog

**Timeline**: 2026-08-01 a 08-04 (3-4 dias)

**Passos**:
1. (2h) Criar organization DataDog
   - Signup DataDog (usar corporate account)
   - Configurar regions (US-East-1 ou EU)
   - API key + APP key (gerar)

2. (2h) Instalar DataDog agent
   - Maestro app: adicionar `dd-trace` ou `datadog-apm`
   - Configurar instrumentação: tracer inicializado
   - Transmissão: logs → DataDog (via agent local ou cloud)

3. (4h) Configurar dashboards APM
   - Monitor principal: Models/Latency/Costs
     * Claude Haiku latency (routing)
     * Claude Sonnet latency (vertical agents)
     * Claude Opus latency (complex queries)
   - Alerts:
     * Latency > 5s → warning
     * Error rate > 5% → critical
     * Token cost > budget → alert

4. (4h) Instrumentar Maestro code
   - Monitorar: router dispatch time
   - Monitorar: RAG query latency
   - Monitorar: model tier transitions (Haiku→Sonnet→Opus)
   - Tag traces: segment, activity, agent_id

**Owner**: Observability + DevOps  
**Success Criteria**: Dashboards live, 1000+ traces coletadas, alerts testadas  
**Metrics**:
- P50/P95/P99 latency por modelo
- Error rate
- Cost per query
- Model distribution (% Haiku/Sonnet/Opus)

---

### 1.4 — D6 G012 Cleanup (2d, investigation → Fase 2) 🗑️ CONSOLIDATION

**O quê**: Investigar projeto Supabase morto (xgluoaaymbdzbbudnwrh) e planejar consolidação

**Q4 Decision**: VIVO → Migrar para projeto principal em Fase 2

**Timeline Hoje (2026-08-01)**: Investigação (4h)

**Perguntas-Chave**:
1. Projeto `xgluoaa` contém dados críticos?
   - [ ] RAG chunks únicos (não em `manta-maestro`)?
   - [ ] Agent definitions únicas?
   - [ ] User/org data crítica?
   - [ ] Resposta: inventário detalhado

2. Por que 2 projetos?
   - [ ] Razão histórica (migração incompleta)?
   - [ ] Multi-tenancy (org1 vs org2)?
   - [ ] Teste (staging)?
   - [ ] Resposta: contexto

3. Outros projetos inativos:
   - `manta-tocantins` (INACTIVE)
   - `manta-rodovias` (INACTIVE)
   - `manta-portal-piloto` (INACTIVE)
   - [ ] Checklist: quais mantém, quais deletam?

**Plano Fase 2 (08-08 a 08-21)**:
1. Backup: export de xgluoaa (se dados críticos)
2. Migração: copiar dados para `ogxxgvgtulrbbppshjie`
3. Validação: nenhuma quebra
4. Cleanup: sugerir desativação xgluoaa

**Owner**: Cloud + MN  
**Success Criteria**: Inventário completo + migração planejada  
**Fase 2 Blocker**: None (Phase 1 = investigação apenas)

---

### 1.5 — S12/S13 Operacionalização (3d) 🚀 CRITICAL PATH

**O quê**: Tornar S12 (Óleo & Gás) e S13 (Edificações) despacháveis no Maestro

**Timeline**: 2026-08-01 a 08-05 (3 dias) — **BLOQUEIA 1.6 + 1.7**

**Dia 1 (08-01)**: RAG Collections

Criar 2 collections em `manta_rag_chunks`:

```sql
-- S12 Óleo & Gás
INSERT INTO rag_collections (name, slug, description) VALUES
('Óleo & Gás', 'og', 'Engenharia civil para downstream + midstream: refinarias, dutovias, terminais');

-- S13 Edificações
INSERT INTO rag_collections (name, slug, description) VALUES
('Edificações', 'edi', 'Residencial, comercial, galpão, hospitalar, data center — estrutura, fundações, sustentabilidade');
```

Ingerir documentos iniciais:
- S12: ANP standards, API 650/653, ASME B31, NFPA 30, HAZOP templates (mín. 10 chunks)
- S13: NBR 15575, LEED standards, BIM guidelines (mín. 10 chunks)

**Dia 2 (08-02)**: Routing Keywords

Registrar em `maestro_routing_keywords`:

```sql
-- S12 Keywords
INSERT INTO maestro_routing_keywords VALUES
('og', 'petróleo'), ('og', 'gasoduto'), ('og', 'oleoduto'), 
('og', 'refinaria'), ('og', 'ANP'), ('og', 'HAZOP'), ('og', 'API 650');

-- S13 Keywords  
INSERT INTO maestro_routing_keywords VALUES
('edi', 'edificação'), ('edi', 'prédio'), ('edi', 'edificio'),
('edi', 'galpão'), ('edi', 'data center'), ('edi', 'NBR 15575'), ('edi', 'LEED');
```

**Dia 3 (08-03)**: SharePoint Routing + Validation

```sql
-- S12 SharePoint Route
INSERT INTO sp_agent_routing VALUES
('agente-oleo-gas', '03_Projetos/OleoGas/*', '*.pdf,*.dwg,*.xlsx', 'metadata');

-- S13 SharePoint Route
INSERT INTO sp_agent_routing VALUES
('agente-edificacoes', '03_Projetos/Edificacoes/*', '*.pdf,*.dwg,*.xlsx', 'metadata');
```

Criar pastas SP (manual ou via MCP):
- `/Manta/03_Projetos/OleoGas/`
- `/Manta/03_Projetos/Edificacoes/`
- `/Manta/Skills/OleoGas/` (para agente .md)
- `/Manta/Skills/Edificacoes/` (para agente .md)

Testar routing:
- [ ] Query com "oleoduto" → agente-oleo-gas?
- [ ] Query com "data center" → agente-edificacoes?
- [ ] SharePoint upload: arquivo em OleoGas/ é indexado?

**Owner**: DevOps + Agentes  
**Success Criteria**: RAG searchable, routing keywords active, SharePoint folders ready  
**Bloqueia**: 1.6 (Smoke Tests) + 1.7 (Slack) — NÃO PODEM RODAR ATÉ 1.5 = ✅

---

### 1.6 — Smoke Tests (1d, após 1.5) ✅ QA VALIDATION

**O quê**: Validar 12 cenários (8 auto + 4 manuais) antes de go-live

**Bloqueado por**: 1.5 (S12/S13 ops completo)

**Timeline**: 2026-08-06 (1 dia) — pode rodar assim que 1.5 = ✅

**8 Testes Automatizados**:
1. Routing S1–S13: cada keyword → segmento correto?
2. RAG S12: query "oleoduto" → S12 chunks?
3. RAG S13: query "edificação" → S13 chunks?
4. SharePoint sync: arquivo novo → Maestro vê em 24h?
5. Maestro dispatch: @manta-maestro mention → response thread?
6. Model tiering: Haiku → Sonnet escalation por complexidade?
7. Embedder (Q1): 1024d vectors = melhor accuracy?
8. RLS (Q3): agent user = vê só seu segmento?

**4 Validações Manuais**:
1. **Prova de conceito S12**: "Projeto oleoduto 200km — estimar orçamento, cronograma, risco"
   - Agente-oleo-gas responde?
   - Handoffs para Manta 05/07/15?
   
2. **Prova de conceito S13**: "Data center em SP — NBR 15575, LEED A, BIM"
   - Agente-edificacoes responde?
   - Disciplinas ativadas (BIM, Ambiental, Estrutural)?

3. **Integração Cowork**: @manta-maestro mention em Teams
   - Menção capturada?
   - Resposta publicada em thread?
   - Link compartilhado em OneNote?

4. **Performance Benchmark**: 1000 queries paralelas
   - Latency P95 < 5s?
   - Error rate < 1%?
   - Cost within budget?

**Owner**: QA  
**Success Criteria**: 12/12 testes passando  
**Prerequisite**: 1.5 = ✅  
**Blocker para**: 1.7 (Slack Announcement)

---

### 1.7 — Slack Announcement (1d, após 1.6) 📢 COMMS

**O quê**: Anunciar go-live em #announcements + status Phase 1

**Bloqueado por**: 1.6 (Smoke tests 100%)

**Timeline**: 2026-08-06 (1 dia) — após 1.6 ✅

**Conteúdo da Mensagem**:

```
🚀 PHASE 1 COMPLETE — Manta Maestro v5.0.1

✅ 6/6 Decisões Executadas:
  • D1: Embedder 384d → 1024d [+11% accuracy]
  • D2: S11 Mineração — formalização Fase 2 GO
  • D3: RLS hardening — 3 tabelas protegidas
  • D4: G012 — projeto Supabase consolidação planejada
  • S12: Óleo & Gás — OPERACIONAL
  • S13: Edificações — OPERACIONAL

📊 Métricas:
  • 23 agentes (20 op + 2 novo + 1 identificado)
  • 9 coleções RAG (204 chunks)
  • Routing keywords: +14 novas (S12+S13)
  • SharePoint: +2 pastas projeto

🎯 Próximo: CHECKPOINT 1 (2026-08-07 12:00)
  Decisão: GO → Fase 2 (Manta-09 + S11 + stable production)

🔗 Documentação:
  • Status: /Manta/Documentação/STATUS-MANTA-v5.0.1-CONSOLIDADO.md
  • Portal: /manta-maestro-status-portal.html
  • Changelog: #manta-architect

📧 Dúvidas? @manta-maestro "qual é a próxima?"
```

**Owner**: Comms  
**Success Criteria**: Mensagem publicada, aprovação MN, link working  
**Prerequisite**: 1.6 = ✅

---

## 📅 CRONOGRAMA VISUAL

```
2026-08-01 (TODAY)
├─ 06:00 → Phase 1 START
├─ 06:00-14:00 → 1.1 D1 Embedder (8h) 🔄 PARALLEL
├─ 06:00-.... → 1.2 D3 RLS Design (1d) 🔄 PARALLEL
├─ 06:00-.... → 1.3 D5 DataDog (4h) 🔄 PARALLEL
├─ 06:00-.... → 1.4 D6 G012 Investigation (4h) 🔄 PARALLEL
├─ 06:00-.... → 1.5 S12/S13 (DAY 1 RAG) 🔄 PARALLEL
└─ 18:00 → Dia 1 status check ✓

2026-08-02
├─ 1.2 D3 RLS Staging testing (starts)
├─ 1.3 D5 DataDog setup (continues)
├─ 1.5 S12/S13 (DAY 2 Routing keywords)
└─ 17:00 → Daily standup ✓

2026-08-03
├─ 1.2 D3 RLS Staging (continues 2/3 days)
├─ 1.5 S12/S13 (DAY 3 SharePoint + validation)
└─ 17:00 → Daily standup ✓

2026-08-04
├─ 1.3 D5 DataDog (COMPLETE expected) ✅
├─ 1.2 D3 RLS Production (starts)
└─ 17:00 → Daily standup ✓

2026-08-05
├─ 1.2 D3 RLS Production (completes) ✅
├─ 1.5 S12/S13 (COMPLETE expected) ✅ ← UNBLOCKS 1.6+1.7
└─ 17:00 → Daily standup ✓

2026-08-06
├─ 1.6 Smoke Tests (8 auto + 4 manual) 🔄
├─ 1.7 Slack Announcement (after 1.6 ✅)
└─ 17:00 → Daily standup ✓

2026-08-07 12:00 ⚡
└─ CHECKPOINT 1 — GO/NO-GO Fase 2
   Avaliar: D1, D3, D5, D6 + S12/S13 + 1.6 + 1.7
   Decisão: GO → Fase 2 (2026-08-08 start)
```

---

## 📊 SUCESSO = CHECKPOINT 1 GO

**6 critérios todos ✅**:
- [ ] D1 Embedder: 384d→1024d migração sucesso
- [ ] D3 RLS: Policies em prod, zero quebras
- [ ] D5 DataDog: Métricas live + dashboards
- [ ] D6 G012: Investigação + migração Fase 2 planejada
- [ ] S12/S13: RAG + routing + SharePoint ✅
- [ ] 1.6+1.7: Smoke tests 100% + announcement sent

**GO Autorização**: MN approva → Fase 2 (2026-08-08)
**NO-GO Contingency**: Extend Fase 1 até resolver, re-checkpoint 2026-08-09

---

## 📞 COMMUNICATIONS

- **Daily standup**: 17:00 UTC (5min status check)
- **Blockers**: Reportar imediatamente (não aguardar standup)
- **Checkpoint**: MN final decision 2026-08-07 12:00 UTC

---

**Status Final**: ✅ Plano executável, 4 decisões capturadas, 7 tarefas detalhadas, timeline clara até GO Fase 2.

Próximo: Execute Phase 1 segundo este plano. Monitorar diariamente. CHECKPOINT 1 em 2026-08-07 12:00.
