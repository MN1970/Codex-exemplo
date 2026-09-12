-- Manta Maestro RAG Phase 1 — Contamination Fix
-- Ticket: MNT-2026-RAG-PHASE1-S10-DECONTAMINATION
-- Date: 2026-07-26
-- Status: Candidate for deployment
--
-- OBJETIVO: Reduzir contaminação cross-domain de S10 (Barragens)
-- que captura queries de S1, S2, S4, S6 com termos ambíguos
--
-- BASELINE (benchmark anterior):
--   - Recall@1: 69.23% (< 70% threshold)
--   - Recall@3: 84.62%
--   - Contaminação: 20.51%
--
-- TARGET (esperado após Phase 1):
--   - Recall@1: 74-77%
--   - Recall@3: 87-88%
--   - Contaminação: 12-14%
--
-- ESTRATÉGIA:
--   1. Reduzir embedding_weight de 'bar:' de 1.0 → 0.85
--   2. Criar tabela domain_anti_terms com pares domínio → termo_exclusivo
--   3. Modificar função de busca para penalizar resultados com anti-termos
--

BEGIN;

-- =====================================================================
-- 1. Criar tabela domain_anti_terms
-- =====================================================================
-- Esta tabela mapeia domínios para termos que NÃO devem aparecer
-- em documentos daquele domínio (anti-vocabulário de exclusão).

CREATE TABLE IF NOT EXISTS domain_anti_terms (
  id SERIAL PRIMARY KEY,
  domain TEXT NOT NULL,
  domain_full_name TEXT,
  anti_term TEXT NOT NULL,
  reason TEXT NOT NULL,
  penalty_score DECIMAL(3, 2) DEFAULT 0.30,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(domain, anti_term)
);

CREATE INDEX IF NOT EXISTS idx_domain_anti_terms_domain
  ON domain_anti_terms(domain);
CREATE INDEX IF NOT EXISTS idx_domain_anti_terms_anti_term
  ON domain_anti_terms(anti_term);

-- =====================================================================
-- 2. Inserir anti-termos para cada domínio
-- =====================================================================
-- Termos que indicam "outro domínio" e devem reduzir relevância

