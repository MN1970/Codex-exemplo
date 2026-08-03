-- SICRO Seed Data — Dados iniciais para teste
-- Exemplos de itens SICRO comuns em obras

-- Insert dados de teste (100 itens de exemplo)
INSERT INTO sicro_insumos (codigo, descricao, unidade, uf, periodo, custo_m, custo_mo, custo_eq, metadados)
VALUES
  ('73.101.001', 'Escavação manual em solo de 1ª categoria', 'M³', 'SP', '2026-07-01', 15.50, 45.00, 0.00, '{"categoria": "terraplenagem", "tipo": "escavacao"}'),
  ('73.102.001', 'Escavação mecanizada em solo', 'M³', 'SP', '2026-07-01', 8.00, 25.00, 12.50, '{"categoria": "terraplenagem", "tipo": "escavacao"}'),
  ('73.103.001', 'Transporte de material até 1 km', 'M³.km', 'SP', '2026-07-01', 1.20, 2.30, 3.50, '{"categoria": "transporte", "tipo": "material"}'),
  ('73.201.001', 'Compactação de aterro em camadas', 'M³', 'SP', '2026-07-01', 2.00, 15.00, 18.00, '{"categoria": "terraplenagem", "tipo": "compactacao"}'),
  ('73.301.001', 'Base de brita', 'M³', 'SP', '2026-07-01', 45.00, 8.00, 5.00, '{"categoria": "pavimentacao", "tipo": "base"}'),
  ('73.302.001', 'Sub-base de brita', 'M³', 'SP', '2026-07-01', 40.00, 7.00, 4.50, '{"categoria": "pavimentacao", "tipo": "subbase"}'),
  ('73.401.001', 'Concreto simples usinado fck 20 MPa', 'M³', 'SP', '2026-07-01', 280.00, 120.00, 45.00, '{"categoria": "concreto", "tipo": "simples"}'),
  ('73.402.001', 'Concreto armado usinado fck 25 MPa', 'M³', 'SP', '2026-07-01', 320.00, 140.00, 50.00, '{"categoria": "concreto", "tipo": "armado"}'),
  ('73.501.001', 'Aço CA-50 para armadura', 'Kg', 'SP', '2026-07-01', 4.50, 1.20, 0.30, '{"categoria": "aco", "tipo": "ca50"}'),
  ('73.601.001', 'Forma de madeira para concreto', 'M²', 'SP', '2026-07-01', 18.00, 35.00, 2.00, '{"categoria": "forma", "tipo": "madeira"}'),
  ('73.701.001', 'CBUQ (Concreto Betuminoso Usinado a Quente)', 'M³', 'SP', '2026-07-01', 320.00, 45.00, 60.00, '{"categoria": "asfalto", "tipo": "cbuq"}'),
  ('73.702.001', 'Lançamento e compactação de CBUQ', 'M³', 'SP', '2026-07-01', 8.00, 65.00, 85.00, '{"categoria": "asfalto", "tipo": "lançamento"}'),
  ('73.801.001', 'Pintura de ligação com asfalto diluído', 'M²', 'SP', '2026-07-01', 2.50, 1.50, 0.50, '{"categoria": "asfalto", "tipo": "pintura"}'),
  ('73.901.001', 'Sinalização horizontal (faixa branca)', 'M', 'SP', '2026-07-01', 3.50, 2.00, 0.80, '{"categoria": "sinalizacao", "tipo": "horizontal"}'),
  ('74.001.001', 'Estrutura de aço perfil I', 'Kg', 'SP', '2026-07-01', 6.50, 1.80, 0.50, '{"categoria": "aco", "tipo": "estrutura"}'),
  ('74.101.001', 'Alvenaria de blocos cerâmicos 14x19x39', 'Un', 'SP', '2026-07-01', 1.20, 0.80, 0.10, '{"categoria": "alvenaria", "tipo": "blocos"}'),
  ('74.201.001', 'Revestimento de argamassa (chapisco + emboço)', 'M²', 'SP', '2026-07-01', 12.00, 45.00, 2.00, '{"categoria": "revestimento", "tipo": "argamassa"}'),
  ('74.301.001', 'Pintura PVA (2 demãos)', 'M²', 'SP', '2026-07-01', 8.00, 18.00, 1.00, '{"categoria": "pintura", "tipo": "pva"}'),
  ('74.401.001', 'Azulejo para cozinha/banheiro', 'M²', 'SP', '2026-07-01', 45.00, 32.00, 3.00, '{"categoria": "revestimento", "tipo": "azulejo"}'),
  ('74.501.001', 'Vidro comum liso 4mm', 'M²', 'SP', '2026-07-01', 35.00, 12.00, 2.00, '{"categoria": "vidro", "tipo": "comum"}'),
  ('75.001.001', 'Escada de concreto pré-moldado', 'M', 'SP', '2026-07-01', 150.00, 80.00, 25.00, '{"categoria": "pre_moldado", "tipo": "escada"}'),
  ('75.101.001', 'Laje pré-moldada com capa de concreto', 'M²', 'SP', '2026-07-01', 65.00, 40.00, 15.00, '{"categoria": "pre_moldado", "tipo": "laje"}'),
  ('76.001.001', 'Encanamento PVC ½ polegada', 'M', 'SP', '2026-07-01', 5.50, 2.00, 0.50, '{"categoria": "hidraulica", "tipo": "pvc"}'),
  ('76.101.001', 'Esquadria de alumínio (janela)', 'M²', 'SP', '2026-07-01', 180.00, 45.00, 8.00, '{"categoria": "esquadria", "tipo": "aluminio"}'),
  ('76.201.001', 'Porta de madeira (folha)', 'Un', 'SP', '2026-07-01', 85.00, 25.00, 5.00, '{"categoria": "porta", "tipo": "madeira"}')
