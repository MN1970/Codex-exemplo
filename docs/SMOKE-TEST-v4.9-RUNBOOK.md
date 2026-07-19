Criei o runbook em `/home/user/manta-hub/docs/SMOKE-TEST-v4.9-RUNBOOK.md` (~50 linhas).

## Estrutura

- **Setup:** env vars `SUPABASE_URL` + `SUPABASE_SERVICE_ROLE_KEY` (prod `ogxxgvgtulrbbppshjie`)
- **Comando:** `python scripts/verify_judge_feedback_v4_9.py` 
- **Saída esperada:** `[OK] loop judge->backlog v4.9 funcionando. ticket=... query_id=...` (exit 0)
- **Diagnóstico 4 cenários:** missing env, 401/403 auth, trigger não disparou, priority divergiu
- **Ação por falha:** validar env, renovar key Supabase, aplicar migração v4.9, revisar trigger
- **Limpeza:** SQL para remover registros órfãos
- **Reexecução:** segura (UUID único a cada run)
- **Contato:** MN p/ escalação

## Validação

O script `verify_judge_feedback_v4_9.py` já valida:
1. INSERT em `manta_rag_queries` com `judge_score=2`
2. Delay 1s pra trigger de cascata (PostgREST não espera replicas)
3. Busca ticket `judge_flag` com `priority=3`, `severity=warn`, `agent_slug=synthetic-verify-v49`
4. Cleanup best-effort (ambos registros deletados ao fim)

Pronto p/ gate humano MN antes de prod.