# RECONCILIAÇÃO v4.2 → v5.0 — RESUMO EXECUTIVO

**Versão:** 5.0.0  
**Data:** 2026-07-25  
**Ticket:** MNT-2026-AGENT-RECONCILIATION  
**Impacto:** BREAKING CHANGE — Todos os agent_ids mudam

---

## O PROBLEMA

| Camada | Estado em v4.2 | Problema |
|--------|-----------------|----------|
| Database | `03-S1`, `03-S10`, `M02`, `M23` | Nomenclatura inconsistente; 28 agent_ids diversos |
| Skills map | `Manta 00`, `Manta 15`, `Manta 16` | Sem padronização; ambiguidade |
| CLAUDE.md | `Manta XX` + `03-S*` | Mistura de esquemas |
| Frontmatter .md | `name: agente-energia` | Sem code unificado |

**Resultado:** Impossível rastrear consistentemente quem é quem.

---

## A SOLUÇÃO (v5.0)

### Taxonomia Unificada

**Um identificador só em todas as camadas:**

```
M00-M10  = Horizontals (11 agentes funcionais)
S01-S10  = Setoriais (10 agentes por segmento)
Skills   = Guards, validadores (fora da tabela de agentes)
```

### Mapa Rápido

| v4.2 | v5.0 | Nome | Tipo |
|------|------|------|------|
| Manta 00 | M00 | Maestro | Horizontal |
| Manta 01 | M01 | Claims | Horizontal |
| Manta 15 | **M08** | Advisory | Horizontal |
| Manta 16 | **M09** | Arquiteto IA | Horizontal |
| 03-S1 | **S01** | Rodovias | Setorial |
| 03-S8 | **S08** | Saneamento | Setorial |
| 03-S10 | **S10** | Barragens | Setorial |

---

## ARQUIVOS ENTREGÁVEIS

| Arquivo | Propósito | Status |
|---------|-----------|--------|
| `pk_agentes.json` | Mapa canônico (JSON) | ✅ Pronto |
| `CLAUDE.md` (v5.0) | Master registry (atualizado) | ✅ Pronto |
| `RECONCILIACAO.md` | Audit report detalhado | ✅ Pronto |
| `RECONCILIACAO-RESUMO.md` | Este arquivo | ✅ Pronto |
| `supabase/migrations/2026_07_25_v5_0_reconciliation.sql` | Script SQL | ✅ Pronto |

---

## PRÓXIMOS PASSOS

### 1️⃣ Aprovação (MN — 1 dia)
- [ ] Review `pk_agentes.json`
- [ ] Review `RECONCILIACAO.md` (seção 4: plano de execução)
- [ ] Aprovar BREAKING CHANGE

### 2️⃣ Migração (2026-07-28 — 1 dia)
- [ ] Executar SQL em Supabase (staging → produção)
- [ ] Testar rollback
- [ ] Validar checksums

### 3️⃣ Aplicação (2026-08-04 — 3 dias)
- [ ] Update agent .md files (frontmatter)
- [ ] Update routing keywords
- [ ] Update Maestro (repo privado)

### 4️⃣ Testes (2026-08-11 — 3 dias)
- [ ] Routing tests (cada segmento)
- [ ] RAG tests (knowledge retrieval)
- [ ] Subagent spawn tests

### 5️⃣ Go-live (2026-08-18)
- [ ] Flip switch em produção
- [ ] Notificar teams

---

## IMPACTOS

### Diretos (Breaking)
- ❌ Qualquer código que use `agent_id = '03-S1'` quebrará
- ❌ Routing keywords em maestro_routing_keywords precisam update
- ✅ Suportado por: `pk_agentes.json` (mapa de migração)

### Indiretos (Vigilância)
- 🟡 RAG queries por agent_id (verificar)
- 🟡 Logging/metrics (filtros por agent_id)
- 🟡 Dashboards (alertas com agent_id antigo)

### Reversibilidade
- ✅ Rollback script incluído em `2026_07_25_v5_0_reconciliation.sql`
- ⏱️ Janela de rollback: ~2 horas pós-migração

---

## FAQ

**P: Por que não `S01`, `S02`, ... em v4.2?**  
R: Convenção histórica usava `03-S1` (Manta 03 = setorial, S1 = primeira). v5.0 simplifica para `S01` (sem prefixo 03).

**P: E os M codes duplicados (M02, M07)?**  
R: v4.2 tinha lacunas (Manta 00, 01, 02, 04, 05, ...). v5.0 consolida em M01-M10 (11 horizontais, sem lacunas).

**P: Manta 15 e 16 colidiram?**  
R: Sim. Skills mapa tinha Manta 16 = arquiteto-ia, mas CLAUDE.md tinha Manta 15 = advisory e Manta 16 = arquiteto-ia. v5.0 resolve: M08 (advisory) + M09 (arquiteto-ia).

**P: Guards (aluci-guard, etc) desaparecem?**  
R: Não! Continuam como SKILLS. Apenas saem de `manta_agent_capabilities` (agentes) e vão para skill registry (validadores).

**P: Quanto tempo leva a migração?**  
R: ~5-10 minutos para SQL. ~2-3 dias para app layer + testes. Go-live no final da sprint (2026-08-18).

**P: Preciso fazer algo antes da migração?**  
R: Sim! Executar `pk_agentes.json` como documento de referência. Não mude código ainda; aguarde aprovação MN.

---

## CONTATOS

- **Arquiteto:** (você/ML)
- **DBA:** (Supabase team)
- **Aprovador:** MN (Manta Negócios)
- **Slack:** #manta-maestro-agents (discussões)

---

**Status:** 🔄 Em revisão MN  
**Próxima atualização:** Após aprovação (esperado 2026-07-26)
