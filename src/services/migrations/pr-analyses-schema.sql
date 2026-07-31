/**
 * Supabase Schema para PR Analyses
 *
 * Cria as tabelas necessárias para persistir análises de PRs
 * no Supabase. Execute este script no Supabase SQL Editor.
 *
 * Histórico:
 * - v1.0: Schema inicial para PR analyses
 */

-- Tabela principal de análises de PR
CREATE TABLE IF NOT EXISTS pr_analyses (
  id BIGSERIAL PRIMARY KEY,
  pr_number INTEGER NOT NULL,
  owner VARCHAR(255) NOT NULL,
  repo VARCHAR(255) NOT NULL,
  title TEXT NOT NULL,
  author VARCHAR(255) NOT NULL,
  branch VARCHAR(255) NOT NULL,
  base_branch VARCHAR(255) DEFAULT 'main',

  -- Análise
  status VARCHAR(50) NOT NULL DEFAULT 'pending',
  files_changed INTEGER DEFAULT 0,
  additions INTEGER DEFAULT 0,
  deletions INTEGER DEFAULT 0,

  -- Resultados
  patterns_count INTEGER DEFAULT 0,
  suggestions_count INTEGER DEFAULT 0,

  -- CI/CD
  ci_triggered BOOLEAN DEFAULT FALSE,
  workflow_run_id BIGINT,
  ci_status VARCHAR(50),
  ci_passed BOOLEAN,
  tests_passed INTEGER,
  tests_failed INTEGER,
  coverage_percentage DECIMAL(5,2),

  -- Timestamps
  analyzed_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  completed_at TIMESTAMP WITH TIME ZONE,
  ci_completed_at TIMESTAMP WITH TIME ZONE,
  duration_ms INTEGER,

  -- Metadados
  error TEXT,
  metadata JSONB,

  -- Índices
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

  UNIQUE(owner, repo, pr_number)
);

-- Tabela de padrões de código detectados
CREATE TABLE IF NOT EXISTS code_patterns (
  id BIGSERIAL PRIMARY KEY,
  pr_analysis_id BIGINT NOT NULL REFERENCES pr_analyses(id) ON DELETE CASCADE,
  pattern_type VARCHAR(50) NOT NULL,
  severity VARCHAR(20) NOT NULL,
  file VARCHAR(500) NOT NULL,
  line_number INTEGER,
  description TEXT NOT NULL,
  confidence DECIMAL(3,2),

  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

  INDEX idx_pr_analysis_id (pr_analysis_id),
  INDEX idx_pattern_type (pattern_type)
);

-- Tabela de sugestões geradas
CREATE TABLE IF NOT EXISTS suggestions (
  id BIGSERIAL PRIMARY KEY,
  pr_analysis_id BIGINT NOT NULL REFERENCES pr_analyses(id) ON DELETE CASCADE,
  suggestion_id VARCHAR(255) UNIQUE NOT NULL,
  type VARCHAR(50) NOT NULL,
  severity VARCHAR(20) NOT NULL,
  file VARCHAR(500),
  title TEXT NOT NULL,
  description TEXT NOT NULL,
  recommendation TEXT NOT NULL,
  examples JSONB,
  confidence DECIMAL(3,2),

  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

  INDEX idx_pr_analysis_id (pr_analysis_id),
  INDEX idx_type (type)
);

-- Tabela de arquivos alterados
CREATE TABLE IF NOT EXISTS changed_files (
  id BIGSERIAL PRIMARY KEY,
  pr_analysis_id BIGINT NOT NULL REFERENCES pr_analyses(id) ON DELETE CASCADE,
  filename VARCHAR(1000) NOT NULL,
  additions INTEGER DEFAULT 0,
  deletions INTEGER DEFAULT 0,
  patch TEXT,
  language VARCHAR(50),

  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

  INDEX idx_pr_analysis_id (pr_analysis_id),
  INDEX idx_filename (filename)
);

