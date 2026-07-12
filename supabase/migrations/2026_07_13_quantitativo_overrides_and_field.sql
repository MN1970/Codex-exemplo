-- v4.7 — Quantitativo overrides (UI) + field measurements (obra)
-- Camadas 3 e 6 do framework TRAINING-QUANTITATIVOS.md.
--
-- Depende de:
--   - public.agent_episodes (v4.7 já em prod — migration
--     2026_07_13_maestro_v4_7_reflexion_episodic_cost.sql).
--   - Agente A (paralelo): public.manta_quantitativos_reconciliacao
--     (a view v_predicted_vs_actual precisa dela; se ausente no momento
--     da aplicação, o bloco DO plpgsql pula a view — a criação da view
--     é IDEMPOTENTE e pode ser re-executada quando a tabela existir).
--
-- Idempotente. Coerente com Fase 1: search_path fixo, security_invoker=on
-- em views, RLS habilitado em todas as tabelas + policy p/ service_role.
-- Rollback: bloco comentado no final.

BEGIN;

-- ============================================================
-- 1. Tabela quantitativo_overrides — camada 3 (human-in-the-loop)
-- ============================================================
-- Captura toda edição manual do operador na UI (OAE MappingPage inline
-- edit + backends futuros). delta_pct é GENERATED — sempre coerente.

