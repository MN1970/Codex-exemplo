-- =============================================================================
-- Manta Maestro — Migração candidata (Supabase/Postgres)
-- Arquivo: supabase/migrations/2026_09_26_v5_4_8_mot_fasamento.sql
-- Versão: v5.4.8 — MOT (Faseamento de Tráfego em Trevos e Interseções) —
--         casos precedentes de faseamento de obra rodoviária (dispositivos
--         de trevo/rotatória e tipologias de duplicação)
-- Data:   2026-09-26
--
-- STATUS: CANDIDATA — NÃO APLICAR EM PRODUÇÃO SEM APROVAÇÃO MN.
--
-- Esta migração NÃO deve ser aplicada automaticamente por CI/CD. Ela é um
-- artefato de revisão: deve ser lida, revisada e só então aplicada
-- manualmente por alguém com aprovação do gate humano MN (ver CLAUDE.md,
-- seção "DEPLOY CHECKLIST").
--
-- Como aplicar (após aprovação MN):
--
--   1) Via Supabase CLI (recomendado):
--        supabase db push
--        (a partir da raiz do repo, com o projeto Supabase linkado)
--
--   2) Via psql direto (ambiente de staging/homolog):
--        psql "$DATABASE_URL" -f supabase/migrations/2026_09_26_v5_4_8_mot_fasamento.sql
--
-- Pré-requisitos:
--   - Extensão `pgvector` habilitada no projeto (para a coluna `embedding`).
--   - Extensão `pgcrypto` habilitada para `gen_random_uuid()` (no Supabase,
--     já vem habilitada por padrão no schema `extensions`).
--
-- Idempotência:
--   - CREATE TYPE usa bloco DO $$ ... $$ com checagem em pg_type, pois
--     Postgres não suporta `CREATE TYPE IF NOT EXISTS`.
--   - CREATE TABLE usa IF NOT EXISTS.
--   - Índices usam IF NOT EXISTS.
--   - Os INSERTs dos 8 casos precedentes são idempotentes via
--     ON CONFLICT (slug) DO NOTHING. A tabela usa `id uuid` gerado
--     automaticamente (gen_random_uuid()), que não serve como chave natural
--     para reaplicações da migração; por isso foi adicionada a coluna
--     `slug text UNIQUE NOT NULL`, derivada de forma determinística de
--     tipologia + subtipo + km/trecho, para servir de chave de conflito.
--
-- Rastreabilidade dos 8 casos: todos vêm de documentos reais do projeto
-- SP-258 (Motiva/CCR) — Anexo 9 (Relatório de Desvios de Tráfego e
-- Sinalização Provisória), cronograma executivo real, e plantas
-- DE-/MD-/MC- lidas diretamente no SharePoint. Ver CLAUDE.md v5.4.8 e a
-- Central de Conhecimento MOT publicada nesta sessão para o detalhamento
-- da auditoria/QA de cada caso.
--
-- Rollback: ver bloco comentado ao final do arquivo.
-- =============================================================================

BEGIN;

-- -----------------------------------------------------------------------------
-- 1) ENUM: mot_tipologia
-- -----------------------------------------------------------------------------
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'mot_tipologia') THEN
        CREATE TYPE mot_tipologia AS ENUM (
            'trevo_parclo',
            'trevo_trombeta',
            'trevo_diamante',
            'duplicacao'
        );
    END IF;
END
$$;

-- -----------------------------------------------------------------------------
-- 2) ENUM: mot_confiabilidade
-- -----------------------------------------------------------------------------
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'mot_confiabilidade') THEN
        CREATE TYPE mot_confiabilidade AS ENUM (
            'confirmado_leitura_integral',
            'confirmado_websearch',
            'inferido'
        );
    END IF;
END
$$;

-- -----------------------------------------------------------------------------
-- 3) TABELA: mot_casos_precedentes
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS mot_casos_precedentes (
    id                          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    -- slug: chave natural determinística (tipologia + subtipo + km/trecho),
    -- usada apenas para permitir ON CONFLICT em INSERTs idempotentes desta
    -- migração; não é exposta como identificador de negócio fora deste arquivo.
    slug                        text NOT NULL,
    tipologia                   mot_tipologia NOT NULL,
    subtipo                     text,
    km_ou_trecho                text,
    num_fases                   integer,
    duracao_dias                integer,
    elemento_critico            text,
    restricao_contorno          text,
    projeto_tipo_manual         text[],
    fonte_documento             text,
    fonte_caminho_sharepoint    text,
    confiabilidade              mot_confiabilidade NOT NULL DEFAULT 'inferido',
    embedding                   vector(1536),
    created_at                  timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT mot_casos_precedentes_slug_key UNIQUE (slug)
);

