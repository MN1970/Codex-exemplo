-- ============================================================================
-- KB EVOLUÍDO — SCHEMA SQL PARA SUPABASE
-- ============================================================================
-- Projeto Manta Associados v4.2
-- Data: 2026-07-30
-- Segmentos: S1-S10 (Rodovias, OAE, Ferrovia, Metrô, Portos, Aeroportos,
--            Saneamento, Energia, Barragens)
-- ============================================================================

-- Extensões necessárias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================================
-- SEÇÃO 1: ENUMS E TIPOS CUSTOMIZADOS
-- ============================================================================

-- Segmentos técnicos (aligned com CLAUDE.md v4.2)
CREATE TYPE segment_type AS ENUM (
  'S1_RODOVIA',
  'S2_OAE',
  'S3_FERROVIA',
  'S4_METRO',
  'S5_TUNEL',
  'S6_PORTO',
  'S7_AEROPORTO',
  'S8_SANEAMENTO',
  'S9_ENERGIA',
  'S10_BARRAGEM'
);

-- Fases do ciclo de vida (8 fases)
CREATE TYPE lifecycle_phase AS ENUM (
  'ESTUDO_PREVIO',
  'PROJETO_BASICO',
  'PROJETO_EXECUTIVO',
  'OBRA_EXECUCAO',
  'OPERACAO_MANUTENCAO',
  'COMPETICAO_LICITACAO',
  'DILIGENCIA_MA',
  'ENCERRAMENTO'
);

-- Tipos de constantes técnicas
CREATE TYPE constant_type AS ENUM (
  'NORMA_TECNICA',
  'COEFICIENTE_PROJETO',
  'FATOR_SEGURANCA',
  'FORMULA_CALCULO',
  'ESPECIFICACAO_MATERIAL',
  'TAXA_PADRAO',
  'LIMITE_TECNICO',
  'PARAMETRO_OPERACIONAL'
);

-- Status de validação
CREATE TYPE validation_status AS ENUM (
  'PROPOSTO',
  'EM_VALIDACAO',
  'VALIDADO',
  'CONTESTADO',
  'REVISAR',
  'DESCONTINUADO'
);

-- Status de feedback
CREATE TYPE feedback_rating AS ENUM (
  'EXCELENTE',
  'BOM',
  'ADEQUADO',
  'INSUFICIENTE',
  'INCORRETO'
);

-- ============================================================================
-- SEÇÃO 2: TABELAS DE CONHECIMENTO (KB)
-- ============================================================================

-- 2.1 KB_CONSTANTS — Constantes técnicas versionadas
-- Armazena K1/K2, normas, fórmulas, coeficientes com histórico
CREATE TABLE kb_constants (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  segment segment_type NOT NULL,
  lifecycle_phase lifecycle_phase NOT NULL,
  constant_name VARCHAR(255) NOT NULL,
  constant_type constant_type NOT NULL,
  constant_value TEXT NOT NULL,
  unit_of_measure VARCHAR(50),
  -- Descrição e contexto
  description TEXT,
  source_reference VARCHAR(255),  -- Norma, paper, lei, URL
  source_year INT,
  -- Validação
  validation_status validation_status NOT NULL DEFAULT 'PROPOSTO',
  confidence_score NUMERIC(3, 2),  -- 0.00 a 1.00
  validated_by UUID,  -- referência para users (auth.users)
  validation_date TIMESTAMP,
  -- Versionamento
  version INT NOT NULL DEFAULT 1,
  is_current BOOLEAN NOT NULL DEFAULT true,
  superseded_by UUID,  -- referência para nova versão
  -- Auditoria
  created_by UUID NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_by UUID,
  updated_at TIMESTAMP,
  notes TEXT,
  CONSTRAINT fk_validated_by FOREIGN KEY (validated_by) REFERENCES auth.users(id),
  CONSTRAINT fk_created_by FOREIGN KEY (created_by) REFERENCES auth.users(id),
  CONSTRAINT fk_updated_by FOREIGN KEY (updated_by) REFERENCES auth.users(id),
  CONSTRAINT fk_superseded FOREIGN KEY (superseded_by) REFERENCES kb_constants(id),
  CONSTRAINT confidence_range CHECK (confidence_score >= 0 AND confidence_score <= 1)
);

CREATE INDEX idx_kb_constants_segment_phase ON kb_constants(segment, lifecycle_phase);
CREATE INDEX idx_kb_constants_name_type ON kb_constants(constant_name, constant_type);
CREATE INDEX idx_kb_constants_status ON kb_constants(validation_status, is_current);
CREATE INDEX idx_kb_constants_source ON kb_constants(source_reference);

-- 2.2 KB_TEMPLATES — Templates reutilizáveis por segmento/fase
-- Estrutura de projetos, seções de relatórios, checklists
CREATE TABLE kb_templates (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  template_name VARCHAR(255) NOT NULL,
  segment segment_type NOT NULL,
  lifecycle_phase lifecycle_phase NOT NULL,
  template_type VARCHAR(100) NOT NULL,  -- 'RELATORIO', 'CHECKLIST', 'ESTIMATIVA', etc.
  content JSONB NOT NULL,  -- Estrutura flexible (seções, campos, etc.)
  -- Metadados
  description TEXT,
  version INT NOT NULL DEFAULT 1,
  is_active BOOLEAN NOT NULL DEFAULT true,
  usage_count INT DEFAULT 0,
  -- Auditoria
  created_by UUID NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_by UUID,
  updated_at TIMESTAMP,
  CONSTRAINT fk_created_by FOREIGN KEY (created_by) REFERENCES auth.users(id),
  CONSTRAINT fk_updated_by FOREIGN KEY (updated_by) REFERENCES auth.users(id)
);

