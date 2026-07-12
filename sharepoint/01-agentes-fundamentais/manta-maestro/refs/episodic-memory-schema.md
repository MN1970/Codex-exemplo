# refs/episodic-memory-schema.md — manta-maestro

Referência canônica da **Memória Episódica** — Upgrade C do roadmap
v4.7 (MNT-IA-20260712-001, §4). Introduz o pilar de memória que
faltava no Maestro v4.6.1: registros de execução persistentes que
alimentam Reflexion (Upgrade A), SkillForge (Upgrade F) e o Learned
Router (V1 da v4.6).

Fonte: prior art listada no §11 do roadmap — Shinn et al. 2023
Reflexion, Park et al. 2023 Generative Agents (memory stream +
reflection), Sumers et al. 2024 "Cognitive architectures for language
agents" (arXiv:2309.02427), Axelsen et al. 2026 MemSkill.

---

## 1. Os 4 pilares de memória

Sumers et al. 2024 formaliza 4 pilares canônicos numa arquitetura
cognitiva de LLM agent. Estado atual na Manta:

| Pilar | O que armazena | Onde vive em v4.6.1 | Onde vive em v4.7 |
|-------|----------------|---------------------|-------------------|
| **Working** | Contexto ativo do turno | System prompt + user turn | System prompt + P2 (Upgrade B) |
| **Episodic** | Execuções passadas ("o que fiz semana passada") | ❌ AUSENTE | ✅ `agent_episodes` (esta ref) |
| **Semantic** | Conhecimento factual do domínio | Coleções RAG (`san:`, `por:`, `academic:`, `mcs:`) | Idem + auto-enrichment (v4.7 §5) |
| **Procedural** | Como fazer as coisas | `SKILL.md` (manuais) | Idem + `sharepoint/03-skills-forjadas/` (SkillForge) |

Este documento cobre APENAS o pilar **Episodic** — o novo em v4.7. Os
outros 3 pilares estão nos refs vizinhos.

---

## 2. Schema DDL — `agent_episodes`

Migração v4.7 candidata em `supabase/migrations/2026_07_13_episodic_memory_v4_7.sql`.
Schema aditivo — não toca tabelas existentes.

```sql
CREATE TABLE IF NOT EXISTS agent_episodes (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    -- Identificação
    agent_id      TEXT NOT NULL,           -- ex: agente-portos, manta-15-advisory
    task_id       UUID NOT NULL,           -- correlação com o P2 emitido
    session_id    UUID,                    -- opcional, correlação com sessão do usuário
    user_id       INTEGER,                 -- FK auth.users (best-effort)
    -- Contrato
    p2_contract   JSONB NOT NULL,          -- P2 completo, imutável
    -- Execução
    tools_used    JSONB NOT NULL DEFAULT '[]',   -- ["RagSearch", "ExecuteCode", ...]
    n_turns       INT  NOT NULL DEFAULT 1,       -- turnos consumidos
    n_reflexion   INT  NOT NULL DEFAULT 0,       -- iterações do Reflexion Loop
    -- Output
    output_final  TEXT,                    -- resposta entregue ao usuário
    output_format TEXT DEFAULT 'markdown', -- markdown | json | xlsx_url
    -- Qualidade
    judge_score   NUMERIC(3,1),            -- 0.0-10.0, do LLM-as-a-judge (v4.6 V5)
    judge_notes   TEXT,
    all_criteria_passed BOOLEAN,           -- do Reflexion (v4.7 A)
    escalated_to_human  BOOLEAN DEFAULT FALSE,
    -- Custo
    cost_usd      NUMERIC(6,4),            -- inclui todas iterações + judge
    model_primary TEXT DEFAULT 'sonnet-4-6',
    -- Vetor (para clustering do SkillForge — v4.7 F)
    embedding     VECTOR(384),             -- multilingual-e5-small do resumo
    -- Timestamps
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    -- Housekeeping
    expires_at    TIMESTAMPTZ,             -- decay policy (§4)
    archived      BOOLEAN DEFAULT FALSE
);

CREATE INDEX ix_agent_episodes_agent    ON agent_episodes(agent_id, created_at DESC);
CREATE INDEX ix_agent_episodes_task     ON agent_episodes(task_id);
CREATE INDEX ix_agent_episodes_quality  ON agent_episodes(judge_score) WHERE archived = FALSE;
CREATE INDEX ix_agent_episodes_embedding ON agent_episodes USING hnsw (embedding vector_cosine_ops);

-- View helper para o SkillForge
CREATE OR REPLACE VIEW v_high_quality_episodes AS
SELECT * FROM agent_episodes
WHERE archived = FALSE
  AND judge_score >= 7.0
  AND all_criteria_passed = TRUE;
```

