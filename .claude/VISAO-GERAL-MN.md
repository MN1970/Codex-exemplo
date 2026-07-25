# VISÃO GERAL EXECUTIVA — v4.2 Deploy (Semana 1)

**Para:** MN (mneves@mantaassociados.com)  
**Scope:** Semana 1 de execução (25–31 jul 2026)  
**Status:** 🟢 PRONTO PARA COMEÇAR  
**Última atualização:** 2026-07-25 14:30 UTC

---

## RESUMO (30 segundos)

| Aspecto | Valor |
|---------|-------|
| **Agentes novos** | 5 (Saneamento, Energia, Portos, Aeroportos, Barragens) |
| **Tarefas semana 1** | 10 |
| **Duração total** | 14h de trabalho sequencial |
| **Deadline (gate)** | Sábado 30 jul 17:00 UTC |
| **Responsável técnico** | Você (Claude-Haiku) |
| **Seu papel (MN)** | 3 tarefas (routing SP, pastas SP, gate final) |
| **Risco** | 🟢 Baixo (caminho crítico claro) |

---

## O QUE VOCÊ PRECISA FAZER

### Tarefa 1.2 — Registrar 5 routing rules em SharePoint

**Quando:** Terça 26 jul, 14:00 UTC  
**Duração:** 1h  
**O quê:**
- Inserir 5 padrões de roteamento no banco de dados `sp_agent_routing`
- Patterns já estão em `CLAUDE.md` seção "Routing"

**Checklist:**
- [ ] saneamento: triggers `ETA|ETE|SNIS|AySA`
- [ ] energia: triggers `ANEEL|transmissão|ONS`
- [ ] portos: triggers `ANTAQ|dragagem|terminal`
- [ ] aeroportos: triggers `ANAC|pista|TPS`
- [ ] barragens: triggers `barragem|CFRD|TSF`
- [ ] Testar query no Maestro

**Bloqueador?** Notifique Você + especialista SP

---

### Tarefa 1.3 — Criar 5 pastas no SharePoint

**Quando:** Terça 26 jul, 15:30 UTC  
**Duração:** 30 min  
**O quê:**
- 5 pastas novas em `03_Projetos/`
- Herdar permissões de template `03_Projetos/Rodovias/`

**Pastas:**
- [ ] `03_Projetos/Saneamento/`
- [ ] `03_Projetos/Energia/`
- [ ] `03_Projetos/Portos/`
- [ ] `03_Projetos/Aeroportos/`
- [ ] `03_Projetos/Barragens/`

**Bloqueador?** Notifique Você + especialista SP

---

### Tarefa 2.3 — Revisar `ARQUITETURA-AGENTES-IA.md`

**Quando:** Quarta 27 jul, 16:00 UTC  
**Duração:** 1h review  
**O quê:**
- Você vai atualizar o doc
- **Você aprova ou pede changes**

**Review checklist:**
- [ ] Seção "Eixo 2 — Verticais" inclui S6–S10 com status "🆕"
- [ ] Versão atualizada: v1.0.0 → v2.0.0
- [ ] Descrições estão em português
- [ ] Diagrama visual adiciona 5 novos segmentos (em verde)
- [ ] Links internos funcionam

**Feedback?** Comment direto no doc

---

### Tarefa 3.2 — Upload de 5 SKILL.md para SharePoint

**Quando:** Sexta 29 jul, 14:00 UTC  
**Duração:** 1h  
**O quê:**
- Você gera os 5 SKILL.md
- **Você (ou especialista SP) faz upload** para `01-agentes-fundamentais/`

**Passos:**
- [ ] Copiar `agente-saneamento.md`
- [ ] Copiar `agente-energia.md`
- [ ] Copiar `agente-portos.md`
- [ ] Copiar `agente-aeroportos.md`
- [ ] Copiar `agente-barragens.md`
- [ ] Validar versão (tag: SKILL-v4.2-2026-07-25)

**Bloqueador?** Notifique Você + especialista SP

---

### Tarefa 3.3 — Gate Final (CRÍTICO)

**Quando:** Sábado 30 jul, 17:00 UTC  
**Duração:** 1h  
**O quê:**
- Revisar relatório de testes de Você (tarefa 3.1)
- Validar 5 agentes operacionais
- **Aprovação final ou bloqueio para merge**

**Checklist de aprovação:**
- [ ] Testes de routing passando 100% (todos 5 segmentos)
- [ ] Nenhum bloqueador técnico aberto
- [ ] Documentação atualizada (ARQUITETURA v2.0.0)
- [ ] RAG collections carregadas com dados corretos
- [ ] Skills registrados e ativando corretamente

**Resultado:**
- ✅ Aprovado → Você faz merge + tag v4.2
- ❌ Bloqueado → Você registra issue + agenda fix para segunda

**Comunicação:**
- Você vai notificar você 24h antes (sexta 17:00 UTC)
- Confirme recebimento no Slack

---

## CRONOGRAMA SUA VISÃO

