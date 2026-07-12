-- M-B — Governance layer ADAPTADO ao schema real de produção
-- Substitui: supabase/migrations/2026_07_12_akp_governance_v4_5.sql
-- Ver: docs/AUDIT-v4.6-vs-PROD.md § Fase 2 M-B
--
-- Ao invés de operar sobre academic_knowledge_elements (que não existe),
-- opera sobre knowledge_extractions (schema real da v4.3 WF-AKP-001).
-- Idempotente.

BEGIN;

-- ============================================================
-- 1. Cross-references entre KEs
-- ============================================================
ALTER TABLE public.knowledge_extractions
  ADD COLUMN IF NOT EXISTS related_kes JSONB DEFAULT '{}'::jsonb;

COMMENT ON COLUMN public.knowledge_extractions.related_kes IS
  'Relações semânticas entre KEs: {"contradicts":["KE-034"],"supports":["KE-012"],"extends":["KE-005"],"supersedes":["KE-001"],"cites":["KE-020"]}. Alimenta view v_akp_contradictions.';

-- View para descoberta de conflitos (schema-invoker por padrão)
CREATE OR REPLACE VIEW public.v_akp_contradictions AS
SELECT
  a.ke_codigo   AS ke_a_codigo,
  a.descricao   AS ke_a_descricao,
  a.tese_codigo AS ke_a_tese,
  contra        AS ke_b_codigo,
  b.descricao   AS ke_b_descricao,
  b.tese_codigo AS ke_b_tese
FROM public.knowledge_extractions a
CROSS JOIN LATERAL jsonb_array_elements_text(
  COALESCE(a.related_kes->'contradicts', '[]'::jsonb)
) AS contra
LEFT JOIN public.knowledge_extractions b ON b.ke_codigo = contra
WHERE jsonb_array_length(COALESCE(a.related_kes->'contradicts','[]'::jsonb)) > 0
ORDER BY a.ke_codigo;

COMMENT ON VIEW public.v_akp_contradictions IS
  'KEs que se contradizem — agente vertical deve citar AMBOS ao responder consulta que caia sobre eles.';

-- ============================================================
-- 2. Versionamento de tese com history
-- ============================================================
-- teses_academicas já tem updated_at + trigger wf_akp_touch_updated_at.
-- Adicionamos revision + snapshot history.

ALTER TABLE public.teses_academicas
  ADD COLUMN IF NOT EXISTS revision INTEGER NOT NULL DEFAULT 1;

CREATE TABLE IF NOT EXISTS public.teses_academicas_history (
  history_id     BIGSERIAL PRIMARY KEY,
  tese_codigo    TEXT NOT NULL,
  revision       INTEGER NOT NULL,
  snapshot       JSONB NOT NULL,
  changed_at     TIMESTAMPTZ DEFAULT NOW(),
  changed_by     TEXT DEFAULT 'system',
  change_reason  TEXT
);

CREATE INDEX IF NOT EXISTS idx_teses_history_codigo
  ON public.teses_academicas_history(tese_codigo, revision DESC);

ALTER TABLE public.teses_academicas_history ENABLE ROW LEVEL SECURITY;

CREATE OR REPLACE FUNCTION public.teses_academicas_snapshot()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.teses_academicas_history
    (tese_codigo, revision, snapshot, changed_by, change_reason)
  VALUES (
    OLD.codigo, OLD.revision, to_jsonb(OLD),
    COALESCE(current_setting('app.current_user', TRUE), 'system'),
    COALESCE(current_setting('app.change_reason', TRUE), NULL)
  );
  NEW.revision := OLD.revision + 1;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SET search_path = public, extensions;

DROP TRIGGER IF EXISTS trg_teses_snapshot ON public.teses_academicas;
CREATE TRIGGER trg_teses_snapshot
  BEFORE UPDATE ON public.teses_academicas
  FOR EACH ROW
  WHEN (OLD.* IS DISTINCT FROM NEW.*)
  EXECUTE FUNCTION public.teses_academicas_snapshot();

-- ============================================================
-- 3. WF-AKP-002 — Curation backlog formal
-- ============================================================
CREATE TABLE IF NOT EXISTS public.akp_curation_backlog (
  id                   BIGSERIAL PRIMARY KEY,
  ticket_id            TEXT UNIQUE NOT NULL,
  segmento             TEXT NOT NULL,
  query_text           TEXT NOT NULL,
  n_occurrences        INTEGER NOT NULL,
  avg_top_similarity   FLOAT,
  status               TEXT NOT NULL DEFAULT 'triage' CHECK (status IN (
                        'triage','accepted','rejected','in_curation','ke_created','closed'
                       )),
  assigned_to          TEXT,
  linked_ke_codigos    TEXT[] DEFAULT '{}',
  first_detected_at    TIMESTAMPTZ NOT NULL,
  last_detected_at     TIMESTAMPTZ NOT NULL,
  triaged_at           TIMESTAMPTZ,
  closed_at            TIMESTAMPTZ,
  notes                TEXT
);

