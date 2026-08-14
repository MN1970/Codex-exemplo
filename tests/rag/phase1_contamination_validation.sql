-- Manta Maestro RAG Phase 1 — Contamination Validation Test Suite
-- Arquivo: tests/rag/phase1_contamination_validation.sql
-- Propósito: Validar 8 queries históricas de contaminação
-- Execução: psql "$SUPABASE_DB_URL" -f tests/rag/phase1_contamination_validation.sql
--
-- BASELINE (benchmark anterior):
--   - Recall@1: 69.23%
--   - Recall@3: 84.62%
--   - Contaminação: 20.51%
--
-- EXPECTED RESULTS (Phase 1):
--   - Recall@1: 74-77% (fixar 5+ queries)
--   - Recall@3: 87-88%
--   - Contaminação: 12-14% (reduzir 30-40%)
--

BEGIN;

-- =====================================================================
-- VALIDAÇÃO 1: Query "terraplenagem" (esperado: S1, baseline captura S10)
-- =====================================================================
-- Esperado: Top resultado deve ser S1 (Rodovias), não S10 (Barragens)
-- Anti-termo aplicado: S10 NÃO contém "terraplenagem rodoviária" como anti-termo
--   → precisa ser penalizado por incluir "aterro" ou "terraplenagem"

SELECT
  'Test #1: terraplenagem rodoviária' as test_name,
  ctq.expected_domain,
  ctq.incorrectly_returned_domain as was_returning,
  'EXPECTED: S1 ranks #1 (improved from rank 3)' as expected_behavior
FROM contamination_test_queries ctq
WHERE ctq.test_query LIKE '%terraplenagem%' AND ctq.id = (
  SELECT MIN(id) FROM contamination_test_queries WHERE test_query LIKE '%terraplenagem%'
);

-- =====================================================================
-- VALIDAÇÃO 2: Query "fundação estrutural" (esperado: S2, baseline captura S10)
-- =====================================================================
SELECT
  'Test #2: fundação estrutural OAE' as test_name,
  ctq.expected_domain,
  ctq.incorrectly_returned_domain as was_returning,
  'EXPECTED: S2 ranks #1 (improved from rank 2)' as expected_behavior
FROM contamination_test_queries ctq
WHERE ctq.test_query LIKE '%fundação%' AND ctq.id = (
  SELECT MIN(id) FROM contamination_test_queries WHERE test_query LIKE '%fundação%'
);

-- =====================================================================
-- VALIDAÇÃO 3: Query "drenagem" (esperado: S1, baseline captura S10)
-- =====================================================================
SELECT
  'Test #3: drenagem rodoviária' as test_name,
  ctq.expected_domain,
  ctq.incorrectly_returned_domain as was_returning,
  'EXPECTED: S1 ranks #1 (improved from rank 4)' as expected_behavior
FROM contamination_test_queries ctq
WHERE ctq.test_query LIKE '%drenagem rodoviária%' AND ctq.id = (
  SELECT MIN(id) FROM contamination_test_queries WHERE test_query LIKE '%drenagem rodoviária%'
);

-- =====================================================================
-- VALIDAÇÃO 4: Query "núcleo de aterro" (esperado: S2, baseline captura S10)
-- =====================================================================
SELECT
  'Test #4: núcleo de aterro ponte' as test_name,
  ctq.expected_domain,
  ctq.incorrectly_returned_domain as was_returning,
  'EXPECTED: S2 ranks #1 (improved from rank 5)' as expected_behavior
FROM contamination_test_queries ctq
WHERE ctq.test_query LIKE '%núcleo de aterro%' AND ctq.id = (
  SELECT MIN(id) FROM contamination_test_queries WHERE test_query LIKE '%núcleo de aterro%'
);

-- =====================================================================
-- VALIDAÇÃO 5: Query "via permanente" (esperado: S4, baseline captura S10)
-- =====================================================================
SELECT
  'Test #5: via permanente metrô' as test_name,
  ctq.expected_domain,
  ctq.incorrectly_returned_domain as was_returning,
  'EXPECTED: S4 ranks #1 (improved from rank 3)' as expected_behavior
FROM contamination_test_queries ctq
WHERE ctq.test_query LIKE '%via permanente%' AND ctq.id = (
  SELECT MIN(id) FROM contamination_test_queries WHERE test_query LIKE '%via permanente%'
);

