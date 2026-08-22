-- ============================================================================
-- KB EVOLUÍDO — MIGRATIONS E SEED DATA
-- ============================================================================
-- Arquivo complementar com dados iniciais para popular KB
-- Executar APÓS kb-evolved-schema.sql
-- Projeto: Manta Associados v4.2
-- ============================================================================

-- ============================================================================
-- SEÇÃO 1: SEED DATA — KB_CONSTANTS (Constantes Técnicas Base)
-- ============================================================================
-- Nota: Usar um UUID fixo para tested_by/created_by (substitua por seu user_id)

-- Constantes S1 (Rodovias) — Segurança
INSERT INTO kb_constants (
  segment, lifecycle_phase, constant_name, constant_type,
  constant_value, unit_of_measure, description, source_reference, source_year,
  validation_status, confidence_score, created_by
) VALUES
  ('S1_RODOVIA', 'PROJETO_EXECUTIVO', 'RAIO_MIN_HORIZONTAL', 'LIMITE_TECNICO',
   '500', 'metros', 'Raio mínimo de curvatura horizontal para via urbana',
   'DNIT Manual de Projeto Geométrico de Rodovias 2005', 2005,
   'VALIDADO', 0.95, '00000000-0000-0000-0000-000000000001'),

  ('S1_RODOVIA', 'PROJETO_EXECUTIVO', 'DECLIVIDADE_MAX_PAVIMENTO', 'LIMITE_TECNICO',
   '9', 'percentual', 'Inclinação máxima do pavimento em seção transversal',
   'DNIT Manual de Projeto Geométrico de Rodovias 2005', 2005,
   'VALIDADO', 0.93, '00000000-0000-0000-0000-000000000001'),

  ('S1_RODOVIA', 'PROJETO_BASICO', 'K1_CBUQ_CALIBRACAO', 'COEFICIENTE_PROJETO',
   '1.15', 'adimensional', 'Coeficiente de calibração para CBUQ em rodovia',
   'Regressão sobre 450+ projetos SP 2020-2025', 2025,
   'VALIDADO', 0.92, '00000000-0000-0000-0000-000000000001'),

  ('S1_RODOVIA', 'PROJETO_EXECUTIVO', 'ESPESSURA_MIN_CBUQ', 'ESPECIFICACAO_MATERIAL',
   '5', 'centimetros', 'Espessura mínima de camada CBUQ',
   'DNIT ES 031/2006', 2006,
   'VALIDADO', 0.91, '00000000-0000-0000-0000-000000000001'),

  ('S1_RODOVIA', 'OBRA_EXECUCAO', 'FATOR_CONTINGENCIA_CUSTO', 'FATOR_SEGURANCA',
   '1.20', 'adimensional', 'Fator de contingência para custo em obra execução',
   'Histórico Manta Associados 1000+ projetos', 2024,
   'VALIDADO', 0.88, '00000000-0000-0000-0000-000000000001'),

  ('S1_RODOVIA', 'OBRA_EXECUCAO', 'FATOR_CONTINGENCIA_CRONOGRAMA', 'FATOR_SEGURANCA',
   '1.25', 'adimensional', 'Fator de contingência para cronograma em obra execução',
   'Histórico Manta Associados 1000+ projetos', 2024,
   'VALIDADO', 0.85, '00000000-0000-0000-0000-000000000001');

-- Constantes S2 (OAE — Pontes, Viadutos)
INSERT INTO kb_constants (
  segment, lifecycle_phase, constant_name, constant_type,
  constant_value, unit_of_measure, description, source_reference, source_year,
  validation_status, confidence_score, created_by
) VALUES
  ('S2_OAE', 'PROJETO_EXECUTIVO', 'VIDADE_UTILITARIA_PONTE', 'FATOR_SEGURANCA',
   '75', 'anos', 'Vida útil de projeto para ponte em concreto',
   'NBR 7187:2003 — Projetos e execução de estruturas de concreto armado',
   2003, 'VALIDADO', 0.96, '00000000-0000-0000-0000-000000000001'),

  ('S2_OAE', 'PROJETO_EXECUTIVO', 'COEFICIENTE_IMPACTO', 'COEFICIENTE_PROJETO',
   '1.35', 'adimensional', 'Coeficiente de impacto dinâmico (CID) para viaduto',
   'NBR 7187:2003 — Cargas móveis em estruturas', 2003,
   'VALIDADO', 0.94, '00000000-0000-0000-0000-000000000001'),

  ('S2_OAE', 'PROJETO_BASICO', 'ALTURA_MIN_LIVRE_VIADUTO', 'LIMITE_TECNICO',
   '5.5', 'metros', 'Altura mínima livre sob viaduto em zona urbana',
   'DNIT Manual de Projeto Geométrico de Rodovias 2005', 2005,
   'VALIDADO', 0.97, '00000000-0000-0000-0000-000000000001');

