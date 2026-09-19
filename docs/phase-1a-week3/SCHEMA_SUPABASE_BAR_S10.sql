/**
 * BARRAGENS S10 — SCHEMA SUPABASE PARA RAG INGESTION
 *
 * Week 3 Phase 1a — Lei 12.334/2010 + Lei 14.066/2020
 *
 * Estrutura:
 *   - Tabela: rag_chunks (chunks estruturados com metadados hierárquicos)
 *   - Prefix: "bar:" (Barragens)
 *   - Estratégia: Full-text search + vector embeddings (Phase 2)
 */

-- ============================================================================
-- CRIAÇÃO DA TABELA RAG_CHUNKS (Genérica para todos os segmentos)
-- ============================================================================

CREATE TABLE IF NOT EXISTS rag_chunks (
  -- Identificadores
  id TEXT PRIMARY KEY UNIQUE,           -- Format: "bar_L12334_0001" | "bar_L14066_0001" | "bar_L12334_CONS_0001"
  segmento TEXT NOT NULL,               -- "S6", "S7", "S8", "S9", "S10"
  prefixo TEXT NOT NULL DEFAULT 'bar',  -- "bar" para Barragens

  -- Documento/Lei
  lei_numero TEXT NOT NULL,             -- "12.334", "14.066"
  lei_titulo TEXT,                      -- "Lei de Segurança de Barragens"
  lei_data_sancao DATE,                 -- "2010-09-16"
  lei_data_vigencia DATE,               -- "2010-12-20" ou "2020-12-23"
  lei_numero_alterada TEXT,             -- Para Lei 14.066: "12.334" (qual lei foi alterada)

  -- Hierarquia Legislativa
  capitulo_numero INTEGER,              -- 1, 2, 3, 4
  capitulo_titulo TEXT,                 -- "Das Barragens e sua Classificação"
  secao_numero TEXT,                    -- "Seção I", "Seção II"
  secao_titulo TEXT,                    -- "Das Definições"
  artigo_numero INTEGER NOT NULL,       -- 1, 2, 3, ..., 35
  artigo_titulo TEXT,                   -- Alguns artigos têm títulos
  paragrafo_numero TEXT,                -- "1º", "2º", "1º-A"
  inciso_numero TEXT,                   -- "I", "II", "III"
  alinea_numero TEXT,                   -- "a", "b", "c"

  -- Tipo de Conteúdo
  categoria TEXT NOT NULL DEFAULT 'artigo',  -- "artigo", "paragrafo", "inciso", "alinea", "alteracao", "artigo_consolidado"
  tipo_alteracao TEXT,                  -- Para Lei 14.066: "modificacao", "adicao_paragrafo", "revogacao"
  artigo_original INTEGER,              -- Para Lei 14.066: qual artigo da Lei 12.334 foi alterado

  -- Conteúdo
  texto TEXT NOT NULL,                  -- Texto completo do chunk
  tamanho_chars INTEGER,                -- Número de caracteres
  tokens_estimado INTEGER,              -- Estimativa para Claude (4 chars/token)

  -- Rastreabilidade
  fonte TEXT DEFAULT 'planalto.gov.br', -- Fonte original
  versao_consolidada BOOLEAN DEFAULT FALSE,  -- Se incorpora alterações Lei 14.066
  tem_alteracoes BOOLEAN DEFAULT FALSE,      -- Se este artigo foi alterado
  alteracoes_lei TEXT,                       -- "14.066" se houve alteração

  -- Metadados e Controle
  criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  atualizado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  ativo BOOLEAN DEFAULT TRUE,

  -- Índices (ver abaixo)
  UNIQUE(lei_numero, artigo_numero, categoria, paragrafo_numero, inciso_numero)
);

-- ============================================================================
-- ÍNDICES PARA PERFORMANCE
-- ============================================================================

-- Índice full-text search (busca por palavras-chave)
CREATE INDEX idx_rag_chunks_fts ON rag_chunks USING GIN(
  to_tsvector('portuguese', texto)
);