---

## 3. Fluxo de injeção pré-tarefa

Antes de emitir o P2, o Maestro consulta episódios similares e
injeta 1-3 exemplos como "shots" — few-shot direto de execuções reais
do próprio agente.

```
┌─────────────────────────────────────────────────────────┐
│ 1. Maestro recebe pedido do usuário                     │
│ 2. Classifica routing → agent_target = X (Learned/rule) │
│ 3. Constrói P2 draft (§Upgrade B)                        │
│ 4. Embeda o P2.objective + context_compressed            │
│ 5. Query:                                                │
│    SELECT * FROM agent_episodes                          │
│    WHERE agent_id = X                                    │
│      AND judge_score >= 7.5                              │
│      AND expires_at > now()                              │
│    ORDER BY embedding <=> $query_emb                     │
│    LIMIT 3;                                              │
│ 6. Injeta os 3 episódios em prompt suplementar:          │
│    "Exemplos recentes de sua execução:"                  │
│    - {ep1.p2.objective} → {ep1.output_final[:800]}       │
│    - {ep2.p2.objective} → {ep2.output_final[:800]}       │
│    - {ep3.p2.objective} → {ep3.output_final[:800]}       │
│ 7. Subagente executa com contexto enriquecido            │
│ 8. Ao final, GRAVA novo episódio em agent_episodes       │
└─────────────────────────────────────────────────────────┘
```

**Poda**: se o agente é novo (< 20 episódios), pula injeção — não vale
o custo de embedding query com base pequena. Fallback: só `SKILL.md`
+ P2 (comportamento v4.6.1).

**Custo**: 1 query pgvector ≈ 10ms + 3 × ~800 tokens de contexto extra
≈ US$0.005 por tarefa. Trade-off aceito.

---

## 4. Política de decay 30/90d

Não guardar tudo para sempre. Decay em 3 camadas:

| Idade | Estado | Ação |
|-------|--------|------|
| 0-30d | **Hot** | Elegível para injeção pré-tarefa (§3). Full JSONB. |
| 30-90d | **Warm** | NÃO injeta mais em §3. Continua elegível para SkillForge clustering (§Upgrade F). Full JSONB. |
| 90d+ | **Cold** | `archived = TRUE`. Perde índice HNSW. Compressão: `p2_contract` reduzido a hash, `output_final` truncado a 400 chars. |
| 180d+ | **Purge** | Delete físico, exceto se `judge_score >= 9.5` (guarda "hall of fame" indefinidamente para arquiteto-IA). |

Job diário: `04:00 UTC` `SELECT run_episodic_decay();`. Ver GH Action
`.github/workflows/episodic-decay.yml` (v4.7 candidate).

**Override**: MN pode marcar episódio como `pinned = TRUE` para
sobreviver à purga (ex: episódios usados como fixtures de teste E2E).

---

## 5. Wipe Test — o sistema DEVE funcionar sem episódios

**Invariante crítica**: se `agent_episodes` for TRUNCATE'd (por
qualquer motivo: bug, restore, decisão MN), o Maestro DEVE continuar
funcionando com performance no baseline v4.6.1.

Isto significa:
- ✅ Routing funciona (Learned Router tem seu próprio dataset em
  `maestro_routing_predictions`)
- ✅ Reflexion Loop funciona (usa P2, não histórico)
- ✅ SkillForge pausa (sem episódios não há o que forjar) — OK
- ✅ Injeção pré-tarefa (§3) faz fallback para "sem exemplos" — OK,
  degrada suavemente
- ✅ LLM-as-a-judge continua (não depende de episódios anteriores)

**Teste E2E**: `tests/maestro/test_wipe_recovery.py` faz TRUNCATE +
roda os 8 cenários do `handoffs-cross-agent.md`. Todos DEVEM passar.