CREATE INDEX idx_kb_templates_segment_phase ON kb_templates(segment, lifecycle_phase);
CREATE INDEX idx_kb_templates_type ON kb_templates(template_type, is_active);
CREATE INDEX idx_kb_templates_name ON kb_templates(template_name);

-- 2.3 KB_PATTERNS — Padrões identificados em projetos
-- Estrutura de custos, cronogramas, riscos recorrentes
CREATE TABLE kb_patterns (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  pattern_name VARCHAR(255) NOT NULL,
  segment segment_type NOT NULL,
  lifecycle_phase lifecycle_phase,  -- NULL = padrão transversal
  pattern_category VARCHAR(100) NOT NULL,  -- 'CUSTO', 'CRONOGRAMA', 'RISCO', 'ESTRUTURA'
  description TEXT,
  -- Padrão em si
  pattern_rule JSONB NOT NULL,  -- Estrutura do padrão (regras, condições)
  -- Evidência
  sample_count INT DEFAULT 0,  -- Quantos projetos suportam este padrão
  confidence_score NUMERIC(3, 2),  -- Confiança baseada em frequency
  evidence_projects UUID[],  -- IDs de projetos que confirma este padrão
  -- Impacto e recomendações
  typical_impact TEXT,  -- Ex: "Aumento de 15-20% no cronograma"
  recommended_mitigation JSONB,  -- Ações sugeridas
  -- Status
  is_active BOOLEAN NOT NULL DEFAULT true,
  -- Auditoria
  discovered_by UUID NOT NULL,
  discovered_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  validated_by UUID,
  validated_at TIMESTAMP,
  CONSTRAINT fk_discovered_by FOREIGN KEY (discovered_by) REFERENCES auth.users(id),
  CONSTRAINT fk_validated_by FOREIGN KEY (validated_by) REFERENCES auth.users(id)
);

CREATE INDEX idx_kb_patterns_segment_category ON kb_patterns(segment, pattern_category);
CREATE INDEX idx_kb_patterns_active ON kb_patterns(is_active);
CREATE INDEX idx_kb_patterns_confidence ON kb_patterns(confidence_score DESC);

-- 2.4 KB_VERSIONS — Histórico de versões (para rastreamento completo)
-- Cada mudança em constantes, templates, padrões gera um registro aqui
CREATE TABLE kb_versions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  entity_type VARCHAR(50) NOT NULL,  -- 'CONSTANT', 'TEMPLATE', 'PATTERN'
  entity_id UUID NOT NULL,
  entity_name VARCHAR(255),
  version_number INT NOT NULL,
  change_type VARCHAR(50) NOT NULL,  -- 'CREATE', 'UPDATE', 'DEPRECATE', 'RESTORE'
  -- Comparação
  previous_value JSONB,
  new_value JSONB,
  changelog TEXT,  -- Descrição legível das mudanças
  -- Quem e quando
  changed_by UUID NOT NULL,
  changed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  approval_by UUID,
  approval_at TIMESTAMP,
  -- Rastreamento
  tag VARCHAR(100),  -- 'HOTFIX', 'FEATURE', 'BREAKING', 'BACKPORT'
  CONSTRAINT fk_changed_by FOREIGN KEY (changed_by) REFERENCES auth.users(id),
  CONSTRAINT fk_approval_by FOREIGN KEY (approval_by) REFERENCES auth.users(id)
);

CREATE INDEX idx_kb_versions_entity ON kb_versions(entity_type, entity_id);
CREATE INDEX idx_kb_versions_changed_at ON kb_versions(changed_at DESC);
CREATE INDEX idx_kb_versions_approval ON kb_versions(approval_by, approval_at);

-- ============================================================================
-- SEÇÃO 3: TABELAS DE FEEDBACK
-- ============================================================================

-- 3.1 PROJECT_INSIGHTS — Insights extraídos de projetos finalizados
-- Retroalimentação do mundo real para modelos
CREATE TABLE project_insights (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  project_id VARCHAR(255) NOT NULL,  -- ID externo do projeto real (MantaID, etc.)
  project_name VARCHAR(255),
  segment segment_type NOT NULL,
  lifecycle_phase lifecycle_phase NOT NULL,
  -- Insights coletados
  insight_category VARCHAR(100) NOT NULL,  -- 'CUSTO_REAL', 'CRONOGRAMA_REAL', 'RISCO_MATERIALIZADO', 'LIÇÃO'
  insight_summary TEXT NOT NULL,
  insight_detail JSONB,  -- Dados estruturados
  -- Comparação com previsão
  predicted_value NUMERIC(15, 2),  -- O que foi previsto
  actual_value NUMERIC(15, 2),  -- O que realmente aconteceu
  variance_percent NUMERIC(5, 2),  -- (actual - predicted) / predicted * 100
  variance_reason TEXT,  -- Por que divergiu
  -- Validação
  validation_status validation_status NOT NULL DEFAULT 'PROPOSTO',
  validated_by UUID,
  validated_at TIMESTAMP,
  -- Relevância
  is_applicable_broader BOOLEAN DEFAULT false,  -- Se relevante além deste projeto
  applicable_segments segment_type[],  -- Onde aplicar
  applicable_phases lifecycle_phase[],
  -- Auditoria
  reported_by UUID NOT NULL,
  reported_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_by UUID,
  updated_at TIMESTAMP,
  CONSTRAINT fk_validated_by FOREIGN KEY (validated_by) REFERENCES auth.users(id),
  CONSTRAINT fk_reported_by FOREIGN KEY (reported_by) REFERENCES auth.users(id),
  CONSTRAINT fk_updated_by FOREIGN KEY (updated_by) REFERENCES auth.users(id)
);

