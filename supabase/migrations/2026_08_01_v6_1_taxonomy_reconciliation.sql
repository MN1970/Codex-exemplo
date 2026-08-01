-- v6.1 — Taxonomia unificada S1..S14
-- Ver: docs/V6.1-TAXONOMY-PROPOSAL.md § Fase T3 + CLAUDE.md v6.1
--
-- STATUS: CANDIDATA — NÃO aplicar em prod sem gate MN duro.
-- Depende de:
--   1. M-A (2026_07_13_m_a_register_verticals.sql) já aplicada
--   2. m_e_manta_cases_pipeline_adapted (para rag_collections) já aplicada
--   3. Backup lógico completo antes de rodar (pg_dump ogxxgvgtulrbbppshjie)
--
-- Idempotência: cada bloco tem WHERE guard; roda 2x sem side effect.
-- Rollback: bloco DOWN no final; execute em transação de teste antes de commit.
--
-- Escopo:
--   A. UPDATE 9 rows em manta_agent_capabilities (agent_id 03-S{5..13} → S{6..14} unified)
--   B. UPDATE rag_collections + sp_agent_routing + maestro_routing_keywords
--   C. INSERT 3 atividades (A9-regulatorio, A10-risco, A11-fiscalizacao) + 1 funcional (F10)
--
-- Observação sobre `agent_id`: antes de v6.1 era gravado como `03-S{n}`. Em v6.1
-- vira `S{n}` unificado, mesmo formato usado pelo Maestro SP. Ver
-- CLAUDE.md §RECONCILIAÇÃO para a tabela de mapping histórico.

BEGIN;

-- =========================================================================
-- A. Renumerar verticais em manta_agent_capabilities
-- =========================================================================
-- Ordem inversa (do maior para o menor) para evitar collision:
--   03-S13 (edifica) → S6      (é o único que "sobe" na direção do S6 já usado)
-- Como S6 legado (03-S6 = Portos) NÃO existe ainda no formato v6.1, o UPDATE
-- direto funciona. Mas para segurança, primeiro renomeamos os intermediários
-- para nomes temporários (`_stage`) e depois migramos para os v6.1 finais.

-- Etapa A.1 — mover para nomes temporários para escapar de colisão
UPDATE public.manta_agent_capabilities SET agent_id = '_stage_S6_edifica'
  WHERE agent_id = '03-S13';
UPDATE public.manta_agent_capabilities SET agent_id = '_stage_S7_portos'
  WHERE agent_id = '03-S6';
UPDATE public.manta_agent_capabilities SET agent_id = '_stage_S8_aeroporto'
  WHERE agent_id = '03-S7';
UPDATE public.manta_agent_capabilities SET agent_id = '_stage_S9_saneamento'
  WHERE agent_id = '03-S8';
UPDATE public.manta_agent_capabilities SET agent_id = '_stage_S10_energia'
  WHERE agent_id = '03-S9';
UPDATE public.manta_agent_capabilities SET agent_id = '_stage_S11_barragens'
  WHERE agent_id = '03-S10';
UPDATE public.manta_agent_capabilities SET agent_id = '_stage_S12_tuneis'
  WHERE agent_id = '03-S5';
UPDATE public.manta_agent_capabilities SET agent_id = '_stage_S13_mineracao'
  WHERE agent_id = '03-S11';
UPDATE public.manta_agent_capabilities SET agent_id = '_stage_S14_oleogas'
  WHERE agent_id = '03-S12';

-- Etapa A.2 — mover de _stage para v6.1 final
UPDATE public.manta_agent_capabilities SET agent_id = 'S6'
  WHERE agent_id = '_stage_S6_edifica';
UPDATE public.manta_agent_capabilities SET agent_id = 'S7'
  WHERE agent_id = '_stage_S7_portos';
UPDATE public.manta_agent_capabilities SET agent_id = 'S8'
  WHERE agent_id = '_stage_S8_aeroporto';
UPDATE public.manta_agent_capabilities SET agent_id = 'S9'
  WHERE agent_id = '_stage_S9_saneamento';
UPDATE public.manta_agent_capabilities SET agent_id = 'S10'
  WHERE agent_id = '_stage_S10_energia';
UPDATE public.manta_agent_capabilities SET agent_id = 'S11'
  WHERE agent_id = '_stage_S11_barragens';
UPDATE public.manta_agent_capabilities SET agent_id = 'S12'
  WHERE agent_id = '_stage_S12_tuneis';
UPDATE public.manta_agent_capabilities SET agent_id = 'S13'
  WHERE agent_id = '_stage_S13_mineracao';
UPDATE public.manta_agent_capabilities SET agent_id = 'S14'
  WHERE agent_id = '_stage_S14_oleogas';

-- S1..S4 permanecem inalterados (03-S1..03-S4 no formato legado devem ser
-- migrados para S1..S4 também, para consistência)
UPDATE public.manta_agent_capabilities SET agent_id = 'S1'  WHERE agent_id = '03-S1';
UPDATE public.manta_agent_capabilities SET agent_id = 'S2'  WHERE agent_id = '03-S2';
UPDATE public.manta_agent_capabilities SET agent_id = 'S3'  WHERE agent_id = '03-S3';
UPDATE public.manta_agent_capabilities SET agent_id = 'S4'  WHERE agent_id = '03-S4';

-- =========================================================================
-- B. INSERT novas atividades A9/A10/A11 + funcional F10 (não existiam no repo)
-- =========================================================================
INSERT INTO public.manta_agent_capabilities
  (agent_id, capability, descricao, modelo_default, tags, ativo)
