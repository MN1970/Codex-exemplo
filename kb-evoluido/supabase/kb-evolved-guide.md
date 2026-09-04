# KB Evoluído — Guia de Implementação e Uso

**Projeto:** Manta Associados v4.2  
**Data:** 2026-07-30  
**Versão:** 1.0.0

---

## 📋 Sumário

1. [Arquitetura](#arquitetura)
2. [Seções do Schema](#seções-do-schema)
3. [Fluxos de Uso Típicos](#fluxos-de-uso-típicos)
4. [Queries Úteis](#queries-úteis)
5. [Integração com Agentes](#integração-com-agentes)
6. [Implementação e Deploy](#implementação-e-deploy)

---

## Arquitetura

O KB Evoluído é estruturado em 4 camadas:

```
┌─────────────────────────────────────────────────────────┐
│         CAMADA DE AUDITORIA & CONFORMIDADE              │
│  kb_audit_log | agent_decisions | constant_validation   │
└─────────────────────────────────────────────────────────┘
                            ▲
┌─────────────────────────────────────────────────────────┐
│          CAMADA DE ML & RETROALIMENTAÇÃO                 │
│  ml_training_data | ml_model_metrics | ml_predictions   │
│  project_insights | model_feedback                       │
└─────────────────────────────────────────────────────────┘
                            ▲
┌─────────────────────────────────────────────────────────┐
│              CAMADA DE CONHECIMENTO                       │
│  kb_constants | kb_templates | kb_patterns | kb_versions │
└─────────────────────────────────────────────────────────┘
```

**Fluxo de dados:**
1. **Conhecimento** entra via `kb_constants`, `kb_templates`, `kb_patterns`
2. **Agentes** consomem constantes para tomar decisões → `agent_decisions`
3. **Projetos reais** geram insights → `project_insights`
4. **Feedback dos users** refina confiança → `model_feedback`, `constant_validation`
5. **ML** treina novos modelos com dados validados → `ml_training_data`, `ml_model_metrics`
6. **Auditoria** registra tudo → `kb_audit_log`

---

## Seções do Schema

### Seção 1: ENUMS e Tipos Customizados

| Tipo | Valores | Descrição |
|------|---------|-----------|
| `segment_type` | S1-S10 | Segmentos técnicos (Rodovias, OAE, Ferrovia, Metrô, Portos, Aeroportos, Saneamento, Energia, Barragens) |
| `lifecycle_phase` | 8 fases | Estudo prévio → Encerramento |
| `constant_type` | 8 tipos | Norma técnica, coeficiente, fórmula, taxa, limite, etc. |
| `validation_status` | 6 status | Proposto → Validado → Descontinuado |
| `feedback_rating` | 5 níveis | Excelente → Incorreto |

### Seção 2: Tabelas de Conhecimento

#### `kb_constants`
- **Propósito:** Armazena constantes técnicas (K1/K2, normas, coeficientes, fórmulas)
- **Versionamento:** `version` + `is_current` + `superseded_by`
- **Validação:** `validation_status` + `confidence_score` (0-1)
- **Rastreamento:** `created_by`, `updated_by`, `validated_by`
- **Índices:** segment+phase, name, status, source

**Exemplos:**
```sql
-- Coeficiente de calibração K1 para pavimento CBUQ em S1 (Rodovia)
INSERT INTO kb_constants (
  segment, lifecycle_phase, constant_name, constant_type,
  constant_value, unit_of_measure, source_reference, source_year,
  validation_status, confidence_score, created_by, notes
) VALUES (
  'S1_RODOVIA', 'PROJETO_EXECUTIVO', 'K1_CBUQ_Calibracao',
  'COEFICIENTE_PROJETO', '1.15', 'adimensional',
  'DNIT Manual de Pavimentacao 2006', 2006,
  'VALIDADO', 0.92, 'uuid-usuario-1',
  'Calibrado em 450 projetos SP 2020-2025'
);

-- Fórmula para cálculo de custo base
INSERT INTO kb_constants (
  segment, lifecycle_phase, constant_name, constant_type,
  constant_value, source_reference,
  validation_status, confidence_score, created_by
) VALUES (
  'S1_RODOVIA', 'PROJETO_BASICO', 'FORMULA_CUSTO_KM',
  'FORMULA_CALCULO', 'custo = A0 + A1*extensao + A2*alt_media + A3*solo_tipo',
  'Regressão sobre 1200 projetos 2015-2025',
  'VALIDADO', 0.88, 'uuid-usuario-1'
);
```

#### `kb_templates`
- **Propósito:** Templates reutilizáveis (estrutura de relatórios, checklists, estimativas)
- **Estrutura flexível:** JSONB armazena seções, campos, validações
- **Rastreamento:** `usage_count` conta quantas vezes foi usado
- **Índices:** segment+phase+type, active status

**Exemplo:**
```sql
INSERT INTO kb_templates (
  template_name, segment, lifecycle_phase, template_type, content,
  description, created_by
) VALUES (
  'Checklist_Projeto_Executivo_Rodovia', 'S1_RODOVIA', 'PROJETO_EXECUTIVO',
  'CHECKLIST',
  jsonb_build_object(
    'secoes', jsonb_build_array(
      jsonb_build_object(
        'nome', 'Geometria',
        'itens', jsonb_build_array(
          'Alinhamento horizontal verificado',
          'Greide verificado',
          'Seção transversal definida',
          'Raios de curvatura >= norma'
        )
      ),
      jsonb_build_object(
        'nome', 'Estrutura do Pavimento',
        'itens', jsonb_build_array(
          'CBR base >= 15%',
          'Espessura CBUQ conforme cálculo',
          'Índice de Grupo <= 4'
        )
      )
    )
  ),
  'Template padrão para PEX de rodovia - atualizado 2026',
  'uuid-usuario-1'
);
```

#### `kb_patterns`
- **Propósito:** Padrões identificados em projetos (custos, cronogramas, riscos)
- **Baseado em evidência:** `sample_count` + `evidence_projects`
- **Confiança:** `confidence_score` baseada em frequência
- **Recomendações:** `recommended_mitigation` com ações sugeridas

**Exemplo:**
```sql
INSERT INTO kb_patterns (
  pattern_name, segment, lifecycle_phase, pattern_category,
  pattern_rule, sample_count, confidence_score,
  typical_impact, recommended_mitigation,
  discovered_by, discovered_at
) VALUES (
  'Aumento_Cronograma_Obras_Urbanas', 'S1_RODOVIA', 'OBRA_EXECUCAO',
  'CRONOGRAMA',
  jsonb_build_object(
    'condicao', 'localizacao = urbana',
    'efeito', 'atraso_meses = 2.1 * (largura_pista / 10)',
    'causa_raiz', 'interferências com serviços (água, gás, telefone)'
  ),
  450, 0.91,
  'Aumento médio de 18-24% no cronograma para obras em área urbana',
  jsonb_build_object(
    'acao1', 'Levantar serviços de concessionárias antes do PEX',
    'acao2', 'Adicionar 20% de contingência ao cronograma',
    'acao3', 'Estabelecer protocolo de coordenação com concessionárias'
  ),
  'uuid-usuario-1', CURRENT_TIMESTAMP
);
```

### Seção 3: Tabelas de Feedback

#### `project_insights`
- **Propósito:** Retroalimentação de projetos finalizados (custo real vs. previsto)
- **Comparação:** `predicted_value` vs `actual_value` + `variance_percent`
- **Generalização:** `is_applicable_broader` marca insights transferíveis
- **Validação:** Expert valida antes de aplicar

**Exemplo:**
```sql
INSERT INTO project_insights (
  project_id, project_name, segment, lifecycle_phase,
  insight_category, insight_summary,
  predicted_value, actual_value, variance_reason,
  reported_by, reported_at
) VALUES (
  'PROJ-2025-001', 'Rodovia BR-101 km 100-120', 'S1_RODOVIA', 'OBRA_EXECUCAO',
  'CUSTO_REAL', 'Custo de escavação foi 35% maior que previsto',
  2500000, 3375000,
  'Rocha alterada não detectada no SPT - houve maior escavação',
  'uuid-usuario-1', CURRENT_TIMESTAMP
);
```

#### `model_feedback`
- **Propósito:** Feedback sobre qualidade das recomendações dos agentes
- **Rating:** Excelente → Incorreto
- **Outcome:** Se foi aplicado e qual foi o resultado

#### `constant_validation`
- **Propósito:** Quando um expert valida, contesta ou aperfeiçoa uma constante
- **Rastreamento:** Todas as validações ficarão nesta tabela

### Seção 4: Tabelas de ML

#### `ml_training_data`
- **Propósito:** Dataset curado para treino (features + target)
- **Qualidade:** `data_quality_score` (0-1)
- **Origem:** Projeto real, simulação ou literatura
- **Split:** TRAIN, VALIDATION, TEST

#### `ml_model_metrics`
- **Propósito:** Performance dos modelos (RMSE, R², precision, recall, F1)
- **Feature importance:** Quais features mais importam
- **Production:** Rastreia modelos em produção com `production_since`

#### `ml_predictions`
- **Propósito:** Cada predição é registrada para validação posterior
- **Outcome:** `actual_value` preenchido quando realidade fica conhecida
- **Intervalo:** `prediction_interval_lower/upper` para incerteza

**Exemplo de análise:**
```sql
-- Predição foi feita em 2026-01-15
INSERT INTO ml_predictions (
  model_id, prediction_id, segment, target_variable,
  input_features, predicted_value, prediction_confidence,
  generated_by_agent, generated_at
) VALUES (
  'custo-estimador-s1-v3', 'PRED-2026-001',
  'S1_RODOVIA', 'CUSTO_TOTAL',
  jsonb_build_object(
    'extensao_km', 15.5,
    'largura_pista', 7.2,
    'solo_tipo', 'argila',
    'localizacao', 'rural'
  ),
  2800000, 0.87,
  'manta-05', '2026-01-15 10:30:00'
);

-- Mais tarde, quando projeto termina, preenche outcome
UPDATE ml_predictions
SET outcome_observed = true,
    actual_value = 3120000,
    actual_date = '2026-07-20',
    variance_percent = 11.43,
    outcome_reported_by = 'uuid-usuario-1',
    outcome_reported_at = CURRENT_TIMESTAMP
WHERE prediction_id = 'PRED-2026-001';
```

### Seção 5: Tabelas de Auditoria

#### `kb_audit_log`
- **Imutável:** Append-only, ninguém deleta
- **Rastreia:** Ação (INSERT/UPDATE/DELETE), entidade, antes/depois, quem, quando, por quê
- **Aprovação:** Mudanças sensíveis requerem aprovação
- **Reversibilidade:** `reversed_by_audit_id` permite rastrear rollbacks

**Exemplo de query:**
```sql
-- Quem mudou a constante K1 nos últimos 30 dias?
SELECT
  action, entity_name, old_values->>'constant_value' as valor_anterior,
  new_values->>'constant_value' as valor_novo,
  performed_by, performed_at, change_reason
FROM kb_audit_log
WHERE entity_type = 'CONSTANT'
  AND entity_name = 'K1_CBUQ_Calibracao'
  AND performed_at > CURRENT_DATE - INTERVAL '30 days'
ORDER BY performed_at DESC;
```

#### `agent_decisions`
- **Rastreamento:** Cada decisão do agente é registrada
- **Justificativa:** `reasoning_steps` documenta passo a passo
- **Outcome:** `outcome_observed` preenchido quando realidade confirma/contradiz
- **Flags:** `is_outlier`, `needs_review`

**Exemplo:**
```sql
INSERT INTO agent_decisions (
  decision_id, agent_id, segment, lifecycle_phase,
  decision_type, decision_category,
  input_parameters, reasoning, decision_rules_applied,
  constants_used, decision_output, decision_confidence,
  made_at
) VALUES (
  'DEC-2026-001', 'manta-05', 'S1_RODOVIA', 'PROJETO_BASICO',
  'CUSTO_ESTIMATION', 'CUSTO_TOTAL',
  jsonb_build_object('extensao', 15.5, 'largura', 7.2),
  'Aplicou modelo custo-estimador-s1-v3 com K1=1.15 (2024 baseline)',
  ARRAY['MODELO_PRODUCAO', 'K1_VALIDADO'],
  jsonb_build_object('K1', 1.15, 'taxa_base', 2800000),
  jsonb_build_object('custo_total', 2800000, 'unidade', 'BRL'),
  0.87,
  '2026-01-15 10:30:00'
);
```

---

## Fluxos de Uso Típicos

### Fluxo 1: Agente Toma Decisão Usando Conhecimento

```
1. Agente (ex: manta-05) recebe request de projeto
   → Query: SELECT * FROM v_current_constants
      WHERE segment = 'S1_RODOVIA'
      AND lifecycle_phase = 'PROJETO_BASICO'
      AND is_current = true

2. Agente aplica constantes (K1, fórmulas, etc.)
   → INSERT INTO agent_decisions (...)

3. Agente retorna recomendação com confiança
   → decision_confidence = 0.87
```

### Fluxo 2: Projeto Real Termina, Gera Insight

```
1. Usuario relata resultado real do projeto
   → INSERT INTO project_insights (...)
      com predicted_value vs actual_value

2. Expert valida insight
   → UPDATE project_insights
      SET validation_status = 'VALIDADO'

3. Se insight for generalizado
   → INSERT INTO kb_patterns (...)
      baseado em múltiplos insights

4. Agentes consomem novo padrão
   → SELECT * FROM v_top_patterns
      WHERE segment = 'S1_RODOVIA'
```

### Fluxo 3: ML Treina Novo Modelo Baseado em Feedback

```
1. Coletar feedback
   → SELECT * FROM model_feedback
      WHERE agent_id = 'manta-05'
      AND feedback_rating IN ('EXCELENTE', 'BOM')
      AND feedback_at > '2026-01-01'

2. Preparar training data
   → INSERT INTO ml_training_data (...)
      com validated examples

3. Treinar modelo
   → INSERT INTO ml_model_metrics (...)
      com RMSE, R², etc.

4. Validar em produção
   → UPDATE ml_model_metrics
      SET is_production = true
      WHERE r_squared > 0.88

5. Rastrear predições reais
   → INSERT INTO ml_predictions (...)
```

### Fluxo 4: Auditoria e Compliance

```
1. Buscar todas as mudanças em constantes críticas
   → SELECT * FROM kb_audit_log
      WHERE entity_type = 'CONSTANT'
      AND estimated_impact_score > 70

2. Verificar aprovações
   → SELECT * FROM kb_audit_log
      WHERE approval_status IN ('PENDING', 'REJECTED')

3. Rastrear decisões questionáveis
   → SELECT * FROM agent_decisions
      WHERE is_outlier = true
      OR needs_review = true
```

---

## Queries Úteis

### Q1: Constantes Críticas para um Segmento/Fase

```sql
SELECT
  constant_name, constant_value, unit_of_measure,
  confidence_score, source_reference,
  validation_status, validated_at
FROM kb_constants
WHERE segment = 'S1_RODOVIA'
  AND lifecycle_phase = 'PROJETO_EXECUTIVO'
  AND is_current = true
  AND validation_status = 'VALIDADO'
  AND confidence_score >= 0.85
ORDER BY confidence_score DESC;
```

### Q2: Performance de Modelos em Produção

```sql
SELECT
  model_id, segment, target_variable,
  r_squared, rmse, mape, test_size,
  trained_at, production_since
FROM ml_model_metrics
WHERE is_production = true
  AND is_active = true
ORDER BY segment, target_variable, r_squared DESC;
```

### Q3: Predições vs Realidade (Análise de Drift)

```sql
WITH pred_analysis AS (
  SELECT
    model_id, segment,
    COUNT(*) as total_preds,
    SUM(CASE WHEN outcome_observed THEN 1 ELSE 0 END) as outcomes,
    AVG(ABS(variance_percent)) as mean_error_pct,
    STDDEV(variance_percent) as error_std_dev
  FROM ml_predictions
  WHERE generated_at > CURRENT_DATE - INTERVAL '90 days'
  GROUP BY model_id, segment
)
SELECT
  model_id, segment, total_preds, outcomes,
  ROUND(mean_error_pct::numeric, 2) as mean_error_pct,
  ROUND(error_std_dev::numeric, 2) as error_std_dev,
  ROUND((outcomes::numeric / total_preds * 100)::numeric, 1) as outcome_coverage_pct
FROM pred_analysis
ORDER BY mean_error_pct DESC;
```

### Q4: Padrões Mais Confiáveis por Segmento

```sql
SELECT
  segment, pattern_category, pattern_name,
  sample_count, confidence_score,
  typical_impact
FROM kb_patterns
WHERE is_active = true
  AND confidence_score >= 0.70
ORDER BY segment, confidence_score DESC;
```

### Q5: Feedback sobre Agentes (Taxa de Satisfação)

```sql
SELECT
  agent_id,
  COUNT(*) as total_feedback,
  SUM(CASE WHEN feedback_rating = 'EXCELENTE' THEN 1 ELSE 0 END) as excellent,
  SUM(CASE WHEN feedback_rating = 'BOM' THEN 1 ELSE 0 END) as good,
  SUM(CASE WHEN feedback_rating = 'ADEQUADO' THEN 1 ELSE 0 END) as adequate,
  SUM(CASE WHEN feedback_rating IN ('INSUFICIENTE', 'INCORRETO') THEN 1 ELSE 0 END) as poor,
  ROUND(
    100.0 * (SUM(CASE WHEN feedback_rating IN ('EXCELENTE', 'BOM') THEN 1 ELSE 0 END)
    / COUNT(*))::numeric, 1
  ) as satisfaction_pct
FROM model_feedback
WHERE feedback_at > CURRENT_DATE - INTERVAL '30 days'
GROUP BY agent_id
ORDER BY satisfaction_pct DESC;
```

### Q6: Constantes Contestadas Recentemete

```sql
SELECT
  cv.constant_name, cv.segment,
  COUNT(*) as num_contestacoes,
  STRING_AGG(cv.alternative_value, ' | ') as valores_alternativos,
  MAX(cv.validated_at) as ultima_contestacao
FROM constant_validation cv
WHERE cv.validation_action = 'CONTESTOU'
  AND cv.validated_at > CURRENT_DATE - INTERVAL '30 days'
GROUP BY cv.constant_name, cv.segment
HAVING COUNT(*) >= 2
ORDER BY num_contestacoes DESC;
```

### Q7: Decisões de Agentes com Outcomes Ruins

```sql
SELECT
  ad.agent_id, ad.decision_type,
  COUNT(*) as total_decisions,
  SUM(CASE WHEN ad.outcome_satisfaction IN ('INSUFICIENTE', 'INCORRETO') THEN 1 ELSE 0 END) as bad_outcomes,
  ROUND(
    100.0 * SUM(CASE WHEN ad.outcome_satisfaction IN ('INSUFICIENTE', 'INCORRETO') THEN 1 ELSE 0 END)
    / COUNT(*)::numeric, 1
  ) as failure_rate_pct,
  ad.decision_rules_applied
FROM agent_decisions ad
WHERE ad.outcome_reported = true
  AND ad.made_at > CURRENT_DATE - INTERVAL '60 days'
GROUP BY ad.agent_id, ad.decision_type, ad.decision_rules_applied
HAVING ROUND(
  100.0 * SUM(CASE WHEN ad.outcome_satisfaction IN ('INSUFICIENTE', 'INCORRETO') THEN 1 ELSE 0 END)
  / COUNT(*)::numeric, 1
) >= 15
ORDER BY failure_rate_pct DESC;
```

### Q8: Audit Log - Rastrear Mudanças em Constante Crítica

```sql
SELECT
  kal.action,
  kal.old_values->>'constant_value' as valor_anterior,
  kal.new_values->>'constant_value' as valor_novo,
  kal.performed_by,
  (SELECT email FROM auth.users WHERE id = kal.performed_by) as usuario_email,
  kal.performed_at,
  kal.change_reason,
  kal.approval_status,
  CASE WHEN kal.approved_by IS NOT NULL
    THEN (SELECT email FROM auth.users WHERE id = kal.approved_by)
    ELSE NULL
  END as aprovado_por
FROM kb_audit_log kal
WHERE kal.entity_type = 'CONSTANT'
  AND kal.entity_name = 'K1_CBUQ_Calibracao'
  AND kal.performed_at > CURRENT_DATE - INTERVAL '90 days'
ORDER BY kal.performed_at DESC;
```

### Q9: Identificar Lacunas de Conhecimento

```sql
-- Quais combinações segment+phase+constant_type estão vazias?
SELECT DISTINCT
  st.segment,
  lp.lifecycle_phase,
  ct.constant_type
FROM (SELECT DISTINCT segment FROM kb_constants) st
CROSS JOIN (SELECT DISTINCT lifecycle_phase FROM kb_constants) lp
CROSS JOIN (
  SELECT 'NORMA_TECNICA'::constant_type as constant_type
  UNION SELECT 'COEFICIENTE_PROJETO'
  UNION SELECT 'FATOR_SEGURANCA'
  UNION SELECT 'ESPECIFICACAO_MATERIAL'
) ct
WHERE NOT EXISTS (
  SELECT 1 FROM kb_constants kc
  WHERE kc.segment = st.segment
    AND kc.lifecycle_phase = lp.lifecycle_phase
    AND kc.constant_type = ct.constant_type
    AND kc.is_current = true
)
ORDER BY st.segment, lp.lifecycle_phase, ct.constant_type;
```

### Q10: Templates Mais Usados

```sql
SELECT
  template_name, segment, lifecycle_phase,
  usage_count,
  version,
  created_at,
  ROUND(
    EXTRACT(DAY FROM CURRENT_TIMESTAMP - created_at)::numeric
  ) as dias_desde_criacao,
  ROUND(
    (usage_count / NULLIF(EXTRACT(DAY FROM CURRENT_TIMESTAMP - created_at), 0))::numeric,
    3
  ) as uso_por_dia
FROM kb_templates
WHERE is_active = true
ORDER BY usage_count DESC
LIMIT 20;
```

---

## Integração com Agentes

### Como um Agente Consome o KB

```python
# Exemplo: Agente manta-05 (orçamento) precisa de constantes
async def estimate_cost(project_data):
    # 1. Query constantes relevantes
    constants = supabase.from_('kb_constants').select(
        'constant_name, constant_value, unit_of_measure, confidence_score'
    ).eq('segment', project_data['segment'])\
     .eq('lifecycle_phase', project_data['lifecycle_phase'])\
     .eq('is_current', True)\
     .eq('validation_status', 'VALIDADO')\
     .execute()

    # 2. Query padrões relevantes
    patterns = supabase.from_('kb_patterns').select(
        'pattern_rule, typical_impact, confidence_score'
    ).eq('segment', project_data['segment'])\
     .eq('is_active', True)\
     .execute()

    # 3. Query templates
    template = supabase.from_('kb_templates').select('content').eq(
        'template_name', 'Checklist_Projeto_Executivo_Rodovia'
    ).single().execute()

    # 4. Usar constantes para calcular
    K1 = float(next(c['constant_value'] for c in constants['data']
                    if c['constant_name'] == 'K1_CBUQ_Calibracao'))

    estimation = calculate(project_data, K1)
    confidence = K1_confidence_score

    # 5. Registrar decisão
    supabase.from_('agent_decisions').insert({
        'decision_id': generate_id(),
        'agent_id': 'manta-05',
        'segment': project_data['segment'],
        'decision_type': 'CUSTO_ESTIMATION',
        'input_parameters': project_data,
        'decision_output': {'cost_estimate': estimation},
        'decision_confidence': confidence,
        'constants_used': {'K1': K1},
        'made_at': datetime.now()
    }).execute()

    return {
        'estimation': estimation,
        'confidence': confidence,
        'reasoning': f'Used K1={K1} (confidence {confidence})',
        'applied_patterns': [p['pattern_rule'] for p in patterns['data']]
    }
```

### Como Rastrear Predictions Reais

```python
# Quando projeto termina e realidade é conhecida
def report_project_outcome(project_id, actual_cost, prediction_id):
    # 1. Atualizar predição
    supabase.from_('ml_predictions').update({
        'outcome_observed': True,
        'actual_value': actual_cost,
        'actual_date': date.today(),
        'variance_percent': ((actual_cost - predicted_cost) / predicted_cost * 100),
        'outcome_reported_by': current_user_id,
        'outcome_reported_at': datetime.now()
    }).eq('prediction_id', prediction_id).execute()

    # 2. Registrar insight
    variance_reason = "Escavação 35% maior que previsto"
    supabase.from_('project_insights').insert({
        'project_id': project_id,
        'segment': 'S1_RODOVIA',
        'lifecycle_phase': 'OBRA_EXECUCAO',
        'insight_category': 'CUSTO_REAL',
        'insight_summary': f'Custo real {variance_pct}% acima previsto',
        'predicted_value': predicted_cost,
        'actual_value': actual_cost,
        'variance_reason': variance_reason,
        'reported_by': current_user_id
    }).execute()

    # 3. Atualizar agent_decision se existir
    supabase.from_('agent_decisions').update({
        'outcome_reported': True,
        'outcome_actual': {'cost': actual_cost},
        'outcome_satisfaction': 'BOM'  # User avalia
    }).eq('project_id', project_id).execute()
```

---

## Implementação e Deploy

### Passo 1: Criar Schema

```bash
# Em seu projeto Supabase, executar kb-evolved-schema.sql
# Via SQL editor ou CLI:
supabase db execute --file kb-evolved-schema.sql
```

### Passo 2: Validar Estrutura

```sql
-- Verificar tabelas criadas
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;

-- Verificar RLS habilitado
SELECT tablename, rowsecurity
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY tablename;
```

### Passo 3: Seed Data Inicial

```sql
-- Popular constantes base (S1-S10)
-- Popular templates por segmento
-- Popular 20-30 padrões iniciais baseado em histórico
-- Todos os arquivos de seed data devem vir em migration separada
```

### Passo 4: Testes

```sql
-- Teste 1: Inserir constante, verificar audit log
BEGIN;
INSERT INTO kb_constants (...) VALUES (...);
SELECT COUNT(*) FROM kb_audit_log WHERE entity_type = 'CONSTANT';
ROLLBACK;

-- Teste 2: Rastrear versionamento
UPDATE kb_constants SET ... WHERE id = '...';
SELECT version, is_current FROM kb_constants WHERE id = '...';

-- Teste 3: RLS - verificar leitura de validados
SELECT COUNT(*) FROM kb_constants WHERE validation_status = 'VALIDADO';
```

### Passo 5: Integração com Agentes

- Adicionar queries em `api/constants.ts` (ou arquivo análogo)
- Adicionar mutation em `api/decisions.ts`
- Testar com agente-manta-05 em staging
- Deploy para produção

### Checklist de Deploy

- [ ] Schema criado sem erros
- [ ] RLS habilitado em todas as tabelas críticas
- [ ] Índices criados e analisados (ANALYZE)
- [ ] Triggers funcionando (teste INSERT/UPDATE)
- [ ] Views criadas e testadas
- [ ] Seed data carregada (constantes base)
- [ ] Agentes testados contra nova KB
- [ ] Audit log funcionando
- [ ] Backups configurados
- [ ] Documentação atualizada no SP

---

## Próximas Fases (Roadmap)

### Fase 1 (Agora): Schema + Views Básicas
- ✅ Criar 12 tabelas
- ✅ Criar 10 índices críticos
- ✅ Criar 6 views para queries comuns
- ✅ Criar 8 triggers de auditoria

### Fase 2 (Jul-Ago): Seed Data + Integração Agentes
- [ ] Carregar 300+ constantes técnicas (S1-S10)
- [ ] Carregar 50+ templates por segmento
- [ ] Carregar 200+ padrões históricos
- [ ] Treinar primeiro modelo ML em training_data
- [ ] Integrar agentes (manta-05, agente-infraestrutura-s1, etc.)

### Fase 3 (Set-Out): Feedback Loop
- [ ] Implementar coleta de project_insights
- [ ] Dashboard de model_feedback (taxa satisfação agentes)
- [ ] Validação de constantes pelo time técnico
- [ ] Primeiros retrainings de modelos

### Fase 4 (Nov): Otimização
- [ ] Análise de drift em ml_predictions
- [ ] Audit compliance reports
- [ ] Performance tuning de índices
- [ ] Cache de constantes mais usadas

---

## Suporte e Troubleshooting

### Problema: RLS bloqueando reads
**Solução:** Verificar policies. Se agente precisa ler, adicionar:
```sql
CREATE POLICY "Agentes podem ler constantes validadas" ON kb_constants
  FOR SELECT
  USING (validation_status = 'VALIDADO');
```

### Problema: Audit log cresce muito
**Solução:** Particionar `kb_audit_log` por `performed_at` (mensal).
Mover dados antigos para archive table.

### Problema: Queries lentas em grandes datasets
**Solução:** Adicionar índices compostos:
```sql
CREATE INDEX idx_ml_predictions_model_segment_outcome
  ON ml_predictions(model_id, segment, outcome_observed);
```

### Problema: Integridade de versionamento quebrada
**Solução:** Trigger força version++:
```sql
CREATE TRIGGER trg_increment_version
  BEFORE UPDATE ON kb_constants
  FOR EACH ROW
  EXECUTE FUNCTION increment_version();
```

---

**Fim do Guia**  
Versão: 1.0.0  
Última atualização: 2026-07-30
