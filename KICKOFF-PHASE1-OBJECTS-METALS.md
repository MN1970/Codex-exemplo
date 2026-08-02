# KICKOFF — Fase 1: Design & Infraestrutura
**Data**: 2026-08-02  
**Status**: 🟢 APROVADO MN — INICIANDO  
**Ticket**: MNT-2026-OBJECTS-METALS  
**Branch**: `claude/manta-maestro-objects-metals-vhfirl`

---

## APROVAÇÃO MN — CONFIRMADA ✅

| Item | Status | Assinado |
|------|--------|----------|
| maestro-objects-metals.md | ✅ Aprovado | MN |
| PLANO-INTERVENCAO-V5.md | ✅ Aprovado | MN |
| ENTENDIMENTO-MANTA-MAESTRO.md | ✅ Aprovado | MN |
| EVOLUCAO-CONHECIMENTO-MAESTRO.md | ✅ Aprovado | MN |
| SUMARIO-EXECUTIVO-MAESTRO.md | ✅ Aprovado | MN |
| maestro-objects-metals.json | ✅ Aprovado | MN |

**Autorização**: Iniciar 6 fases (15 semanas, $50K investimento)

---

## TIMELINE FASE 1 (Semanas 1-2)

### SEMANA 1 (Começando HOJE)

#### 1.1 Validação Schema (DBA)
- [ ] DBA revisa `maestro-objects-metals.md` seção "Arquitetura de Dados v5.0"
- [ ] Valida 8 tabelas Supabase
- [ ] Gera script `migrations/001_maestro_objects_metals_v5.0.sql`
- [ ] Cria índices (performance)
- [ ] Propõe mudanças (se houver)

**Dono**: DBA Supabase  
**Bloqueador**: Nenhum  
**Saída**: Schema SQL validado

#### 1.2 Mapeamento dos 20 Agentes (Tech Lead + Product)
- [ ] Extrai de `CLAUDE.md` + `.claude/agents/*.md` os 20 agentes
- [ ] Popula `maestro-objects-metals.json` com dados reais:
  - `code`, `slug`, `aliases`
  - `domain`, `axis`
  - `default_tier` (Haiku/Sonnet/Opus)
  - `specializations` (keywords)
  - `rag_collections` (prefixos)
  - `handoff_targets` (outros agentes)
  - `status` (Operational, Partial, etc.)
  - `success_rate` (baseline atual)
  - `avg_cost_per_call`

- [ ] Lista final validada com stakeholders

**Dono**: Tech Lead + Product  
**Bloqueador**: Nenhum  
**Saída**: agents.json completo (20 linhas)

#### 1.3 Protótipo MSE (Engenheiro IA)
- [ ] Implementa `def select_metal(prompt, agent_object) -> Metal`
- [ ] Heurísticas v1:
  - complexity_score (multi_domain, high_stakes, ambiguous, novel)
  - Escalação: complexity > 0.75 → Opus; > 0.50 → Sonnet; else default
  - Histórico (query execution_log, success rates)
  - Trade-off (0.9 × success - 0.1 × cost)
- [ ] Testes: 50+ casos (simples → complexo)
- [ ] Notebook ou script standalone

**Dono**: Engenheiro IA  
**Bloqueador**: Nenhum  
**Saída**: MSE v0.1 (código + testes)

### SEMANA 2

#### 2.1 Refinar Schema (DBA + IA)
- [ ] Feedback do prototipo MSE → ajustes na schema (se precisar)
- [ ] Exemplo: adicionar coluna `escalation_confidence_threshold` em `agent_metal_mapping`?
- [ ] Script SQL final (pronto para deploy)

**Dono**: DBA + Engenheiro IA  
**Bloqueador**: Depende de 1.3  
**Saída**: schema.sql v1.0

#### 2.2 Desenhar Agent Relationships (~30 linhas)
- [ ] Extrai de `SKILL.md` dos 20 agentes os handoffs explícitos
- [ ] Mapeia: source_agent → target_agent, trigger_keywords, condition
- [ ] Exemplo:
  ```
  agente-saneamento → agente-energia
  trigger: ["subestação", "LT", "eletricidade"]
  condition: IF mention AND critical
  relationship: "Handoff"
  ```
