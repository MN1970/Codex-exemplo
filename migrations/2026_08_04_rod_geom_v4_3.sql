-- Migration: Consolidação Fase I — Geometria de Rodovias (v4.3)
-- Date: 2026-08-04
-- Description: Insere documentação de geometria em Supabase RAG
-- Agente: Manta 03-S1 (agente-infraestrutura)
-- Collection: rodovias (prefix: rod:geom:*)

BEGIN;

-- Criar coleção se não existir
INSERT INTO rag_collections (name, prefix, description, version)
VALUES (
  'rodovias',
  'rod:',
  'Conhecimento técnico de projetos rodoviários (geometria, pavimentação, terraplenagem, drenagem, O&M)',
  '4.3'
)
ON CONFLICT (name) DO UPDATE SET version = '4.3';

-- Doc 00: Índice Maestro
INSERT INTO rag_chunks (
  collection_id,
  prefix,
  chunk_id,
  title,
  content,
  document_source,
  sequence_order,
  tags,
  created_at,
  updated_at
) VALUES (
  (SELECT id FROM rag_collections WHERE name = 'rodovias'),
  'rod:geom:indice',
  'chunk_00_maestro_001',
  'Índice Maestro — Geometria de Rodovias v4.3',
  'Estrutura de conhecimento com 20 tópicos especializados. Cobertura: normas DNIT, elementos geométricos, cálculos práticos, softwares (MX Road, Civil 3D), SICRO, drone mapping, interseções, drenagem, segurança, testes, reabilitação, integração Manta, templates, roadmap futuro. Total: 9 documentos consolidados, 20 agentes Sonnet, ~12k linhas de documentação. Status: Fase I completa, pronta para Fase II.',
  '00-indice-maestro.md',
  1,
  ARRAY['indice', 'estrutura', 'v4.3', 'maestro'],
  NOW(),
  NOW()
);

-- Doc 01: Elementos Geométricos
INSERT INTO rag_chunks (
  collection_id,
  prefix,
  chunk_id,
  title,
  content,
  document_source,
  sequence_order,
  tags,
  created_at,
  updated_at
) VALUES (
  (SELECT id FROM rag_collections WHERE name = 'rodovias'),
  'rod:geom:h',
  'chunk_01_elementos_h_001',
  'Alinhamento Horizontal — Conceitos Fundamentais',
  'Componentes: retas, arcos, transições com clotóide. Raio mínimo por velocidade: Vd=80→R_mín=220m, Vd=100→R_mín=340m. Superelevação máxima: e_máx=7% (federal/estadual). Fórmula: R_mín=V²/(127×(e+f)). Tabelas DNIT ES 101/97 para todas as velocidades. Visibilidade garantida em curva. Comprimento mínimo reta: 4×Vd (segundos).',
  '01-elementos-geometricos.md',
  1,
  ARRAY['alinhamento', 'horizontal', 'raio', 'superelevacao', 'elementos'],
  NOW(),
  NOW()
);

INSERT INTO rag_chunks (
  collection_id,
  prefix,
  chunk_id,
  title,
  content,
  document_source,
  sequence_order,
  tags,
  created_at,
  updated_at
) VALUES (
  (SELECT id FROM rag_collections WHERE name = 'rodovias'),
  'rod:geom:v',
  'chunk_01_elementos_v_001',
  'Alinhamento Vertical — Parábolas e Frenagem',
  'Componentes: rampas (i_máx=6-10% conforme Vd), curvas parabólicas (côncavas e convexas). Raio vertical mínimo: Kv_mín. Distância de parada: D=V²/(254×(f+i)). Fórmula parabólica: y=x²/(2R). Exemplo: Vd=100→D≈137m. Critério de visibilidade: deve-se enxergar objeto a 0.6m a distância D. Inclinações máximas por velocidade.',
  '01-elementos-geometricos.md',
  2,
  ARRAY['alinhamento', 'vertical', 'parábola', 'frenagem', 'visibilidade'],
  NOW(),
  NOW()
);

