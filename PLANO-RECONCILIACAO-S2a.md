# Plano de Reconciliação — Manta Maestro v4.2 → v5.0

**Ticket:** MNT-2026-RECONCILIACAO-AGENTS-S2a  
**Data:** 2026-07-25  
**Responsável:** Claude Code (manta-maestro-agent-reconciliation-owoqml)  

---

## 1. Diagnóstico

Relatório gerado pelo `reconciliacao-agentes.py`:

| Métrica | Valor |
|---------|-------|
| Agentes no banco | 28 |
| Códigos no mapa SKILL.md v4.0 | 13 |
| **Divergências totais** | **33 conflitos** |
| Setoriais (`03-S*`) no banco | 13 |
| M-scheme (`M*`) no banco | 12 |
| Guards (skill-based) no banco | 3 |

### Problemas críticos

1. **24 agentes no banco, invisíveis ao SKILL.md**: 03-S5-S13, M02, M07, M12-M23, 3 guards
2. **9 agentes no SKILL.md, inexistentes no banco**: 02, 02-C, 04-07, 13-15
3. **Colisão de Manta 15**: registrado como `advisory` no SKILL.md e como `manta-arquiteto-ia` no frontmatter
4. **Cobertura RAG incompleta**: apenas 26 KEs vetorizados cobrem 4 dos 28 agentes

---

## 2. Taxonomia proposta (v5.0)

Identificador único `agent_id` em TODAS as camadas:

```
M00        — Maestro (orquestrador)
M01–M19    — Agentes funcionais (claims, contratual, orcamento, ..., advisory)
S01–S13    — Agentes setoriais (substitui 03-S1, 03-S2, ..., 03-S13)
[skills]   — Guards: aluci-guard, consist-guard, context-guardian (saem de manta_agent_capabilities)
```

### Mapeamento de migração

#### Setoriais: `03-S*` → `S*`
| Antigo | Novo | Setor | Status |
|--------|------|-------|--------|
| 03-S1 | S01 | Rodovias | operacional |
| 03-S2 | S02 | OAE (pontes/viadutos) | operacional |
| 03-S3 | S03 | Ferrovia | conhecimento invisível |
| 03-S4 | S04 | Metrô | operacional |
| 03-S5 | S05 | Túneis | sem conhecimento |
| 03-S6 | S06 | Portos | novo (jul 2026) |
| 03-S7 | S07 | Aeroportos | novo (jul 2026) |
| 03-S8 | S08 | Saneamento | novo (jul 2026) — PRIORIDADE AySA |
| 03-S9 | S09 | Energia | novo (jul 2026) — ANEEL/State Grid |
| 03-S10 | S10 | Barragens | novo (jul 2026) |
| 03-S11 | S11 | [TBD] | roadmap |
| 03-S12 | S12 | [TBD] | roadmap |
| 03-S13 | S13 | [TBD] | roadmap |

#### Funcionais: legado `02/02-C/04-07/13-15`
| Antigo | Novo | Nome | Status |
|--------|------|------|--------|
| 02-C | M02 | Claims | reconciliar com M02 |
| 02 | M03 | Contratual | novo |
| 04 | M04 | Imobiliário | novo |
| 05 | M05 | Orçamento | novo |
| 06 | M06 | Modelagem | novo |
| 07 | M07 | Cronograma | colisão com M07 existing |
| 13 | M13 | Business Dev | colisão com M13 existing |
| 14 | M14 | Apresentações | novo |
| 15 | [resolve colisão] | Advisory / Arquiteto | requer decision |

#### Colisão especial: Manta 15
Atualmente registrado como:
- **SKILL.md v4.0**: `manta_code: "15"` → `advisory`
- **Frontmatter agente-arquiteto-ia**: `manta_code: "Manta 15"` → `manta-arquiteto-ia`

**Resolução proposta**: Atribuir `M16` a `advisory` e criar novo código `M99` (ou `M24`) para `manta-arquiteto-ia`.

---

## 3. Ações de migração

### Fase 1: Preparação e validação (dia 1)

- [ ] **P1.1** Validar esta taxonomia v5.0 com stakeholders (MN + head de produto)
- [ ] **P1.2** Exportar estado atual de `manta_agent_capabilities` para versionamento
- [ ] **P1.3** Criar tabela temporária `manta_agent_capabilities_v4_archive` (backup)

### Fase 2: Banco de dados

- [ ] **P2.1** Renomear `03-S*` → `S*` em `manta_agent_capabilities`
  - [ ] Atualizar 13 linhas (S01–S13)
  - [ ] Manter `ativo`, `modelo_default`, timestamps
  
- [ ] **P2.2** Remover guards da tabela `manta_agent_capabilities`
  - [ ] Deletar 3 linhas (aluci-guard, consist-guard, context-guardian)
  - [ ] Migrar para tabela `manta_skills_registry` (novo)