ALTER TABLE public.akp_curation_backlog ENABLE ROW LEVEL SECURITY;
CREATE INDEX IF NOT EXISTS idx_akp_backlog_status
  ON public.akp_curation_backlog(status);
CREATE INDEX IF NOT EXISTS idx_akp_backlog_segmento
  ON public.akp_curation_backlog(segmento);

-- Função de promoção — lê manta_rag_queries + hits_count agrupado por query
-- e cria tickets AKP-002-NNNNN. Roda diariamente via cron.
CREATE OR REPLACE FUNCTION public.promote_gaps_to_backlog(
  min_occurrences INTEGER DEFAULT 3
)
RETURNS TABLE (
  ticket_id     TEXT,
  action        TEXT,
  segmento_out  TEXT,
  query_out     TEXT
)
LANGUAGE plpgsql SET search_path = public, extensions AS $$
DECLARE
  gap_rec RECORD;
  existing_id BIGINT;
  new_ticket TEXT;
  next_seq INTEGER;
BEGIN
  FOR gap_rec IN
    SELECT
      COALESCE(q.tipo, 'sem-segmento') AS segmento,
      q.query_text,
      COUNT(*)::INTEGER AS n_occ,
      NULLIF(AVG(q.hits_count::FLOAT), 0) AS avg_hits,
      MAX(q.timestamp) AS last_seen
    FROM public.manta_rag_queries q
    WHERE q.timestamp > NOW() - INTERVAL '30 days'
      AND q.query_text IS NOT NULL
    GROUP BY 1, 2
    HAVING COUNT(*) >= min_occurrences
       AND COALESCE(AVG(q.hits_count::FLOAT), 0) < 3.0  -- baixa recuperação
  LOOP
    SELECT id INTO existing_id
      FROM public.akp_curation_backlog
     WHERE segmento = gap_rec.segmento
       AND query_text = gap_rec.query_text
       AND status NOT IN ('closed', 'rejected')
     LIMIT 1;

    IF existing_id IS NOT NULL THEN
      UPDATE public.akp_curation_backlog
         SET n_occurrences = gap_rec.n_occ,
             avg_top_similarity = gap_rec.avg_hits,
             last_detected_at = gap_rec.last_seen
       WHERE id = existing_id;
      SELECT b.ticket_id INTO new_ticket
        FROM public.akp_curation_backlog b WHERE b.id = existing_id;
      ticket_id := new_ticket; action := 'updated';
    ELSE
      SELECT COALESCE(MAX(SUBSTRING(t.ticket_id FROM 9)::INTEGER), 0) + 1
        INTO next_seq FROM public.akp_curation_backlog t
       WHERE t.ticket_id LIKE 'AKP-002-%';
      new_ticket := 'AKP-002-' || LPAD(next_seq::TEXT, 5, '0');
      INSERT INTO public.akp_curation_backlog
        (ticket_id, segmento, query_text, n_occurrences, avg_top_similarity,
         first_detected_at, last_detected_at)
      VALUES (
        new_ticket, gap_rec.segmento, gap_rec.query_text,
        gap_rec.n_occ, gap_rec.avg_hits,
        gap_rec.last_seen, gap_rec.last_seen
      );
      ticket_id := new_ticket; action := 'created';
    END IF;
    segmento_out := gap_rec.segmento;
    query_out    := gap_rec.query_text;
    RETURN NEXT;
  END LOOP;
END;
$$;

-- ============================================================
-- 4. Human approval workflow — change requests
-- ============================================================
CREATE TABLE IF NOT EXISTS public.agent_change_requests (
  id                BIGSERIAL PRIMARY KEY,
  request_id        TEXT UNIQUE NOT NULL,
  change_type       TEXT NOT NULL CHECK (change_type IN (
                     'new_agent','new_collection','new_ke_batch','agent_binding',
                     'routing_rule','ke_edit','ke_removal','other'
                    )),
  target_slug       TEXT,
  proposed_diff     TEXT,
  justification     TEXT NOT NULL,
  proposed_by       TEXT NOT NULL,
  proposed_at       TIMESTAMPTZ DEFAULT NOW(),
  status            TEXT NOT NULL DEFAULT 'pending' CHECK (status IN (
                     'pending','approved','rejected','applied','cancelled'
                    )),
  applied_at        TIMESTAMPTZ,
  applied_migration TEXT
);