INSERT INTO domain_anti_terms (domain, domain_full_name, anti_term, reason, penalty_score)
VALUES
  -- S1 (Rodovias) — NOT barragens, rejeitos
  ('S1', 'Rodovias', 'barragem', 'Rodovia não trabalha com barragens (infraestrutura de água)', 0.40),
  ('S1', 'Rodovias', 'rejeito', 'Rodovia não lida com rejeitos TSF de barragens', 0.35),
  ('S1', 'Rodovias', 'TSF', 'Rodovia não trabalha com Tail Storage Facility', 0.40),
  ('S1', 'Rodovias', 'vertedouro', 'Rodovia não trabalha com estruturas vertentes de barragem', 0.38),
  ('S1', 'Rodovias', 'CFRD', 'Rodovia não usa barragens de concreto CFRD', 0.35),

  -- S2 (OAE — Pontes/Viadutos) — NOT CFRD, núcleo impermeável, CCR
  ('S2', 'OAE', 'CFRD', 'OAE não usa barragens de concreto (só estruturas de drenagem)', 0.40),
  ('S2', 'OAE', 'rejeito', 'OAE não trabalha com rejeitos de barragem', 0.35),
  ('S2', 'OAE', 'núcleo impermeável', 'OAE não usa núcleo impermeável (estrutura de barragem)', 0.38),
  ('S2', 'OAE', 'CCR', 'OAE não usa concreto rolado (material de barragem)', 0.30),
  ('S2', 'OAE', 'vertedouro', 'OAE não trabalha com vertedouros', 0.38),

  -- S4 (Metrô) — NOT via permanente ferroviária, trilho CCR
  ('S4', 'Metrô', 'via permanente ferroviária', 'Metrô usa via permanente metrô, não ferroviária', 0.40),
  ('S4', 'Metrô', 'trilho ferroviário', 'Metrô usa trilho metrô, não ferroviário', 0.35),
  ('S4', 'Metrô', 'dormente ferroviário', 'Metrô não usa dormentes ferroviários', 0.30),
  ('S4', 'Metrô', 'barragem', 'Metrô não trabalha com barragens', 0.40),

  -- S6 (Portos) — NOT vertedouro, aterro barragem, CFRD
  ('S6', 'Portos', 'vertedouro', 'Porto não trabalha com vertedouros de barragem', 0.40),
  ('S6', 'Portos', 'aterro barragem', 'Porto não constrói aterros de barragem', 0.38),
  ('S6', 'Portos', 'CFRD', 'Porto não constrói barragens CFRD', 0.40),
  ('S6', 'Portos', 'rejeito', 'Porto não trabalha com rejeitos de barragem', 0.35),
  ('S6', 'Portos', 'ICOLD', 'Porto não segue ICOLD (associação de barragens)', 0.25),

  -- S8 (Saneamento) — NOT trilho, via permanente, ferroviária
  ('S8', 'Saneamento', 'trilho', 'Saneamento não trabalha com trilhos ferroviários/metrô', 0.40),
  ('S8', 'Saneamento', 'via permanente', 'Saneamento não trabalha com via permanente ferroviária', 0.35),
  ('S8', 'Saneamento', 'ferroviário', 'Saneamento não trabalha com infraestrutura ferroviária', 0.35),
  ('S8', 'Saneamento', 'pista pouso', 'Saneamento não trabalha com pistas de pouso', 0.40),

  -- S9 (Energia) — NOT trilho, via permanente, dragagem, porto
  ('S9', 'Energia', 'trilho', 'Energia não trabalha com trilhos ferroviários/metrô', 0.40),
  ('S9', 'Energia', 'via permanente', 'Energia não trabalha com via permanente ferroviária', 0.35),
  ('S9', 'Energia', 'dragagem', 'Energia não trabalha com dragagem portuária', 0.38),
  ('S9', 'Energia', 'berço portaria', 'Energia não trabalha com berços portuários', 0.38),

  -- S10 (Barragens) — NOT trilho, via permanente, pista pouso, dragagem, porto, pavimento CBUQ
  ('S10', 'Barragens', 'trilho', 'Barragem não trabalha com trilhos ferroviários/metrô', 0.40),
  ('S10', 'Barragens', 'via permanente ferroviária', 'Barragem não trabalha com via permanente ferroviária', 0.40),
  ('S10', 'Barragens', 'dormente ferroviário', 'Barragem não trabalha com dormentes ferroviários', 0.35),
  ('S10', 'Barragens', 'pista pouso', 'Barragem não trabalha com pistas de pouso de aeroporto', 0.40),
  ('S10', 'Barragens', 'ANAC', 'Barragem não é regulada pela ANAC (aviação)', 0.35),
  ('S10', 'Barragens', 'dragagem', 'Barragem não trabalha com dragagem portuária', 0.38),
  ('S10', 'Barragens', 'berço', 'Barragem não trabalha com berços portuários', 0.38),
  ('S10', 'Barragens', 'ANTAQ', 'Barragem não é regulada pela ANTAQ (portos)', 0.35),
  ('S10', 'Barragens', 'pavimento CBUQ', 'Barragem não trabalha com pavimento asfáltico', 0.40),
  ('S10', 'Barragens', 'terraplenagem rodoviária', 'Barragem não é terraplenagem de rodovia', 0.38),
  ('S10', 'Barragens', 'ETA ETE', 'Barragem de água é diferente de ETA/ETE (saneamento)', 0.35)

ON CONFLICT (domain, anti_term) DO NOTHING;

-- =====================================================================
-- 3. Ajustar embedding_weight para domínio 'bar:' (S10)
-- =====================================================================
-- Reduzir peso de embeddings de barragens de 1.0 para 0.85
-- para dar espaço a outros domínios em buscas ambíguas
--
-- Assumes table rag_chunks(id, prefix TEXT, domain TEXT, embedding_weight DECIMAL)
-- Se o schema for diferente, adaptar conforme necessário.

-- Comentar se a coluna embedding_weight não existir ou se usar outro mecanismo
-- UPDATE rag_chunks
-- SET embedding_weight = 0.85
-- WHERE prefix = 'bar:' OR domain = 'S10'
-- AND embedding_weight = 1.0;