CREATE INDEX idx_project_insights_project ON project_insights(project_id);
CREATE INDEX idx_project_insights_segment_phase ON project_insights(segment, lifecycle_phase);
CREATE INDEX idx_project_insights_category ON project_insights(insight_category);
CREATE INDEX idx_project_insights_validation ON project_insights(validation_status, is_applicable_broader);
CREATE INDEX idx_project_insights_variance ON project_insights(variance_percent);

-- 3.2 MODEL_FEEDBACK — Avaliação de recomendações dos agentes
-- User feedback sobre a qualidade das respostas dos agentes
CREATE TABLE model_feedback (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  agent_id VARCHAR(100) NOT NULL,  -- 'manta-01', 'agente-infraestrutura-s1', etc.
  request_id UUID,  -- ID único da sessão/prompt original
  request_context JSONB,  -- Contexto do request (segmento, fase, tipo)
  -- Recomendação gerada
  recommendation_type VARCHAR(100),  -- 'CUSTO', 'CRONOGRAMA', 'RISCO', 'ESTRUTURA'
  recommendation_summary TEXT,
  recommendation_confidence NUMERIC(3, 2),  -- Confiança relatada pelo agente
  recommendation_data JSONB,
  -- Feedback do user
  feedback_rating feedback_rating NOT NULL,
  feedback_comment TEXT,
  is_useful BOOLEAN,
  would_use_again BOOLEAN,
  -- Impacto observado (se aplicado)
  outcome_reported BOOLEAN DEFAULT false,
  outcome_vs_reality TEXT,  -- Como saiu na prática
  outcome_variance NUMERIC(5, 2),  -- Diferença em %
  -- Auditoria
  feedback_by UUID NOT NULL,
  feedback_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  project_id VARCHAR(255),  -- Projeto relacionado (se houver)
  CONSTRAINT fk_feedback_by FOREIGN KEY (feedback_by) REFERENCES auth.users(id)
);

CREATE INDEX idx_model_feedback_agent ON model_feedback(agent_id);
CREATE INDEX idx_model_feedback_rating ON model_feedback(feedback_rating);
CREATE INDEX idx_model_feedback_request ON model_feedback(request_id);
CREATE INDEX idx_model_feedback_outcome ON model_feedback(outcome_reported, outcome_variance);
CREATE INDEX idx_model_feedback_time ON model_feedback(feedback_at DESC);

-- 3.3 CONSTANT_VALIDATION — Validação/contestação de constantes
-- Quando usuários validam ou contestam uma constante técnica
CREATE TABLE constant_validation (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  constant_id UUID NOT NULL,
  constant_name VARCHAR(255),
  segment segment_type,
  -- Ação de validação
  validation_action VARCHAR(50) NOT NULL,  -- 'VALIDOU', 'CONTESTOU', 'APERFEIÇOOU'
  confidence_level feedback_rating NOT NULL,
  evidence_provided TEXT,
  evidence_attachment JSONB,  -- URLs, docs, etc.
  alternative_value TEXT,  -- Se contestação, qual o valor correto
  -- Contexto
  validation_context JSONB,  -- Onde foi usado, com sucesso ou não
  project_id VARCHAR(255),
  -- Auditoria
  validated_by UUID NOT NULL,
  validated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  notes TEXT,
  CONSTRAINT fk_constant_id FOREIGN KEY (constant_id) REFERENCES kb_constants(id),
  CONSTRAINT fk_validated_by FOREIGN KEY (validated_by) REFERENCES auth.users(id)
);

CREATE INDEX idx_constant_validation_constant ON constant_validation(constant_id);
CREATE INDEX idx_constant_validation_action ON constant_validation(validation_action);
CREATE INDEX idx_constant_validation_time ON constant_validation(validated_at DESC);
CREATE INDEX idx_constant_validation_user ON constant_validation(validated_by);

-- ============================================================================
-- SEÇÃO 4: TABELAS DE ML
-- ============================================================================

