# CHECKLIST EXECUTÁVEL — SEMANA 1 (Deploy v4.2)

**Período:** 2026-07-25 a 2026-07-31  
**Versão:** v4.2 (5 novos agentes: Portos, Aeroportos, Saneamento, Energia, Barragens)  
**Data de atualização:** 2026-07-25 14:30 UTC  

---

## RESUMO DE STATUS

| Status | Qtd | Ícone |
|--------|-----|-------|
| ✅ Completo | 2 | `[✅]` |
| 🔄 Em progresso | 0 | `[🔄]` |
| ⏳ Bloqueado | 0 | `[⏳]` |
| ⬜ Não iniciado | 8 | `[⬜]` |
| **TOTAL** | **10** | |

---

## FASE 1 — Infra & Base (Seg–Ter: 25–26 jul)

### 1.1 — Criar 5 coleções RAG em Supabase

- **Status:** `[⬜]` Não iniciado
- **Responsável:** Você (Claude-Haiku) + especialista BD
- **Prazo:** Terça 26 jul, 09:00 UTC
- **Duração estimada:** 2h
- **Dependências:** Nenhuma (parallelizável)
- **Próximas tarefas bloqueadas:** 2.2, 2.3
- **Ações:**
  - [ ] Criar collection `saneamento` (prefixo `san:`)
  - [ ] Criar collection `energia` (prefixo `ene:`)
  - [ ] Criar collection `portos` (prefixo `por:`)
  - [ ] Criar collection `aeroportos` (prefixo `aer:`)
  - [ ] Criar collection `barragens` (prefixo `bar:`)
  - [ ] Validar conexão via API Supabase
- **Notas:**
  - Fontes iniciais já listadas em CLAUDE.md seção RAG
  - Padrão: `key: "segment:doc-type:uuid"`, `metadata: {source, segment, version}`

---

### 1.2 — Inserir 5 routing rules em `sp_agent_routing` (SharePoint)

- **Status:** `[⬜]` Não iniciado
- **Responsável:** MN (Manta) ou especialista SP
- **Prazo:** Terça 26 jul, 14:00 UTC
- **Duração estimada:** 1h
- **Dependências:** Nenhuma
- **Próximas tarefas bloqueadas:** 2.3
- **Ações:**
  - [ ] Registrar padrão saneamento em `sp_agent_routing`
  - [ ] Registrar padrão energia
  - [ ] Registrar padrão portos
  - [ ] Registrar padrão aeroportos
  - [ ] Registrar padrão barragens
  - [ ] Testar resolução de query no Maestro
- **Notas:**
  - Patterns já estão em CLAUDE.md > Routing rules
  - Validar sincronização com Maestro 00

---

### 1.3 — Criar 5 pastas SP para novos segmentos

- **Status:** `[⬜]` Não iniciado
- **Responsável:** MN (SharePoint admin) ou especialista infra
- **Prazo:** Terça 26 jul, 15:30 UTC
- **Duração estimada:** 30 min
- **Dependências:** Nenhuma
- **Próximas tarefas bloqueadas:** Nenhuma (independente)
- **Ações:**
  - [ ] Criar pasta `03_Projetos/Saneamento/`
  - [ ] Criar pasta `03_Projetos/Energia/`
  - [ ] Criar pasta `03_Projetos/Portos/`
  - [ ] Criar pasta `03_Projetos/Aeroportos/`
  - [ ] Criar pasta `03_Projetos/Barragens/`
  - [ ] Definir permissões (leitura público, escrita=agentes)
- **Notas:**
  - Usar template padrão Manta (herdar de `03_Projetos/Rodovias/`)
  - Documentação em pt-BR

---

## FASE 2 — Registro & Config (Qua–Qui: 27–28 jul)

### 2.1 — Registrar 5 skills no catálogo