- [ ] **P2.3** Reconciliar `M*` duplicados e gaps
  - [ ] Resolver colisão M07, M13 vs. 07, 13 legacy
  - [ ] Resolver colisão M15 → Atribuir código distinto a `manta-arquiteto-ia`
  - [ ] Inserir M01, M03, M04, M05, M06, M14 (agentes legado faltando)

- [ ] **P2.4** Criar vista `v_agent_registry` em Supabase
  ```sql
  SELECT agent_id, nome_funcional, setor, modelo_default, ativo, know_vecs, updated_at
  FROM manta_agent_capabilities
  ORDER BY agent_id;
  ```

### Fase 3: Repositório de código

- [ ] **P3.1** Renomear agent files em `.claude/agents/`
  - De: `agente-rodovias.md` → `S01-rodovias.md`
  - De: `agente-saneamento.md` → `S08-saneamento.md`
  - (E outros)

- [ ] **P3.2** Atualizar CLAUDE.md master
  - Secção "Mapa de agentes": trocar `03-S*` por `S*`
  - Secção "Routing": trocar `03-S*` por `S*` nas regras do Maestro
  - Secção "RAG": atualizar prefixos de storage (`san:`, `ene:`, ...) → ainda válidos

- [ ] **P3.3** Criar `pk_agentes.json` (source of truth v5.0)
  ```json
  {
    "version": "5.0",
    "timestamp": "2026-07-25T...",
    "agents": [
      {"agent_id": "M00", "nome": "Maestro", "tipo": "router"},
      {"agent_id": "M01", "nome": "Claims", "tipo": "funcional"},
      ...
      {"agent_id": "S01", "nome": "Rodovias", "tipo": "setorial"},
      ...
    ]
  }
  ```

- [ ] **P3.4** Atualizar todos os SKILL.md
  - Trocar `manta_code: "03-S8"` por `manta_code: "S08"`
  - Trocar `manta_code: "02"` por `manta_code: "M03"` (contratual)
  - Trocar `manta_code: "15"` por `manta_code: "M16"` (advisory)
  - Adicionar novos: M01, M04–M06, M14 com `.md` files

### Fase 4: RAG e conhecimento

- [ ] **P4.1** Vetorizar conhecimento faltante para 19 agentes
  - Prioridade: S03, S09, S10, S11–S13 (os que têm KE registrado mas não vetorizado)
  - Depois: M01–M06, M14, M17–M23 (roadmap)

- [ ] **P4.2** Atualizar prefixos de storage em `rag_chunks`
  - `03-S8:...` → `S08:...` (saneamento)
  - `03-S9:...` → `S09:...` (energia)
  - etc.

### Fase 5: CI/CD e validação

- [ ] **P5.1** Atualizar `reconciliacao-agentes.py`
  - Trocar `SKILL_MAP_V4` por `SKILL_MAP_V5` (com M00, S01–S13)
  - Adicionar modo `--strict` (exit 1 se houver gap)

- [ ] **P5.2** Criar hook SessionStart
  ```bash
  python3 reconciliacao-agentes.py --db-json <conexão> --skills-dir .claude/skills --pk pk_agentes.json --strict
  # Exit 1 bloqueia sessão se houver divergência
  ```

- [ ] **P5.3** Testar routing do Maestro
  - Prompts de teste para cada S* (S01–S10)
  - Verificar que roteamento funciona com novos agent_ids

---

## 4. Rollback (contingência)

Se algo quebrar durante a migração:

```bash
# Restaurar banco de dados
psql manta_db < manta_agent_capabilities_v4_archive.sql

# Restaurar código
git revert <commit-da-fase-3>
git revert <commit-da-fase-2>
```

---

## 5. Checklist de go-live

- [ ] Todas as fases 1–4 completadas e testadas em staging
- [ ] Aprovação MN (assinatura)
- [ ] Backup confirmado
- [ ] Maestro (M00) roteando corretamente para S01–S10
- [ ] RAG recuperando documentos para todos os 28 agentes
- [ ] Hook SessionStart bloqueando divergências
- [ ] Documentação atualizada (README, ARQUITETURA-AGENTES-IA.md)

---

## 6. Benefícios esperados

| Aspecto | Antes | Depois |
|---------|-------|--------|
| Agentes visíveis ao SKILL.md | 13 (46%) | 28 (100%) |
| Agentes com KE vetorizado | 4 (14%) | 28 (100%) planejado |
| Nomenclatura consistente | divergente (03-S*, M*, legacy) | única (M00, M01–M19, S01–S13) |
| Routing ambíguo | SIM (multiple families) | NÃO (determinístico) |
| Risco operacional | ALTO (silent failures) | BAIXO (validação em CI) |

---

## 7. Próximos passos

1. **Aprovação**: CEO/CTO assina este plano
2. **Sprint planning**: 3–5 dias de work
3. **Execução**: Fases 1–4 em sequência, com testing entre cada uma
4. **Comunicação**: Notificar todos os usuários de agentes antes de go-live
5. **Monitoramento pós-go-live**: 1 semana de observação (logs, telemetria)
