-- Supabase DDL para tabela rag_chunks
-- Saneamento RAG (S8) — Lei 14.026, SNIS, e coleções futuras
-- Deploy: dev.supabase.co → public schema

BEGIN;

-- Tabela principal
CREATE TABLE IF NOT EXISTS public.rag_chunks (
  -- Identificadores
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  segmento TEXT NOT NULL,  -- 'S8-Saneamento', 'S6-Portos', etc.
  prefix TEXT NOT NULL DEFAULT 'san:',  -- storage prefix
  documento_id TEXT NOT NULL,  -- chave única dentro do segmento

  -- Sequência & Conteúdo
  chunk_seq INTEGER NOT NULL DEFAULT 0,  -- ordem no documento
  titulo TEXT,  -- nome do registro/artigo
  conteudo TEXT NOT NULL,  -- corpo (400-500 tokens)
  embedding_text TEXT,  -- para sentence-transformers (max 500 chars)

  -- Contexto estruturado
  metadata_json JSONB,  -- tipo, ano, estado, indicadores, estrutura legal, etc.

  -- Ciclo de vida
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  expires_at TIMESTAMP WITH TIME ZONE,  -- 30 dias para SNIS, NULL para legislação

  -- Auditoria
  created_by TEXT,  -- usuário que fez upload
  source_url TEXT,  -- origem (API endpoint ou arquivo)

  CONSTRAINT rag_chunks_documento_seq UNIQUE (documento_id, chunk_seq)
);

-- Índices para performance
CREATE INDEX idx_rag_chunks_segmento
  ON public.rag_chunks(segmento);

CREATE INDEX idx_rag_chunks_documento
  ON public.rag_chunks(documento_id);

CREATE INDEX idx_rag_chunks_prefix
  ON public.rag_chunks(prefix);

CREATE INDEX idx_rag_chunks_created_at
  ON public.rag_chunks(created_at DESC);

CREATE INDEX idx_rag_chunks_expires_at
  ON public.rag_chunks(expires_at)
  WHERE expires_at IS NOT NULL;

-- Índice fulltext (para busca de legislação)
CREATE INDEX idx_rag_chunks_conteudo_fts
  ON public.rag_chunks
  USING GIN (to_tsvector('portuguese', conteudo));

-- Índice JSONB (para consultas por metadados)
CREATE INDEX idx_rag_chunks_metadata
  ON public.rag_chunks
  USING GIN (metadata_json);