- **Status:** `[⬜]` Não iniciado
- **Responsável:** Você (Claude-Haiku) + especialista skill-registry
- **Prazo:** Quarta 27 jul, 10:00 UTC
- **Duração estimada:** 1.5h
- **Dependências:** Nenhuma
- **Próximas tarefas bloqueadas:** 3.1 (testes)
- **Ações:**
  - [ ] Registrar `skill:agente-saneamento` com triggers (ETA, ETE, SNIS, AySA)
  - [ ] Registrar `skill:agente-energia` com triggers (ANEEL, transmissão, ONS)
  - [ ] Registrar `skill:agente-portos` com triggers (ANTAQ, dragagem, terminal)
  - [ ] Registrar `skill:agente-aeroportos` com triggers (ANAC, pista, TPS)
  - [ ] Registrar `skill:agente-barragens` com triggers (CFRD, TSF, SIGBM)
  - [ ] Validar descrições e aliases em cada registry entry
- **Notas:**
  - Patterns já mapeados em CLAUDE.md > Routing
  - Tier default: Sonnet (todos S6–S10)

---

### 2.2 — Carregar dados nas 5 coleções RAG

- **Status:** `[⬜]` Não iniciado
- **Responsável:** Você (Claude-Haiku) + especialista RAG/contenúdo
- **Prazo:** Quarta 27 jul, 13:00 UTC
- **Duração estimada:** 3h
- **Dependências:** ✅ **Tarefa 1.1 completa** (coleções criadas em Supabase)
- **Próximas tarefas bloqueadas:** 3.1
- **Ações:**
  - [ ] Importar SNIS + Lei 14.026 → collection `saneamento`
  - [ ] Importar ANEEL editais + EPE R1–R5 → collection `energia`
  - [ ] Importar ANTAQ + PIANC → collection `portos`
  - [ ] Importar ANAC/RBAC + ICAO Annex 14 → collection `aeroportos`
  - [ ] Importar ICOLD + CBDB + Lei 12.334 → collection `barragens`
  - [ ] Validar embedding + busca semântica
- **Notas:**
  - Documentos fonte já listados em CLAUDE.md
  - Format: JSON chunks com metadata mínima (source, versão, data)

---

### 2.3 — Atualizar `ARQUITETURA-AGENTES-IA.md` no SP

- **Status:** `[⬜]` Não iniciado
- **Responsável:** Você (Claude-Haiku) + MN review
- **Prazo:** Quarta 27 jul, 16:00 UTC
- **Duração estimada:** 1h
- **Dependências:** ✅ **Tarefas 1.2 + 2.1 completas** (routing registrado, skills prontos)
- **Próximas tarefas bloqueadas:** 3.2
- **Ações:**
  - [ ] Copiar seção "Eixo 2 — Verticais" de CLAUDE.md
  - [ ] Adicionar diagrama visual (5 novos segmentos em verde)
  - [ ] Atualizar tabela de status (S5 → parcial, S6–S10 → novo)
  - [ ] Validar versão em títulos (v1.0.0 → v2.0.0)
  - [ ] Revisão MN: @mneves acionar para approve antes de commit
- **Notas:**
  - Arquivo em SP: `01-agentes-fundamentais/ARQUITETURA-AGENTES-IA.md`
  - Manter histórico de versões (changelog inline)

---

## FASE 3 — Validação & Testes (Sex–Sab: 29–30 jul)

### 3.1 — Testar routing do Maestro com prompts de cada segmento

- **Status:** `[⬜]` Não iniciado
- **Responsável:** Você (Claude-Haiku) + especialista Maestro
- **Prazo:** Sexta 29 jul, 09:00 UTC
- **Duração estimada:** 2h
- **Dependências:** ✅ **Tarefas 1.2, 2.1, 2.2 completas**
- **Próximas tarefas bloqueadas:** Nenhuma (pré-requisito para gate humano)
- **Ações:**
  - [ ] Testar routing saneamento: prompt com "ETA", "SNIS", "AySA" → agente-saneamento
  - [ ] Testar routing energia: prompt com "ANEEL", "transmissão", "ONS" → agente-energia
  - [ ] Testar routing portos: prompt com "ANTAQ", "dragagem", "terminal" → agente-portos
  - [ ] Testar routing aeroportos: prompt com "ANAC", "pista", "TPS" → agente-aeroportos
  - [ ] Testar routing barragens: prompt com "barragem", "CFRD", "TSF" → agente-barragens
  - [ ] Validar que skills se ativam corretamente
  - [ ] Documentar qualquer fallback inesperado
- **Notas:**
  - Usar prompts reais de clientes quando possível
  - Log de testes em `test-logs/routing-validation-2026-07-29.txt`

---

