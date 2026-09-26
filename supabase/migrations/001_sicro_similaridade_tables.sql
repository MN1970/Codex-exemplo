-- SICRO Similaridade Integration — Supabase Schema v1.0
-- Tables para busca, composição de preço e auditoria

-- 1. Índice principal SICRO
CREATE TABLE IF NOT EXISTS sicro_insumos (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  codigo VARCHAR(20) UNIQUE NOT NULL,
  descricao TEXT NOT NULL,
  unidade VARCHAR(10) NOT NULL,
  uf VARCHAR(2) NOT NULL,
  periodo DATE NOT NULL,
  custo_m DECIMAL(10, 2) COMMENT 'Material',
  custo_mo DECIMAL(10, 2) COMMENT 'Mão-de-obra',
  custo_eq DECIMAL(10, 2) COMMENT 'Equipamento',
  embedding vector(384),
  metadados JSONB DEFAULT '{}',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- 2. Histórico de preços SICRO (série temporal)
CREATE TABLE IF NOT EXISTS sicro_price_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  codigo VARCHAR(20) NOT NULL,
  uf VARCHAR(2) NOT NULL,
  periodo DATE NOT NULL,
  custo_m DECIMAL(10, 2),
  custo_mo DECIMAL(10, 2),
  custo_eq DECIMAL(10, 2),
  custo_total DECIMAL(10, 2),
  created_at TIMESTAMP DEFAULT NOW(),
  CONSTRAINT fk_codigo FOREIGN KEY (codigo) REFERENCES sicro_insumos(codigo) ON DELETE CASCADE
);

-- 3. Mapeamento de obsolescência e migração de códigos
CREATE TABLE IF NOT EXISTS sicro_migration_map (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  codigo_antigo VARCHAR(20) NOT NULL UNIQUE,
  codigo_novo VARCHAR(20) NOT NULL,
  motivo TEXT,
  data_migracao DATE NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  CONSTRAINT fk_codigo_novo FOREIGN KEY (codigo_novo) REFERENCES sicro_insumos(codigo) ON DELETE CASCADE
);

-- 4. Histórico de uso Manta (priors para RelevanceRanker)
CREATE TABLE IF NOT EXISTS manta_sicro_usage (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  codigo VARCHAR(20) NOT NULL,
  projeto_id VARCHAR(50),
  frequency INT DEFAULT 1,
  ultimo_uso TIMESTAMP DEFAULT NOW(),
  score_uso DECIMAL(3, 2) DEFAULT 0.5,
  created_at TIMESTAMP DEFAULT NOW(),
  CONSTRAINT fk_codigo FOREIGN KEY (codigo) REFERENCES sicro_insumos(codigo) ON DELETE CASCADE
);

-- 5. Equivalências SICRO ↔ SINAPI (benchmarking)
CREATE TABLE IF NOT EXISTS sicro_sinapi_equivalence (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  codigo_sicro VARCHAR(20) NOT NULL,
  codigo_sinapi VARCHAR(20),
  descricao_sinapi TEXT,
  score_similaridade DECIMAL(3, 2) COMMENT 'BM25+TF-IDF score',
  confianca_equivalencia DECIMAL(3, 2) COMMENT '0-1, banda de decisão',
  created_at TIMESTAMP DEFAULT NOW(),
  CONSTRAINT fk_codigo_sicro FOREIGN KEY (codigo_sicro) REFERENCES sicro_insumos(codigo) ON DELETE CASCADE
);

-- 6. Normas técnicas associadas (NBR, DNIT, ANAC, ABNT, etc)
CREATE TABLE IF NOT EXISTS sicro_normas (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  codigo_sicro VARCHAR(20) NOT NULL,
  norma_id VARCHAR(50) NOT NULL,
  norma_descricao TEXT,
  relevancia INT DEFAULT 1,
  created_at TIMESTAMP DEFAULT NOW(),
  CONSTRAINT fk_codigo_sicro FOREIGN KEY (codigo_sicro) REFERENCES sicro_insumos(codigo) ON DELETE CASCADE,
  UNIQUE(codigo_sicro, norma_id)
);

-- 7. Auditoria de buscas (para aluci-guard e análise de uso)
CREATE TABLE IF NOT EXISTS sicro_auditoria_busca (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  descricao_entrada TEXT NOT NULL,
  codigo_resultado VARCHAR(20),
  score_confianca DECIMAL(3, 2),
  banda_decisao VARCHAR(20),
  flags JSONB DEFAULT '{}',
  timestamp_busca TIMESTAMP DEFAULT NOW(),
  usuario VARCHAR(100),
  projeto_id VARCHAR(50)
);

-- Índices para performance
CREATE INDEX idx_sicro_codigo ON sicro_insumos(codigo);
CREATE INDEX idx_sicro_uf_periodo ON sicro_insumos(uf, periodo);
CREATE INDEX idx_sicro_embedding ON sicro_insumos USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX idx_price_history_codigo_uf_periodo ON sicro_price_history(codigo, uf, periodo);
CREATE INDEX idx_migration_map_antigo ON sicro_migration_map(codigo_antigo);
CREATE INDEX idx_migration_map_novo ON sicro_migration_map(codigo_novo);
CREATE INDEX idx_manta_usage_codigo ON manta_sicro_usage(codigo);
CREATE INDEX idx_manta_usage_projeto ON manta_sicro_usage(projeto_id);
CREATE INDEX idx_sinapi_equivalence_sicro ON sicro_sinapi_equivalence(codigo_sicro);
CREATE INDEX idx_normas_codigo ON sicro_normas(codigo_sicro);
CREATE INDEX idx_auditoria_timestamp ON sicro_auditoria_busca(timestamp_busca);
CREATE INDEX idx_auditoria_codigo ON sicro_auditoria_busca(codigo_resultado);

-- Views para consultas comuns
CREATE OR REPLACE VIEW sicro_precos_atuais AS
SELECT DISTINCT ON (s.codigo, s.uf)
  s.codigo,
  s.descricao,
  s.unidade,
  s.uf,
  s.custo_m,
  s.custo_mo,
  s.custo_eq,
  (s.custo_m + s.custo_mo + s.custo_eq) as custo_total,
  s.periodo,
  s.updated_at
FROM sicro_insumos s
ORDER BY s.codigo, s.uf, s.periodo DESC;

CREATE OR REPLACE VIEW sicro_com_historico AS
SELECT
  s.codigo,
  s.descricao,
  s.unidade,
  s.uf,
  s.custo_m as custo_m_atual,
  s.custo_mo as custo_mo_atual,
  s.custo_eq as custo_eq_atual,
  h.custo_total as custo_total_mes_anterior,
  ((s.custo_m + s.custo_mo + s.custo_eq) - h.custo_total) / h.custo_total * 100 as variacao_pct,
  s.periodo,
  h.periodo as periodo_anterior
FROM sicro_insumos s
LEFT JOIN sicro_price_history h ON s.codigo = h.codigo
  AND s.uf = h.uf
  AND h.periodo = DATE_TRUNC('month', s.periodo - INTERVAL '1 month')::date;