CREATE TABLE IF NOT EXISTS public.agent_change_reviews (
  id           BIGSERIAL PRIMARY KEY,
  request_id   TEXT NOT NULL REFERENCES public.agent_change_requests(request_id) ON DELETE CASCADE,
  reviewer     TEXT NOT NULL,
  decision     TEXT NOT NULL CHECK (decision IN ('approve','reject','comment')),
  comment      TEXT,
  reviewed_at  TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE (request_id, reviewer)
);

ALTER TABLE public.agent_change_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.agent_change_reviews  ENABLE ROW LEVEL SECURITY;

CREATE INDEX IF NOT EXISTS idx_change_requests_status
  ON public.agent_change_requests(status);
CREATE INDEX IF NOT EXISTS idx_change_reviews_req
  ON public.agent_change_reviews(request_id);

CREATE OR REPLACE FUNCTION public.update_change_request_status()
RETURNS TRIGGER LANGUAGE plpgsql SET search_path = public, extensions AS $$
DECLARE
  n_approve INTEGER; n_reject INTEGER; cur_status TEXT;
BEGIN
  SELECT status INTO cur_status FROM public.agent_change_requests
   WHERE request_id = NEW.request_id;
  IF cur_status NOT IN ('pending') THEN RETURN NEW; END IF;
  SELECT COUNT(*) FILTER (WHERE decision='approve'),
         COUNT(*) FILTER (WHERE decision='reject')
    INTO n_approve, n_reject
    FROM public.agent_change_reviews WHERE request_id = NEW.request_id;
  IF n_reject >= 1 THEN
    UPDATE public.agent_change_requests SET status='rejected'
     WHERE request_id = NEW.request_id;
  ELSIF n_approve >= 2 THEN
    UPDATE public.agent_change_requests SET status='approved'
     WHERE request_id = NEW.request_id;
  END IF;
  RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_change_review ON public.agent_change_reviews;
CREATE TRIGGER trg_change_review
  AFTER INSERT OR UPDATE ON public.agent_change_reviews
  FOR EACH ROW EXECUTE FUNCTION public.update_change_request_status();

CREATE OR REPLACE VIEW public.v_change_requests_open AS
SELECT
  r.request_id, r.change_type, r.target_slug, r.proposed_by, r.proposed_at, r.status,
  (SELECT COUNT(*) FROM public.agent_change_reviews rv
    WHERE rv.request_id=r.request_id AND rv.decision='approve') AS n_approvals,
  (SELECT COUNT(*) FROM public.agent_change_reviews rv
    WHERE rv.request_id=r.request_id AND rv.decision='reject') AS n_rejects,
  ARRAY(SELECT rv.reviewer FROM public.agent_change_reviews rv
         WHERE rv.request_id=r.request_id ORDER BY rv.reviewed_at) AS reviewers,
  r.justification
FROM public.agent_change_requests r
WHERE r.status IN ('pending','approved')
ORDER BY r.proposed_at DESC;

COMMIT;

-- ============================================================
-- ROLLBACK
-- ============================================================
-- BEGIN;
-- DROP VIEW    IF EXISTS public.v_change_requests_open;
-- DROP TRIGGER IF EXISTS trg_change_review ON public.agent_change_reviews;
-- DROP FUNCTION IF EXISTS public.update_change_request_status();
-- DROP TABLE   IF EXISTS public.agent_change_reviews;
-- DROP TABLE   IF EXISTS public.agent_change_requests;
-- DROP FUNCTION IF EXISTS public.promote_gaps_to_backlog(INTEGER);
-- DROP TABLE   IF EXISTS public.akp_curation_backlog;
-- DROP TRIGGER IF EXISTS trg_teses_snapshot ON public.teses_academicas;
-- DROP FUNCTION IF EXISTS public.teses_academicas_snapshot();
-- DROP TABLE   IF EXISTS public.teses_academicas_history;
-- ALTER TABLE public.teses_academicas DROP COLUMN IF EXISTS revision;
-- DROP VIEW    IF EXISTS public.v_akp_contradictions;
-- ALTER TABLE public.knowledge_extractions DROP COLUMN IF EXISTS related_kes;
-- COMMIT;