CREATE TABLE IF NOT EXISTS public.quantitativo_overrides (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id      TEXT NOT NULL,
  sap_code        TEXT NOT NULL,
  qty_original    NUMERIC NOT NULL,
  qty_override    NUMERIC NOT NULL,
  delta_pct       NUMERIC GENERATED ALWAYS AS (
                    CASE
                      WHEN qty_original IS NULL OR qty_original = 0 THEN NULL
                      ELSE ROUND(
                        ((qty_override - qty_original) / qty_original) * 100.0,
                        3
                      )
                    END
                  ) STORED,
  override_reason TEXT,
  reviewed_by     TEXT,           -- email do operador
  reviewed_at     TIMESTAMPTZ,
  source_backend  TEXT NOT NULL,  -- 'oae' | 'ifc' | 'iluminacao' | ...
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE  public.quantitativo_overrides IS
  'Overrides manuais aplicados pelo operador em UIs de quantitativos (camada 3 do TRAINING-QUANTITATIVOS.md). Alimenta o backlog de bugs recorrentes e o LessonInjector.';
COMMENT ON COLUMN public.quantitativo_overrides.delta_pct IS
  'Delta em % entre qty_override (humano) e qty_original (extractor). GENERATED — não escrever manualmente.';
COMMENT ON COLUMN public.quantitativo_overrides.source_backend IS
  'Slug do backend de origem: oae, ifc, iluminacao, pavimentacao, sinalizacao, sondagem, terraplenagem, landxml, estrutural.';

CREATE INDEX IF NOT EXISTS idx_qo_project
  ON public.quantitativo_overrides(project_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_qo_sap
  ON public.quantitativo_overrides(sap_code, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_qo_backend_sap
  ON public.quantitativo_overrides(source_backend, sap_code);

ALTER TABLE public.quantitativo_overrides ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS p_service_role_all ON public.quantitativo_overrides;
CREATE POLICY p_service_role_all
  ON public.quantitativo_overrides
  FOR ALL TO service_role
  USING (true) WITH CHECK (true);

-- ============================================================
-- 2. Tabela field_measurements — camada 6 (medição pós-obra)
-- ============================================================
-- Uma linha por (project_id, sap_code) medido em obra. Referencia o
-- episódio ORIGINAL que gerou a predição, para permitir backfill de
-- lessons_learned via backfill_field_measurement().

CREATE TABLE IF NOT EXISTS public.field_measurements (
  id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id     TEXT NOT NULL,
  sap_code       TEXT NOT NULL,
  qty_measured   NUMERIC NOT NULL,
  unit           TEXT,
  measured_by    TEXT NOT NULL,   -- email
  measured_at    DATE NOT NULL DEFAULT CURRENT_DATE,
  notes          TEXT,
  episode_id     UUID REFERENCES public.agent_episodes(id) ON DELETE SET NULL,
  created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE public.field_measurements IS
  'Medições reais de obra pós-execução (camada 6 do TRAINING-QUANTITATIVOS.md). Cruzada com o predito em v_predicted_vs_actual e propaga delta para lessons_learned via backfill_field_measurement().';
COMMENT ON COLUMN public.field_measurements.episode_id IS
  'Episódio original que gerou a predição (opcional). Quando setado, o backfill anexa lesson predicted_vs_actual=±X.Y%.';

CREATE INDEX IF NOT EXISTS idx_fm_project
  ON public.field_measurements(project_id, sap_code);
CREATE INDEX IF NOT EXISTS idx_fm_sap
  ON public.field_measurements(sap_code, measured_at DESC);
CREATE INDEX IF NOT EXISTS idx_fm_episode
  ON public.field_measurements(episode_id) WHERE episode_id IS NOT NULL;

ALTER TABLE public.field_measurements ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS p_service_role_all ON public.field_measurements;
CREATE POLICY p_service_role_all
  ON public.field_measurements
  FOR ALL TO service_role
  USING (true) WITH CHECK (true);

-- ============================================================
-- 3. View v_predicted_vs_actual — depende do Agente A
-- ============================================================
-- Cria APENAS se manta_quantitativos_reconciliacao existir (Agente A
-- cria em paralelo). Se ausente, a view fica pendente — re-rodar esta
-- migration (é idempotente) após Agente A aplicar a dele.

DO $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM information_schema.tables
     WHERE table_schema = 'public'
       AND table_name   = 'manta_quantitativos_reconciliacao'
  ) THEN
    EXECUTE $VIEW$
      CREATE OR REPLACE VIEW public.v_predicted_vs_actual
        WITH (security_invoker = on)
      AS
      SELECT
        r.project_id,
        r.sap_code,
        r.qty_predicted,
        f.qty_measured,
        f.unit,
        CASE
          WHEN r.qty_predicted IS NULL OR r.qty_predicted = 0 THEN NULL
          ELSE ROUND(
            ((f.qty_measured - r.qty_predicted) / r.qty_predicted) * 100.0, 3
          )
        END AS delta_pct,
        CASE
          WHEN r.qty_predicted IS NULL OR r.qty_predicted = 0 THEN 'sem_predicao'
          WHEN ABS((f.qty_measured - r.qty_predicted) / r.qty_predicted) < 0.05
            THEN 'acurado <5%'
          WHEN ABS((f.qty_measured - r.qty_predicted) / r.qty_predicted) < 0.10
            THEN 'moderado 5-10%'
          ELSE 'divergente >10%'
        END AS banda,
        f.measured_by,
        f.measured_at,
        f.episode_id
      FROM public.manta_quantitativos_reconciliacao r
      JOIN public.field_measurements f
        ON f.project_id = r.project_id AND f.sap_code = r.sap_code;
    $VIEW$;

    COMMENT ON VIEW public.v_predicted_vs_actual IS
      'Cruza manta_quantitativos_reconciliacao (predito) com field_measurements (real) por (project_id, sap_code). Classifica em 3 bandas: acurado <5% / moderado 5-10% / divergente >10%. security_invoker=on.';
  ELSE
    RAISE NOTICE 'v_predicted_vs_actual NOT created: table manta_quantitativos_reconciliacao missing (Agente A must run first). Re-run this migration after that table exists.';
  END IF;
END$$;

-- ============================================================
-- 4. Função backfill_field_measurement — plpgsql
-- ============================================================
-- INSERT em field_measurements + UPDATE em agent_episodes anexando
-- lesson `predicted_vs_actual = ±X.Y%` ao array lessons_learned.
-- Retorna o UUID do field_measurement criado.

CREATE OR REPLACE FUNCTION public.backfill_field_measurement(
    p_project_id   TEXT,
    p_sap_code     TEXT,
    p_qty_measured NUMERIC,
    p_measured_by  TEXT,
    p_unit         TEXT DEFAULT NULL,
    p_notes        TEXT DEFAULT NULL,
    p_episode_id   UUID DEFAULT NULL
) RETURNS UUID
LANGUAGE plpgsql
SET search_path = public, extensions
AS $$
DECLARE
  v_fm_id       UUID;
  v_episode_id  UUID := p_episode_id;
  v_qty_pred    NUMERIC;
  v_delta_pct   NUMERIC;
  v_lesson      TEXT;
BEGIN
  -- Se episode_id não veio, tenta achar o episódio mais recente
  -- do project_id via task_description (padrão "[project_id] ...").
  IF v_episode_id IS NULL THEN
    SELECT id INTO v_episode_id
      FROM public.agent_episodes
     WHERE task_description ILIKE '[' || p_project_id || ']%'
     ORDER BY created_at DESC
     LIMIT 1;
  END IF;

  INSERT INTO public.field_measurements(
    project_id, sap_code, qty_measured, unit,
    measured_by, notes, episode_id
  ) VALUES (
    p_project_id, p_sap_code, p_qty_measured, p_unit,
    p_measured_by, p_notes, v_episode_id
  ) RETURNING id INTO v_fm_id;

  -- Se conseguir cruzar com a predição (via reconciliação do Agente A),
  -- anexa lição ao episódio linkado.
  IF v_episode_id IS NOT NULL AND EXISTS (
    SELECT 1 FROM information_schema.tables
     WHERE table_schema='public' AND table_name='manta_quantitativos_reconciliacao'
  ) THEN
    EXECUTE format(
      'SELECT qty_predicted FROM public.manta_quantitativos_reconciliacao
        WHERE project_id = %L AND sap_code = %L LIMIT 1',
      p_project_id, p_sap_code
    ) INTO v_qty_pred;

    IF v_qty_pred IS NOT NULL AND v_qty_pred <> 0 THEN
      v_delta_pct := ROUND(
        ((p_qty_measured - v_qty_pred) / v_qty_pred) * 100.0, 2
      );
      v_lesson := 'predicted_vs_actual (' || p_sap_code || ') = '
               || CASE WHEN v_delta_pct >= 0 THEN '+' ELSE '' END
               || v_delta_pct::TEXT || '%';

      UPDATE public.agent_episodes
         SET lessons_learned = COALESCE(lessons_learned, '{}') || v_lesson
       WHERE id = v_episode_id
         AND NOT (v_lesson = ANY (COALESCE(lessons_learned, '{}')));
    END IF;
  END IF;

  RETURN v_fm_id;
END;
$$;

COMMENT ON FUNCTION public.backfill_field_measurement(
  TEXT, TEXT, NUMERIC, TEXT, TEXT, TEXT, UUID
) IS
  'Registra medição de campo pós-obra e anexa lesson predicted_vs_actual=±X.Y% no agent_episode original. Idempotente por lesson (não duplica).';

COMMIT;

-- ============================================================
-- Rollback (comentado)
-- ============================================================
-- BEGIN;
-- DROP FUNCTION IF EXISTS public.backfill_field_measurement(
--   TEXT, TEXT, NUMERIC, TEXT, TEXT, TEXT, UUID);
-- DROP VIEW     IF EXISTS public.v_predicted_vs_actual;
-- DROP TABLE    IF EXISTS public.field_measurements;
-- DROP TABLE    IF EXISTS public.quantitativo_overrides;
-- COMMIT;