- [ ] Valida com product

**Dono**: Tech Lead  
**Bloqueador**: Depende de 1.2  
**Saída**: agent_relationships.json (30 linhas)

#### 2.3 Apresentar v2 ao MN (Gate)
- [ ] Apresenta schema finalizado
- [ ] Apresenta 20 agentes mapeados
- [ ] Mostra protótipo MSE
- [ ] MN aprova ou pede ajustes

**Dono**: Tech Lead  
**Bloqueador**: Depende de 2.1, 2.2  
**Saída**: ✅ Aprovação para Fase 2

---

## ASSIGNMENTS

| Função | Responsável | Email |
|--------|-------------|-------|
| DBA | [TBD] | — |
| Tech Lead | [TBD] | — |
| Engenheiro IA | [TBD] | — |
| Product Manager | [TBD] | — |
| DevOps/Ops | [TBD] | — |

**Ação**: MN nomeia responsáveis por cada função.

---

## ENTREGÁVEIS ESPERADOS (FIM DA FASE 1)

1. ✅ **schema.sql** — Tabelas + índices (pronto para migrate)
2. ✅ **agents.json** — 20 agentes com todos os metadados
3. ✅ **agent_relationships.json** — Handoffs explícitos (~30)
4. ✅ **agent_metal_mapping.json** — Alocação default + escalação
5. ✅ **mse_prototype.py** — Metal Selection Engine v0.1 + testes
6. ✅ **PR branch updated** — Documentação incorpora feedback MN

---

## DEPENDÊNCIAS EXTERNAS

### viniciusmagnos/manta-hub (Phase A MCP — paralelo)

Enquanto Fase 1 roda aqui, **em paralelo**:
- [ ] Merge PR `manta-hub#3`
- [ ] Deploy MCP na VPS
- [ ] E2E test
- [ ] Setup Cowork connector

**Coordenador**: Vinicius (backend)  
**Timeline**: 1 semana  
**Bloqueador para Fase 4?** Não — Fase 1-3 são design-only

---

## RISCOS & MITIGAÇÕES

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| Schema incompleta | Média | Alto | Validação DBA semana 1 |
| 20 agentes mal mapeados | Baixa | Alto | Product review semana 2 |
| MSE heurísticas falham em testes | Média | Médio | Iteração rápida (protótipo) |
| MN rejeita design | Baixa | Crítico | Já aprovado, só refine |

---

## CHECKLIST SAÍDA FASE 1

- [ ] Schema validado (DBA assinado)
- [ ] 20 agentes mapeados (product confirmado)
- [ ] MSE prototipado (50+ testes passando)
- [ ] Relationships desenhadas (tech lead validou)
- [ ] MN aprova v2 (gate passou)
- [ ] PR #51 atualizado com feedback
- [ ] Ticket MNT-2026-OBJECTS-METALS criado no Jira
- [ ] Fase 2 pode começar

---

## PRÓXIMAS REUNIÕES

| Data | Reunião | Duração | Agenda |
|------|---------|---------|--------|
| 2026-08-02 (HOJE) | Kickoff | 30 min | Assignments + DBA questions |
| 2026-08-06 (Dia 3) | Status midweek | 15 min | Bloqueadores |
| 2026-08-09 (Dia 6) | Schema + MSE review | 45 min | Validação |
| 2026-08-13 (Dia 10) | MN gate approval | 30 min | v2 final |

---

## COMUNICAÇÃO

- **Slack**: #manta-maestro-objects-metals (channel criado)
- **Jira**: MNT-2026-OBJECTS-METALS
- **Drive**: /Manta Associados/IA/Maestro v5.0 (compartilhado)
- **Escalação**: Qualquer bloqueador → MN direto (não espera reunião)

---

**Status**: 🟢 FASE 1 INICIADA  
**Proxima revisão**: 2026-08-06 (midweek)

Data: 2026-08-02 | Versão: 1.0

