# 📋 DECISÕES MN — PHASE 1 (2026-08-01)

**Decisor**: Mauricio Neves (MN)  
**Data**: 2026-08-01  
**Status**: ✅ **TODAS AS 4 DECISÕES CAPTURADAS**

---

## Q1 — D1 Embedder Fase 0

**Pergunta**: Qual é a dimensão atual? Migrar agora ou depois?

**Decisão**: ✅ **384-dimensional → Migrar AGORA (Fase 0)**

**Implicações**:
- Embedder atual: 384-dimensional
- Ação: Migrar para 1024-dimensional EM FASE 0 (hoje/amanhã)
- Timeline: ~8 horas (design 2h + migration 4h + testing 2h)
- Aprovação: GO para Cloud executar
- Benefício: Acurácia RAG melhora 11-14% conforme doc EMBEDDER-DECISION.md

**Plano de Ação**:
1. Cloud: Design migration strategy (2h)
2. Cloud: Executar migration 384d → 1024d (4h)
3. QA: Validar embeddings (2h)
4. Documentar: Resultado em logs/fase-1/1.1-embedder-fase0.log

**Deadline**: 2026-08-01 18:00 UTC

---

## Q2 — D2 S11 Mineração

**Pergunta**: Formalizar S11 na Fase 2?

**Decisão**: ✅ **SIM — Formalizar S11 na Fase 2**

**Implicações**:
- S11 (Mineração) identificado em produção (`manta_agent_capabilities`, ativo=true desde 2026-07-12)
- Ação: Criar agente-mineracao.md + RAG + routing + SharePoint (idêntico a S12/S13)
- Timeline: 3 dias (Fase 2, semana 2 — 2026-08-15 a 08-17)
- Aprovação: GO para formalização completa

**Plano de Ação** (Fase 2):
1. Criar `.claude/agents/agente-mineracao.md` (frontmatter + descrição)
2. Criar RAG collection `min:` com documentação de mineração (NRM, JORC, etc.)
3. Registrar routing keywords em `maestro_routing_keywords` (minero, mineração, cava, aluvionar, TSF, etc.)
4. Criar pasta SharePoint `/Manta/03_Projetos/Mineracao/`
5. Publicar em produção (go-live 3 segmentos: S11/S12/S13)

**Owner**: DevOps + Agentes  
**Deadline**: 2026-08-17  

**Nota**: Mesmo processo de S12/S13 — reutilizar checklist.

---

## Q3 — D3 RLS Hardening

**Pergunta**: Aprovar plano de 8 dias?

**Decisão**: ✅ **SIM mas ACELERAR — 5 dias total**

**Implicações**:
- Ao invés de: 2d design + 3d staging + 2d prod + 1d verify (8d)
- Novo: 1d design + 2d staging + 2d prod (5d total)
- Timeline: 2026-08-01 a 2026-08-05 (compressed)
- Risco: Maior, mas factível se Security trabalhar em paralelo

**Plano de Ação** (Compressed 5 dias):

**Dia 1 (2026-08-01)**: Design
- Security: Draft RLS policies para 3 tabelas
  - `rag_collections`: agent vê apenas collections do seu segmento
  - `sp_agent_routing`: agent vê apenas suas rotas
  - `maestro_routing_keywords`: admin apenas
- SQL: Escrito e pronto para apply

**Dias 2-3 (2026-08-02 a 08-03)**: Staging Testing
- Deploy SQL em staging (`manta-staging` Supabase)
- Testes: Admin (full access) ✅ / Agent (restricted) ✅ / Anon (rejected) ✅
- 0 quebras antes de ir pra prod

**Dias 4-5 (2026-08-04 a 08-05)**: Produção
- Deploy SQL em produção (`ogxxgvgtulrbbppshjie`)
- Monitorar queries (latência <500ms)
- Confirm: Dados segregados por role

**Deadline**: 2026-08-05 18:00 UTC  
**Owner**: Security + Database  
**Aprovação**: GO para compressed timeline

---

## Q4 — D6 G012 Projeto Supabase

**Pergunta**: Projeto xgluoaaymbdzbbudnwrh está vivo ou morto?