-- =====================================================================
-- VALIDAÇÃO 6: Query "dragagem" (esperado: S6, baseline captura S10)
-- =====================================================================
SELECT
  'Test #6: dragagem porto' as test_name,
  ctq.expected_domain,
  ctq.incorrectly_returned_domain as was_returning,
  'EXPECTED: S6 ranks #1 (improved from rank 2)' as expected_behavior
FROM contamination_test_queries ctq
WHERE ctq.test_query LIKE '%dragagem%' AND ctq.id = (
  SELECT MIN(id) FROM contamination_test_queries WHERE test_query LIKE '%dragagem%'
);

-- =====================================================================
-- VALIDAÇÃO 7: Query "concreto rolado" (esperado: S2, baseline captura S10)
-- =====================================================================
SELECT
  'Test #7: concreto rolado estrutura' as test_name,
  ctq.expected_domain,
  ctq.incorrectly_returned_domain as was_returning,
  'EXPECTED: S2 ranks #1 (improved from rank 4)' as expected_behavior
FROM contamination_test_queries ctq
WHERE ctq.test_query LIKE '%concreto rolado%' AND ctq.id = (
  SELECT MIN(id) FROM contamination_test_queries WHERE test_query LIKE '%concreto rolado%'
);

-- =====================================================================
-- VALIDAÇÃO 8: Query "aterro" (esperado: S1, baseline captura S10)
-- =====================================================================
SELECT
  'Test #8: aterro rodoviário' as test_name,
  ctq.expected_domain,
  ctq.incorrectly_returned_domain as was_returning,
  'EXPECTED: S1 ranks #1 (improved from rank 3)' as expected_behavior
FROM contamination_test_queries ctq
WHERE ctq.test_query LIKE '%aterro rodoviário%' AND ctq.id = (
  SELECT MIN(id) FROM contamination_test_queries WHERE test_query LIKE '%aterro rodoviário%'
);

-- =====================================================================
-- RESUMO: Contagem de testes e status
-- =====================================================================
SELECT
  'Phase 1 Validation Summary' as summary,
  COUNT(*) as total_queries,
  COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_validation,
  COUNT(CASE WHEN status = 'passed' THEN 1 END) as passed,
  COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed
FROM contamination_test_queries;

-- =====================================================================
-- RESUMO: Anti-termos cadastrados por domínio
-- =====================================================================
SELECT
  domain,
  domain_full_name,
  COUNT(*) as anti_terms_count,
  ARRAY_AGG(DISTINCT anti_term ORDER BY anti_term) as anti_terms_list,
  ROUND(AVG(penalty_score)::NUMERIC, 2) as avg_penalty_score
FROM domain_anti_terms
GROUP BY domain, domain_full_name
ORDER BY domain;

-- =====================================================================
-- SETUP PARA PRÓXIMO STEP (Phase 2 — validação de embedding)
-- =====================================================================
-- Query para marcar testes como "em validação"
-- (Executar após Phase 1 ser deployado em staging)

-- UPDATE contamination_test_queries
-- SET
--   status = 'in_progress',
--   tested_at = NOW()
-- WHERE status = 'pending';

COMMIT;

-- =====================================================================
-- NOTAS PARA EXECUÇÃO MANUAL
-- =====================================================================
--
-- 1. Executar em STAGING primeiro:
--    psql "$STAGING_DB_URL" -f tests/rag/phase1_contamination_validation.sql
--
-- 2. Verificar resultado de cada validação (#1 a #8):
--    - Deve retornar expected_domain = S1/S2/S4/S6 conforme query
--    - was_returning deve ser S10 (problema histórico)
--    - expected_behavior descreve a correção esperada
--
-- 3. Após Phase 1 deployment:
--    - Re-executar esta query suite
--    - Atualizar status em contamination_test_queries para 'passed'
--    - Comparar Recall@1, Recall@3 contra baseline
--
-- 4. Critério de sucesso (Phase 1):
--    - Recall@1: >= 74% (baseline 69.23%)
--    - Recall@3: >= 87% (baseline 84.62%)
--    - Contaminação: <= 14% (baseline 20.51%)
--    - Todos 8 testes: status = 'passed'
--
-- =====================================================================