-- 4.1 ML_TRAINING_DATA — Dados preparados para treino de modelos
-- Datasets curados, features engenheirizadas, labels para supervised learning
CREATE TABLE ml_training_data (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  dataset_id VARCHAR(100) NOT NULL,  -- Nome do dataset (ex: 'cost_estimation_s1_v2')
  dataset_version INT NOT NULL DEFAULT 1,
  segment segment_type,
  lifecycle_phase lifecycle_phase,
  -- Dados de entrada (features)
  input_features JSONB NOT NULL,  -- Estrutura variável (x1, x2, x3, ...)
  input_hash VARCHAR(64),  -- SHA-256 para dedup
  feature_count INT,
  -- Label/target
  target_variable VARCHAR(100),  -- 'CUSTO_TOTAL', 'CRONOGRAMA_MESES', 'RISCO_SCORE'
  target_value NUMERIC(15, 2),
  target_unit VARCHAR(50),
  -- Qualidade e rastreamento
  data_quality_score NUMERIC(3, 2),  -- 0-1 (completude, consistência)
  source_type VARCHAR(50),  -- 'PROJETO_REAL', 'SIMULACAO', 'LITERATURA'
  source_reference VARCHAR(255),
  source_date DATE,
  -- ML metadata
  used_in_training BOOLEAN DEFAULT false,
  training_split VARCHAR(50),  -- 'TRAIN', 'VALIDATION', 'TEST'
  train_model_id VARCHAR(100),  -- Qual modelo foi treinado
  -- Auditoria
  prepared_by UUID NOT NULL,
  prepared_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_prepared_by FOREIGN KEY (prepared_by) REFERENCES auth.users(id)
);

CREATE INDEX idx_ml_training_data_dataset ON ml_training_data(dataset_id, dataset_version);
CREATE INDEX idx_ml_training_data_segment ON ml_training_data(segment, lifecycle_phase);
CREATE INDEX idx_ml_training_data_target ON ml_training_data(target_variable);
CREATE INDEX idx_ml_training_data_split ON ml_training_data(training_split);
CREATE INDEX idx_ml_training_data_quality ON ml_training_data(data_quality_score DESC);

-- 4.2 ML_MODEL_METRICS — Performance de modelos treinados
-- Métricas de ML (RMSE, MAE, R², precision, recall, F1)
CREATE TABLE ml_model_metrics (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  model_id VARCHAR(100) NOT NULL,  -- 'custo-estimador-s1-v3', etc.
  model_type VARCHAR(100) NOT NULL,  -- 'LINEAR_REGRESSION', 'GRADIENT_BOOSTING', 'NEURAL_NET'
  segment segment_type,
  lifecycle_phase lifecycle_phase,
  target_variable VARCHAR(100),  -- O que prediz
  -- Dataset usado no treino
  dataset_id VARCHAR(100),
  dataset_version INT,
  train_size INT,
  validation_size INT,
  test_size INT,
  -- Métricas de regressão
  mae NUMERIC(15, 4),  -- Mean Absolute Error
  rmse NUMERIC(15, 4),  -- Root Mean Squared Error
  mape NUMERIC(5, 2),  -- Mean Absolute Percentage Error
  r_squared NUMERIC(5, 4),  -- R²
  -- Métricas de classificação (se aplicável)
  accuracy NUMERIC(5, 4),
  precision NUMERIC(5, 4),
  recall NUMERIC(5, 4),
  f1_score NUMERIC(5, 4),
  -- Feature importance
  top_features JSONB,  -- [{feature: 'x1', importance: 0.35}, ...]
  -- Status e deployment
  is_production BOOLEAN DEFAULT false,
  production_since TIMESTAMP,
  is_active BOOLEAN DEFAULT true,
  -- Auditoria
  trained_by UUID NOT NULL,
  trained_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  validated_by UUID,
  validated_at TIMESTAMP,
  CONSTRAINT fk_trained_by FOREIGN KEY (trained_by) REFERENCES auth.users(id),
  CONSTRAINT fk_validated_by FOREIGN KEY (validated_by) REFERENCES auth.users(id)
);

CREATE INDEX idx_ml_model_metrics_id ON ml_model_metrics(model_id);
CREATE INDEX idx_ml_model_metrics_segment ON ml_model_metrics(segment, target_variable);
CREATE INDEX idx_ml_model_metrics_production ON ml_model_metrics(is_production, is_active);
CREATE INDEX idx_ml_model_metrics_performance ON ml_model_metrics(rmse, r_squared);

-- 4.3 ML_PREDICTIONS — Predições geradas e seus outcomes reais
-- Registro de cada predição para validação posterior
CREATE TABLE ml_predictions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  model_id VARCHAR(100) NOT NULL,
  prediction_id VARCHAR(100) NOT NULL UNIQUE,  -- ID único da predição
  segment segment_type,
  lifecycle_phase lifecycle_phase,
  target_variable VARCHAR(100),
  -- Input
  input_features JSONB NOT NULL,
  -- Predição
  predicted_value NUMERIC(15, 4) NOT NULL,
  predicted_unit VARCHAR(50),
  prediction_confidence NUMERIC(5, 4),  -- Confiança (0-1)
  prediction_interval_lower NUMERIC(15, 4),  -- Intervalo de confiança
  prediction_interval_upper NUMERIC(15, 4),
  -- Outcome real (preenchido posteriormente)
  outcome_observed BOOLEAN DEFAULT false,
  actual_value NUMERIC(15, 4),
  actual_date DATE,  -- Quando a realidade foi observada
  variance_value NUMERIC(15, 4),  -- actual - predicted
  variance_percent NUMERIC(5, 2),  -- (actual - predicted) / predicted * 100
  outcome_within_interval BOOLEAN,  -- Se real caiu no intervalo
  -- Contexto
  project_id VARCHAR(255),
  request_id UUID,
  used_constants JSONB,  -- Quais constantes foram usadas
  -- Auditoria
  generated_by_agent VARCHAR(100),  -- 'manta-05', etc.
  generated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  outcome_reported_by UUID,
  outcome_reported_at TIMESTAMP,
  CONSTRAINT fk_outcome_reported_by FOREIGN KEY (outcome_reported_by) REFERENCES auth.users(id)
);