### 3.2 — Upload dos 5 SKILL.md para SP

- **Status:** `[⬜]` Não iniciado
- **Responsável:** MN ou especialista SP/documentação
- **Prazo:** Sexta 29 jul, 14:00 UTC
- **Duração estimada:** 1h
- **Dependências:** ✅ **Tarefas 2.1 + 2.3 completas** (skills registrados, arquitetura atualizada)
- **Próximas tarefas bloqueadas:** Nenhuma
- **Ações:**
  - [ ] Copiar `agente-saneamento.md` → SP `01-agentes-fundamentais/`
  - [ ] Copiar `agente-energia.md` → SP `01-agentes-fundamentais/`
  - [ ] Copiar `agente-portos.md` → SP `01-agentes-fundamentais/`
  - [ ] Copiar `agente-aeroportos.md` → SP `01-agentes-fundamentais/`
  - [ ] Copiar `agente-barragens.md` → SP `01-agentes-fundamentais/`
  - [ ] Validar links internos
- **Notas:**
  - SKILL.md já estão em `.claude/agents/` deste repositório
  - Versionar com tag de data (SKILL-v4.2-2026-07-25)

---

### 3.3 — Gate humano: aprovação MN antes de merge

- **Status:** `[⬜]` Bloqueado até 3.1
- **Responsável:** MN (mneves@mantaassociados.com)
- **Prazo:** Sábado 30 jul, 17:00 UTC **DEADLINE**
- **Duração estimada:** 1h review
- **Dependências:** ✅ **Tarefas 3.1 + 3.2 completas** (testes passando, docs atualizados)
- **Próximas tarefas bloqueadas:** Merge & deploy em produção
- **Ações:**
  - [ ] MN: revisar relatório de testes (3.1)
  - [ ] MN: validar que 5 segmentos estão operacionais
  - [ ] MN: revisar arquitetura atualizada (2.3)
  - [ ] MN: aprovação final (comentário: "Aprovado para merge v4.2")
  - [ ] Você: merge para main branch
  - [ ] Você: tag release `v4.2` com changelog
- **Notas:**
  - Bloquear merge se houver falhas em 3.1
  - Notificar MN por Slack 24h antes (sex 29 às 17h)

---

## CRONOGRAMA COMPRESSO — Semana 1

```
SEG 25 jul  |  Você: início — ler checklist, preparar Supabase
TER 26 jul  |  1.1 (09:00) + 1.2 (14:00) + 1.3 (15:30) — base infra
QUA 27 jul  |  2.1 (10:00) + 2.2 (13:00) + 2.3 (16:00) — config & docs
QUI 28 jul  |  Slack review + ajustes (se necessário)
SEX 29 jul  |  3.1 (09:00) + 3.2 (14:00) — validação
SÁB 30 jul  |  3.3 (17:00) — gate MN + merge
DOM 31 jul  |  Buffer & contingência
```

---

## MATRIZ DE RESPONSABILIDADES

| Tarefa | Você (Haiku) | MN (Manta) | Especialista BD | Esp. SP | Esp. Maestro |
|--------|--------------|-----------|-----------------|---------|--------------|
| 1.1 RAG | ✅ Lead | 🤝 Apoio | ✅ Co-lead | — | — |
| 1.2 Routing | — | ✅ Lead | — | 🤝 Apoio | — |
| 1.3 Pastas SP | — | ✅ Lead | — | 🤝 Apoio | — |
| 2.1 Skills | ✅ Lead | 🤝 Apoio | — | — | — |
| 2.2 Carga RAG | ✅ Lead | — | 🤝 Apoio | — | — |
| 2.3 Arquitetura | ✅ Lead | ✅ Review | — | 🤝 Apoio | — |
| 3.1 Testes | ✅ Lead | 🤝 Apoio | — | — | ✅ Co-lead |
| 3.2 Upload SP | — | ✅ Lead | — | 🤝 Apoio | — |
| 3.3 Gate MN | 🤝 Apoio | ✅ Lead | — | — | — |

**Legenda:**
- `✅ Lead` = Proprietário da tarefa, decisão final
- `✅ Co-lead` = Responsável compartilhado
- `🤝 Apoio` = Suporte / revisão / validação

---

## DEPENDÊNCIAS E CAMINHOS CRÍTICOS

