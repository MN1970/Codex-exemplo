# Consolidação de 15 Investigações Paralelas — Manta Maestro v5.0.1

**Data**: 31 de julho de 2026  
**Método**: 15+ Sonnets em paralelo (workflow completado em ~17 minutos)  
**Status**: ✅ Consolidado com recomendações priorizadas  

---

## 🎯 RECOMENDAÇÕES CRÍTICAS (Gate MN #2)

### Prioridade IMEDIATA (semana 1-2 de agosto)

| Item | Recomendação | Urgência | Prazo | Impacto |
|------|--------------|----------|-------|---------|
| **G010 — Embedder** | OPÇÃO B: Migrar para multilingual-e5 (1024-d) | 🔴 CRÍTICO | 1 semana | RAG +11-14% acurácia (Recall, MRR, NDCG) |
| **RLS Security** | OPÇÃO 2: Full testing cycle (8 dias) | 🔴 CRÍTICO | 8 dias | Fecha vulnerabilidade de integridade |
| **S12/S13 Deployment** | Executar completo Fase 1 Sprint 2 | 🟠 ALTA | 1 semana | 2 segmentos novos operacionais |
| **G012 — Supabase xgluoaa** | OPÇÃO 1: Confirmar + remover | 🟠 ALTA | 7-14 dias | Remove confusão operacional |

### Prioridade ALTA (agosto, paralelo)

| Item | Recomendação | Prazo | ROI |
|------|--------------|-------|-----|
| **A9 — Regulatório (Manta-09)** | CRIAR agente horizontal dedicado | 1-2 meses | Payback <4 meses (100h/ano economizadas) |
| **Observability v1** | OPÇÃO B: DataDog APM | 10-14 dias | Debugging 2-4h → 15-30min |
| **S11 Mineração** | OPÇÃO A: Formalizar após S12/S13 validação | 2026-08-21 | Capacidade pronta, timing flex |

### Prioridade MÉDIA (future roadmap)

| Item | Recomendação | Timing |
|------|--------------|--------|
| **A10 — Risco (Manta-10)** | Formalizar APÓS Manta-09 | Setembro+ |
| **3 Projetos INACTIVE** | Consolidar/arquivar (AI-7/AI-8) | Setembro+ |
| **Embedder Validation** | Confirmar dimensão real em Supabase (G010 Fase 0) | Agosto |

---

## 📊 MATRIZ DE DECISÃO — 6 QUESTÕES MN

Antes de aprovar Fase 1 deployment paralelo completo, confirmar:

### D1: Embedder (G010) — Qual modelo?

**Contexto**: 3 documentos contradizem; A/B test comprova multilingual-e5 +11-14% melhor.

```
┌─────────────────────┬────────────┬──────────┬──────────┐
│ Modelo              │ Status     │ Tested   │ SLA      │
├─────────────────────┼────────────┼──────────┼──────────┤
│ bge-small (384-d)   │ Atual (?)  │ ❌ Não   │ 5.2ms    │
│ multilingual-e5     │ Recomendado│ ✅ Sim   │ 25ms ✅  │
│ bge-m3 (1024-d)     │ Teorizado  │ ❌ Não   │ 20-30ms  │
└─────────────────────┴────────────┴──────────┴──────────┘

RECOMENDAÇÃO: multilingual-e5 (empirically validated)
MN DECISION: Aprovar? [SIM/NÃO/DIFERIDO]
```

### D2: S11 Mineração — Quando formalizar?

```
OPÇÃO A: Após S12/S13 validação (2026-08-21)
  → Risco: reduzido | Timeline: +3 semanas | Custo: 30-40h

OPÇÃO B: Paralelo com S12/S13 (2026-08-07)
  → Risco: médio | Timeline: +0 semanas | Custo: 30-50h

OPÇÃO D: Preparar agora, go-live depois (hybrid)
  → Risco: baixo | Timeline: flex | Custo: 20-30h now + later

MN DECISION: A / B / D / Postergar?
```

### D3: RLS Security — Janela de deploy?

```
OPÇÃO 1: Emergência <6h (se anon em cliente web)
  → Timeline: 2026-08-01 (amanhã)
  
OPÇÃO 2: Full testing (8 dias)
  → Timeline: 2026-08-02 a 2026-08-07 (com Fase 1 deploy)

MN DECISION: 1 / 2? [Confirmar primeiro se anon está exposto]
```

### D4: A9 Regulatório — Criar Manta-09?

```
Opção 1: Manter distribuído (status quo)
  → Custo: 0 inicial; 120-160h/ano ineficiência

Opção 2: Criar Manta-09 horizontal (RECOMENDADO)
  → Custo: 32h inicial; ROI 100h/ano economizadas (payback <4 meses)
  → Ganho: eliminação de duplicação, handoff eficiente, escalabilidade

MN DECISION: Criar? [SIM/NÃO/FASE 2]
```

### D5: Observability v1 — Qual plataforma?

