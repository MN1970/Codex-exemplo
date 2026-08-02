# 🚀 PHASE 2 — ROADMAP COMPLETO

**Status**: ⏳ **PLANIFICADO** (aguarda CHECKPOINT 1 GO)  
**Timeline**: 2026-08-08 a 2026-08-21 (14 dias)  
**Dependência**: Phase 1 CHECKPOINT 1 GO/NO-GO (2026-08-07 12:00)

---

## 📋 VISÃO GERAL PHASE 2

Phase 2 finaliza a operacionalização de Manta Maestro v5.0.1, adicionando 3 novos segmentos (S11/S12/S13) e consolidando infraestrutura crítica (RLS + DataDog + Supabase).

| Task | Componente | Timeline | Owner | Status |
|------|-----------|----------|-------|--------|
| **2.1** | D2 S11 Mineração | 08-15 a 08-17 | DevOps | Formalização |
| **2.2** | D4 Manta-09 Regulatório | 08-08 a 08-14 | Arquitetura | Novo agente |
| **2.3** | D3 RLS Produção | 08-04 a 08-05 | Security | Hardening |
| **2.4** | D5 DataDog Estável | 08-01 a 08-04 | Observability | Setup |
| **2.5** | D6 G012 Migração | 08-08 a 08-21 | Cloud | Consolidação |
| **2.6** | S12/S13 Production | 08-05+ | DevOps | Go-live |
| **2.7** | Estabilidade 14d+ | 08-08 a 08-21 | Todos | Monitoramento |

---

## 🎯 DECISÕES Q1-Q4 → EXECUÇÃO PHASE 2

### Q1: Embedder (✅ COMPLETO)
- **Decisão**: 1024d bge-m3, apenas documentar
- **Action em Phase 2**: Nenhuma (resolvido em Phase 1)
- **Status**: ✅ Done

### Q2: S11 Mineração (✅ GO)
- **Decisão**: SIM — Formalizar em Phase 2
- **Action**: Criar agente-mineracao.md + RAG + routing + SharePoint
- **Timeline**: 08-15 a 08-17 (semana 2 Phase 2)
- **Mesmo processo**: S12/S13, reutilizar checklist

### Q3: RLS Hardening (✅ GO)
- **Decisão**: SIM, acelerar para 5 dias (comprimido)
- **Action**: Design 1d + Staging 2d + Prod 2d
- **Timeline**: 08-01 a 08-05 (já em Phase 1!)
- **Produção**: 08-04 a 08-05, antes de Phase 2 começar

### Q4: G012 Supabase (✅ GO)
- **Decisão**: VIVO — Migrar xgluoaa para principal
- **Action**: Backup + consolidação + validação
- **Timeline**: 08-08 a 08-21 (Phase 2 full span)
- **Owner**: Cloud + DevOps

---

## 📊 TASKS PHASE 2 (7 PARALELOS)

### Task 2.1 — D2 S11 Mineração (DevOps)

**Escopo**: Formalizar S11 (já em produção mas sem agente.md/RAG/routing)

**Deliverables**:
1. `.claude/agents/agente-mineracao.md` (frontmatter + spec)
2. RAG collection `min:` (25-30 chunks)
   - NRM (Norma Regulamentadora 22)
   - JORC (Joint Ore Reserves Committee)
   - NI 43-101 (Canadense, referência)
   - Legislação mineração (ANM, SME, CIM)
3. Routing keywords (10+): mineração, cava, aluvionar, TSF, JORC, NRM, lavra
4. SharePoint folder: `/03_Projetos/Mineracao/`

**Timeline**: 08-15 a 08-17 (3 dias)  
**Owner**: DevOps  
**Blocker**: Nenhum (paralelo)  

**Checklist** (reutilizar S12/S13):
- [ ] Agent spec criada + reviewed
- [ ] RAG collection criada + 25+ chunks
- [ ] Routing keywords registradas
- [ ] SharePoint folders criadas + templates
- [ ] Maestro consegue rotear "mineração" → S11? ✅
- [ ] Go-live com S12/S13 simultâneo

---

### Task 2.2 — D4 Manta-09 Regulatório (Arquitetura)

**Escopo**: Criar agente horizontal dedicado a A9 (Regulatório)

**Situação atual**: A9 (Regulatório) distribuído entre verticais (ANEEL em S9, ANAC em S7, etc.). Sem agente horizontal centralizado.

**Decisão Phase 2**: Criar Manta-09 (como Manta 05 orçamento, Manta 07 cronograma, Manta 15 advisory).

**Deliverables**:
1. Agente Manta-09 (regulatório horizontal)
   - Centraliza análise ANEEL/ANAC/ANTAQ/ANP compliance
   - Referencia normas de todos segmentos
   - Handoff de S1-S13 quando necessário
