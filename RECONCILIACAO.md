# RECONCILIAÇÃO — Manta Maestro v4.2 → v5.0

**Data:** 2026-07-25  
**Ticket:** MNT-2026-AGENT-RECONCILIATION  
**Status:** 🔄 Em implementação

---

## 1. DIVERGÊNCIAS IDENTIFICADAS

### 1.1 Nomenclatura Agent IDs

| Camada | Formato | Exemplos | Problemas |
|--------|---------|----------|-----------|
| **Database** (manta_agent_capabilities) | `03-S*`, `M**` | 03-S1, 03-S10, M02, M23 | Ambíguo (03 = Manta 03?), difícil rastrear |
| **Skills map** (v4.0.0) | `Manta XX` | Manta 00, Manta 01, Manta 15 | Falta padronização para skills guards |
| **CLAUDE.md** | `Manta XX` + `03-S*` | Manta 00, Manta 03-S1 | Inconsistência com database |
| **Agent .md files** | `agente-nome` | agente-energia | Sem código unificado no frontmatter |

**Raiz do problema:** Sem documento único (PK v5.0) que defina o mapa canônico.

---

### 1.2 Cobertura de Agentes

**Database (28 agent_ids encontrados):**
```
Setoriais:      03-S1, 03-S2, 03-S3, 03-S4, 03-S5, 03-S6, 03-S7, 
                03-S8, 03-S9, 03-S10, 03-S11, 03-S12, 03-S13 (13)
M-scheme:       M02, M07, M12, M13, M16, M17, M18, M19, M20, M21, M22, M23 (12)
Guards (skill): aluci-guard, consist-guard, context-guardian (3)
```

**Skills map (13 códigos em SKILL.md):**
```
Horizontals:    Manta 00, 01, 02, 04, 05, 06, 07, 13, 14, 15, 16 (11)
Setoriais:      03-S1, S8 (2)
```

**CLAUDE.md (20 agentes listados):**
```
Horizontals:    Manta 00, 01, 02, 04, 05, 06, 07, 13, 14, 15, 16 (11)
Setoriais:      03-S1 through 03-S10 (10)
```

---

### 1.3 Conflitos Específicos

#### Conflito A: Manta 15 duplicado
- **Skills:** `manta-arquiteto-ia` → `Manta 16`
- **CLAUDE.md:** `Manta 15` = advisory, `Manta 16` = arquiteto-ia
- **Problema:** Código 16 designado para arquiteto-ia em skill, mas CLAUDE.md também lista 16
- **Resolução (v5.0):** `Manta 15 → M08 (advisory)`, `Manta 16 → M09 (arquiteto-ia)`

#### Conflito B: Guards registrados como agentes
- **Database:** aluci-guard, consist-guard, context-guardian em `manta_agent_capabilities`
- **Conceitual:** Validadores são SKILLS, não agentes
- **Resolução:** Remover da tabela de agentes; manter em tabela de skills

#### Conflito C: 03-S11, 03-S12, 03-S13 órfãos
- **Database:** Registrados mas não mencionados em CLAUDE.md
- **Status:** Desconhecido
- **Ação:** Investigar e decidir (remover ou documentar)

#### Conflito D: M-scheme disperso
- **Database:** M02, M07, M12-M23 (12 códigos)
- **CLAUDE.md:** Apenas M00-M01, M02, M04-M07, M13-M16 (descrito como "Manta")
- **Problema:** Lacuna na sequência
- **Resolução:** Consolidar para M01-M10 (11 agentes horizontais)

---

## 2. SOLUÇÃO PROPOSTA (v5.0)

### 2.1 Taxonomia Unificada

**Um único identificador (`agent_id`)** para todas as camadas:

| Faixa | Uso | Exemplos | Quantidade |
|-------|-----|----------|-----------|
| **M00-M10** | Horizontais (funcionales) | M00 (maestro), M01 (claims), M05 (orçamento) | 11 |
| **S01-S13** | Setoriais (segmentos) | S01 (rodovias), S08 (saneamento), S10 (barragens) | 13 |
| **Skills** | Validadores, guards | aluci-guard, consist-guard, context-guardian | 3 (fora de agentes) |

**Mapa de migração 4.2 → 5.0:**

```
# Horizontals
Manta 00  → M00 (maestro)
Manta 01  → M01 (claims)
Manta 02  → M02 (contratual)
Manta 04  → M04 (imobiliario)
Manta 05  → M05 (orcamento)
Manta 06  → M06 (modelagem)
Manta 07  → M07 (cronograma)
Manta 13  → M03 (bd, antes M13)
Manta 14  → M10 (apresentacoes, antes M14)
Manta 15  → M08 (advisory, renumbered para resolver conflito)
Manta 16  → M09 (arquiteto-ia, renumbered)

# Setoriais
03-S1 → S01 (rodovias)
03-S2 → S02 (oae)
03-S3 → S03 (ferrovia)
03-S4 → S04 (metro)
03-S5 → S05 (tuneis, parcial)
03-S6 → S06 (portos)
03-S7 → S07 (aeroportos)
03-S8 → S08 (saneamento, PRIORIDADE)
03-S9 → S09 (energia)
03-S10 → S10 (barragens)

# Orphans (decision pending)
03-S11, 03-S12, 03-S13 → investigar
M12, M17-M23 → roadmap (ativo=false até terem conhecimento)

# Guards (SKILL, not agent)
aluci-guard → skill (remover de manta_agent_capabilities)
consist-guard → skill (remover de manta_agent_capabilities)
context-guardian → skill (remover de manta_agent_capabilities)
```