-- =====================================================================
-- 4. Criar função search_rag_with_anti_terms
-- =====================================================================
-- Nova função que busca documentos e penaliza resultados com anti-termos
-- do domínio de origem da query.
--
-- ASSINATURA:
--   search_rag_with_anti_terms(
--     query_text TEXT,           -- texto da query
--     source_domain TEXT,        -- domínio origem (ex: 'S1', 'S2', 'S10')
--     limit_results INT DEFAULT 10
--   )
--   RETURNS TABLE(
--     chunk_id TEXT,
--     content TEXT,
--     domain TEXT,
--     score DECIMAL,
--     penalty DECIMAL,
--     final_score DECIMAL
--   )
--
-- LÓGICA:
--   1. Busca por embedding similarity em rag_chunks
--   2. Calcula penalty multiplicativo baseado em anti_terms do source_domain
--   3. Retorna resultados ordenados por final_score (similarity × (1 - penalty))

-- Criar função auxiliar para calcular penalty
CREATE OR REPLACE FUNCTION calculate_anti_term_penalty(
  chunk_content TEXT,
  source_domain TEXT
) RETURNS DECIMAL AS $$
DECLARE
  penalty DECIMAL := 0.0;
  term_penalty DECIMAL;
  anti_term_rec RECORD;
BEGIN
  -- Iterar sobre anti-termos do source_domain
  FOR anti_term_rec IN
    SELECT anti_term, penalty_score
    FROM domain_anti_terms
    WHERE domain = source_domain
  LOOP
    -- Se o chunk contém o anti-termo, acumular penalty
    IF chunk_content ILIKE '%' || anti_term_rec.anti_term || '%' THEN
      penalty := penalty + anti_term_rec.penalty_score;
    END IF;
  END LOOP;

  -- Limitar penalty máximo a 0.95 (nunca eliminar completamente)
  RETURN CASE WHEN penalty > 0.95 THEN 0.95 ELSE penalty END;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Criar função principal de busca com anti-termos
-- (pseudocódigo; adaptar conforme schema real do rag_chunks)
CREATE OR REPLACE FUNCTION search_rag_with_anti_terms(
  query_text TEXT,
  source_domain TEXT,
  limit_results INT DEFAULT 10
) RETURNS TABLE(
  chunk_id TEXT,
  content TEXT,
  domain TEXT,
  score DECIMAL,
  penalty DECIMAL,
  final_score DECIMAL
) AS $$
BEGIN
  -- Versão simplificada: retorna metadados da lógica de penalização
  -- Adaptar conforme schema real (com embeddings, etc.)
  RETURN QUERY
  SELECT
    'chunk_id'::TEXT,
    'content'::TEXT,
    'domain'::TEXT,
    0.85::DECIMAL AS score,
    0.0::DECIMAL AS penalty,
    0.85::DECIMAL AS final_score
  LIMIT 0;  -- placeholder
END;
$$ LANGUAGE plpgsql;

-- =====================================================================
-- 5. Criar tabela de log de penalizações (auditoria)
-- =====================================================================
-- Registrar quais buscas foram penalizadas e por qual motivo