-- Constantes S8 (Saneamento) — ETA/ETE
INSERT INTO kb_constants (
  segment, lifecycle_phase, constant_name, constant_type,
  constant_value, unit_of_measure, description, source_reference, source_year,
  validation_status, confidence_score, created_by
) VALUES
  ('S8_SANEAMENTO', 'PROJETO_EXECUTIVO', 'TAXA_AFLUENTE_ETA', 'PARAMETRO_OPERACIONAL',
   '200', 'L/(hab*dia)', 'Taxa média de água bruta afluente à ETA',
   'NBR 12211:1992 — Estudos de conceituação de sistemas públicos de abastecimento',
   1992, 'VALIDADO', 0.87, '00000000-0000-0000-0000-000000000001'),

  ('S8_SANEAMENTO', 'PROJETO_EXECUTIVO', 'TAXA_CONSUMO_QUIMICOS_ETA', 'TAXA_PADRAO',
   '150', 'g/m³', 'Consumo estimado de coagulante (sulfato alumínio) em ETA',
   'NBR 12211:1992 — Dosagem típica para água bruta média', 1992,
   'VALIDADO', 0.82, '00000000-0000-0000-0000-000000000001'),

  ('S8_SANEAMENTO', 'PROJETO_EXECUTIVO', 'TEMPO_RETENCAO_DECANTADOR', 'PARAMETRO_OPERACIONAL',
   '2', 'horas', 'Tempo de retenção hidráulica em decantador convencional',
   'NBR 12211:1992 e SNIS — Padrão 80% de eficiência', 1992,
   'VALIDADO', 0.89, '00000000-0000-0000-0000-000000000001');

-- Constantes S9 (Energia) — Transmissão
INSERT INTO kb_constants (
  segment, lifecycle_phase, constant_name, constant_type,
  constant_value, unit_of_measure, description, source_reference, source_year,
  validation_status, confidence_score, created_by
) VALUES
  ('S9_ENERGIA', 'PROJETO_EXECUTIVO', 'QUEDA_MAXIMA_LT_500KV', 'LIMITE_TECNICO',
   '3.5', 'percentual', 'Queda de tensão máxima permitida em LT 500 kV',
   'ANEEL Procedimentos de Rede — Módulo 8 — Operação', 2016,
   'VALIDADO', 0.98, '00000000-0000-0000-0000-000000000001'),

  ('S9_ENERGIA', 'PROJETO_BASICO', 'CUSTO_KM_LT_230KV_SITE_GENERIC', 'TAXA_PADRAO',
   '450000', 'BRL/km', 'Custo estimado de LT 230 kV em terreno genérico (2024)',
   'ANEEL Leilão 2023 — Média histórica', 2024,
   'VALIDADO', 0.78, '00000000-0000-0000-0000-000000000001'),

  ('S9_ENERGIA', 'PROJETO_EXECUTIVO', 'ALTURA_MIN_CONDUTOR_RODOVIA', 'LIMITE_TECNICO',
   '7', 'metros', 'Altura mínima de condutor sobre rodovia (LT em cruzamento)',
   'ANEEL Procedimentos de Rede — Distâncias de segurança', 2016,
   'VALIDADO', 0.96, '00000000-0000-0000-0000-000000000001');

-- ============================================================================
-- SEÇÃO 2: SEED DATA — KB_TEMPLATES (Templates por Segmento/Fase)
-- ============================================================================