INSERT INTO rag_chunks (
  collection_id,
  prefix,
  chunk_id,
  title,
  content,
  document_source,
  sequence_order,
  tags,
  created_at,
  updated_at
) VALUES (
  (SELECT id FROM rag_collections WHERE name = 'rodovias'),
  'rod:geom:seção',
  'chunk_01_elementos_secao_001',
  'Seção Transversal — Largura, Taludes, Drenagem',
  'Componentes: eixo (referência), faixas de rolamento (3.3-3.75m cada), acostamentos (2-2.5m), taludes (corte/aterro). Declividade transversal: 2-3% (para drenar). Inclinação talude em corte: 1:1 (H<5m), 1:1.5 (H=5-10m), 1:2+ (H>10m). Inclinação talude em aterro: 1:1.5 (granular), 1:2 (coesivo). Banqueta de corte: 5m altura máxima, 2-4m largura. Drenagem integrada em pé de talude.',
  '01-elementos-geometricos.md',
  3,
  ARRAY['seção', 'transversal', 'taludes', 'banqueta', 'drenagem'],
  NOW(),
  NOW()
);

-- Doc 02: Cálculos Práticos
INSERT INTO rag_chunks (
  collection_id,
  prefix,
  chunk_id,
  title,
  content,
  document_source,
  sequence_order,
  tags,
  created_at,
  updated_at
) VALUES (
  (SELECT id FROM rag_collections WHERE name = 'rodovias'),
  'rod:geom:cálculos',
  'chunk_02_calc_001',
  'Caso 1: BR Federal Vd=100 — Cálculos Passo-a-Passo',
  'Rodovia: BR federal, topografia plana, VDM=2000 veículos/dia. Geometria: Vd=100→R_mín=340m, e_máx=7%, Kv_mín=80m. Exemplo curva: R=500m, e=4.7%, L_clotóide=110m. Distância parada: D=137m, f_banqueta=4.7m. Pavimento: CBUQ 5cm + BGS 15cm. Orçamento: ~R$95/m² (CBUQ)=R$685k/km, total ~R$5.2M/km incluindo terraplenagem/drenagem.',
  '02-calculos-praticos.md',
  1,
  ARRAY['cálculos', 'caso', 'br', 'vd100', 'orçamento'],
  NOW(),
  NOW()
);

-- Doc 03: Softwares
INSERT INTO rag_chunks (
  collection_id,
  prefix,
  chunk_id,
  title,
  content,
  document_source,
  sequence_order,
  tags,
  created_at,
  updated_at
) VALUES (
  (SELECT id FROM rag_collections WHERE name = 'rodovias'),
  'rod:geom:softwares',
  'chunk_03_softwares_001',
  'MX Road — Fluxo de Trabalho para Projeto Geométrico',
  'Software 3D para projeto geométrico de rodovias. Workflow: (1) Importar topografia (LAS/DXF), (2) Desenhar alinhamento H, (3) Definir alinhamento V (greide), (4) Seções transversais automáticas, (5) Gerar volumes/relatórios. Macros: superelevação automática (ES 101/97), banquetas de corte, relatórios DNIT. Saída: planta, perfil, seções, memoriais. Tempo: topografia→projeto básico ~2-3 semanas.',
  '03-softwares-referencias.md',
  1,
  ARRAY['software', 'mxroad', 'automação', 'projeto'],
  NOW(),
  NOW()
);

-- Doc 05: Normas DNIT
INSERT INTO rag_chunks (
  collection_id,
  prefix,
  chunk_id,
  title,
  content,
  document_source,
  sequence_order,
  tags,
  created_at,
  updated_at
) VALUES (
  (SELECT id FROM rag_collections WHERE name = 'rodovias'),
  'rod:geom:normas',
  'chunk_05_normas_001',
  'DNIT ES 101/97 — Norma de Projeto Geométrico',
  'Norma fundamental para projeto de rodovias brasileiras. Seções: (1) Definições, (2) Velocidade de projeto, (3) Elementos geométricos, (4) Alinhamento horizontal, (5) Alinhamento vertical, (6) Seção transversal, (7) Interseções. Tabelas: raio mínimo por Vd, superelevação máxima, comprimento mínimo retas, Kv mínimo. Checklist de conformidade obrigatória antes de aprovação executiva.',
  '05-normas-dnit-brasileiras.md',
  1,
  ARRAY['normas', 'dnit', 'es101', 'referência'],
  NOW(),
  NOW()
);