2. Routing keywords: regulatório, licença, compliance, ANEEL, ANAC, etc.
3. RAG collection (opcional): normas-chave ABNT/leis
4. Model tier: Sonnet (normal), Opus (complexo)

**Timeline**: 08-08 a 08-14 (semana 1, antes de S11 formalização)  
**Owner**: Arquitetura + Manta 15  
**Blocker**: Nenhum (paralelo)

**Nota**: Coordenar com Manta 15 (advisory) para evitar overlap.

---

### Task 2.3 — D3 RLS Produção (Security)

**Status**: JÁ EM COURSE em Phase 1 (08-01 a 08-05)

**Escopo**: Aplicar RLS em 3 tabelas críticas

**Tabelas**:
1. `rag_collections` — agent vê apenas collections do seu segmento
2. `sp_agent_routing` — agent vê apenas suas rotas
3. `maestro_routing_keywords` — admin only (não agent visibility)

**Timeline**:
- Design: 08-01 (1d)
- Staging: 08-02 a 08-03 (2d)
- Production: 08-04 a 08-05 (2d)

**Owner**: Security + Database  
**Blocker**: Nenhum (paralelo, mas completa antes Phase 2)

**Go-live**: 2026-08-05 18:00 (antes de Phase 2 começar em 08-08)

---

### Task 2.4 — D5 DataDog (Observability)

**Status**: JÁ EM COURSE em Phase 1 (08-01 a 08-04)

**Escopo**: Setup APM, dashboards, alertas

**Deliverables**:
1. DataDog org + API key
2. Instrumentação agentes (SDK)
3. Dashboards:
   - Latência Maestro router (<500ms target)
   - RAG query performance
   - Agent response times
   - Error rates
4. Alertas: latência >500ms, errors >1%, downtime

**Timeline**: 08-01 a 08-04 (3-4d)  
**Owner**: Observability  
**Blocker**: Nenhum (paralelo)

**Go-live**: 2026-08-04 (antes Phase 2 começar)

---

### Task 2.5 — D6 G012 Supabase Consolidation (Cloud)

**Escopo**: Migrar projeto `xgluoaaymbdzbbudnwrh` → projeto principal `ogxxgvgtulrbbppshjie`

**Investigação Phase 1**: 08-01 a 08-02  
**Execução Phase 2**: 08-08 a 08-21

**Plano de Ação**:

**Dia 1 (08-08)**: Assessment
- [ ] Conectar a xgluoaaymbdzbbudnwrh
- [ ] Listar dados presentes (tables, rows)
- [ ] Identificar o que é importante vs legacy
- [ ] Documentar checklist migração

**Dias 2-10 (08-09 a 08-18)**: Execução
- [ ] Backup xgluoaa antes qualquer mudança
- [ ] Migrar dados críticos para ogxxgvgtulrbbppshjie
- [ ] Atualizar referências em CLAUDE.md/SKILL.md
- [ ] Redirecionar conexões do xgluoaa → principal
- [ ] Testar continuidade (zero data loss)

**Dias 11-14 (08-19 a 08-21)**: Cleanup
- [ ] Verificar zero quebras pós-migração
- [ ] Documentar lições aprendidas
- [ ] Sugerir deativar xgluoaa (após sucesso)

**Timeline**: 08-08 a 08-21 (14 dias, não urgente)  
**Owner**: Cloud + DevOps  
**Blocker**: Nenhum (não critica, pode ser paralelo)

---

### Task 2.6 — S12/S13 Production Go-live (DevOps)

**Escopo**: Publicar S12 (Óleo & Gás) + S13 (Edificações) em produção

**Dependência**: Task 1.5 completo (Phase 1)

**Deliverables**:
- RAG collections: og:*, edi:* ativas
- Routing keywords: 10+ per agent
- SharePoint folders: `/03_Projetos/OleoGas/`, `/03_Projetos/Edificacoes/`
- Maestro consegue rotear S12/S13? ✅

**Timeline**: 08-05+ (imediato após Task 1.5 completo)  
**Owner**: DevOps  
**Blocker**: Task 1.5 ✅ (crítico em Phase 1)

**Go-live**: Mesmo dia que S11 (08-17) para 3 segmentos simultâneos

---

### Task 2.7 — Estabilidade 14+ Dias (Todos)

**Escopo**: Monitoramento contínuo pós go-live de S11/S12/S13

**Atividades**:
- Daily standup 17:00 UTC (continuar)
- Monitor DataDog dashboards (latência, errors)
- Verificar RLS não quebrou (queries ainda <500ms)
- Feedback dos agentes (S11/S12/S13 funcionando?)
- Log de issues/hotfixes

**Timeline**: 08-08 a 08-21 (14 dias)  
**Owner**: Todos (on-call rotation)