-- Índices por coluna para filtros rápidos
CREATE INDEX idx_rag_chunks_lei_numero ON rag_chunks(lei_numero);
CREATE INDEX idx_rag_chunks_artigo_numero ON rag_chunks(artigo_numero);
CREATE INDEX idx_rag_chunks_categoria ON rag_chunks(categoria);
CREATE INDEX idx_rag_chunks_segmento ON rag_chunks(segmento);
CREATE INDEX idx_rag_chunks_capitulo ON rag_chunks(capitulo_numero);
CREATE INDEX idx_rag_chunks_versao_cons ON rag_chunks(versao_consolidada);
CREATE INDEX idx_rag_chunks_ativo ON rag_chunks(ativo);

-- Índice composto para queries hierárquicas
CREATE INDEX idx_rag_chunks_hierarquia ON rag_chunks(
  lei_numero,
  capitulo_numero,
  artigo_numero,
  paragrafo_numero,
  inciso_numero
);

-- Índice para rastreabilidade de alterações
CREATE INDEX idx_rag_chunks_alteracoes ON rag_chunks(
  lei_numero_alterada,
  artigo_original,
  tipo_alteracao
);

-- ============================================================================
-- TRIGGERS PARA AUDITORIA
-- ============================================================================

-- Atualizar campo atualizado_em automaticamente
CREATE OR REPLACE FUNCTION update_rag_chunks_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.atualizado_em = CURRENT_TIMESTAMP;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_rag_chunks_timestamp
BEFORE UPDATE ON rag_chunks
FOR EACH ROW
EXECUTE FUNCTION update_rag_chunks_timestamp();

-- ============================================================================
-- COMENTÁRIOS PARA DOCUMENTAÇÃO
-- ============================================================================

COMMENT ON TABLE rag_chunks IS
  'Tabela centralizada de chunks para RAG. Armazena fragmentos de documentos legislativos estruturados com metadados hierárquicos.';

COMMENT ON COLUMN rag_chunks.id IS
  'ID único no formato: prefixo_lei_numero (bar_L12334_0001). Identifica univocamente cada chunk.';

COMMENT ON COLUMN rag_chunks.lei_numero IS
  'Número da lei no formato DD.DDD (12.334, 14.066). Permite grouping e versionamento.';

COMMENT ON COLUMN rag_chunks.categoria IS
  'Tipo de elemento legislativo: "artigo" (padrão), "paragrafo" (§), "inciso" (I, II), "alinea" (a, b), "alteracao" (Lei 14.066)';

COMMENT ON COLUMN rag_chunks.versao_consolidada IS
  'TRUE se o chunk incorpora alterações Lei 14.066 (Lei 12.334 + Lei 14.066 merged).';

COMMENT ON COLUMN rag_chunks.tokens_estimado IS
  'Tokens aproximados (4 caracteres = 1 token). Usado para estimativa de custo LLM.';

-- ============================================================================
-- VIEWS ÚTEIS PARA QUERYS FREQUENTES
-- ============================================================================

-- View: Lei 12.334/2010 original (sem alterações)
CREATE OR REPLACE VIEW v_lei_12334_original AS
SELECT *
FROM rag_chunks
WHERE lei_numero = '12.334'
  AND versao_consolidada = FALSE
  AND categoria IN ('artigo', 'paragrafo', 'inciso')
  AND ativo = TRUE
ORDER BY artigo_numero,
  CASE WHEN paragrafo_numero IS NULL THEN 0 ELSE 1 END,
  COALESCE(paragrafo_numero, '');

-- View: Lei 12.334/2010 consolidada (com alterações Lei 14.066)
CREATE OR REPLACE VIEW v_lei_12334_consolidada AS
SELECT *
FROM rag_chunks
WHERE lei_numero = '12.334'
  AND versao_consolidada = TRUE
  AND categoria IN ('artigo_consolidado')
  AND ativo = TRUE
ORDER BY artigo_numero;

-- View: Alterações Lei 14.066/2020
CREATE OR REPLACE VIEW v_lei_14066_alteracoes AS
SELECT *
FROM rag_chunks
WHERE lei_numero = '14.066'
  AND categoria = 'alteracao'
  AND ativo = TRUE
ORDER BY artigo_original, tipo_alteracao;