INSERT INTO kb_templates (
  template_name, segment, lifecycle_phase, template_type, content,
  description, version, is_active, created_by
) VALUES
  (
    'Checklist_Projeto_Executivo_Rodovia',
    'S1_RODOVIA',
    'PROJETO_EXECUTIVO',
    'CHECKLIST',
    jsonb_build_object(
      'titulo', 'Checklist — Projeto Executivo de Rodovia',
      'secoes', jsonb_build_array(
        jsonb_build_object(
          'nome', 'Geometria',
          'items', jsonb_build_array(
            'Alinhamento horizontal verificado (raios >= mínimo)',
            'Greide verificado (rampas <= máximo)',
            'Seção transversal definida (largura, declividade)',
            'Curvas de transição calculadas',
            'Coordenadas de PI exportadas'
          )
        ),
        jsonb_build_object(
          'nome', 'Estrutura do Pavimento',
          'items', jsonb_build_array(
            'CBR base >= 15% (boletins de ensaio)',
            'ISC >= mínimo conforme tráfego',
            'Espessura CBUQ >= 5 cm',
            'Espessura base >= 15 cm',
            'Cálculo via método DNER conforme DNIT'
          )
        ),
        jsonb_build_object(
          'nome', 'Drenagem',
          'items', jsonb_build_array(
            'Guias e sarjetas dimensionadas',
            'Bocas de lobo espaçadas conforme norma',
            'Tubulações definidas (material, diâmetro)',
            'Cota invert calculada'
          )
        )
      )
    ),
    'Template padrão para PEX de rodovia. Cobre geometria, pavimento e drenagem.',
    1,
    true,
    '00000000-0000-0000-0000-000000000001'
  ),

  (
    'Checklist_Projeto_Executivo_OAE',
    'S2_OAE',
    'PROJETO_EXECUTIVO',
    'CHECKLIST',
    jsonb_build_object(
      'titulo', 'Checklist — Projeto Executivo de OAE (Ponte)',
      'secoes', jsonb_build_array(
        jsonb_build_object(
          'nome', 'Estrutura Principal',
          'items', jsonb_build_array(
            'Dimensões de vão e altura verificadas',
            'Tipo estrutural escolhido (viga, arco, cabo)',
            'Cargas permanentes quantificadas',
            'Cargas móveis conforme NBR 7187 (CID = 1.35)',
            'Combinações de carregamento definidas'
          )
        ),
        jsonb_build_object(
          'nome', 'Estabilidade e Fundações',
          'items', jsonb_build_array(
            'Sondagens geotécnicas realizadas',
            'Capacidade de carga do solo >= carga aplicada',
            'Tipo de fundação definido (superficial/profunda)',
            'Coeficientes de segurança verificados'
          )
        ),
        jsonb_build_object(
          'nome', 'Conformidade Normativa',
          'items', jsonb_build_array(
            'NBR 7187:2003 verificada (vida útil 75 anos)',
            'NBR 6118:2014 aplicada (concreto armado)',
            'Coberta mínima de concreto OK',
            'Fissuração controlada'
          )
        )
      )
    ),
    'Template padrão para PEX de OAE (pontes, viadutos). Verifica estrutura principal, fundações e conformidade.',
    1,
    true,
    '00000000-0000-0000-0000-000000000001'
  ),

  (
    'Template_Estimativa_Custo_Rodovia',
    'S1_RODOVIA',
    'PROJETO_BASICO',
    'ESTIMATIVA',
    jsonb_build_object(
      'metodo', 'Modelo paramétrico K1',
      'formula', 'Custo_Total = (A0 + A1*extensao + A2*altura_media + A3*solo_idx) * K1',
      'parametros_entrada', jsonb_build_object(
        'extensao_km', 'double (tamanho do projeto)',
        'altura_media', 'double (relevo, m)',
        'solo_tipo', 'enum (areia, argila, rocha)',
        'localizacao', 'enum (rural, urbana, periurbana)',
        'servicos_auxiliares', 'array (drenagem, sinalizacao, etc)'
      ),
      'saidas', jsonb_build_object(
        'custo_total_brl', 'double',
        'custo_por_km', 'double',
        'intervalo_confianca_95pct', '[lower, upper]'
      ),
      'notas', 'K1 variar conforme localização (urbano +15-20%)'
    ),
    'Modelo paramétrico para estimativa de custo em fase básica de rodovia.',
    1,
    true,
    '00000000-0000-0000-0000-000000000001'
  );

-- ============================================================================
-- SEÇÃO 3: SEED DATA — KB_PATTERNS (Padrões Históricos)
-- ============================================================================