CREATE INDEX idx_ml_predictions_model ON ml_predictions(model_id);
CREATE INDEX idx_ml_predictions_id ON ml_predictions(prediction_id);
CREATE INDEX idx_ml_predictions_outcome ON ml_predictions(outcome_observed);
CREATE INDEX idx_ml_predictions_variance ON ml_predictions(variance_percent);
CREATE INDEX idx_ml_predictions_time ON ml_predictions(generated_at DESC);
CREATE INDEX idx_ml_predictions_project ON ml_predictions(project_id);

-- ============================================================================
-- SEÇÃO 5: TABELAS DE AUDITORIA
-- ============================================================================

-- 5.1 KB_AUDIT_LOG — Log completo de todas as mudanças na KB
-- Rastreamento detalhado de quem, o quê, quando, por quê
CREATE TABLE kb_audit_log (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  action VARCHAR(100) NOT NULL,  -- 'INSERT', 'UPDATE', 'DELETE', 'APPROVE', 'RESTORE'
  entity_type VARCHAR(50) NOT NULL,  -- 'CONSTANT', 'TEMPLATE', 'PATTERN', 'TRAINING_DATA'
  entity_id UUID,
  entity_name VARCHAR(255),
  -- Dados antes/depois
  old_values JSONB,
  new_values JSONB,
  -- Quem e contexto
  performed_by UUID NOT NULL,
  performed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  ip_address INET,
  user_agent TEXT,
  session_id VARCHAR(255),
  -- Razão e impacto
  change_reason TEXT,
  approval_status VARCHAR(50),  -- 'PENDING', 'APPROVED', 'REJECTED'
  approved_by UUID,
  approved_at TIMESTAMP,
  -- Impacto estimado
  affected_agents TEXT[],  -- Quais agentes são impactados
  affected_projects VARCHAR(255)[],  -- Quais projetos são impactados
  estimated_impact_score INT,  -- 0-100, quanto impacto tem
  -- Reversibilidade
  reversible BOOLEAN DEFAULT true,
  reversed_by_audit_id UUID,  -- Se foi revertido, qual audit_log fez isso
  CONSTRAINT fk_performed_by FOREIGN KEY (performed_by) REFERENCES auth.users(id),
  CONSTRAINT fk_approved_by FOREIGN KEY (approved_by) REFERENCES auth.users(id),
  CONSTRAINT fk_reversed_by FOREIGN KEY (reversed_by_audit_id) REFERENCES kb_audit_log(id)
);

CREATE INDEX idx_kb_audit_log_time ON kb_audit_log(performed_at DESC);
CREATE INDEX idx_kb_audit_log_entity ON kb_audit_log(entity_type, entity_id);
CREATE INDEX idx_kb_audit_log_user ON kb_audit_log(performed_by);
CREATE INDEX idx_kb_audit_log_approval ON kb_audit_log(approval_status);
CREATE INDEX idx_kb_audit_log_impact ON kb_audit_log(estimated_impact_score DESC);

-- 5.2 AGENT_DECISIONS — Decisões de agentes com confiança e justificativa
-- Rastreamento das escolhas dos agentes para análise posterior
CREATE TABLE agent_decisions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  decision_id VARCHAR(100) NOT NULL UNIQUE,  -- ID único da decisão
  agent_id VARCHAR(100) NOT NULL,  -- 'manta-05', 'agente-infraestrutura-s2', etc.
  agent_version VARCHAR(50),  -- Qual versão do agente
  segment segment_type,
  lifecycle_phase lifecycle_phase,
  -- Contexto da decisão
  request_id UUID,
  project_id VARCHAR(255),
  decision_type VARCHAR(100),  -- 'CUSTO_ESTIMATION', 'RISCO_ASSESSMENT', 'TEMPLATE_SELECTION'
  decision_category VARCHAR(100),
  -- Input
  input_parameters JSONB NOT NULL,  -- Parâmetros do projeto
  -- Processo de decisão
  reasoning TEXT,  -- Por que foi tomada esta decisão
  reasoning_steps JSONB,  -- Passo a passo do raciocínio
  decision_rules_applied VARCHAR(255)[],  -- Quais regras foram usadas
  constants_used JSONB,  -- Quais constantes KB foram aplicadas
  -- Decisão e confiança
  decision_output JSONB NOT NULL,
  decision_confidence NUMERIC(3, 2),  -- 0-1
  alternative_options JSONB,  -- [{option: '...', score: 0.7}, ...]
  -- Outcome real (preenchido posteriormente)
  outcome_reported BOOLEAN DEFAULT false,
  outcome_actual JSONB,  -- Como saiu na prática
  outcome_satisfaction feedback_rating,  -- User avaliou
  outcome_vs_prediction TEXT,
  -- Flags para análise
  is_outlier BOOLEAN DEFAULT false,  -- Saiu muito do padrão
  needs_review BOOLEAN DEFAULT false,  -- Decisão questionável
  -- Auditoria
  made_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  outcome_reported_at TIMESTAMP,
  outcome_reported_by UUID,
  CONSTRAINT fk_outcome_reported_by FOREIGN KEY (outcome_reported_by) REFERENCES auth.users(id)
);