```
1.1 (Supabase)
  ↓
  2.2 (Carga RAG)
    ↓
    3.1 (Testes routing)
      ↓
      3.3 (Gate MN) ← CRÍTICO
      
1.2 (Routing) ─→ 2.3 (Arquitetura) ─→ 3.2 (Upload SP)
  ↓
  2.1 (Skills) ─→ 3.1 (Testes)

Parallelizáveis: 1.1, 1.2, 1.3, 2.1
```

**Caminho crítico:** 1.1 → 2.2 → 3.1 → 3.3 (14 horas de trabalho sequencial)

---

## CONTATOS & ESCALAÇÃO

| Papel | Nome/Email | Slack | Timezone |
|-------|-----------|-------|----------|
| Product Owner (Gate) | MN (mneves@mantaassociados.com) | @mneves | UTC-3 |
| Lead Técnico (Você) | Claude-Haiku | — | UTC |
| Especialista Supabase | [TBD] | — | — |
| Especialista SharePoint | [TBD] | — | — |
| Especialista Maestro | [TBD] | — | — |

**Escalação:**
- ❌ Bloqueador infra → MN no Slack (notificação urgente)
- ⚠️ Desvio > 30 min de prazo → notify MN + log em `DESVIOS.md`
- ✅ Conclusão > prazo estimado → celebrate + log lições aprendidas

---

## CHECKPOINTS DIÁRIOS

### Terça 26 jul (08:00 UTC)
- [ ] Você: status de 1.1 (Supabase)
- [ ] MN: confirmação de responsáveis especialistas
- [ ] Você: teste de conectividade API

### Quarta 27 jul (08:00 UTC)
- [ ] Você: status de 2.1 + 2.2
- [ ] MN: validação de 1.2 + 1.3 (routing + pastas)
- [ ] Você: primeiros testes de embedding

### Quinta 28 jul (08:00 UTC)
- [ ] Você: status final de 2.2 (carga RAG)
- [ ] MN: revisão de 2.3 (arquitetura)
- [ ] Você: plano de testes para sexta

### Sexta 29 jul (17:00 UTC)
- [ ] Você: relatório completo de 3.1 (testes)
- [ ] MN: notificação pre-gate (24h para 30 jul 17:00)

### Sábado 30 jul (17:00 UTC)
- [ ] MN: aprovação final ou bloqueio
- [ ] Você: merge + tag v4.2

---

## COMO USAR ESTE CHECKLIST

1. **Status tracking:** Marque `[✅]` quando cada item for concluído
2. **Daily standup:** Use seção "CHECKPOINTS DIÁRIOS" para reports
3. **Bloqueadores:** Log qualquer issue em seção "BLOQUEADORES" (veja abaixo)
4. **Desvios:** Registre prazos / responsáveis alterados em "HISTÓRICO"
5. **Merge:** Só após 3.3 aprovado por MN

---

## BLOQUEADORES (Live Tracking)

| ID | Item | Causa | Assignee | Desde | ETA fix |
|----|----|-------|----------|-------|----------|
| — | — | — | — | — | — |

*Nenhum bloqueador ativo no início.*

---

## HISTÓRICO DE MUDANÇAS

| Data | Mudança | Autor | Razão |
|------|---------|-------|-------|
| 2026-07-25 14:30 | Checklist v1.0 criado | Você | Consolidação executável |
| — | — | — | — |

---

## ARTEFATOS DE SAÍDA (Ao final da semana)

- `CHECKLIST-SEMANA1-EXEC.md` (este arquivo, atualizado)
- `test-logs/routing-validation-2026-07-29.txt` (Você, 3.1)
- `DESVIOS.md` (Você, contínuo)
- `RELEASE-v4.2.md` (Você, após 3.3)
- 5 coleções RAG em Supabase (`san:*`, `ene:*`, `por:*`, `aer:*`, `bar:*`)
- 5 pastas SP em `03_Projetos/*`
- 5 SKILL.md uploads em SP `01-agentes-fundamentais/`
- Tag Git: `v4.2` com changelog integrado

---

**Criado:** 2026-07-25 14:30 UTC  
**Próxima review:** Terça 26 jul 08:00 UTC  
**Status global:** 🟢 **ATIVO** (0% bloqueado)