-- Tabela de histórico de intents
CREATE TABLE IF NOT EXISTS commit_intents (
  id BIGSERIAL PRIMARY KEY,
  pr_analysis_id BIGINT NOT NULL REFERENCES pr_analyses(id) ON DELETE CASCADE,
  commit_message TEXT NOT NULL,
  action VARCHAR(50) NOT NULL,
  target VARCHAR(50) NOT NULL,
  confidence DECIMAL(3,2),
  params JSONB,
  reasoning TEXT,

  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

  INDEX idx_pr_analysis_id (pr_analysis_id),
  INDEX idx_action (action)
);

-- Tabela de métricas agregadas
CREATE TABLE IF NOT EXISTS pr_metrics_daily (
  id BIGSERIAL PRIMARY KEY,
  date DATE NOT NULL,
  owner VARCHAR(255) NOT NULL,
  repo VARCHAR(255) NOT NULL,

  -- Contadores
  total_prs_analyzed INTEGER DEFAULT 0,
  successful_analyses INTEGER DEFAULT 0,
  failed_analyses INTEGER DEFAULT 0,

  -- Estatísticas
  avg_files_changed DECIMAL(10,2),
  avg_additions INTEGER,
  avg_deletions INTEGER,
  avg_suggestions DECIMAL(10,2),
  avg_patterns DECIMAL(10,2),

  -- CI/CD
  prs_with_ci INTEGER DEFAULT 0,
  ci_success_rate DECIMAL(5,2),
  avg_test_pass_rate DECIMAL(5,2),
  avg_coverage DECIMAL(5,2),
  avg_duration_ms INTEGER,

  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

  UNIQUE(date, owner, repo),
  INDEX idx_date (date),
  INDEX idx_owner_repo (owner, repo)
);

-- Índices para melhor performance
CREATE INDEX IF NOT EXISTS idx_pr_analyses_owner_repo ON pr_analyses(owner, repo);
CREATE INDEX IF NOT EXISTS idx_pr_analyses_status ON pr_analyses(status);
CREATE INDEX IF NOT EXISTS idx_pr_analyses_analyzed_at ON pr_analyses(analyzed_at);
CREATE INDEX IF NOT EXISTS idx_pr_analyses_created_at ON pr_analyses(created_at);

-- RLS (Row Level Security) - Proteção de dados por tenant
ALTER TABLE pr_analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE code_patterns ENABLE ROW LEVEL SECURITY;
ALTER TABLE suggestions ENABLE ROW LEVEL SECURITY;
ALTER TABLE changed_files ENABLE ROW LEVEL SECURITY;
ALTER TABLE commit_intents ENABLE ROW LEVEL SECURITY;
ALTER TABLE pr_metrics_daily ENABLE ROW LEVEL SECURITY;

-- Políticas de RLS (exemplo para seu tenant)
-- Ajuste conforme necessário
CREATE POLICY "Enable read access for all users" ON pr_analyses
  FOR SELECT USING (true);

CREATE POLICY "Enable insert for authenticated users" ON pr_analyses
  FOR INSERT WITH CHECK (true);

CREATE POLICY "Enable update for authenticated users" ON pr_analyses
  FOR UPDATE USING (true) WITH CHECK (true);

-- Views úteis
CREATE OR REPLACE VIEW v_pr_analysis_summary AS
SELECT
  pa.pr_number,
  pa.owner,
  pa.repo,
  pa.title,
  pa.author,
  pa.status,
  pa.files_changed,
  pa.additions,
  pa.deletions,
  COUNT(DISTINCT cp.id) as pattern_count,
  COUNT(DISTINCT s.id) as suggestion_count,
  pa.ci_passed,
  pa.coverage_percentage,
  pa.analyzed_at,
  pa.completed_at,
  pa.duration_ms
FROM pr_analyses pa
LEFT JOIN code_patterns cp ON pa.id = cp.pr_analysis_id
LEFT JOIN suggestions s ON pa.id = s.pr_analysis_id
GROUP BY pa.id;

CREATE OR REPLACE VIEW v_pattern_distribution AS
SELECT
  pattern_type,
  severity,
  COUNT(*) as count,
  ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM code_patterns), 2) as percentage
FROM code_patterns
GROUP BY pattern_type, severity
ORDER BY count DESC;