CREATE INDEX idx_agent_decisions_agent ON agent_decisions(agent_id);
CREATE INDEX idx_agent_decisions_type ON agent_decisions(decision_type);
CREATE INDEX idx_agent_decisions_outcome ON agent_decisions(outcome_reported);
CREATE INDEX idx_agent_decisions_confidence ON agent_decisions(decision_confidence);
CREATE INDEX idx_agent_decisions_time ON agent_decisions(made_at DESC);
CREATE INDEX idx_agent_decisions_outlier ON agent_decisions(is_outlier, needs_review);
CREATE INDEX idx_agent_decisions_project ON agent_decisions(project_id);

-- ============================================================================
-- SEÇÃO 6: TRIGGERS PARA AUDITORIA AUTOMÁTICA
-- ============================================================================

-- Função para registrar mudanças em kb_constants
CREATE OR REPLACE FUNCTION audit_kb_constants()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO kb_audit_log (
    action,
    entity_type,
    entity_id,
    entity_name,
    old_values,
    new_values,
    performed_by,
    change_reason,
    approval_status
  ) VALUES (
    TG_OP::TEXT,
    'CONSTANT',
    CASE WHEN TG_OP = 'DELETE' THEN OLD.id ELSE NEW.id END,
    CASE WHEN TG_OP = 'DELETE' THEN OLD.constant_name ELSE NEW.constant_name END,
    CASE WHEN TG_OP IN ('UPDATE', 'DELETE') THEN row_to_json(OLD) ELSE NULL END,
    CASE WHEN TG_OP IN ('INSERT', 'UPDATE') THEN row_to_json(NEW) ELSE NULL END,
    CASE WHEN TG_OP = 'DELETE' THEN OLD.updated_by ELSE NEW.updated_by END,
    NEW.notes,
    'PENDING'
  );
  RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_audit_kb_constants
AFTER INSERT OR UPDATE OR DELETE ON kb_constants
FOR EACH ROW
EXECUTE FUNCTION audit_kb_constants();

-- Função para registrar mudanças em kb_templates
CREATE OR REPLACE FUNCTION audit_kb_templates()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO kb_audit_log (
    action,
    entity_type,
    entity_id,
    entity_name,
    old_values,
    new_values,
    performed_by,
    approval_status
  ) VALUES (
    TG_OP::TEXT,
    'TEMPLATE',
    CASE WHEN TG_OP = 'DELETE' THEN OLD.id ELSE NEW.id END,
    CASE WHEN TG_OP = 'DELETE' THEN OLD.template_name ELSE NEW.template_name END,
    CASE WHEN TG_OP IN ('UPDATE', 'DELETE') THEN row_to_json(OLD) ELSE NULL END,
    CASE WHEN TG_OP IN ('INSERT', 'UPDATE') THEN row_to_json(NEW) ELSE NULL END,
    CASE WHEN TG_OP = 'DELETE' THEN OLD.updated_by ELSE NEW.updated_by END,
    'PENDING'
  );
  RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_audit_kb_templates
AFTER INSERT OR UPDATE OR DELETE ON kb_templates
FOR EACH ROW
EXECUTE FUNCTION audit_kb_templates();

-- Função para registrar mudanças em kb_patterns
CREATE OR REPLACE FUNCTION audit_kb_patterns()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO kb_audit_log (
    action,
    entity_type,
    entity_id,
    entity_name,
    old_values,
    new_values,
    performed_by,
    approval_status
  ) VALUES (
    TG_OP::TEXT,
    'PATTERN',
    CASE WHEN TG_OP = 'DELETE' THEN OLD.id ELSE NEW.id END,
    CASE WHEN TG_OP = 'DELETE' THEN OLD.pattern_name ELSE NEW.pattern_name END,
    CASE WHEN TG_OP IN ('UPDATE', 'DELETE') THEN row_to_json(OLD) ELSE NULL END,
    CASE WHEN TG_OP IN ('INSERT', 'UPDATE') THEN row_to_json(NEW) ELSE NULL END,
    CASE WHEN TG_OP = 'DELETE' THEN OLD.validated_by ELSE NEW.validated_by END,
    'PENDING'
  );
  RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_audit_kb_patterns
AFTER INSERT OR UPDATE OR DELETE ON kb_patterns
FOR EACH ROW
EXECUTE FUNCTION audit_kb_patterns();

-- Função para auto-atualizar timestamp updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = CURRENT_TIMESTAMP;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_updated_at_kb_constants
BEFORE UPDATE ON kb_constants
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_update_updated_at_kb_templates
BEFORE UPDATE ON kb_templates
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_update_updated_at_project_insights
BEFORE UPDATE ON project_insights
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- SEÇÃO 7: POLÍTICAS RLS (Row Level Security)
-- ============================================================================
-- Nota: RLS exige role-based access. Adaptar policies conforme arquitetura de auth.