**Success criteria**:
- Zero data loss
- Latência Maestro <500ms
- Agentes S11/S12/S13 despacháveis
- RLS funcionando (segregação confirmada)
- Zero critical incidents (ou hotfixed em <1h)

---

## 📅 CRONOGRAMA PHASE 2

```
WEEK 1 (08-08 a 08-14)
├── Mon 08-08
│   ├── Phase 1 CHECKPOINT 1 resultado (12:00 UTC)
│   ├── Task 2.2 Manta-09 design inicia
│   └── Task 2.5 G012 assessment inicia
├── Tue-Wed 08-09 a 08-10
│   ├── Task 2.2 Manta-09 review
│   └── Task 2.5 G012 migração inicia
├── Thu-Fri 08-11 a 08-12
│   ├── Task 2.2 Manta-09 testing
│   └── Task 2.5 G012 validação
└── Sat-Sun 08-13 a 08-14
    ├── Buffer/catch-up
    └── Prep for S11 formalização

WEEK 2 (08-15 a 08-21)
├── Mon 08-15
│   ├── Task 2.1 S11 Mineração inicia (3d sprint)
│   └── Task 2.5 G012 cleanup
├── Tue-Wed 08-16 a 08-17
│   ├── Task 2.1 S11 testing
│   └── 🟢 S11/S12/S13 GO-LIVE (simultâneo)
├── Thu-Fri 08-18 a 08-19
│   ├── Estabilidade monitoramento
│   └── Hotfixes se necessário
└── Sat-Sun 08-20 a 08-21
    ├── Estabilidade final check
    └── Documentação lessons learned
```

---

## 🎯 SUCCESS CRITERIA PHASE 2

Phase 2 é sucesso se:

1. ✅ **S11/S12/S13 operacionais** — 3 novos segmentos em produção
2. ✅ **Maestro roteia S11/S12/S13** — Keywords detectadas, agents despachados
3. ✅ **Manta-09 ativo** — Agente regulatório horizontal centralizado
4. ✅ **RLS hardened** — Dados segregados por role, queries <500ms
5. ✅ **DataDog monitorando** — Dashboards ao vivo, alertas funcionando
6. ✅ **G012 consolidado** — xgluoaa migrado ou descartado
7. ✅ **14d+ estabilidade** — Zero critical incidents, SLA 99.9%
8. ✅ **Documentação atualizada** — CLAUDE.md v5.0.2, SKILL.md v5.0.2

---

## 🔗 DEPENDÊNCIAS & BLOCKERS

### Bloqueadores Phase 2:
- 🔴 **Phase 1 CHECKPOINT GO** (2026-08-07 12:00) — sem isso, Phase 2 não começa
- 🔴 **Task 1.5 DevOps** (S12/S13 ops) — se não completo em Phase 1, atrasará go-live

### Paralelos (sem dependência):
- Task 2.2 (Manta-09) — independente
- Task 2.5 (G012) — independente
- Task 2.4 (DataDog) — completa antes Phase 2, mas não bloqueia
- Task 2.3 (RLS) — completa antes Phase 2, mas não bloqueia

---

## 📊 PHASE 2 IMPACT

**Resultado esperado**:

```
Manta Maestro v5.0.1 (Phase 1)
    + 3 novos segmentos (Phase 2)
    + 1 agente horizontal (Manta-09)
    + RLS segurança
    + DataDog observability
    = 26 agentes operacionais + 1 novo (Manta-09)
    = S1-S13 (13 segmentos) + S5 parcial
    = 14+ coleções RAG
    = Produção estável, monitorada, segura
```

**Capacidade adicionada**:
- Mineração (S11) — cava, subterrânea, aluvionar, TSF
- Óleo & Gás (S12) — downstream, midstream, refinaria
- Edificações (S13) — residencial, comercial, data center
- Regulatório (Manta-09) — compliance horizontal

---

## 🚀 PRÓXIMAS AÇÕES

**Hoje (Phase 1)**:
- ✅ Aprovar Phase 2 roadmap
- ✅ Confirmar owners para cada task
- ✅ Preparar templates (reutilizar S12/S13 para S11)

**CHECKPOINT 1 (2026-08-07 12:00)**:
- Decisão GO/NO-GO
- Se GO → Phase 2 inicia 08-08
- Se NO-GO → Extend Phase 1, reprogram Phase 2

**Phase 2 Kickoff (2026-08-08)**:
- Task 2.2 (Manta-09) e Task 2.5 (G012) iniciam
- Task 2.1 (S11) inicia semana 2
- Daily standups continuam 17:00 UTC

---

**Status**: ⏳ Phase 2 pronto para lançamento. Aguardando GO de Phase 1 CHECKPOINT (2026-08-07 12:00).