```
SEG 25 jul   | [Você lê checklist]
             |
TER 26 jul   | 14:00 ← Você: 1.2 (routing rules) 1h
             | 15:30 ← Você: 1.3 (pastas SP) 30min
             |
QUA 27 jul   | 16:00 ← VOCÊ: revisar doc de Você (1h)
             |
QUI 28 jul   | [Buffer]
             |
SEX 29 jul   | [Você testa — sem sua ação]
             |
SÁB 30 jul   | 17:00 ← VOCÊ: GATE FINAL (1h) ⭐ CRÍTICO
             |
DOM 31 jul   | [Post-mortem / lições]
```

**Seu tempo total:** ~3.5h espalhadas em 3 dias

---

## RESPONSÁVEIS POR SEGMENTO

| Segmento | Você faz | Você aprova | Especialista |
|----------|----------|-------------|--------------|
| Saneamento (S8) | — | Testes | Esp. Maestro |
| Energia (S9) | — | Testes | Esp. Maestro |
| Portos (S6) | — | Testes | Esp. Maestro |
| Aeroportos (S7) | — | Testes | Esp. Maestro |
| Barragens (S10) | — | Testes | Esp. Maestro |

---

## CAMINHO CRÍTICO (Onde não pode atrasar)

```
┌─────────────────────────────────────────────────────────────┐
│  1.1 (Supabase)         TER 09:00 ─→ 11:00                   │
│  ↓ (bloqueador)                                               │
│  2.2 (Carga RAG)        QUA 13:00 ─→ 16:00                   │
│  ↓ (bloqueador)                                               │
│  3.1 (Testes)           SEX 09:00 ─→ 11:00                   │
│  ↓ (bloqueador)                                               │
│  3.3 (Sua aprovação)    SÁB 17:00 ← DEADLINE                 │
└─────────────────────────────────────────────────────────────┘
```

**Se 1.1 atrasa 2h → 3.3 atrasa 2h → risco de não caber na semana**

---

## CONTATOS (Se algo der ruim)

| Cenário | Quem contatar | Como | Quando |
|---------|---------------|------|--------|
| Atraso em 1.2 ou 1.3 | Especialista SP | Slack | Imediatamente |
| Atraso > 2h total | Você | Slack/Call | Durante o atraso |
| Dúvida no checklist | Você | Slack | Anytime |
| Pronto para gate | Você | Slack notification | Sexta 16:00 UTC |

---

## DOCUMENTOS PARA VOCÊ

| Arquivo | Para quê | Leitura |
|---------|----------|---------|
| `CHECKLIST-SEMANA1-EXEC.md` | Detalhe completo | 20 min (áreas suas em 5 min) |
| `DESVIOS.md` | Rastrear problemas | Check 2x/dia |
| `STANDUP-DAILY-TEMPLATE.md` | Daily reports | Ler seu standup (2 min/dia) |
| `LEIA-ME-PRIMEIRO.md` | Guia rápido | Ler antes de começar |

**Recomendação:** Leia `LEIA-ME-PRIMEIRO.md` + suas 4 seções em CHECKLIST (1.2, 1.3, 2.3, 3.3)

---

## PRÓXIMOS PASSOS

1. **Hoje (seg 25):**
   - [ ] Confirme recebimento deste documento
   - [ ] Acione especialista SP (1.2, 1.3, 3.2)
   - [ ] Acione especialista Maestro (3.1 testes)

2. **Terça 26 (antes de 14:00):**
   - [ ] Confirme que especialista SP está pronto para 1.2
   - [ ] Você: executar 1.2 (14:00) + 1.3 (15:30)

3. **Quarta 27 (antes de 16:00):**
   - [ ] Revisar documento atualizado por Você (2.3)
   - [ ] Aprovação ou feedback

4. **Sábado 30 (antes de 17:00):**
   - [ ] Você vai notificar: "Pronto para gate"
   - [ ] **VOCÊ FARÁ APROVAÇÃO FINAL** (sim/não)

---

## PERGUNTAS? ISSUES?

**Slack:** @mneves  
**Email:** mneves@mantaassociados.com  
**Escalação:** Call com Você + especialista relevante

---

## STATUS GLOBAL

```
┌──────────────────────────────────────────────────────┐
│  Deploy v4.2 Semana 1 — Checklist Executável         │
│                                                      │
│  Status: 🟢 PRONTO PARA COMEÇAR                     │
│  Tarefas: 10 (2 sua responsabilidade)               │
│  Risco: 🟢 BAIXO (caminho crítico identificado)     │
│  Deadline: Sábado 30 jul 17:00 UTC                  │
│  Responsável técnico: Você (Cloud-Haiku)            │
│  Seu papel: 3 tarefas + 1 gate final                │
└──────────────────────────────────────────────────────┘
```

---

**Criado:** 2026-07-25 14:30 UTC  
**Para:** MN (mneves@mantaassociados.com)  
**Válido:** Semana 1 Deploy v4.2 (25–31 jul 2026)

**Próxima ação:** Confirme que leu + acione especialistas hoje