CREATE OR REPLACE VIEW v_suggestion_effectiveness AS
SELECT
  type,
  COUNT(*) as total_suggestions,
  ROUND(AVG(confidence), 3) as avg_confidence,
  ROUND(AVG(CAST(confidence > 0.8 AS INT)) * 100, 1) as high_confidence_percentage
FROM suggestions
GROUP BY type
ORDER BY total_suggestions DESC;

-- Função para calcular métricas diárias
CREATE OR REPLACE FUNCTION calculate_daily_metrics()
RETURNS void AS $$
BEGIN
  INSERT INTO pr_metrics_daily (
    date, owner, repo,
    total_prs_analyzed, successful_analyses, failed_analyses,
    avg_files_changed, avg_additions, avg_deletions,
    avg_suggestions, avg_patterns,
    prs_with_ci, ci_success_rate, avg_test_pass_rate,
    avg_coverage, avg_duration_ms
  )
  SELECT
    CURRENT_DATE,
    pa.owner,
    pa.repo,
    COUNT(DISTINCT pa.id),
    COUNT(CASE WHEN pa.status = 'completed' THEN 1 END),
    COUNT(CASE WHEN pa.status = 'failed' THEN 1 END),
    ROUND(AVG(pa.files_changed), 2),
    ROUND(AVG(pa.additions), 0),
    ROUND(AVG(pa.deletions), 0),
    ROUND(AVG(pa.suggestions_count), 2),
    ROUND(AVG(pa.patterns_count), 2),
    COUNT(CASE WHEN pa.ci_triggered THEN 1 END),
    ROUND(AVG(CASE WHEN pa.ci_triggered THEN CAST(pa.ci_passed AS INT) END) * 100, 2),
    ROUND(AVG(pa.tests_passed::NUMERIC / NULLIF(pa.tests_passed + pa.tests_failed, 0) * 100), 2),
    ROUND(AVG(pa.coverage_percentage), 2),
    ROUND(AVG(pa.duration_ms), 0)
  FROM pr_analyses pa
  WHERE DATE(pa.analyzed_at) = CURRENT_DATE
  GROUP BY pa.owner, pa.repo
  ON CONFLICT (date, owner, repo)
  DO UPDATE SET
    total_prs_analyzed = EXCLUDED.total_prs_analyzed,
    successful_analyses = EXCLUDED.successful_analyses,
    failed_analyses = EXCLUDED.failed_analyses,
    avg_files_changed = EXCLUDED.avg_files_changed,
    avg_additions = EXCLUDED.avg_additions,
    avg_deletions = EXCLUDED.avg_deletions,
    avg_suggestions = EXCLUDED.avg_suggestions,
    avg_patterns = EXCLUDED.avg_patterns,
    prs_with_ci = EXCLUDED.prs_with_ci,
    ci_success_rate = EXCLUDED.ci_success_rate,
    avg_test_pass_rate = EXCLUDED.avg_test_pass_rate,
    avg_coverage = EXCLUDED.avg_coverage,
    avg_duration_ms = EXCLUDED.avg_duration_ms,
    updated_at = NOW();
END;
$$ LANGUAGE plpgsql;

-- Comentários para documentação
COMMENT ON TABLE pr_analyses IS 'Registro principal de análises de PRs com dados agregados';
COMMENT ON TABLE code_patterns IS 'Padrões de código detectados automaticamente em PRs';
COMMENT ON TABLE suggestions IS 'Sugestões de melhoria geradas para PRs';
COMMENT ON TABLE changed_files IS 'Lista de arquivos alterados em cada PR';
COMMENT ON TABLE commit_intents IS 'Histórico de intents extraídos de mensagens de commit';
COMMENT ON COLUMN pr_analyses.status IS 'pending, analyzing, analyzed, triggering_ci, monitoring_build, completed, failed';
COMMENT ON COLUMN code_patterns.pattern_type IS 'complexity, duplication, missing-types, missing-tests, performance, security, accessibility, documentation';
COMMENT ON COLUMN suggestions.severity IS 'info, warning, critical';