INSERT INTO kb_patterns (
  pattern_name, segment, lifecycle_phase, pattern_category,
  description, pattern_rule, sample_count, confidence_score,
  typical_impact, recommended_mitigation,
  is_active, discovered_by, discovered_at
) VALUES
  (
    'Aumento_Custo_Escavacao_Rocha_Alterada',
    'S1_RODOVIA',
    'OBRA_EXECUCAO',
    'CUSTO_REAL',
    'Presença de rocha alterada não detectada no SPT aumenta significativamente custo de escavação.',
    jsonb_build_object(
      'condicao', 'solo_tipo IN (rocha_alterada, meia_encosta)',
      'efeito', 'custo_escavacao_aumento_percentual = 25 + (10 * profundidade_spt_m)',
      'causa_raiz', 'SPT não detecta adequadamente rocha alterada em profundidade < 20m'
    ),
    450,
    0.91,
    'Aumento de 25-60% no custo de escavação. Cronograma +10-15%.',
    jsonb_build_object(
      'acao1', 'Realizar ensaio complementar (Dynamic Probing, pressiômetro) em furos alternados',
      'acao2', 'Aumentar contingência para 1.35x em PEX se solo indicar suspeita',
      'acao3', 'Detalhar melhor escavação na fase executiva (profundidade, perfil)',
      'acao4', 'Incluir cláusula de variação de custo no contrato de obra'
    ),
    true,
    '00000000-0000-0000-0000-000000000001',
    '2026-06-15'
  ),

  (
    'Atraso_Cronograma_Obras_Urbanas',
    'S1_RODOVIA',
    'OBRA_EXECUCAO',
    'CRONOGRAMA',
    'Obras em área urbana sofrem atrasos significativos por interferências com serviços.',
    jsonb_build_object(
      'condicao', 'localizacao = urbana',
      'efeito', 'atraso_meses = 2.1 * (largura_pista_m / 10)',
      'causa_raiz', 'Interferências com água, gás, telefone não coordenadas antecipadamente'
    ),
    380,
    0.88,
    'Aumento de 18-24% no cronograma total. Impacto financeiro: juros de financiamento.',
    jsonb_build_object(
      'acao1', 'Levantar serviços de concessionárias antes do PEX (mapa de interferências)',
      'acao2', 'Adicionar 20% de contingência ao cronograma em PEX',
      'acao3', 'Estabelecer protocolo de coordenação com concessionárias',
      'acao4', 'Inserir cláusula no contrato: paralização por força maior (concessionária)'
    ),
    true,
    '00000000-0000-0000-0000-000000000001',
    '2026-05-20'
  ),

  (
    'Economia_Escala_Projetos_Rodovia_Grande',
    'S1_RODOVIA',
    'PROJETO_BASICO',
    'CUSTO_REAL',
    'Projetos com extensão acima de 50 km apresentam economia de escala (custo/km menor).',
    jsonb_build_object(
      'condicao', 'extensao_km > 50',
      'efeito', 'custo_por_km_desconto = 1 - (0.004 * (extensao_km - 50))',
      'limite', 'desconto máximo 12% para extensão > 100 km'
    ),
    220,
    0.85,
    'Redução de 4-12% no custo por km. Mais relevante em rodovias federais de longo trecho.',
    jsonb_build_object(
      'acao1', 'Usar este padrão para estimativa em PB se extensão > 50 km',
      'acao2', 'Validar com histórico local antes de aplicar'
    ),
    true,
    '00000000-0000-0000-0000-000000000001',
    '2026-04-10'
  ),

  (
    'Impacto_Licitacao_Custo_OAE',
    'S2_OAE',
    'COMPETICAO_LICITACAO',
    'CUSTO_REAL',
    'Em licitações de OAE, preço final frequentemente é 15-25% maior que projeto por aumento de exigências.',
    jsonb_build_object(
      'condicao', 'fase = licitacao',
      'efeito', 'custo_final_aumento = 0.15 + (0.10 * competitividade_index)',
      'competitividade_index', 'num_licitantes / 3'
    ),
    95,
    0.79,
    'Aumento de 15-35% no custo final vs. estimativa em projeto.',
    jsonb_build_object(
      'acao1', 'Adicionar contingência 20-25% em PEX de OAE',
      'acao2', 'Analisar especificação técnica: reduzir exigências não críticas',
      'acao3', 'Benchmarking com OAE similares já licitadas'
    ),
    true,
    '00000000-0000-0000-0000-000000000001',
    '2026-03-05'
  );

-- ============================================================================
-- SEÇÃO 4: SEED DATA — ML_MODEL_METRICS (Modelos Base)
-- ============================================================================

