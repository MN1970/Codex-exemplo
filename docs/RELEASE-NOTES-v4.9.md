# v4.9 - Fechar loop de aprendizado (2026-07-19)

## Visão Geral

Versão v4.9 implementa o **loop de aprendizado end-to-end** do Maestro com 5 pipes paralelas idempotentes, todas com gate humano pré-apply.

**Data de release:** 2026-07-19 (produção via Supabase MCP)  
**Status:** ✅ Implantado

## 5 Pipes Paralelas

### Pipe 1: Consolidação diária (`consolidate_old_episodes()`)
- **O quê:** cron GH Action 08:00 UTC consolida episódios de >7 dias no arquivo
- **Arquivo:** `backends/shared/manta_shared/episode_consolidation.py`
- **Gatilho:** `consolidate_old_episodes(archive_root, max_age_days=7)` via função SQL ou wrapper Python
- **Outcome:** libera RAM, preserva auditoria

### Pipe 2: Ingestão pós-obra (`/field-measurement` endpoint)
- **O quê:** novo endpoint AskCAD `POST /api/field-measurement` para coleta de dados no canteiro
- **Schema:** `{session_id, project_id, measurement_type, values, location, timestamp}`
- **Destino:** tabela `field_measurements` em `askcad.db`
- **Uso:** alimenta refinamento de premissas de cenários terraplenagem

### Pipe 3: Learned router v4.6 (skip formal)
- **Status:** migration de v4.6 fica pendente em prod
- **Razão:** dados sintéticos apenas; no A/B testing; produtividade atual (baseline heurística) > ganho esperado
- **Decidido:** defer até v4.8 com dataset real de >500 queries

### Pipe 4: Seed Manta Cases v4.9
- **Coleção:** `mcs:` (priority 120 > academic 100)
- **Casos:** 23 Knowledge Elements de 3 fontes:
  - **OAE 622** (Rio Queluz, BR-116/SP) — 8 KEs (rebar patterns, bearing specs)
  - **EPR BR-365** (Ponta Grossa) — 10 KEs (terraplenagem, geotecnia solo mole)
  - **AySA anonimizado** (saneamento Argentina) — 5 KEs (ETA/ETE design, SNIS compliance)
- **Ingestão:** via `backends/mcp/scripts/ingest_manta_cases.py`
- **Validação:** smoke test OK em produção (AKP-JF-00001)

### Pipe 5: Judge feedback loop D1' (adaptado)
- **Schema real (prod):** `manta_rag_queries` + coluna `judge_score` nova
- **Trigger:** função SQL `trigger_judge_flag_on_low_score` → insere em `akp_curation_backlog`
- **Gating:** `judge_score < 3` (critério rigoroso)
- **Outcome:** tickets automáticos para revisor humano (MN)
- **OBS:** agent_response_flags não existe em prod; adaptado ao schema enxuto

## Mudanças Técnicas

### Migration SQL (v4.9)
**Arquivo:** `supabase/migrations/2026_07_19_v4_9_closes_learning_loop.sql`

```sql
-- Nova tabela field_measurements (AskCAD)
CREATE TABLE field_measurements (
  id SERIAL PRIMARY KEY,
  session_id UUID NOT NULL,
  project_id TEXT,
  measurement_type TEXT,
  values JSONB,
  location TEXT,
  timestamp TIMESTAMP DEFAULT NOW()
);

-- Judge score em manta_rag_queries (novo)
ALTER TABLE manta_rag_queries 
  ADD COLUMN judge_score INT CHECK (judge_score >= 0 AND judge_score <= 10);

-- Função trigger judge flag
CREATE OR REPLACE FUNCTION trigger_judge_flag_on_low_score()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.judge_score IS NOT NULL AND NEW.judge_score < 3 THEN
    INSERT INTO akp_curation_backlog (source, ref, created_at)
    VALUES ('judge_low_score', NEW.id::TEXT, NOW())
    ON CONFLICT DO NOTHING;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Segurança: REVOKE grants excessivos
REVOKE ALL ON v_judge_feedback_health FROM PUBLIC;
GRANT SELECT ON v_judge_feedback_health TO authenticated;
```

### Breaking Changes
- **`promote_gaps_to_backlog(INTEGER, FLOAT, INTEGER)`**  
  Assinatura mudou: antes aceitava apenas `(INTEGER)`. Novo: `(max_age_days, min_confidence, batch_size)`.  
  **Impacto:** queries antigas quebram; script de verify refatorado para novo signature.

- **Rollback:** bloco `DROP TABLE IF EXISTS field_measurements CASCADE;` no final do migration SQL.

### Hardening pós-apply
- ✅ REVOKE grants em views sensíveis (`v_judge_feedback_health`, `v_akp_contradictions`)
- ✅ Cron YAML rename: `.github/workflows/v4.9-consolidate-episodes.yml` (antes: `akp-daily-cron.yml`)
- ✅ Verify script refactor: `tests/v4_9/verify_learning_loop.py` (idempotencia testada)

## Commits Associados
| Hash | Mensagem |
|------|----------|
| `55274b8` | v4.9 base: 5 pipes scaffolding |
| `c8b86f0` | Adapt Pipe 5 para schema real (manta_rag_queries direto) |
| `cc9baf3` | Fix WHEN condition na trigger judge_flag |

## Smoke Test
**Caso de teste:** AKP-JF-00001 (query síntese de 3 papers com judge_score=2)  
**Resultado:** ✅ Idempotencia OK, trigger disparou, backlog alimentado corretamente

## Próximos passos (v4.10)
1. Recolher >500 queries reais para dataset do learned router
2. A/B test: heurística vs ML
3. Formalizar learned router em prod (v4.8 original fica como rollback)
4. Integrar `/field-measurement` → cenários terraplenagem (dashboards ao vivo)