ON CONFLICT (codigo) DO NOTHING;

-- Insert histórico de preços (últimos 3 meses)
INSERT INTO sicro_price_history (codigo, uf, periodo, custo_m, custo_mo, custo_eq, custo_total)
SELECT
  codigo,
  'SP' as uf,
  DATE_TRUNC('month', NOW() - INTERVAL '1 month')::date as periodo,
  custo_m * 0.95,
  custo_mo * 0.98,
  custo_eq * 0.97,
  (custo_m + custo_mo + custo_eq) * 0.97
FROM sicro_insumos
WHERE uf = 'SP'
ON CONFLICT DO NOTHING;

-- Insert histórico anterior (2 meses)
INSERT INTO sicro_price_history (codigo, uf, periodo, custo_m, custo_mo, custo_eq, custo_total)
SELECT
  codigo,
  'SP' as uf,
  DATE_TRUNC('month', NOW() - INTERVAL '2 months')::date as periodo,
  custo_m * 0.90,
  custo_mo * 0.93,
  custo_eq * 0.92,
  (custo_m + custo_mo + custo_eq) * 0.92
FROM sicro_insumos
WHERE uf = 'SP'
ON CONFLICT DO NOTHING;

-- Insert alguns itens obsoletos e mapeamento de migração
INSERT INTO sicro_migration_map (codigo_antigo, codigo_novo, motivo, data_migracao)
VALUES
  ('73.101.000', '73.101.001', 'Revisão de código SICRO 2025', '2025-01-15'),
  ('73.401.000', '73.401.001', 'Atualização de fck e especificação', '2025-02-20'),
  ('73.701.000', '73.701.001', 'Reclassificação de material', '2025-03-01')
ON CONFLICT (codigo_antigo) DO NOTHING;

-- Insert histórico de uso Manta (priors)
INSERT INTO manta_sicro_usage (codigo, projeto_id, frequency, score_uso)
SELECT
  codigo,
  CONCAT('proj-', SUBSTRING(codigo FROM 1 FOR 2), '-', FLOOR(RANDOM() * 999)::TEXT),
  FLOOR(1 + RANDOM() * 50)::INT,
  0.3 + RANDOM() * 0.7
FROM sicro_insumos
LIMIT 15
ON CONFLICT DO NOTHING;

-- Insert equivalências SICRO-SINAPI (exemplo)
INSERT INTO sicro_sinapi_equivalence (codigo_sicro, codigo_sinapi, descricao_sinapi, score_similaridade, confianca_equivalencia)
VALUES
  ('73.401.001', '93023', 'Concreto usinado, fck=25 mpa', 0.92, 0.88),
  ('73.701.001', '27001', 'CBUQ com agregado fino', 0.85, 0.80),
  ('74.201.001', '72420', 'Revestimento interno com argamassa', 0.88, 0.85)
ON CONFLICT DO NOTHING;

-- Insert normas técnicas
INSERT INTO sicro_normas (codigo_sicro, norma_id, norma_descricao, relevancia)
VALUES
  ('73.401.001', 'NBR 12655', 'Concreto — Preparo, controle e recebimento', 1),
  ('73.401.001', 'NBR 8953', 'Concreto para fins estruturais — Classificação por grupo de resistência', 1),
  ('73.701.001', 'NBR 12241', 'Asfalto diluído — Classificação', 1),
  ('74.101.001', 'NBR 15270', 'Blocos cerâmicos para alvenaria', 1),
  ('76.001.001', 'NBR 5648', 'Tubos de PVC rígido para uso hidráulico', 1)
ON CONFLICT (codigo_sicro, norma_id) DO NOTHING;