---

### 2.2 Arquivos Criados/Atualizados

| Arquivo | Versão | Ação | Status |
|---------|--------|------|--------|
| `pk_agentes.json` | 5.0 | Criar | ✅ Pronto |
| `CLAUDE.md` | 5.0 | Atualizar | ✅ Pronto |
| `RECONCILIACAO.md` | 1.0 | Criar | ✅ Este arquivo |
| `supabase/migrations/2026_07_25_v5_0_reconciliation.sql` | — | Criar | 🔄 Próximo |
| `.claude/agents/*.md` | — | Atualizar frontmatter | ⏳ Pendente |

---

## 3. PLANO DE EXECUÇÃO

### Fase 1: Audit & Planning (Atual)
- [x] Identificar divergências (seção 1)
- [x] Propor solução (seção 2)
- [x] Criar `pk_agentes.json`
- [x] Atualizar `CLAUDE.md` com v5.0
- [x] Documentar reconciliação (este arquivo)
- [ ] Gate MN: aprovação para prosseguir

### Fase 2: Database Migration (Semana de 2026-07-28)
- [ ] Script SQL de migração:
  ```sql
  -- Rename agent_ids em manta_agent_capabilities
  UPDATE manta_agent_capabilities SET agent_id = 'S01' WHERE agent_id = '03-S1';
  -- ... (12 mais)
  
  -- Remove guards
  DELETE FROM manta_agent_capabilities WHERE agent_id IN 
    ('aluci-guard', 'consist-guard', 'context-guardian');
  
  -- Consolidate Manta → M scheme
  UPDATE manta_agent_capabilities SET agent_id = 'M08' WHERE agent_id = 'Manta 15';
  -- ... (mais)
  ```

- [ ] Testar rollback em staging
- [ ] Executar em produção (durante janela de manutenção)
- [ ] Verificar integridade (checksums)

### Fase 3: Application Layer (Semana de 2026-08-04)
- [ ] Update `.claude/agents/*.md` frontmatter (adicionar `agent_id: S0X`)
- [ ] Update descriptions (03-S* → S*)
- [ ] Update routing keywords em `maestro_routing_keywords`
- [ ] Update `sp_agent_routing` table

### Fase 4: Validation (Semana de 2026-08-11)
- [ ] Test routing: prompts de cada segmento
- [ ] Test knowledge retrieval: RAG queries por S01-S10
- [ ] Test subagent spawning com novos agent_ids
- [ ] Monitor logs (erros de agent_id mismatch)

### Fase 5: Go-Live (2026-08-18)
- [ ] Atualizar operacional Maestro (repo privado) com novos agent_ids
- [ ] Notificar times (Manta Associados, clientes)
- [ ] Manter v4.2 branch para rollback se necessário
- [ ] Arquivar docs v4.2

---

## 4. RISCOS & MITIGAÇÕES

| Risco | Severidade | Mitigação |
|-------|-----------|-----------|
| Agent_id mismatch entre banco e subagents | 🔴 Alta | Script de validação cruzada; teste em staging antes de prod |
| Routing keywords desync | 🟡 Média | Sincronizar CLAUDE.md ↔ maestro_routing_keywords durante migration |
| Downtime durante migration | 🟡 Média | Janela de manutenção noturna; read-only mode antes de migration |
| Orphan agents (03-S11-S13) não esclarecidos | 🟢 Baixa | Decidir até 2026-08-01; update taxonomy se necessário |

---

## 5. VERIFICAÇÃO PÓS-MIGRAÇÃO

Executar após Phase 3:

```bash
# Check agent_ids em database
SELECT COUNT(DISTINCT agent_id) FROM manta_agent_capabilities;
# Esperado: 22 (M00-M09, M10 + S01-S10, + roadmap M-codes com ativo=false)

# Check guards foram removidos
SELECT COUNT(*) FROM manta_agent_capabilities 
  WHERE agent_id IN ('aluci-guard', 'consist-guard', 'context-guardian');
# Esperado: 0

# Check routing keywords não quebrados
SELECT COUNT(*) FROM maestro_routing_keywords WHERE agent_slug = 'S01';
# Esperado: > 0 (palavras-chave para S01 rodovias)

# Check knowledge vectors recuperáveis
SELECT COUNT(*) FROM rag_chunks WHERE agent_id = 'S08';
# Esperado: >= 7 (KEs de saneamento)
```

---

## 6. REFERÊNCIAS

- **PK v5.0:** `/pk_agentes.json` (este repo)
- **Database schema:** Supabase `manta_agent_capabilities`, `maestro_routing_keywords`
- **Master CLAUDE.md:** Este repo (v5.0)
- **Ticket MN:** MNT-2026-AGENT-RECONCILIATION (Jira/Monday.com)
- **Original v4.2 task:** MNT-2026-UPGRADE-AGENTS-S6S10

---

## 7. ASSINATURAS & APROVAÇÕES

| Papel | Nome | Data | Assinatura |
|------|------|------|-----------|
| Product Owner | MN (Manta Neg) | — | ☐ Pendente |
| Tech Lead | — | — | ☐ Pendente |
| DBA (Supabase) | — | — | ☐ Pendente |

---

**Próximo passo:** Submeter para aprovação MN antes de proceder à Fase 2.