```
Opção A: CloudWatch (AWS)         | $158-400/mês | 5-7 dias | Sem APM nativo
Opção B: DataDog (recomendado)    | $200-600/mês | 10-14d   | APM completo ✅
Opção C: New Relic                | $500-600/mês | 12-16d   | Flat cost
Opção D: Prometheus+Grafana       | Grátis       | 14-21d   | Operação manual

MN DECISION: A / B / C / D? [Default: B se ativa, senão D]
```

### D6: G012 Supabase — Ação?

```
OPÇÃO 1: Confirmar (MN no dashboard) + Remover (2-3 dias)
  → Remove confusão, zero custo

OPÇÃO 2: Migrar dados antes (21-28 dias, se houver dados únicos)

OPÇÃO 3: Manter como "legado documentado" (não recomendado)

MN DECISION: 1 / 2 / 3? [Confirmação prévia: projeto xgluoaa existe/tem dados?]
```

---

## ✅ GATE MN #2 CHECKLIST

Antes de autorizar paralelo completo, confirmar:

- [ ] **D1 aprovado** — Embedder: multilingual-e5 SIM?
- [ ] **D2 aprovado** — S11: Opção A/B/D?
- [ ] **D3 aprovado** — RLS: 1 ou 2? (depende confirmação anon)
- [ ] **D4 aprovado** — Manta-09: criar agora ou Fase 2?
- [ ] **D5 aprovado** — Observability: A/B/C/D?
- [ ] **D6 confirmado** — Supabase: MN confirma xgluoaa via dashboard?

**Uma vez aprovadas**: liberado deploy paralelo COMPLETO (Fase 1 + observability v1 + RLS hardening em paralelo).

---

## 📋 ROADMAP CONSOLIDADO (Pós-Gate MN)

### Fase 1 (Semana 1: 2026-08-01 a 2026-08-07)

```
Paralelo:
  ├─ Sprint 1: S12/S13 RAG + SharePoint + routing
  ├─ Sprint 1: RLS policies aplicadas (se D3=2)
  ├─ Sprint 1: Embedder Fase 0 (verificação real Supabase)
  ├─ Sprint 1: Observability v1 setup (se D5≠Postergar)
  └─ Sprint 1: G012 AI-1 confirmação MN

  ├─ Sprint 2: Smoke tests + validation
  ├─ Sprint 2: Embedder Fases 1-4 (reindexação) se confirmado 384d→1024d
  └─ Sprint 2: Slack announcement

  ├─ Sprint 3: S11 prep (agente .md + RAG) se D2=D/paralelo
  └─ Sprint 3: Post-deployment monitoring (7 dias)
```

### Fase 2 (Semana 2-4: 2026-08-08 a 2026-08-21)

```
Sequencial após Fase 1 validação:
  ├─ Manta-09 (A9 Regulatório) go-live — se D4=SIM
  ├─ S11 go-live (se D2=A) — paralelo com Manta-09
  └─ A10 (Risco) formalização — depende Manta-09
```

### Fase 3 (Setembro+)

```
Consolidação + Scale:
  ├─ 3 projetos Supabase INACTIVE (consolidação/arquivamento)
  ├─ Multi-tenancy implementation (após D1/RLS resolvidos)
  └─ Learning loops + self-healing routing
```

---

## 🔴 ACHADOS CRÍTICOS DE SEGURANÇA

### RLS Desabilitado (3 Tabelas)

**Tabelas**: `rag_collections`, `sp_agent_routing`, `maestro_routing_keywords`  
**Risco**: Chave anon pode envenenar routing crítico  
**Remediação**: SQL pronta, ~30min deploy, 0 downtime esperado  
**Status**: Bloqueado por D3 approval (emergência vs. full testing)

### Embedder Dimensão Ambígua (G010)

**Problema**: 3 fontes contradizem (384d vs. 1024d vs. multilingual-e5)  
**Impacto**: RAG silenciosamente degradada se incompatível  
**Prova**: A/B test mostra +11-14% com multilingual-e5  
**Bloqueador**: Verificação real Supabase (Fase 0, 4h)

### Projeto Supabase Morto (G012)

**Projeto**: `xgluoaaymbdzbbudnwrh` (inacessível)  
**Referência**: SKILL.md SharePoint (fora do git)  
**Impacto**: Confusão operacional + possível perda de dados  
**Ação**: AI-1 confirmação MN dashboard

---

## 📞 PRÓXIMAS AÇÕES

**Aguardando**: Respostas Gate MN #2 (6 decisões D1-D6)  
**Quando aprovado**: Deploy paralelo completo começa 2026-08-01  
**Esperado**: Todos os 5 fases Fase 1 + observability + hardening em paralelo  
**Resultado**: v5.0.1 production-ready + S12/S13 operacionais + observability v1 + RLS fechado

---

**Status**: 🟠 **Bloqueado por Gate MN #2**  
**Autor**: Workflow 15 Sonnets  
**Complexidade**: 3 decisões críticas, 3 aprox, todas com trade-offs documentados  
**Recomendação**: Reunião 30min MN para decisões 6; liberação simultânea de Fase 1 paralelo após
