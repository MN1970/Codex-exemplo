# v_akp_judge_health - Decision Brief (v4.6 to v4.9 Adaptation)

## Context
v_akp_judge_health foi criada na v4.6 (llm-judge original) apontando para agent_response_flags. Em prod, a v4.6 foi adaptada: as colunas judge_* vivem inline em manta_rag_queries e agent_response_flags nunca foi criada. A view v4.6 sobreviveu porque foi criada com WITH SECURITY INVOKER apontando para manta_rag_queries diretamente durante uma reconciliacao anterior.

## Current state (2026-07-19)
View ainda existe em prod. Continua funcional (retorna JSON de saude por segmento). Nenhum consumer conhecido no manta-hub (ver grep).

## Decision: KEEP-WITH-COMMENT
Manter a view. Adicionar COMMENT ON VIEW anotando que a v4.9 introduziu v_judge_feedback_health como sucessora canonica. Nao dropar agora — risco de quebrar dashboard SP ou Cowork que consulta silenciosamente.

## Follow-up (v5.0)
Se em 90 dias (2026-10-19) nenhum consumer for identificado via telemetria, deprecar a view em v5.0 via DROP VIEW IF EXISTS + entrada no rollback.

## Reference
* Migration v4.9: supabase/migrations/2026_07_13_judge_feedback_loop_v4_9_adapted.sql
* Nova view canonica: public.v_judge_feedback_health (v4.9)
* Comment adicionado 2026-07-19 via Supabase MCP.