-- Tabela auxiliar: cadastro denormalizado SNIS
-- Otimiza consultas "qual a cobertura em X estado?" sem parsing JSONB
CREATE TABLE IF NOT EXISTS public.snis_cadastro (
  id UUID PRIMARY KEY,
  rag_chunk_id UUID NOT NULL REFERENCES public.rag_chunks(id) ON DELETE CASCADE,
  ano INTEGER NOT NULL,
  estado CHAR(2) NOT NULL,
  municipio TEXT NOT NULL,
  nome_prestador TEXT NOT NULL,
  cnpj VARCHAR(14),
  regime_prestacao TEXT,

  -- Indicadores principais
  populacao_atendida INTEGER,
  volume_faturado_m3 FLOAT8,
  tarifa_agua_r_per_m3 FLOAT8,
  indice_perda_pct FLOAT8,
  cobertura_agua_pct FLOAT8,
  cobertura_esgoto_pct FLOAT8,
  taxa_tratamento_esgoto_pct FLOAT8,

  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Índices para snis_cadastro
CREATE INDEX idx_snis_estado_ano
  ON public.snis_cadastro(estado, ano);

CREATE INDEX idx_snis_municipio
  ON public.snis_cadastro(municipio);

CREATE INDEX idx_snis_cnpj
  ON public.snis_cadastro(cnpj)
  WHERE cnpj IS NOT NULL;

-- RLS Policies (acesso público para leitura)
ALTER TABLE public.rag_chunks ENABLE ROW LEVEL SECURITY;

CREATE POLICY "rag_chunks_select_public"
  ON public.rag_chunks
  FOR SELECT
  USING (true);

CREATE POLICY "rag_chunks_insert_authenticated"
  ON public.rag_chunks
  FOR INSERT
  WITH CHECK (auth.role() = 'authenticated');

CREATE POLICY "rag_chunks_update_owner"
  ON public.rag_chunks
  FOR UPDATE
  USING (auth.uid()::text = created_by OR auth.role() = 'service_role')
  WITH CHECK (auth.uid()::text = created_by OR auth.role() = 'service_role');

ALTER TABLE public.snis_cadastro ENABLE ROW LEVEL SECURITY;

CREATE POLICY "snis_cadastro_select_public"
  ON public.snis_cadastro
  FOR SELECT
  USING (true);

-- Function: atualizar updated_at automaticamente
CREATE OR REPLACE FUNCTION public.update_rag_chunks_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER rag_chunks_updated_at
  BEFORE UPDATE ON public.rag_chunks
  FOR EACH ROW
  EXECUTE FUNCTION public.update_rag_chunks_updated_at();

-- Function: cleanup automático de chunks expirados
CREATE OR REPLACE FUNCTION public.cleanup_expired_rag_chunks()
RETURNS TABLE(deleted_count INTEGER) AS $$
DECLARE
  count INTEGER;
BEGIN
  DELETE FROM public.rag_chunks
  WHERE expires_at IS NOT NULL
    AND expires_at < now();

  GET DIAGNOSTICS count = ROW_COUNT;
  RETURN QUERY SELECT count;
END;
$$ LANGUAGE plpgsql;

-- Function: busca por indicadores SNIS
CREATE OR REPLACE FUNCTION public.search_snis_by_estado_indicador(
  p_estado CHAR(2),
  p_indicador TEXT,
  p_ano INTEGER DEFAULT 2024
)
RETURNS TABLE(
  nome_prestador TEXT,
  municipio TEXT,
  regime_prestacao TEXT,
  valor_indicador FLOAT8
) AS $$
BEGIN
  CASE p_indicador
    WHEN 'cobertura_agua' THEN
      RETURN QUERY
      SELECT s.nome_prestador, s.municipio, s.regime_prestacao, s.cobertura_agua_pct
      FROM public.snis_cadastro s
      WHERE s.estado = p_estado AND s.ano = p_ano
      ORDER BY s.cobertura_agua_pct DESC NULLS LAST;

    WHEN 'cobertura_esgoto' THEN
      RETURN QUERY
      SELECT s.nome_prestador, s.municipio, s.regime_prestacao, s.cobertura_esgoto_pct
      FROM public.snis_cadastro s
      WHERE s.estado = p_estado AND s.ano = p_ano
      ORDER BY s.cobertura_esgoto_pct DESC NULLS LAST;

    WHEN 'indice_perda' THEN
      RETURN QUERY
      SELECT s.nome_prestador, s.municipio, s.regime_prestacao, s.indice_perda_pct
      FROM public.snis_cadastro s
      WHERE s.estado = p_estado AND s.ano = p_ano
      ORDER BY s.indice_perda_pct ASC NULLS LAST;

    WHEN 'tarifa_agua' THEN
      RETURN QUERY
      SELECT s.nome_prestador, s.municipio, s.regime_prestacao, s.tarifa_agua_r_per_m3
      FROM public.snis_cadastro s
      WHERE s.estado = p_estado AND s.ano = p_ano
      ORDER BY s.tarifa_agua_r_per_m3 DESC NULLS LAST;

    ELSE
      RAISE EXCEPTION 'Indicador desconhecido: %', p_indicador;
  END CASE;
END;
$$ LANGUAGE plpgsql;

-- View: resumo SNIS por estado
CREATE OR REPLACE VIEW public.snis_resumo_estado AS
SELECT
  s.ano,
  s.estado,
  COUNT(DISTINCT s.nome_prestador) as qtd_prestadores,
  SUM(s.populacao_atendida) as populacao_total,
  AVG(s.cobertura_agua_pct) as cobertura_agua_media,
  AVG(s.cobertura_esgoto_pct) as cobertura_esgoto_media,
  AVG(s.indice_perda_pct) as indice_perda_media,
  AVG(s.tarifa_agua_r_per_m3) as tarifa_media
FROM public.snis_cadastro s
GROUP BY s.ano, s.estado
ORDER BY s.ano DESC, s.estado;

COMMIT;

-- ============================================================================
-- INSERTS INICIAIS (Demo data para Week 3)
-- ============================================================================

INSERT INTO public.rag_chunks (
  id, segmento, prefix, documento_id, chunk_seq, titulo, conteudo, metadata_json, embedding_text, created_at, expires_at
) VALUES
  (
    '5aac5b74-2c3a-bf83-10c5-ab4c8ab1a85c',
    'S8-Saneamento',
    'san:',
    'SNIS-2024',
    0,
    'SABESP (São Paulo, SP)',
    'Prestador: SABESP\nLocalização: São Paulo, SP\nCNPJ: 01631114000172\nRegime: Concessão\nAno de referência: 2024\n\nIndicadores SNIS:\n  - População atendida: 10.500.000\n  - Volume faturado: 1.150.000 m³\n  - Tarifa média água: R$ 3.50/m³\n  - Índice de perda: 30.2%\n  - Cobertura água: 99.5%\n  - Cobertura esgoto: 88.3%\n  - Taxa tratamento esgoto: 95.1%',
    '{"tipo": "SNIS_cadastro", "ano": 2024, "estado": "SP", "municipio": "São Paulo", "regime": "Concessão", "indicadores": {"populacao": 10500000, "volume_faturado_m3": 1150000.0, "tarifa_agua_r_per_m3": 3.5, "perda_pct": 30.2, "cobertura_agua_pct": 99.5, "cobertura_esgoto_pct": 88.3, "tratamento_esgoto_pct": 95.1}, "confianca": "official"}'::jsonb,
    'SABESP (São Paulo, SP) Prestador: SABESP. Localização: São Paulo, SP. CNPJ 01631114000172...',
    now(),
    now() + interval '30 days'
  ),
  (
    'b8f1e2a3-4c5d-6e7f-8a9b-0c1d2e3f4g5h',
    'S8-Saneamento',
    'san:',
    'LEI-14026-2020-LEI',
    0,
    'Lei 14.026/2020 — Capítulo 1 — Art. 1 (caput)',
    'Documento: Lei 14.026/2020\nCapítulo 1: Disposições Gerais\nArtigo 1: Art. 1\n\nEsta Lei estabelece diretrizes nacionais para o saneamento básico e para a política federal de saneamento básico, altera a Lei nº 9.984, de 17 de julho de 2000, para atribuir à Agência Nacional de Águas e Saneamento Básico (ANA) competência para editar normas de referência nacionais para o saneamento básico.',
    '{"tipo": "Lei_14026", "documento": "Lei 14.026/2020", "estrutura": {"capitulo": 1, "capitulo_nome": "Disposições Gerais", "artigo": 1, "artigo_titulo": "Art. 1", "paragrafo": null}, "confianca": "official"}'::jsonb,
    'Lei 14.026/2020 Capítulo 1 Art. 1 Esta Lei estabelece diretrizes nacionais para o saneamento básico...',
    now(),
    NULL
  )
ON CONFLICT (documento_id, chunk_seq) DO NOTHING;

INSERT INTO public.snis_cadastro (
  id, rag_chunk_id, ano, estado, municipio, nome_prestador, cnpj, regime_prestacao,
  populacao_atendida, volume_faturado_m3, tarifa_agua_r_per_m3, indice_perda_pct,
  cobertura_agua_pct, cobertura_esgoto_pct, taxa_tratamento_esgoto_pct
) VALUES
  (
    '6bbab885-3d4e-cf94-11d6-bc5d9f9b6d9e',
    '5aac5b74-2c3a-bf83-10c5-ab4c8ab1a85c',
    2024,
    'SP',
    'São Paulo',
    'SABESP',
    '01631114000172',
    'Concessão',
    10500000,
    1150000.0,
    3.50,
    30.2,
    99.5,
    88.3,
    95.1
  )
ON CONFLICT DO NOTHING;

-- ============================================================================
-- VIEWS & UTILITIES
-- ============================================================================

-- View: estatísticas RAG por documento
CREATE OR REPLACE VIEW public.rag_chunks_stats AS
SELECT
  segmento,
  documento_id,
  COUNT(*) as qtd_chunks,
  SUM(LENGTH(conteudo)) as bytes_total,
  MIN(created_at) as data_criacao,
  MAX(updated_at) as data_atualizacao,
  COUNT(CASE WHEN expires_at IS NOT NULL THEN 1 END) as chunks_com_expiracao
FROM public.rag_chunks
GROUP BY segmento, documento_id
ORDER BY segmento, documento_id;

-- View: chunks vencidos ou a vencer
CREATE OR REPLACE VIEW public.rag_chunks_expiring_soon AS
SELECT
  id,
  segmento,
  documento_id,
  titulo,
  expires_at,
  (expires_at - now())::text as tempo_restante
FROM public.rag_chunks
WHERE expires_at IS NOT NULL
  AND expires_at < now() + interval '3 days'
ORDER BY expires_at ASC;

GRANT SELECT ON ALL TABLES IN SCHEMA public TO anon, authenticated;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO anon, authenticated;
