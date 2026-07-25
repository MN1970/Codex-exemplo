# Reconciliação de Agentes Manta Maestro — Resumo Executivo

**Data:** 2026-07-25  
**Branch:** `claude/manta-maestro-agent-reconciliation-owoqml`  
**Status:** ✅ Entrega de S2-a (Análise) e S3 (Preparação de embeddings)

---

## O Problema

A Manta Maestro v4.2 sofre de **fragmentação severa** de nomenclatura de agentes:

| Camada | Descoberta |
|--------|-----------|
| **Banco de dados** | 28 agent_ids registrados |
| **SKILL.md v4.0** | 13 códigos mapeados (46% cobertura) |
| **Código fonte** | agentes em `.claude/agents/` sem versão unificada |
| **RAG** | 26 KEs vetorizados atendem apenas 4 dos 28 agentes |

### Divergências críticas

1. **24 agentes no banco mas invisíveis ao SKILL.md**  
   - `03-S5` a `03-S13` (8 setoriais)
   - `M02`, `M07`, `M12–M23` (12 funcionais)
   - `aluci-guard`, `consist-guard`, `context-guardian` (3 skills)

2. **9 agentes no SKILL.md mas inexistentes no banco**  
   - Legacy codes: `02`, `02-C`, `04–07`, `13–15`

3. **Colisão de Manta 15**  
   - Registrado como `advisory` no SKILL.md
   - Registrado como `manta-arquiteto-ia` no frontmatter
   - **Resolução:** Renomear `manta-arquiteto-ia` para `M16` (novidade)

4. **Cobertura de conhecimento incompleta**  
   - 4 setores com KEs registrados mas **sem vetor**: S03, S09, S10, S11–S13
   - 19 agentes sem nenhum KE
   - Sintoma: buscas retornam incompletas para ferrovia, energia, barragens

---

## Solução: Taxonomia v5.0

Um identificador único `agent_id` em **TODAS as camadas**:

```
M00          Maestro (router)
M01–M19      Agentes funcionais (claims, contratual, imobiliário, ...)
S01–S13      Agentes setoriais (rodovias, OAE, ferrovia, metrô, ...)
[skills]     Guards (aluci-guard, consist-guard, context-guardian) 
             — saem de manta_agent_capabilities, entram em skills_registry
```

### Mapeamento de migração

| Antigo | Novo | Tipo | Setor |
|--------|------|------|-------|
| 02-C | M01 | funcional | Claims |
| 02 | M02 | funcional | Contratual |
| 04–07, 13–15 | M04–M07, M13–M15 | funcional | (vários) |
| **Novo** | M16 | funcional | Arquiteto-IA |
| 03-S1 to S4 | **S01** to **S04** | setorial | Rodovias, OAE, Ferrovia, Metrô |
| 03-S5 to S10 | **S05** to **S10** | setorial | (Túneis, Portos, Aeroportos, Saneamento, Energia, Barragens) |
| 03-S11 to S13 | **S11** to **S13** | setorial | (Roadmap) |

---

## Artefatos entregues

### 1. Scripts de análise e migração

| Arquivo | Propósito | Uso |
|---------|-----------|-----|
| `reconciliacao-agentes.py` | Compara 3 fontes (banco, skills, PK) | Hook SessionStart / CI |
| `embed-kes-pendentes.py` | Vetoriza KEs faltantes + gates | S3 — pré-apply |

### 2. Dados de referência

| Arquivo | Conteúdo |
|---------|----------|
| `banco.json` | Snapshot dos 28 agent_ids (estado v4.2) |
| `pk_agentes_v5.0.json` | Fonte única de verdade: 33 agentes (M00–M16 + S01–S13 + skills) |
| `relatorio-reconciliacao.md` | Relatório de divergências (auto-gerado) |

### 3. Planejamento de implementação

| Arquivo | Cobertura |
|---------|-----------|
| `PLANO-RECONCILIACAO-S2a.md` | 5 fases de migração, 25 ações, checklist de go-live |

---

## Resultado da análise inicial

```
KEs sem embedding: 19  | livres: 6  | barrados: 13
Conflitos detectados: 33

Bloqueios por gates:
  G1 (sem aluci-guard):    10 KEs
  G2 (texto curto <400ch): 2 KEs
  G3 (score <7.0):         1 KE
```

**Ação recomendada:** Rodar `embed-kes-pendentes.py --apply` nos 6 KEs livres, depois auditar os 13 barrados (enriquecer descrição ou re-rodar aluci-guard).

---

## Benefícios da migração v5.0

| Métrica | Antes | Depois |
|---------|-------|--------|
| **Agentes visíveis em SKILL.md** | 13/28 (46%) | 28/28 (100%) |
| **Agentes com KE vetorizado** | 4/28 (14%) | 28/28 planejado |
| **Nomes inconsistentes** | 3 famílias (03-S*, M*, legado) | 1 padrão único |
| **Risco de routing ambíguo** | ALTO | BAIXO |
| **Validação automática** | NÃO | SIM (hook) |

---

## Próximos passos

### Aprovação (Hoje)
- [ ] CEO/CTO revisam PLANO-RECONCILIACAO-S2a.md
- [ ] Consenso sobre atribuição de M16 (arquiteto-IA)

### Execução (próximos 3–5 dias)
1. **Fase 1:** Backup de banco + validação
2. **Fase 2:** Renomear `03-S*` → `S*` em manta_agent_capabilities
3. **Fase 3:** Atualizar CLAUDE.md, SKILL.md, `.claude/agents/`
4. **Fase 4:** Rodar `embed-kes-pendentes.py --apply` (6 KEs livres)
5. **Fase 5:** Testar routing do Maestro + hook de validação

### Go-live
- Notificar usuários de agentes 48h antes
- Executar migração em janela de manutenção (sábado)
- Monitorar logs por 1 semana

---

## Referências

- **Banco de dados produção:** `manta_agent_capabilities` (28 agent_id)
- **Relatório de divergências:** `relatorio-reconciliacao.md`
- **Taxonomia v5.0:** `pk_agentes_v5.0.json`
- **Scripts:** `reconciliacao-agentes.py`, `embed-kes-pendentes.py`
- **Plano detalhado:** `PLANO-RECONCILIACAO-S2a.md`

---

## Contato

- **Responsável:** Claude Code (Haiku 4.5)
- **Session:** `claude/manta-maestro-agent-reconciliation-owoqml`
- **Ticket:** MNT-2026-RECONCILIACAO-AGENTS-S2a