-- Habilitar RLS
ALTER TABLE kb_constants ENABLE ROW LEVEL SECURITY;
ALTER TABLE kb_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE kb_patterns ENABLE ROW LEVEL SECURITY;
ALTER TABLE kb_versions ENABLE ROW LEVEL SECURITY;
ALTER TABLE project_insights ENABLE ROW LEVEL SECURITY;
ALTER TABLE model_feedback ENABLE ROW LEVEL SECURITY;
ALTER TABLE constant_validation ENABLE ROW LEVEL SECURITY;
ALTER TABLE ml_training_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE ml_model_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE ml_predictions ENABLE ROW LEVEL SECURITY;
ALTER TABLE kb_audit_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_decisions ENABLE ROW LEVEL SECURITY;

-- Policy genérica: leitura pública para KB_CONSTANTS (validadas)
CREATE POLICY "Constantes validadas são públicas" ON kb_constants
  FOR SELECT
  USING (validation_status = 'VALIDADO' AND is_current = true);

-- Policy: apenas criador pode editar constantes
CREATE POLICY "Criar/editar constantes é restrito ao autor" ON kb_constants
  FOR ALL
  USING (auth.uid() = created_by OR auth.uid() = updated_by)
  WITH CHECK (auth.uid() = created_by OR auth.uid() = updated_by);

-- Policy: leitura de templates ativos
CREATE POLICY "Templates ativos são públicos" ON kb_templates
  FOR SELECT
  USING (is_active = true);

-- Policy: leitura de padrões validados
CREATE POLICY "Padrões validados são públicos" ON kb_patterns
  FOR SELECT
  USING (is_active = true AND confidence_score >= 0.7);

-- Policy: audit log é read-only para o gerador
CREATE POLICY "Audit log é imutável após criação" ON kb_audit_log
  FOR SELECT
  USING (auth.uid() = performed_by OR auth.uid() = approved_by);

-- Policy: agent decisions - leitura para usuários relevantes
CREATE POLICY "Agent decisions visível ao gerador e outcome reporter" ON agent_decisions
  FOR SELECT
  USING (true);  -- TODO: refinar conforme modelo de permissões

-- ============================================================================
-- SEÇÃO 8: VIEWS ÚTEIS PARA QUERIES
-- ============================================================================

-- View: Constantes atuais por segmento
CREATE OR REPLACE VIEW v_current_constants AS
SELECT
  segment,
  lifecycle_phase,
  constant_name,
  constant_type,
  constant_value,
  unit_of_measure,
  confidence_score,
  source_reference,
  is_current
FROM kb_constants
WHERE is_current = true
  AND validation_status = 'VALIDADO'
ORDER BY segment, lifecycle_phase, constant_name;

-- View: Performance de modelos em produção
CREATE OR REPLACE VIEW v_production_models AS
SELECT
  model_id,
  segment,
  target_variable,
  model_type,
  r_squared,
  rmse,
  mape,
  test_size,
  is_production,
  production_since,
  trained_at
FROM ml_model_metrics
WHERE is_production = true
  AND is_active = true
ORDER BY segment, target_variable, r_squared DESC;

-- View: Padrões mais confiáveis por segmento
CREATE OR REPLACE VIEW v_top_patterns AS
SELECT
  pattern_name,
  segment,
  lifecycle_phase,
  pattern_category,
  confidence_score,
  sample_count,
  typical_impact,
  is_active
FROM kb_patterns
WHERE is_active = true
ORDER BY segment, confidence_score DESC;

-- View: Histórico de decisões com outcomes
CREATE OR REPLACE VIEW v_agent_decision_outcomes AS
SELECT
  ad.agent_id,
  ad.decision_type,
  ad.decision_confidence,
  ad.outcome_reported,
  ad.outcome_satisfaction,
  COUNT(*) as total_decisions,
  SUM(CASE WHEN ad.outcome_reported = true THEN 1 ELSE 0 END) as outcomes_observed,
  AVG(CASE WHEN ad.outcome_satisfaction IS NOT NULL THEN
    CASE
      WHEN ad.outcome_satisfaction = 'EXCELENTE' THEN 5
      WHEN ad.outcome_satisfaction = 'BOM' THEN 4
      WHEN ad.outcome_satisfaction = 'ADEQUADO' THEN 3
      WHEN ad.outcome_satisfaction = 'INSUFICIENTE' THEN 2
      WHEN ad.outcome_satisfaction = 'INCORRETO' THEN 1
    END
  END) as avg_satisfaction_score
FROM agent_decisions ad
GROUP BY ad.agent_id, ad.decision_type, ad.decision_confidence, ad.outcome_reported, ad.outcome_satisfaction;

-- View: Predições com análise de desvio
CREATE OR REPLACE VIEW v_prediction_analysis AS
SELECT
  model_id,
  segment,
  target_variable,
  COUNT(*) as total_predictions,
  SUM(CASE WHEN outcome_observed = true THEN 1 ELSE 0 END) as outcomes_reported,
  AVG(prediction_confidence) as avg_confidence,
  AVG(ABS(variance_percent)) as avg_absolute_error_pct,
  SUM(CASE WHEN outcome_within_interval = true THEN 1 ELSE 0 END) as within_interval_count,
  MAX(variance_percent) as max_error_pct,
  MIN(variance_percent) as min_error_pct
FROM ml_predictions
GROUP BY model_id, segment, target_variable;

-- ============================================================================
-- SEÇÃO 9: ÍNDICES ADICIONAIS PARA PERFORMANCE
-- ============================================================================