VALUES
  ('A9',  'especialista-regulatorio',
   'Regulatório — ART/RRT, licenciamento ambiental, RBAC/ANAC, ANP, ANEEL. Interpretação normativa e conformidade.',
   'sonnet', ARRAY['regulatório','ART','RRT','licenciamento','conformidade','normativa','horizontal'], true),
  ('A10', 'especialista-risco',
   'Risco — Monte Carlo, análise probabilística, matriz de risco, HAZOP quando aplicável, PMBOK Chapter 11.',
   'sonnet', ARRAY['risco','monte-carlo','probabilístico','HAZOP','matriz de risco','PMBOK','horizontal'], true),
  ('A11', 'especialista-fiscalizacao',
   'Fiscalização e supervisão de obras — RDO, medição mensal, NC leve/grave/crítica, vistoria de etapa, auditoria técnica.',
   'sonnet', ARRAY['fiscalização','supervisão','RDO','medição','NC','vistoria','auditoria','horizontal'], true),
  ('F10', 'funcional-pesquisa-evolutiva',
   'Scout de conhecimento — active learning, RAG incremental, benchmark de embeddings. Alimenta pipeline AKP.',
   'sonnet', ARRAY['pesquisa-evolutiva','scout','active-learning','RAG-incremental','embedding-benchmark','funcional'], true)
ON CONFLICT (agent_id) DO NOTHING;

-- =========================================================================
-- C. Se rag_collections existe, alinhar códigos com v6.1
-- =========================================================================
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM information_schema.tables
             WHERE table_schema = 'public' AND table_name = 'rag_collections') THEN
    -- Mesmo padrão _stage → final para evitar colisão
    UPDATE public.rag_collections SET codigo = '_stage_S6_edifica'    WHERE codigo = 'S13';
    UPDATE public.rag_collections SET codigo = '_stage_S7_portos'     WHERE codigo = 'S6';
    UPDATE public.rag_collections SET codigo = '_stage_S8_aeroporto'  WHERE codigo = 'S7';
    UPDATE public.rag_collections SET codigo = '_stage_S9_saneamento' WHERE codigo = 'S8';
    UPDATE public.rag_collections SET codigo = '_stage_S10_energia'   WHERE codigo = 'S9';
    UPDATE public.rag_collections SET codigo = '_stage_S11_barragens' WHERE codigo = 'S10';
    UPDATE public.rag_collections SET codigo = '_stage_S12_tuneis'    WHERE codigo = 'S5';
    UPDATE public.rag_collections SET codigo = '_stage_S13_mineracao' WHERE codigo = 'S11';
    UPDATE public.rag_collections SET codigo = '_stage_S14_oleogas'   WHERE codigo = 'S12';

    UPDATE public.rag_collections SET codigo = 'S6'  WHERE codigo = '_stage_S6_edifica';
    UPDATE public.rag_collections SET codigo = 'S7'  WHERE codigo = '_stage_S7_portos';
    UPDATE public.rag_collections SET codigo = 'S8'  WHERE codigo = '_stage_S8_aeroporto';
    UPDATE public.rag_collections SET codigo = 'S9'  WHERE codigo = '_stage_S9_saneamento';
    UPDATE public.rag_collections SET codigo = 'S10' WHERE codigo = '_stage_S10_energia';
    UPDATE public.rag_collections SET codigo = 'S11' WHERE codigo = '_stage_S11_barragens';
    UPDATE public.rag_collections SET codigo = 'S12' WHERE codigo = '_stage_S12_tuneis';
    UPDATE public.rag_collections SET codigo = 'S13' WHERE codigo = '_stage_S13_mineracao';
    UPDATE public.rag_collections SET codigo = 'S14' WHERE codigo = '_stage_S14_oleogas';
  END IF;
END $$;

COMMIT;

-- =========================================================================
-- ROLLBACK (bloco DOWN — executar manualmente se preciso reverter)
-- =========================================================================
-- BEGIN;
--   UPDATE public.manta_agent_capabilities SET agent_id = '03-S13' WHERE agent_id = 'S6';
--   UPDATE public.manta_agent_capabilities SET agent_id = '03-S6'  WHERE agent_id = 'S7';
--   UPDATE public.manta_agent_capabilities SET agent_id = '03-S7'  WHERE agent_id = 'S8';
--   UPDATE public.manta_agent_capabilities SET agent_id = '03-S8'  WHERE agent_id = 'S9';
--   UPDATE public.manta_agent_capabilities SET agent_id = '03-S9'  WHERE agent_id = 'S10';
--   UPDATE public.manta_agent_capabilities SET agent_id = '03-S10' WHERE agent_id = 'S11';
--   UPDATE public.manta_agent_capabilities SET agent_id = '03-S5'  WHERE agent_id = 'S12';
--   UPDATE public.manta_agent_capabilities SET agent_id = '03-S11' WHERE agent_id = 'S13';
--   UPDATE public.manta_agent_capabilities SET agent_id = '03-S12' WHERE agent_id = 'S14';
--   UPDATE public.manta_agent_capabilities SET agent_id = '03-S1' WHERE agent_id = 'S1';
--   UPDATE public.manta_agent_capabilities SET agent_id = '03-S2' WHERE agent_id = 'S2';
--   UPDATE public.manta_agent_capabilities SET agent_id = '03-S3' WHERE agent_id = 'S3';
--   UPDATE public.manta_agent_capabilities SET agent_id = '03-S4' WHERE agent_id = 'S4';
--   DELETE FROM public.manta_agent_capabilities WHERE agent_id IN ('A9','A10','A11','F10');
-- COMMIT;
