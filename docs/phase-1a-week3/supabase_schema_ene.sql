-- ANEEL Editais RAG Schema (S9 - Energia)
-- Prefix: ene:
-- Table: rag_chunks

-- Main chunks table (shared across all segments)
-- Already exists, just add indexes for ene: prefix

CREATE INDEX IF NOT EXISTS idx_rag_chunks_ene_prefix
  ON rag_chunks(chunk_key)
  WHERE chunk_key ILIKE 'ene:%';

CREATE INDEX IF NOT EXISTS idx_rag_chunks_ene_edital
  ON rag_chunks USING GIN(metadata)
  WHERE metadata->>'source' = 'aneel_edital';

-- Metadata structure for ANEEL editais
/*
metadata: {
  "source": "aneel_edital",
  "edital_id": "EDITAL-2024-001",
  "data_publicacao": "2024-01-15",
  "tipo_licitacao": "LT",  // "LT" | "Subestação" | "Ambos"
  "tensao_kv": 345,
  "regiao": "Sudeste",  // "Norte" | "Nordeste" | "Centro-Oeste" | "Sudeste" | "Sul"
  "empresas_interessadas": ["Empresa A", "Empresa B"],
  "valor_estimado_r": 150000000,
  "cronograma": {
    "data_edital": "2024-01-15",
    "encerramento_consulta": "2024-02-15",
    "resultado_julgamento": "2024-06-15",
    "data_concessao": "2024-07-15"
  },
  "secao_tipo": "sumario|requisitos|cronograma|documentacao|penalidades",
  "paginas": "15-17",
  "pdf_url": "https://dadosabertos.aneel.gov.br/.../edital-2024-001.pdf",
  "quality_metrics": {
    "ocr_quality": 0.95,
    "text_extraction_confidence": 0.92,
    "parsing_completeness": 0.88
  }
}
*/

-- Example queries:
-- 1. Find all chunks for a specific edital
SELECT chunk_key, content
FROM rag_chunks
WHERE metadata->>'edital_id' = 'EDITAL-2024-001'
ORDER BY metadata->>'secao_tipo', chunk_key;

-- 2. Find editais by region
SELECT DISTINCT metadata->>'edital_id', metadata->>'data_publicacao'
FROM rag_chunks
WHERE metadata->>'source' = 'aneel_edital'
  AND metadata->>'regiao' = 'Sudeste'
ORDER BY metadata->>'data_publicacao' DESC;

-- 3. Find editais by tension and type
SELECT DISTINCT
  metadata->>'edital_id',
  metadata->>'tipo_licitacao',
  metadata->>'tensao_kv'
FROM rag_chunks
WHERE metadata->>'source' = 'aneel_edital'
  AND (metadata->>'tipo_licitacao' = 'LT' OR metadata->>'tipo_licitacao' = 'Ambos')
  AND (metadata->>'tensao_kv')::integer >= 345
ORDER BY metadata->>'data_publicacao' DESC;

-- 4. Find chunks by section type (for RAG retrieval)
SELECT chunk_key, content, metadata
FROM rag_chunks
WHERE metadata->>'source' = 'aneel_edital'
  AND metadata->>'secao_tipo' = 'requisitos'
  AND metadata->>'tensao_kv' = '345'
ORDER BY chunk_key;

-- 5. Quality metrics for QA
SELECT
  COUNT(*) as total_chunks,
  COUNT(DISTINCT metadata->>'edital_id') as unique_editais,
  ROUND(AVG((metadata->'quality_metrics'->>'ocr_quality')::float)::numeric, 3) as avg_ocr_quality,
  ROUND(AVG((metadata->'quality_metrics'->>'text_extraction_confidence')::float)::numeric, 3) as avg_extraction_confidence
FROM rag_chunks
WHERE metadata->>'source' = 'aneel_edital';

-- Key chunk naming convention:
-- ene:EDITAL-2024-001:sumario:001
-- ene:EDITAL-2024-001:requisitos:001
-- ene:EDITAL-2024-001:cronograma:001
-- ene:EDITAL-2024-001:documentacao:001
-- ene:EDITAL-2024-001:penalidades:001
