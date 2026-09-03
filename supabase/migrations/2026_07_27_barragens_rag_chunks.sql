-- Manta Maestro v4.2 — criação de chunks RAG para Barragens (S10)
-- Ticket: MNT-2026-UPGRADE-AGENTS-S6S10
--
-- Este arquivo cria e popula a tabela rag_chunks para o segmento "barragens".
-- Os chunks são baseados nas fontes iniciais definidas em CLAUDE.md:
--   - ICOLD (International Commission on Large Dams)
--   - CBDB (Comitê Brasileiro de Barragens)
--   - SIGBM (Sistema de Informações de Barragens, ANM)
--   - SNISB (Sistema Nacional de Informações sobre Segurança de Barragens, ANA)
--   - Lei 12.334/2010 + Lei 14.066/2020
--   - NBR 13028, NBR 8681
--
-- Executar via:
--   supabase db push
-- ou
--   psql "$SUPABASE_DB_URL" -f supabase/migrations/2026_07_27_barragens_rag_chunks.sql

BEGIN;

-- =====================================================================
-- 1. Criar tabela rag_chunks (idempotente)
-- =====================================================================
-- Se a tabela já existe, o CREATE IF NOT EXISTS garante que não há erro.
-- Estrutura: id (UUID), segmento (text), prefix_storage (text),
--            titulo (text), conteudo (text), fonte (text),
--            criado_em (timestamptz), tokens (int, opcional)

CREATE TABLE IF NOT EXISTS public.rag_chunks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  segmento TEXT NOT NULL,
  prefix_storage TEXT NOT NULL,
  titulo TEXT NOT NULL,
  conteudo TEXT NOT NULL,
  fonte TEXT NOT NULL,
  criado_em TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  tokens INTEGER,
  metadata JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Criar índices para melhor performance
CREATE INDEX IF NOT EXISTS idx_rag_chunks_segmento ON public.rag_chunks(segmento);
CREATE INDEX IF NOT EXISTS idx_rag_chunks_prefix_storage ON public.rag_chunks(prefix_storage);
CREATE INDEX IF NOT EXISTS idx_rag_chunks_fonte ON public.rag_chunks(fonte);

-- =====================================================================
-- 2. Inserir chunks de exemplo para o segmento "barragens"
-- =====================================================================
-- Cada chunk representa um documento/seção de uma fonte de referência.
-- Os chunks cobrem as principais normas, legislação e organismos
-- reguladores do segmento de barragens no Brasil.

INSERT INTO public.rag_chunks
  (segmento, prefix_storage, titulo, conteudo, fonte, tokens)
VALUES
  -- Chunk 1: Lei 12.334/2010 (marco regulatório)
  (
    'barragens',
    'bar:',
    'Lei 12.334/2010 - Política Nacional de Segurança de Barragens',
    'A Lei nº 12.334, de 20 de setembro de 2010, institui a Política Nacional de Segurança de Barragens (PNSB) aplicável à segurança de barragens destinadas à acumulação de água para quaisquer usos, à disposição final ou temporária de rejeitos e à acumulação de resíduos industriais. A lei estabelece os critérios e procedimentos de segurança, fiscalização e controle de barragens por órgãos federais, estaduais e municipais. Define-se como barramento todo obstáculo colocado transversalmente ao leito de um rio para retenção de água, com altura do eixo da fundação ao coroamento maior ou igual a 15 metros ou com volume do reservatório maior ou igual a 3 hectares-metro (hm³).',
    'Lei 12.334/2010',
    285
  ),

  -- Chunk 2: Lei 14.066/2020 (complementação e rompimentos)
  (
    'barragens',
    'bar:',
    'Lei 14.066/2020 - Complementações à Política Nacional de Segurança de Barragens',
    'A Lei nº 14.066, de 30 de setembro de 2020, altera a Lei nº 12.334, de 2010, para aprimorar o marco legal de segurança de barragens. Inclui a responsabilidade dos operadores de barragens de rejeitos de mineração por rompimentos, estabelece protocolos de fiscalização mais rigorosos, amplia o escopo para barragens de disposição de resíduos industriais e prevê penalidades mais severas para não cumprimento das normas de segurança. A lei cria obrigações de monitoramento contínuo, elaboração de planos de ação de emergência e comunicação com comunidades potencialmente afetadas.',
    'Lei 14.066/2020',
    278
  ),

  -- Chunk 3: ICOLD - Relatórios técnicos internacionais
  (
    'barragens',
    'bar:',
    'ICOLD Bulletins - Padrões Internacionais de Barragens',
    'A International Commission on Large Dams (ICOLD), fundada em 1928, publica bulletins técnicos e guidelines que estabelecem os padrões internacionais para projeto, construção, operação e manutenção de grandes barragens. Os bulletins cobrem tópicos como: análise de risco, seepage control, instrumentação, drenagem, concreto em barragens, barragens de aterro, fundações e segurança sísmica. Os documentos da ICOLD são referência obrigatória em projetos de barragens de médio e grande porte, servindo como base para normalização em diversos países, incluindo o Brasil.',
    'ICOLD',
    268
  ),

  -- Chunk 4: CBDB e SIGBM (regulação brasileira)
  (
    'barragens',
    'bar:',
    'CBDB e SIGBM - Regulação e Fiscalização Brasileira de Barragens',
    'O Comitê Brasileiro de Barragens (CBDB) estabelece diretrizes técnicas para barragens no Brasil, enquanto o Sistema de Informações de Barragens (SIGBM), mantido pela Agência Nacional de Mineração (ANM), centraliza dados de barragens de rejeitos. O SIGBM é uma plataforma obrigatória para registro, monitoramento e reporte de dados técnicos de barragens de mineração. A legislação brasileira exige que operadores de barragens de rejeitos cumpram com regulações rigorosas de segurança, incluindo auditorias independentes anuais, planos de fechamento e provisões financeiras para garantia de segurança.',
    'CBDB / SIGBM / ANM',
    285
  ),

  -- Chunk 5: NBR 13028 e NBR 8681 (normas técnicas)
  (
    'barragens',
    'bar:',
    'NBR 13028 e NBR 8681 - Normas Técnicas ABNT para Barragens',
    'A NBR 13028:2017 especifica requisitos para segurança, projeto e construção de barragens de terra e enrocamento. A NBR 8681:2003 estabelece ações e segurança nas estruturas de concreto. Estas normas definem critérios de estabilidade, fatores de segurança, análise de fundações, instrumentação, inspeção e manutenção. As normas cobrem: análise de seepage, estabilidade de taludes, critérios de drenagem interna e externa, proteção contra erosão, monitoramento de deformações e pressões. Compliance com estas normas é obrigatório para barragens brasileiras e representa os melhores práticas internacionais adaptadas ao contexto local.',
    'NBR 13028:2017 / NBR 8681:2003',
    302
  )
ON CONFLICT DO NOTHING;

-- =====================================================================
-- 3. Validações pós-inserção
-- =====================================================================
-- Contar chunks inseridos para barragens
-- SELECT COUNT(*) FROM public.rag_chunks WHERE segmento = 'barragens';

COMMIT;

-- =====================================================================
-- ROLLBACK (executar manualmente se necessário)
-- =====================================================================
-- BEGIN;
-- DELETE FROM public.rag_chunks WHERE segmento = 'barragens';
-- COMMIT;