**Decisão**: ✅ **VIVO — Migrar para projeto principal**

**Implicações**:
- Projeto `xgluoaaymbdzbbudnwrh` está ativo/vivo
- Ação: Migrar referências para projeto principal (`ogxxgvgtulrbbppshjie`)
- Timeline: Fase 2 (não bloqueia Fase 1, mas começa investigação hoje)
- Aprovação: GO para consolidação de 2 projetos em 1

**Plano de Ação**:

**Hoje (2026-08-01)**: Investigação
- Cloud: Verificar dados em xgluoaa (existem projetos/dados importantes lá?)
- Identificar o que precisa ser migrado vs descartado
- Documentar checklist de migração

**Fase 2 (2026-08-08 a 08-21)**: Execução
- Backup de dados críticos de xgluoaa
- Migrar/consolidar para `ogxxgvgtulrbbppshjie` (projeto principal)
- Validar: Nenhuma quebra, dados íntegros
- Sugerir: Deativar xgluoaa após sucesso migração

**Deadline**: 2026-08-21 (Fase 2)  
**Owner**: Cloud + DevOps  
**Nota**: Este é um G012 (gap) que estava aberto. Agora GO para resolução.

---

## 📊 RESUMO DE IMPACTO

| Decisão | Impacto | Timeline | Status |
|---------|---------|----------|--------|
| **Q1** | Embedder 384d → 1024d | 2026-08-01 (8h) | 🟢 GO |
| **Q2** | S11 formalização | 2026-08-15 (Fase 2) | 🟢 GO |
| **Q3** | RLS compressed 5d | 2026-08-01 a 08-05 | 🟢 GO (risco+reward) |
| **Q4** | G012 migração projeto | 2026-08-08 a 08-21 (Fase 2) | 🟢 GO |

---

## 🚀 ACTIONS IMEDIATAS (Hoje — 2026-08-01)

### Para Cloud (Q1 + Q4)
- [ ] Verificar dimensão vetor em `manta_rag_chunks` (Q1 confirmar 384d)
- [ ] Design migration strategy 384d → 1024d
- [ ] Investigar dados em xgluoaa (Q4 checklist)
- [ ] Deadline: 18:00 UTC

### Para Security (Q3)
- [ ] Iniciar design RLS policies (1d compressed)
- [ ] Draft SQL para 3 tabelas
- [ ] Preparar plano staging testing (2d)
- [ ] Deadline: 18:00 UTC

### Para DevOps (Q2)
- [ ] Revisar processo S12/S13 (será usado para S11 em Fase 2)
- [ ] Preparar template para agent-mineracao.md
- [ ] Agendar fase 2 sprint (08-15)
- [ ] Deadline: 2026-08-08

### Para QA (Phase 1)
- [ ] Preparar smoke tests para 1.6 (após 1.5 completa)
- [ ] Incluir: embedder quality test (Q1)
- [ ] Incluir: RLS validation (Q3)

---

## 📅 CHECKPOINT 1 — CRITÉRIO GO

**Data**: 2026-08-07 12:00 UTC

| Item | Critério GO | Status |
|------|-------------|--------|
| D1 Embedder | Migração 384d → 1024d completa + testing ✅ | 🔄 In Progress |
| D3 RLS | Policies em produção + zero quebras + staging 100% ✅ | 🔄 In Progress |
| D5 DataDog | Métricas coletando + dashboards ativos ✅ | 🔄 In Progress |
| D6 G012 | Investigação completa, migração fase 2 planejada ✅ | 🔄 In Progress |
| S12/S13 | RAG + routing + SP criados, 1.6 testes 100% ✅ | 🔄 In Progress |

**Decisão**: 5/5 critérios ✅ = **GO → Fase 2 (2026-08-08)**

---

## 📋 APROVAÇÃO

**Decisor**: Mauricio Neves (MN)  
**Data**: 2026-08-01 HH:MM UTC  
**Assinatura**: ✅ Respondido via AskUserQuestion  

**Próximo**: Comunicar decisões aos owners (Cloud, Security, DevOps, QA) e monitorar execução diária até checkpoint.