-- View: Cross-reference (Lei 12.334 artigo + suas alterações Lei 14.066)
CREATE OR REPLACE VIEW v_cross_reference_alteracoes AS
SELECT
  orig.id AS id_lei_12334,
  orig.artigo_numero,
  orig.texto AS texto_original,
  COALESCE(alter.id, 'N/A') AS id_lei_14066,
  COALESCE(alter.texto, 'Sem alterações') AS alteracao,
  COALESCE(alter.tipo_alteracao, 'N/A') AS tipo_alteracao
FROM v_lei_12334_original orig
LEFT JOIN rag_chunks alter ON
  alter.lei_numero = '14.066'
  AND alter.artigo_original = orig.artigo_numero
  AND alter.ativo = TRUE
ORDER BY orig.artigo_numero;

-- ============================================================================
-- DADOS DE EXEMPLO (SEED DATA)
-- ============================================================================

-- Lei 12.334/2010 — Metadados
INSERT INTO rag_chunks (
  id, segmento, lei_numero, lei_titulo, lei_data_sancao, lei_data_vigencia,
  capitulo_numero, capitulo_titulo, artigo_numero, categoria, texto, tamanho_chars, tokens_estimado
) VALUES (
  'bar_L12334_meta',
  'S10',
  '12.334',
  'Lei de Segurança de Barragens',
  '2010-09-16',
  '2010-12-20',
  NULL,
  NULL,
  0,
  'metadados',
  'Lei nº 12.334, de 16 de setembro de 2010. Estabelece a Política Nacional de Segurança de Barragens destinadas à acumulação de água para quaisquer usos, à geração de energia elétrica e ao abatimento de cheias; cria o Sistema Nacional de Informações sobre Segurança de Barragens; altera a redação do art. 35 da Lei nº 9.433, de 8 de janeiro de 1997; e revoga a Lei nº 7.797, de 10 de julho de 1989, e suas alterações.',
  315,
  79
) ON CONFLICT(id) DO NOTHING;

-- Lei 14.066/2020 — Metadados
INSERT INTO rag_chunks (
  id, segmento, lei_numero, lei_numero_alterada, lei_titulo, lei_data_sancao, lei_data_vigencia,
  categoria, texto, tamanho_chars, tokens_estimado
) VALUES (
  'bar_L14066_meta',
  'S10',
  '14.066',
  '12.334',
  'Lei de Segurança de Barragens',
  '2020-10-02',
  '2020-12-23',
  'metadados_alteracao',
  'Lei nº 14.066, de 2 de outubro de 2020. Altera a Lei nº 12.334, de 16 de setembro de 2010, que estabelece a Política Nacional de Segurança de Barragens.',
  209,
  53
) ON CONFLICT(id) DO NOTHING;

-- ============================================================================
-- QUERIES DE TESTE
-- ============================================================================

/*
-- Busca por palavras-chave em português
SELECT id, artigo_numero, SUBSTRING(texto, 1, 100) as preview
FROM rag_chunks
WHERE to_tsvector('portuguese', texto) @@ to_tsquery('portuguese', 'barragem & segurança')
  AND ativo = TRUE
LIMIT 10;

-- Listar todos os artigos alterados pela Lei 14.066
SELECT DISTINCT artigo_original, tipo_alteracao, COUNT(*) as num_chunks
FROM v_cross_reference_alteracoes
WHERE id_lei_14066 != 'N/A'
GROUP BY artigo_original, tipo_alteracao;

-- Contar chunks por lei
SELECT lei_numero, categoria, COUNT(*) as total
FROM rag_chunks
WHERE ativo = TRUE
GROUP BY lei_numero, categoria
ORDER BY lei_numero, categoria;

-- Lei 12.334 consolidada — artigos com alterações
SELECT artigo_numero, artigo_titulo, tem_alteracoes, alteracoes_lei
FROM rag_chunks
WHERE versao_consolidada = TRUE
  AND tem_alteracoes = TRUE
  AND ativo = TRUE
ORDER BY artigo_numero;
*/

-- ============================================================================
-- GRANT PERMISSIONS (adaptado conforme autenticação)
-- ============================================================================

-- Se usar JWT/RLS (recomendado):
-- ALTER TABLE rag_chunks ENABLE ROW LEVEL SECURITY;
-- CREATE POLICY "read_public" ON rag_chunks FOR SELECT USING (ativo = TRUE);
-- CREATE POLICY "write_admin" ON rag_chunks FOR INSERT WITH CHECK (auth.role() = 'admin');