-- -----------------------------------------------------------------------------
-- 4) ÍNDICES
-- -----------------------------------------------------------------------------

-- HNSW para busca por similaridade de cosseno em embeddings (RAG).
CREATE INDEX IF NOT EXISTS idx_mot_casos_precedentes_embedding_hnsw
    ON mot_casos_precedentes
    USING hnsw (embedding vector_cosine_ops);

-- Filtros comuns de consulta: por tipologia e por número de fases.
CREATE INDEX IF NOT EXISTS idx_mot_casos_precedentes_tipologia
    ON mot_casos_precedentes (tipologia);

CREATE INDEX IF NOT EXISTS idx_mot_casos_precedentes_num_fases
    ON mot_casos_precedentes (num_fases);

-- -----------------------------------------------------------------------------
-- 5) SEED — 8 casos precedentes reais (levantamento SP-258 / cliente CCR/Motiva)
-- -----------------------------------------------------------------------------

INSERT INTO mot_casos_precedentes (
    slug, tipologia, subtipo, km_ou_trecho, num_fases, duracao_dias,
    elemento_critico, restricao_contorno, projeto_tipo_manual,
    fonte_documento, fonte_caminho_sharepoint, confiabilidade
) VALUES
-- Caso 1
(
    'sp258-km230-50-trevo-parclo-rotatoria',
    'trevo_parclo',
    'Parclo com rotatória',
    'km 230,50 (grafias divergentes: 230+800 geometria / 230+500 planilha desvio)',
    2,
    330,
    'OAE (passagem inferior, gabarito 5,50m)',
    '9 ramos, rotatórias nos dois lados R=25m; OAE inicia junto (relação II), não depois, do dispositivo viário',
    ARRAY['Tipo 20','Tipo 21','Tipo 22'],
    'MD/MC-SPD230258.230.231-620-F07 + Cronograma EDT 1.1.2.5.2/1.1.2.6.1',
    '02_CLIENTE/15_CCR/25_SP-258_FEL 03/01_MAT REC/01. PROJETOS/02_GE',
    'confirmado_leitura_integral'
),
-- Caso 2
(
    'sp258-km263-trevo-trombeta-pista-leste',
    'trevo_trombeta',
    'Trombeta Pista Leste',
    'km 263,00 / 263+250',
    NULL,
    120,
    'OAE km 263+580 (vão 30m, TB-450) em trilha paralela de 300 dias',
    'Laço R=35m, rampa 18,7%; ramais periféricos R=193,50/100/61/50m',
    ARRAY['Tipo 20','Tipo 22'],
    'DE-SPD263258-263.264-620-F01 + MC-SPD263258-263.264-620-C01-101',
    '02_CLIENTE/15_CCR/10_DUPLICACAO_258/02_REC/02_WE_TRANSFER/.../km 263+250 - Dispositivo',
    'confirmado_leitura_integral'
),
-- Caso 3
(
    'sp258-km265-trevo-diamante-rotatoria',
    'trevo_diamante',
    'Diamante com rotatória',
    'km 265,00',
    NULL,
    120,
    'Viaduto 162,13m ligando 2 rotatórias (662,16 m²) — sem linha própria de OAE no cronograma, risco de prazo',
    '6 ramos (100-600) + 2 rotatórias R=25m interno',
    ARRAY['Tipo 20','Tipo 22'],
    'DE-SPD265258-265.266-620-F01_201 a 206',
    '02_CLIENTE/15_CCR/10_DUPLICACAO_258/02_REC/02_WE_TRANSFER/.../km 265+000 - Dispositivo',
    'confirmado_leitura_integral'
),
-- Caso 4
(
    'sp258-km282-trevo-diamante-sem-rotatoria',
    'trevo_diamante',
    'Diamante sem rotatória',
    'km 282,00 ("Diamante 003" no Caderno de Premissas)',
    NULL,
    120,
    'OAE 195,1 m² não listada no Caderno de Premissas (divergência de fonte)',
    '5 ramos (não 4); planta ainda cita nota "velocidade na rotatória=30km/h" pendente confirmação com equipe de projeto (contradição com o nome do dispositivo)',
    ARRAY['Tipo 7','Tipo 11','Tipo 12','Tipo 20','Tipo 21'],
    'DE-SPD282258-282.283-620-F01_201 a 207',
    '02_CLIENTE/15_CCR/10_DUPLICACAO_258/02_REC/02_WE_TRANSFER/2_Itemização Material Técnico/6_Dispositivos/In023-Retorno Tipo U010/010 - km 282 (Alternativa Final)',
    'inferido'
),
-- Caso 5
(
    'sp258-duplicacao-canteiro-central-70-5km',
    'duplicacao',
    'Duplicação com Canteiro Central',
    '70,5 km (premissa Anexo 9)',
    2,
    NULL,
    'Canteiro Central',
    'Fase 1 Tipo 5 → Fase 2 Tipo 2; 3 frentes simultâneas, 500m/mês/frente',
    ARRAY['Tipo 5','Tipo 2'],
    'Anexo 9 - Relatório de Desvios de Tráfego e Sinalização Provisória',
    '02_CLIENTE/15_CCR/10_DUPLICACAO_258/03_ELAB/00_Trabalho Entregue á MOTIVA/11_SP-258 Entrega Final',
    'confirmado_leitura_integral'
),
-- Caso 6
(
    'sp258-duplicacao-total-4faixas-canteiro-central-113km',
    'duplicacao',
    'Duplicação Total 4 faixas com Canteiro Central',
    '113 km (nota do próprio Anexo 9: "ajustar conforme trecho real do contrato")',
    3,
    NULL,
    'Canteiro Central',
    'Fase 1 Tipo 3/04 → Fase 2 Tipo 08/09,12/14 → Fase 3 Tipo 18/19; agrupamento 12/14 é suspeito (Tipo 12 e 14 não são família coerente)',
    ARRAY['Tipo 3','Tipo 4','Tipo 8','Tipo 9','Tipo 12','Tipo 14','Tipo 18','Tipo 19'],
    'Anexo 9',
    '02_CLIENTE/15_CCR/10_DUPLICACAO_258/03_ELAB/00_Trabalho Entregue á MOTIVA/11_SP-258 Entrega Final',
    'confirmado_leitura_integral'
),
-- Caso 7
(
    'sp258-duplicacao-2mais1-new-jersey-70-5km-vs-18-75km',
    'duplicacao',
    'Duplicação (2+1) com New Jersey',
    '70,5 km premissa vs ~18,75 km real no cronograma (divergência não explicada)',
    2,
    NULL,
    'Barreira New Jersey',
    'Fase 1 Tipo 5 → Fase 2 Tipo 4; seção quase-duplicada no Anexo 9 usa Tipo 11 para o mesmo cenário (possível erro de cópia)',
    ARRAY['Tipo 5','Tipo 4','Tipo 11'],
    'Anexo 9',
    '02_CLIENTE/15_CCR/10_DUPLICACAO_258/03_ELAB/00_Trabalho Entregue á MOTIVA/11_SP-258 Entrega Final',
    'confirmado_leitura_integral'
),
-- Caso 8
(
    'sp258-duplicacao-total-4faixas-new-jersey-sem-extensao',
    'duplicacao',
    'Duplicação Total 4 faixas com New Jersey',
    'sem extensão declarada no Anexo 9 (lacuna da fonte)',
    1,
    NULL,
    'Barreira New Jersey',
    'Desvio bidirecional único em mão dupla; texto confirma explicitamente "não será previsto sistema PARE/SIGA"',
    ARRAY['Tipo 20','Tipo 22'],
    'Anexo 9',
    '02_CLIENTE/15_CCR/10_DUPLICACAO_258/03_ELAB/00_Trabalho Entregue á MOTIVA/11_SP-258 Entrega Final',
    'confirmado_leitura_integral'
)
ON CONFLICT (slug) DO NOTHING;

COMMIT;

-- =============================================================================
-- ROLLBACK (executar manualmente, fora desta migração, se necessário reverter)
-- =============================================================================
--
-- BEGIN;
--
-- DROP INDEX IF EXISTS idx_mot_casos_precedentes_num_fases;
-- DROP INDEX IF EXISTS idx_mot_casos_precedentes_tipologia;
-- DROP INDEX IF EXISTS idx_mot_casos_precedentes_embedding_hnsw;
--
-- DROP TABLE IF EXISTS mot_casos_precedentes;
--
-- DROP TYPE IF EXISTS mot_confiabilidade;
-- DROP TYPE IF EXISTS mot_tipologia;
--
-- COMMIT;
-- =============================================================================