Motivação: memória é *aditiva* (Sumers 2024 §5.3). Se vira
*dependência dura*, o sistema fica frágil. Mantemos episódios como
"gordura", não como "esqueleto".

---

## 6. Três exemplos de queries úteis

### 6.1 Detectar agente com quality em queda

```sql
-- Agentes com judge_score em queda nos últimos 14d vs 14d anteriores
WITH janelas AS (
  SELECT
    agent_id,
    AVG(judge_score) FILTER (WHERE created_at > now() - INTERVAL '14 days') AS score_recente,
    AVG(judge_score) FILTER (WHERE created_at BETWEEN now() - INTERVAL '28 days' AND now() - INTERVAL '14 days') AS score_anterior
  FROM agent_episodes
  WHERE archived = FALSE
  GROUP BY agent_id
  HAVING COUNT(*) FILTER (WHERE created_at > now() - INTERVAL '28 days') >= 10
)
SELECT
  agent_id,
  ROUND(score_recente::numeric, 2) AS score_recente,
  ROUND(score_anterior::numeric, 2) AS score_anterior,
  ROUND((score_recente - score_anterior)::numeric, 2) AS delta
FROM janelas
WHERE score_recente < score_anterior - 0.5
ORDER BY delta ASC;
```

Uso: MN roda semanalmente para saber quem precisa retrain.

### 6.2 Pescar episódios ruins do agente-portos para investigar

```sql
SELECT
  id,
  created_at,
  p2_contract->>'objective' AS objetivo,
  judge_score,
  judge_notes,
  escalated_to_human,
  n_reflexion,
  cost_usd
FROM agent_episodes
WHERE agent_id = 'agente-portos'
  AND judge_score < 6.0
  AND archived = FALSE
ORDER BY created_at DESC
LIMIT 20;
```

Uso: input direto para o gate humano do SkillForge (§F) — episódios
ruins geralmente apontam para skills faltando.

### 6.3 Encontrar candidatos a SkillForge — clusters densos

```sql
-- 5-nearest neighbors por embedding, filtrado por qualidade alta
WITH seed AS (
  SELECT id, agent_id, embedding
  FROM agent_episodes
  WHERE agent_id = 'agente-portos'
    AND judge_score >= 7.5
    AND archived = FALSE
  LIMIT 100
),
vizinhos AS (
  SELECT
    s.id AS seed_id,
    ae.id AS vizinho_id,
    (s.embedding <=> ae.embedding) AS dist,
    ae.p2_contract->>'objective' AS obj_vizinho
  FROM seed s
  CROSS JOIN LATERAL (
    SELECT id, embedding, p2_contract
    FROM agent_episodes
    WHERE archived = FALSE
      AND agent_id = s.agent_id
      AND id <> s.id
    ORDER BY s.embedding <=> embedding
    LIMIT 5
  ) ae
)
SELECT seed_id, COUNT(*) AS n_similares
FROM vizinhos
WHERE dist < 0.15
GROUP BY seed_id
HAVING COUNT(*) >= 4
ORDER BY n_similares DESC;
```

Uso: alimenta o passo 1 (Clustering) do pipeline SkillForge (§Upgrade F).

---

## 7. Instrumentação e observabilidade

- **View `v_episodic_health`**: por agente, mostra n_episodes,
  avg_score, avg_cost, n_escalations, oldest_hot, oldest_warm.
- **Alerta Slack**: `judge_score` cai > 1.0 em janela 7d ⇒ ping MN.
- **Alerta Slack**: `agent_episodes` cresce > 10x baseline em 24h ⇒
  ping MN (possível loop patológico).
- **Dashboard**: `manta-hub/dashboard/pages/episodic.tsx` — timeline
  interativa dos 500 últimos episódios com filtros por agente,
  score, escalation.

---

## Ver também

- `SKILL.md` §14.C — política operacional da Memória Episódica
- `p2-contract-template.md` — o P2 é armazenado no campo `p2_contract`
- `reflexion-loop-guide.md` — iterações do Reflexion são gravadas em
  `n_reflexion` + `all_criteria_passed`
- `skillforge-pipeline.md` — consumidor principal via
  `v_high_quality_episodes`
- Roadmap MNT-IA-20260712-001 §4 + §11 — motivação e prior art
- Sumers et al. 2024 arXiv:2309.02427 — os 4 pilares canônicos