-- Índices para queries de versionamento
CREATE INDEX idx_kb_constants_superseded ON kb_constants(superseded_by)
WHERE superseded_by IS NOT NULL;

CREATE INDEX idx_kb_patterns_evidence_projects ON kb_patterns
USING GIN (evidence_projects);

-- Índices para análise temporal
CREATE INDEX idx_project_insights_reported_at ON project_insights(reported_at DESC);
CREATE INDEX idx_model_feedback_feedback_at ON model_feedback(feedback_at DESC);
CREATE INDEX idx_ml_predictions_generated_at ON ml_predictions(generated_at DESC);

-- Índices para busca em JSON
CREATE INDEX idx_kb_constants_value_gin ON kb_constants USING GIN (constant_value);
CREATE INDEX idx_kb_templates_content_gin ON kb_templates USING GIN (content);
CREATE INDEX idx_kb_patterns_rule_gin ON kb_patterns USING GIN (pattern_rule);

-- Índices compostos para queries comuns
CREATE INDEX idx_agent_decisions_agent_type_outcome ON agent_decisions(agent_id, decision_type, outcome_reported);
CREATE INDEX idx_ml_predictions_model_outcome_time ON ml_predictions(model_id, outcome_reported, generated_at DESC);
CREATE INDEX idx_constant_validation_constant_action_time ON constant_validation(constant_id, validation_action, validated_at DESC);

-- ============================================================================
-- SEÇÃO 10: CONSTRAINSTS DE INTEGRIDADE
-- ============================================================================

-- Garante que versões não possam retroceder
ALTER TABLE kb_constants
ADD CONSTRAINT check_version_increment
CHECK (version > 0);

-- Garante que confidence scores estejam no intervalo 0-1
ALTER TABLE kb_constants
ADD CONSTRAINT check_confidence_range
CHECK (confidence_score IS NULL OR (confidence_score >= 0 AND confidence_score <= 1));

-- Garante que sample_count não seja negativo
ALTER TABLE kb_patterns
ADD CONSTRAINT check_sample_count
CHECK (sample_count >= 0);

-- Garante que tamanho de treino/validação/teste seja positivo
ALTER TABLE ml_model_metrics
ADD CONSTRAINT check_dataset_sizes
CHECK (train_size > 0 AND validation_size > 0 AND test_size > 0);

-- Garante que actual_value = NULL se outcome_observed = false
ALTER TABLE ml_predictions
ADD CONSTRAINT check_outcome_consistency
CHECK (
  (outcome_observed = false AND actual_value IS NULL) OR
  (outcome_observed = true AND actual_value IS NOT NULL)
);

-- ============================================================================
-- SEÇÃO 11: COMENTÁRIOS E DOCUMENTAÇÃO
-- ============================================================================

COMMENT ON TABLE kb_constants IS
'Constantes técnicas versionadas (K1/K2, normas, coeficientes).
Cada mudança é rastreada em kb_versions e kb_audit_log.
Validação por experts com confidence_score registrado.';

COMMENT ON TABLE kb_templates IS
'Templates reutilizáveis por segmento e fase (relatórios, checklists).
Rastreia uso (usage_count) para identificar templates mais populares.';

COMMENT ON TABLE kb_patterns IS
'Padrões identificados em projetos (custos, cronogramas, riscos).
Baseado em sample_count reais. Versionado com confiança.';

COMMENT ON TABLE project_insights IS
'Retroalimentação de projetos finalizados: custo real vs. previsto,
cronograma real vs. previsto, riscos materializados.
Fundamental para evolução dos agentes.';

COMMENT ON TABLE model_feedback IS
'Feedback dos usuários sobre qualidade das recomendações dos agentes.
Avalia se a recomendação foi útil, aplicável, acurada.';

COMMENT ON TABLE ml_training_data IS
'Dataset curado para treino de modelos de ML.
Cada row é um exemplo (features + target).
Rastreia data source e qualidade.';

COMMENT ON TABLE ml_model_metrics IS
'Métricas de performance dos modelos (RMSE, R², precision, recall).
Identifica melhor modelo por segment/target_variable.
Rastreia modelos em produção.';

COMMENT ON TABLE ml_predictions IS
'Registro de cada predição para validação posterior.
Compara predicted_value com actual_value quando outcome fica disponível.
Base para análise de drift e retraining.';

COMMENT ON TABLE kb_audit_log IS
'Log imutável de TODAS as mudanças na KB.
Rastreia ação, entidade, antes/depois, quem, quando, por quê.
Suporta compliance, rollback, análise de impacto.';

COMMENT ON TABLE agent_decisions IS
'Rastreamento das decisões de agentes com confiança e justificativa.
Essencial para entender como agentes raciocinam e melhorar.
Outcome_reported permite validação posterior.';

-- ============================================================================
-- FIM DO SCHEMA
-- ============================================================================
-- Data: 2026-07-30
-- Projeto: KB Evoluído — Manta Associados v4.2
-- Próximas etapas:
--   1. Popular constantes técnicas (S1-S10) em kb_constants
--   2. Criar templates por segmento/fase em kb_templates
--   3. Configurar RLS policies conforme modelo de auth
--   4. Implementar triggers de auditoria adicionais conforme necesário
--   5. Testar performance de índices e otimizar conforme uso real
-- ============================================================================