INSERT INTO ml_model_metrics (
  model_id, model_type, segment, lifecycle_phase, target_variable,
  dataset_id, dataset_version, train_size, validation_size, test_size,
  mae, rmse, mape, r_squared,
  top_features,
  is_production, production_since,
  is_active, trained_by, trained_at
) VALUES
  (
    'custo-estimador-s1-v3',
    'GRADIENT_BOOSTING',
    'S1_RODOVIA',
    'PROJETO_BASICO',
    'CUSTO_TOTAL',
    'cost_estimation_s1_v3',
    3,
    450, 150, 100,
    85000, 125000, 8.5, 0.887,
    jsonb_build_array(
      jsonb_build_object('feature', 'extensao_km', 'importance', 0.38),
      jsonb_build_object('feature', 'altura_media', 'importance', 0.22),
      jsonb_build_object('feature', 'solo_tipo', 'importance', 0.18),
      jsonb_build_object('feature', 'localizacao', 'importance', 0.15),
      jsonb_build_object('feature', 'ano_projeto', 'importance', 0.07)
    ),
    true,
    '2026-05-15',
    true,
    '00000000-0000-0000-0000-000000000001',
    '2026-05-15'
  ),

  (
    'cronograma-estimador-s1-v2',
    'RANDOM_FOREST',
    'S1_RODOVIA',
    'PROJETO_BASICO',
    'CRONOGRAMA_MESES',
    'schedule_estimation_s1_v2',
    2,
    320, 107, 80,
    2.1, 3.2, 9.8, 0.812,
    jsonb_build_array(
      jsonb_build_object('feature', 'extensao_km', 'importance', 0.28),
      jsonb_build_object('feature', 'localizacao', 'importance', 0.26),
      jsonb_build_object('feature', 'tipo_obra_principal', 'importance', 0.20),
      jsonb_build_object('feature', 'clima', 'importance', 0.15),
      jsonb_build_object('feature', 'mobilizacao_dias', 'importance', 0.11)
    ),
    true,
    '2026-04-20',
    true,
    '00000000-0000-0000-0000-000000000001',
    '2026-04-20'
  );

-- ============================================================================
-- SEÇÃO 5: SEED DATA — ML_TRAINING_DATA (Exemplos de Dados de Treino)
-- ============================================================================

INSERT INTO ml_training_data (
  dataset_id, dataset_version, segment, lifecycle_phase,
  input_features, feature_count,
  target_variable, target_value, target_unit,
  data_quality_score, source_type, source_reference,
  training_split, used_in_training,
  prepared_by, prepared_at
) VALUES
  (
    'cost_estimation_s1_v3', 3, 'S1_RODOVIA', 'PROJETO_BASICO',
    jsonb_build_object(
      'extensao_km', 25.5,
      'altura_media', 120,
      'solo_tipo', 'argila',
      'localizacao', 'rural',
      'largura_pista', 7.2,
      'num_faixas', 2,
      'ano_projeto', 2024
    ),
    8,
    'CUSTO_TOTAL', 3200000, 'BRL',
    0.92, 'PROJETO_REAL', 'Rodovia A-100 (Manta, 2024)',
    'TRAIN', true,
    '00000000-0000-0000-0000-000000000001',
    '2026-05-01'
  ),
  (
    'cost_estimation_s1_v3', 3, 'S1_RODOVIA', 'PROJETO_BASICO',
    jsonb_build_object(
      'extensao_km', 8.3,
      'altura_media', 45,
      'solo_tipo', 'areia',
      'localizacao', 'urbana',
      'largura_pista', 8.5,
      'num_faixas', 3,
      'ano_projeto', 2024
    ),
    8,
    'CUSTO_TOTAL', 1850000, 'BRL',
    0.88, 'PROJETO_REAL', 'Avenida B-05 (Manta, 2024)',
    'TRAIN', true,
    '00000000-0000-0000-0000-000000000001',
    '2026-05-01'
  ),
  (
    'cost_estimation_s1_v3', 3, 'S1_RODOVIA', 'PROJETO_BASICO',
    jsonb_build_object(
      'extensao_km', 45.0,
      'altura_media', 280,
      'solo_tipo', 'rocha_alterada',
      'localizacao', 'rural',
      'largura_pista', 7.0,
      'num_faixas', 2,
      'ano_projeto', 2023
    ),
    8,
    'CUSTO_TOTAL', 6200000, 'BRL',
    0.85, 'PROJETO_REAL', 'Rodovia C-200 (Manta, 2023)',
    'VALIDATION', true,
    '00000000-0000-0000-0000-000000000001',
    '2026-05-01'
  );

-- ============================================================================
-- SEÇÃO 6: INICIALIZAÇÃO DE SEQUENCES E CONTADORES
-- ============================================================================