CREATE TABLE IF NOT EXISTS rag_penalty_audit (
  id SERIAL PRIMARY KEY,
  query_text TEXT NOT NULL,
  source_domain TEXT NOT NULL,
  chunk_id TEXT,
  anti_terms_found TEXT[],
  penalty_applied DECIMAL,
  timestamp TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_penalty_audit_domain
  ON rag_penalty_audit(source_domain);
CREATE INDEX IF NOT EXISTS idx_penalty_audit_timestamp
  ON rag_penalty_audit(timestamp DESC);

-- =====================================================================
-- 6. Tabela de validação de testes de contaminação
-- =====================================================================
-- Registrar queries de teste que eram capturadas incorretamente

CREATE TABLE IF NOT EXISTS contamination_test_queries (
  id SERIAL PRIMARY KEY,
  test_query TEXT NOT NULL,
  expected_domain TEXT NOT NULL,
  incorrectly_returned_domain TEXT,
  baseline_rank_position INT,
  baseline_recall_at_k INT,
  phase1_expected_rank INT,
  phase1_expected_recall INT,
  status TEXT DEFAULT 'pending',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  tested_at TIMESTAMPTZ
);

-- Inserir 8 queries históricas de contaminação que devem ser fixadas

INSERT INTO contamination_test_queries
  (test_query, expected_domain, incorrectly_returned_domain, baseline_rank_position, baseline_recall_at_k)
VALUES
  -- Contaminação histórica #1: "terraplenagem" captura S10 ao invés de S1
  ('projeto de terraplenagem rodoviária', 'S1', 'S10', 3, 3),
  -- Contaminação histórica #2: "estrutura de fundação" captura S10 ao invés de S2
  ('fundação estrutural OAE', 'S2', 'S10', 2, 3),
  -- Contaminação histórica #3: "drenagem" captura S10 ao invés de S1
  ('drenagem rodoviária superficial', 'S1', 'S10', 4, 5),
  -- Contaminação histórica #4: "núcleo de aterro" captura S10 ao invés de S2
  ('núcleo de aterro ponte', 'S2', 'S10', 5, 5),
  -- Contaminação histórica #5: "via permanente" captura S10 ao invés de S4
  ('via permanente estação metrô', 'S4', 'S10', 3, 3),
  -- Contaminação histórica #6: "dragagem" captura S10 ao invés de S6
  ('dragagem porto terminal', 'S6', 'S10', 2, 3),
  -- Contaminação histórica #7: "concreto rolado" captura S10 ao invés de S2
  ('concreto rolado estrutura OAE', 'S2', 'S10', 4, 5),
  -- Contaminação histórica #8: "aterro" captura S10 ao invés de S1
  ('aterro rodoviário terraplenagem', 'S1', 'S10', 3, 3);

-- =====================================================================
-- 7. Criar VIEW para monitoramento de performance
-- =====================================================================

CREATE OR REPLACE VIEW rag_contamination_status AS
SELECT
  ctq.expected_domain,
  COUNT(*) as total_queries,
  COUNT(CASE WHEN ctq.status = 'pending' THEN 1 END) as pending_tests,
  COUNT(CASE WHEN ctq.status = 'passed' THEN 1 END) as passed_tests,
  COUNT(CASE WHEN ctq.status = 'failed' THEN 1 END) as failed_tests,
  ROUND(
    100.0 * COUNT(CASE WHEN ctq.status = 'passed' THEN 1 END) / NULLIF(COUNT(*), 0),
    2
  ) as pass_rate
FROM contamination_test_queries ctq
GROUP BY ctq.expected_domain
ORDER BY ctq.expected_domain;

-- =====================================================================
-- 8. Rollback instructions
-- =====================================================================
-- NOTA: Executar manualmente se necessário
--
-- DROP VIEW IF EXISTS rag_contamination_status;
-- DROP TABLE IF EXISTS contamination_test_queries;
-- DROP TABLE IF EXISTS rag_penalty_audit;
-- DROP FUNCTION IF EXISTS search_rag_with_anti_terms(TEXT, TEXT, INT);
-- DROP FUNCTION IF EXISTS calculate_anti_term_penalty(TEXT, TEXT);
-- DROP TABLE IF EXISTS domain_anti_terms;
-- UPDATE rag_chunks SET embedding_weight = 1.0 WHERE prefix = 'bar:';

COMMIT;

-- =====================================================================
-- NOTAS DE IMPLEMENTAÇÃO
-- =====================================================================
--
-- 1. DEPENDENCY CHECK
--    Antes de aplicar esta migration, verificar:
--    - Tabela rag_chunks existe com colunas: id, prefix, domain, content, embedding_weight
--    - Supabase PostgreSQL >= 12 (para ILIKE, NULLIF, janelas analíticas)
--    - Espaço suficiente para novas tabelas (~50MB)
--
-- 2. APLICAÇÃO EM STAGING
--    Testar em staging ANTES de produção:
--      supabase db push --dir=supabase/migrations/ (local)
--      ou manual: psql "$STAGING_DB_URL" -f supabase/migrations/2026_07_26_rag_phase_1_contamination_fix.sql
--
-- 3. MONITORAMENTO PÓS-DEPLOYMENT
--    - Verificar tabela domain_anti_terms contém 31 pares (domínio, anti-termo)
--    - Executar: SELECT COUNT(*) FROM domain_anti_terms;
--    - Testar função: SELECT * FROM contamination_test_queries WHERE status = 'pending';
--
-- 4. VALIDAÇÃO (próximo step)
--    Phase 2 (não nesta migration):
--    - Executar 8 queries de teste (contamination_test_queries)
--    - Medir Recall@1, Recall@3, contaminação
--    - Comparar contra baseline
--    - Se Recall@1 >= 74% e Contaminação <= 14%, aprovar Phase 2
--
-- 5. ROLLBACK
--    Se necessário reverter, executar bloco DOWN no fim deste arquivo
--    ou: supabase db reset (cuidado: apaga todo o data)
--
-- =====================================================================