-- Doc 06: Interseções
INSERT INTO rag_chunks (
  collection_id,
  prefix,
  chunk_id,
  title,
  content,
  document_source,
  sequence_order,
  tags,
  created_at,
  updated_at
) VALUES (
  (SELECT id FROM rag_collections WHERE name = 'rodovias'),
  'rod:geom:intersecoes',
  'chunk_06_intersecoes_001',
  'Rotatória — Dimensionamento e Desempenho',
  'Tipo de interseção em nível com circulação contínua. Dimensões típicas: R_ext=25-40m, R_int=12-15m, largura faixa=3.5-4.5m. Cálculo: capacidade em função de R, número de faixas, tráfego. Vantagem: reduz velocidade, menor custo que desnível. Desvantagem: não adequada para tráfego muito alto (>3000 veículos/hora). Aplicação: interseções municipais, rodovias estaduais.',
  '06-intersecoes-dispositivos-seguranca.md',
  1,
  ARRAY['interseções', 'rotatória', 'dimensionamento', 'capacidade'],
  NOW(),
  NOW()
);

-- Doc 07: Balanço de Massa
INSERT INTO rag_chunks (
  collection_id,
  prefix,
  chunk_id,
  title,
  content,
  document_source,
  sequence_order,
  tags,
  created_at,
  updated_at
) VALUES (
  (SELECT id FROM rag_collections WHERE name = 'rodovias'),
  'rod:geom:bruckner',
  'chunk_07_bruckner_001',
  'Diagrama de Brückner — Otimização de Transporte Terra',
  'Técnica de otimização para minimizar custo de movimento terra. Método: (1) Calcular volume acumulado por seção, (2) Plotar em diagrama (abcissas=estacionamento, ordenadas=volume acumulado), (3) Ler linhas de compensação (deslocamento horizontal mínimo). Free Haul Distance (FHD): distância onde custo transporte=escavação. Exemplo: se FHD=100m, volumes com d<100m compensam localmente; d>100m buscam borrow areas. Python script disponível para automação.',
  '07-balanço-massa-movimento-terra.md',
  1,
  ARRAY['bruckner', 'otimização', 'terraplenagem', 'fhd'],
  NOW(),
  NOW()
);

-- Doc 08: Especializações
INSERT INTO rag_chunks (
  collection_id,
  prefix,
  chunk_id,
  title,
  content,
  document_source,
  sequence_order,
  tags,
  created_at,
  updated_at
) VALUES (
  (SELECT id FROM rag_collections WHERE name = 'rodovias'),
  'rod:geom:especializacoes',
  'chunk_08_especial_001',
  'Especializações Paralelas — 20 Agentes Sonnet Consolidados',
  '20 tópicos especializados: (1) Normas DNIT ES 101/97, (2) Curvas horizontais avançadas (clotóides duplas, espirais), (3) Superelevação (3 métodos), (4) Visibilidade 3D, (5) Alinhamento vertical, (6) Seção transversal avançada, (7) Pavimentação, (8) Casos reais (BR-116, BR-101, BR-163), (9) MX Road, (10) Civil 3D, (11) SICRO, (12) Drone mapping, (13) Interseções, (14) Drenagem, (15) Segurança, (16) Testes Python, (17) Reabilitação, (18) Integração agente, (19) Templates, (20) Roadmap ML/otimização.',
  '08-especializacoes-paralelas.md',
  1,
  ARRAY['especializações', 'consolidação', 'workflow', 'agentes'],
  NOW(),
  NOW()
);

-- Criar índices para otimizar busca
CREATE INDEX IF NOT EXISTS idx_rag_chunks_prefix ON rag_chunks(prefix);
CREATE INDEX IF NOT EXISTS idx_rag_chunks_collection_id ON rag_chunks(collection_id);
CREATE INDEX IF NOT EXISTS idx_rag_chunks_tags ON rag_chunks USING GIN(tags);

-- Validação final
SELECT
  (SELECT COUNT(*) FROM rag_chunks WHERE prefix LIKE 'rod:geom:%') as total_geom_chunks,
  (SELECT COUNT(DISTINCT prefix) FROM rag_chunks WHERE prefix LIKE 'rod:geom:%') as unique_prefixes,
  (SELECT version FROM rag_collections WHERE name = 'rodovias') as collection_version;

COMMIT;

-- Summary:
-- ✅ Criada coleção 'rodovias' (v4.3)
-- ✅ Inseridos 8 documentos principais
-- ✅ Sub-prefixos: rod:geom:h, rod:geom:v, rod:geom:seção, rod:geom:cálculos, rod:geom:softwares, rod:geom:normas, rod:geom:intersecoes, rod:geom:bruckner, rod:geom:especializacoes
-- ✅ Criados índices para otimizar retrieval
-- Próximas migrações: rod:pav:*, rod:terra:*, rod:dren:*, rod:om:* (Fase II)
