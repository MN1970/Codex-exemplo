# Maestro — Execução em Paralelo com 8 Agentes Sonnet

**Versão**: v4.3  
**Data**: 2026-07-26  
**Ticket**: MNT-2026-MAESTRO-PARALELO-8-SONNET  
**Autor**: Manta Associados (Claude Code)

---

## Visão Geral

Configuração otimizada do Maestro (Manta 00 router) para executar **8 agentes Sonnet em paralelo**, distribuindo carga de trabajo em intake multi-disciplina.

### Objetivo

- Reduzir latência de resposta para projetos que exigem análise simultânea de múltiplas disciplinas
- Aproveitar arquitetura fan-out disponível no Claude SDK
- Manter consistência de modelo (Sonnet 5 como baseline)
- Priorizar saneamento (AySA) e energia (ANEEL/State Grid)

---

## Arquitetura

### Pool de 8 Agentes (Claude Sonnet 5)

```
Maestro (Manta 00)
    ├─→ [1] Manta 02 — contratual (análise documental)
    ├─→ [2] Manta 04 — imobiliario (projetos imob.)
    ├─→ [3] Manta 05 — orcamento (custos)
    ├─→ [4] Manta 07 — cronograma (prazos)
    ├─→ [5] Manta 13 — bd (viabilidade)
    ├─→ [6] Manta 14 — apresentacoes (docs)
    ├─→ [7] Manta 03-S8 — agente-saneamento (AySA 🔴)
    └─→ [8] Manta 03-S9 — agente-energia (ANEEL/State Grid 🔴)
```

### Fluxo de Execução

```
[Usuário input]
      ↓
[Maestro — intake Q2]
      ↓
[Classificação disciplina + contexto]
      ↓
[Fan-out paralelo aos 8 agentes]
      ↓
[Aguardar respostas (timeout 120s/agente)]
      ↓
[Síntese + ranking de relevância]
      ↓
[Output ao usuário]
```

**Tempo estimado**: 3-5s (vs. 30-45s sequencial)

---

## Especificação Técnica

### Modelo Padrão
- **Tier**: Claude Sonnet 5 (modelo padrão pool)
- **Fallback leve**: Haiku 4.5 (queries estruturadas < 500 tokens)
- **Fallback pesado**: Opus 5 (síntese final se contexto > 50k tokens)

### Limites
| Parâmetro | Valor | Notas |
|-----------|-------|-------|
| Agentes paralelos | 8 | Fixo, respeitando quota Claude SDK |
| Timeout/agente | 120s | Falha graciosa se exceder |
| Contexto max/agente | 200k tokens | Janela padrão Sonnet |
| Peso síntese | Opus 5 | Só se resultado > 50k tokens |

### Priorização
1. **🔴 Crítica**: Saneamento (S8-AySA), Energia (S9-ANEEL)
2. **🟡 Alta**: Orçamento (05), Cronograma (07), Contratual (02)
3. **🟢 Normal**: Imobiliário (04), BD (13), Apresentações (14)

---

## Casos de Uso

### ✓ USAR paralelização (fan-out 8 agentes)
- Projeto multi-disciplina (ex: saneamento + transmissão + imobiliário)
- Intake complexo que envolve ≥3 disciplinas diferentes
- Análise de viabilidade que exige custo + cronograma + legal simultâneos
- Documentação integrada (parecer + orçamento + cronograma + apresentação)

**Exemplo**: "Projeto de ETA com AySA + conexão subestação + terreno"
→ Dispara S8 (saneamento) + S9 (energia) + 04 (imob.) + 05 (orçamento) em paralelo

### ✗ NÃO usar paralelização
- Query de uma única disciplina (roubar vs. Sonnet puro)
- Projeto pequeno que não justifica overhead
- Debugs/testes (usar Haiku direto)

---

## Integração com Supabase

Tabela `maestro_agent_pool` (nova):

```sql
CREATE TABLE maestro_agent_pool (
  agent_code TEXT PRIMARY KEY,
  agent_name TEXT NOT NULL,
  model_tier TEXT DEFAULT 'sonnet',
  max_concurrent INT DEFAULT 1,
  timeout_sec INT DEFAULT 120,
  priority INT DEFAULT 0,
  pool_group TEXT DEFAULT 'parallel-8-sonnet',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

INSERT INTO maestro_agent_pool VALUES
  ('Manta 02', 'contratual', 'sonnet', 1, 120, 90),
  ('Manta 04', 'imobiliario', 'sonnet', 1, 120, 50),
  ('Manta 05', 'orcamento', 'sonnet', 1, 120, 100),
  ('Manta 07', 'cronograma', 'sonnet', 1, 120, 100),
  ('Manta 13', 'bd', 'sonnet', 1, 120, 70),
  ('Manta 14', 'apresentacoes', 'sonnet', 1, 120, 50),
  ('Manta 03-S8', 'agente-saneamento', 'sonnet', 1, 120, 200),
  ('Manta 03-S9', 'agente-energia', 'sonnet', 1, 120, 200);
```

---

## Implementação (Roadmap)

- [ ] **Sprint 1** (semana de 29 jul)
  - Atualizar CLAUDE.md (v4.3) ✓ DONE
  - Upload para SP ← YOU ARE HERE
  - Adicionar table maestro_agent_pool no Supabase

- [ ] **Sprint 2** (5-12 ago)
  - Implementar fan-out no Maestro SDK
  - Teste com 3 prompts multi-disciplina
  - Benchmark: latência vs. throughput

- [ ] **Sprint 3** (12-19 ago)
  - Ativar paralelização em produção
  - Monitoramento via DUNE/observability
  - Rollout gradual (10% → 100% traffic)

---

## Referências

- [CLAUDE.md v4.3](../../../CLAUDE.md) — Registry mestre
- [Maestro Routing Rules](../ARQUITETURA-AGENTES-IA.md) — Detalhes de classificação
- [Claude SDK Fan-Out](https://docs.anthropic.com) — Documentação oficial
- [Ticket MNT-2026-MAESTRO-PARALELO-8-SONNET](https://jira.manta.local/browse/MNT-2026-MAESTRO-PARALELO-8-SONNET)

---

**Status**: 🆕 DRAFT  
**Próxima revisão**: 2026-08-26