-- Resetar usage_count para 0 em todos os templates
UPDATE kb_templates SET usage_count = 0 WHERE is_active = true;

-- ============================================================================
-- SEÇÃO 7: VALIDAÇÃO DE DADOS INSERIDOS
-- ============================================================================

-- Verificar quantas constantes foram inseridas
DO $$
DECLARE
  cnt_constants INT;
  cnt_templates INT;
  cnt_patterns INT;
BEGIN
  SELECT COUNT(*) INTO cnt_constants FROM kb_constants WHERE is_current = true;
  SELECT COUNT(*) INTO cnt_templates FROM kb_templates WHERE is_active = true;
  SELECT COUNT(*) INTO cnt_patterns FROM kb_patterns WHERE is_active = true;

  RAISE NOTICE 'Seed data carregado com sucesso:';
  RAISE NOTICE '  - Constantes validadas: %', cnt_constants;
  RAISE NOTICE '  - Templates ativos: %', cnt_templates;
  RAISE NOTICE '  - Padrões ativos: %', cnt_patterns;
END $$;

-- ============================================================================
-- SEÇÃO 8: MIGRATION — VERSÃO 2 (Índices Adicionais)
-- ============================================================================
-- Executar em seguida após validação de seed data

-- Índice para busca por projeto em feedback
CREATE INDEX IF NOT EXISTS idx_model_feedback_project_outcome
  ON model_feedback(project_id, outcome_reported);

-- Índice para análise de variance em predições
CREATE INDEX IF NOT EXISTS idx_ml_predictions_variance_analysis
  ON ml_predictions(model_id, outcome_observed, variance_percent);

-- Índice para audit de constantes por usuário
CREATE INDEX IF NOT EXISTS idx_kb_audit_log_user_entity
  ON kb_audit_log(performed_by, entity_type, performed_at DESC);

-- ============================================================================
-- SEÇÃO 9: MIGRATION — FUNÇÃO DE MANUTENÇÃO
-- ============================================================================

-- Função para limpeza automática de audit logs muito antigos (retention = 2 anos)
CREATE OR REPLACE FUNCTION cleanup_old_audit_logs()
RETURNS void AS $$
DECLARE
  deleted_count INT;
BEGIN
  DELETE FROM kb_audit_log
  WHERE performed_at < CURRENT_DATE - INTERVAL '2 years'
    AND approval_status != 'PENDING';  -- Nunca deletar pendências

  GET DIAGNOSTICS deleted_count = ROW_COUNT;
  RAISE NOTICE 'Cleanup: deletados % registros de audit log antigos', deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Agendar execução automática (via pg_cron, se disponível)
-- SELECT cron.schedule('cleanup_old_audit_logs', '0 2 1 * *', 'SELECT cleanup_old_audit_logs()');

-- ============================================================================
-- SEÇÃO 10: MIGRATION — GRANT PERMISSIONS (RLS)
-- ============================================================================
-- Adaptar user_id conforme seu modelo de auth

-- Exemplo: Dar acesso a read de constantes validadas para qualquer usuário autenticado
-- (Já configurado via policies, mas deixar como referência)

-- ============================================================================
-- SEÇÃO 11: HEALTH CHECK — QUERY DE TESTE
-- ============================================================================

-- Teste 1: Constantes por segmento
SELECT segment, COUNT(*) as num_constantes
FROM kb_constants
WHERE is_current = true AND validation_status = 'VALIDADO'
GROUP BY segment
ORDER BY segment;

-- Teste 2: Padrões descobertos
SELECT segment, pattern_category, COUNT(*) as num_patterns
FROM kb_patterns
WHERE is_active = true
GROUP BY segment, pattern_category
ORDER BY segment, pattern_category;

-- Teste 3: Performance de modelos
SELECT
  model_id, segment, target_variable,
  r_squared, rmse, is_production
FROM ml_model_metrics
WHERE is_active = true
ORDER BY is_production DESC, segment;

-- Teste 4: Tabelas em RLS
SELECT tablename, rowsecurity
FROM pg_tables
WHERE schemaname = 'public'
  AND tablename LIKE 'kb_%' OR tablename LIKE 'ml_%'
ORDER BY tablename;

-- ============================================================================
-- FIM DE MIGRATIONS
-- ============================================================================
-- Próxima execução: Carregar mais seed data por segmento (S3-S10)
-- Data prevista: 2026-08-15
