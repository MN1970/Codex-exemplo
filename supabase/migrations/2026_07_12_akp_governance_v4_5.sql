-- Manta Maestro v4.5 — Governance Layer
-- Ticket: MNT-2026-GOVERNANCE-LAYER
--
-- Fecha os 4 gaps estruturais do backlog do ecossistema:
--   #7  Cross-references entre KEs (contradicts/supports)
--   #8  Versionamento de tese com history table
--   #10 Feedback loop → curation backlog (WF-AKP-002 formalizado)
--   #13 Human approval workflow para mudanças no ecossistema
--
-- Aditivo sobre v4.4. Idempotente.

BEGIN;

-- =====================================================================
-- #7 Cross-references entre KEs
-- =====================================================================
-- Um KE pode contradizer, corroborar, estender ou substituir outro.
-- Ex.: tese A defende alteamento a jusante, tese B critica → contradicts.
-- Modelo: JSONB por KE, semântica em 5 tipos.

ALTER TABLE academic_knowledge_elements
  ADD COLUMN IF NOT EXISTS related_kes JSONB DEFAULT '{}'::jsonb;

COMMENT ON COLUMN academic_knowledge_elements.related_kes IS
  'JSONB com relações semânticas: {"contradicts":["KE-034"],"supports":["KE-012"],"extends":["KE-005"],"supersedes":["KE-001"],"cites":["KE-020"]}';

-- View para descoberta rápida de conflitos
CREATE OR REPLACE VIEW v_akp_contradictions AS
SELECT
  ake_a.id                                   AS ke_a_id,
  ake_a.titulo                                AS ke_a_titulo,
  ake_a.segmento                              AS ke_a_segmento,
  ake_a.tese_id                               AS ke_a_tese,
  contra_id::text                             AS ke_b_id,
  ake_b.titulo                                AS ke_b_titulo,
  ake_b.tese_id                               AS ke_b_tese
FROM academic_knowledge_elements ake_a
CROSS JOIN LATERAL jsonb_array_elements_text(
  COALESCE(ake_a.related_kes->'contradicts','[]'::jsonb)
) AS contra_id
LEFT JOIN academic_knowledge_elements ake_b ON ake_b.id = contra_id
WHERE jsonb_array_length(COALESCE(ake_a.related_kes->'contradicts','[]'::jsonb)) > 0
ORDER BY ake_a.segmento, ake_a.id;

COMMENT ON VIEW v_akp_contradictions IS
  'KEs que se contradizem — o agente vertical deve citar AMBOS quando responder.';

-- =====================================================================
-- #8 Versionamento de tese
-- =====================================================================
-- Se uma tese for revisada (versão nova, errata, complemento), preserva
-- histórico em vez de sobrescrever silenciosamente.

ALTER TABLE academic_theses
  ADD COLUMN IF NOT EXISTS revision INTEGER NOT NULL DEFAULT 1;

CREATE TABLE IF NOT EXISTS academic_theses_history (
  history_id     BIGSERIAL PRIMARY KEY,
  tese_id        TEXT NOT NULL,
  revision       INTEGER NOT NULL,
  snapshot       JSONB NOT NULL,        -- row inteira serializada no momento da mudança
  changed_at     TIMESTAMPTZ DEFAULT NOW(),
  changed_by     TEXT DEFAULT 'system', -- usuário ou 'system' para trigger
  change_reason  TEXT
);

CREATE INDEX IF NOT EXISTS idx_theses_history_tese
  ON academic_theses_history(tese_id, revision DESC);

-- Trigger: cada UPDATE em academic_theses cria snapshot da versão ANTERIOR
-- + incrementa revision. Não cria snapshot em INSERT (revision=1 default).
CREATE OR REPLACE FUNCTION academic_theses_snapshot() RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO academic_theses_history (tese_id, revision, snapshot, changed_by, change_reason)
  VALUES (
    OLD.id,
    OLD.revision,
    to_jsonb(OLD),
    COALESCE(current_setting('app.current_user', TRUE), 'system'),
    COALESCE(current_setting('app.change_reason', TRUE), NULL)
  );
  NEW.revision := OLD.revision + 1;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_academic_theses_snapshot ON academic_theses;
CREATE TRIGGER trg_academic_theses_snapshot
  BEFORE UPDATE ON academic_theses
  FOR EACH ROW
  WHEN (OLD.* IS DISTINCT FROM NEW.*)
  EXECUTE FUNCTION academic_theses_snapshot();

-- =====================================================================
-- #10 WF-AKP-002 — Curation Backlog Loop
-- =====================================================================
-- Formaliza o backlog de curadoria acadêmica: cada gap detectado pela
-- view v_akp_gap_candidates vira uma linha que pode ser triada, atribuída
-- e concluída.

CREATE TABLE IF NOT EXISTS akp_curation_backlog (
  id                   BIGSERIAL PRIMARY KEY,
  ticket_id            TEXT UNIQUE NOT NULL,   -- 'AKP-002-<seq>'
  segmento             TEXT NOT NULL,
  query_text           TEXT NOT NULL,
  n_occurrences        INTEGER NOT NULL,
  avg_top_similarity   FLOAT,
  status               TEXT NOT NULL DEFAULT 'triage' CHECK (status IN (
                        'triage',        -- recém-detectado
                        'accepted',      -- MN validou como gap real
                        'rejected',      -- MN rejeitou (query mal-formulada, fora escopo, etc.)
                        'in_curation',   -- em curadoria (buscando tese)
                        'ke_created',    -- KE(s) novo(s) criado(s) e ingerido(s)
                        'closed'         -- fechado, done
                       )),
  assigned_to          TEXT,             -- usuário responsável
  linked_ke_ids        TEXT[] DEFAULT '{}',  -- KEs criados p/ fechar o gap
  first_detected_at    TIMESTAMPTZ NOT NULL,
  last_detected_at     TIMESTAMPTZ NOT NULL,
  triaged_at           TIMESTAMPTZ,
  closed_at            TIMESTAMPTZ,
  notes                TEXT
);

CREATE INDEX IF NOT EXISTS idx_akp_backlog_status   ON akp_curation_backlog(status);
CREATE INDEX IF NOT EXISTS idx_akp_backlog_segmento ON akp_curation_backlog(segmento);

-- Função que sincroniza v_akp_gap_candidates → akp_curation_backlog.
-- Roda periodicamente (cron via pg_cron ou GitHub Action).
CREATE OR REPLACE FUNCTION promote_gaps_to_backlog(
  min_occurrences INTEGER DEFAULT 3,
  max_top_sim     FLOAT DEFAULT 0.30
)
RETURNS TABLE (
  ticket_id       TEXT,
  action          TEXT,   -- 'created' | 'updated' | 'skipped'
  segmento        TEXT,
  query_text      TEXT
)
LANGUAGE plpgsql AS $$
DECLARE
  gap_rec RECORD;
  existing_id BIGINT;
  new_ticket_id TEXT;
  next_seq INTEGER;
BEGIN
  FOR gap_rec IN
    SELECT
      g.segmento,
      g.query_text,
      g.n_occurrences,
      g.avg_top_sim,
      g.last_seen
    FROM v_akp_gap_candidates g
    WHERE g.n_occurrences >= min_occurrences
      AND (g.avg_top_sim IS NULL OR g.avg_top_sim <= max_top_sim)
  LOOP
    SELECT id INTO existing_id
      FROM akp_curation_backlog
     WHERE segmento = gap_rec.segmento
       AND query_text = gap_rec.query_text
       AND status NOT IN ('closed', 'rejected')
     LIMIT 1;

    IF existing_id IS NOT NULL THEN
      UPDATE akp_curation_backlog
         SET n_occurrences = gap_rec.n_occurrences,
             avg_top_similarity = gap_rec.avg_top_sim,
             last_detected_at = gap_rec.last_seen
       WHERE id = existing_id;
      action := 'updated';
      SELECT b.ticket_id INTO new_ticket_id FROM akp_curation_backlog b WHERE b.id = existing_id;
    ELSE
      SELECT COALESCE(MAX(SUBSTRING(t.ticket_id FROM 9)::INTEGER), 0) + 1
        INTO next_seq
        FROM akp_curation_backlog t
       WHERE t.ticket_id LIKE 'AKP-002-%';
      new_ticket_id := 'AKP-002-' || LPAD(next_seq::TEXT, 5, '0');
      INSERT INTO akp_curation_backlog (
        ticket_id, segmento, query_text, n_occurrences, avg_top_similarity,
        first_detected_at, last_detected_at
      ) VALUES (
        new_ticket_id, gap_rec.segmento, gap_rec.query_text,
        gap_rec.n_occurrences, gap_rec.avg_top_sim,
        gap_rec.last_seen, gap_rec.last_seen
      );
      action := 'created';
    END IF;

    ticket_id  := new_ticket_id;
    segmento   := gap_rec.segmento;
    query_text := gap_rec.query_text;
    RETURN NEXT;
  END LOOP;
  RETURN;
END;
$$;

COMMENT ON FUNCTION promote_gaps_to_backlog IS
  'Lê v_akp_gap_candidates e cria/atualiza tickets AKP-002-* em akp_curation_backlog. Roda diariamente via cron.';

-- =====================================================================
-- #13 Human Approval Workflow
-- =====================================================================
-- MN hoje é gate único. Escalar → 2 aprovadores mínimo p/ mudanças em
-- produção (novos agentes, novos KEs, ativação de coleções).

CREATE TABLE IF NOT EXISTS agent_change_requests (
  id                   BIGSERIAL PRIMARY KEY,
  request_id           TEXT UNIQUE NOT NULL,  -- 'CR-<YYYY>-<seq>'
  change_type          TEXT NOT NULL CHECK (change_type IN (
                        'new_agent',
                        'new_collection',
                        'new_ke_batch',
                        'agent_binding',
                        'routing_rule',
                        'ke_edit',
                        'ke_removal',
                        'other'
                       )),
  target_slug          TEXT,               -- ex.: 'agente-tuneis' ou 'academic-knowledge'
  proposed_diff        TEXT,               -- diff textual ou SQL do que muda
  justification        TEXT NOT NULL,      -- por que
  proposed_by          TEXT NOT NULL,
  proposed_at          TIMESTAMPTZ DEFAULT NOW(),
  status               TEXT NOT NULL DEFAULT 'pending' CHECK (status IN (
                        'pending',    -- aguardando revisões
                        'approved',   -- ≥2 approvals sem rejeitos
                        'rejected',   -- ≥1 rejeição
                        'applied',    -- foi executado
                        'cancelled'   -- retirado pelo proposer
                       )),
  applied_at           TIMESTAMPTZ,
  applied_migration    TEXT                -- ref ao arquivo SQL que executou
);

CREATE TABLE IF NOT EXISTS agent_change_reviews (
  id           BIGSERIAL PRIMARY KEY,
  request_id   TEXT NOT NULL REFERENCES agent_change_requests(request_id) ON DELETE CASCADE,
  reviewer     TEXT NOT NULL,
  decision     TEXT NOT NULL CHECK (decision IN ('approve','reject','comment')),
  comment      TEXT,
  reviewed_at  TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE (request_id, reviewer)
);

CREATE INDEX IF NOT EXISTS idx_change_requests_status ON agent_change_requests(status);
CREATE INDEX IF NOT EXISTS idx_change_reviews_req     ON agent_change_reviews(request_id);

-- Trigger: quando review acumula, promove status conforme regra
-- (>= 2 approvals sem nenhum reject → approved; >=1 reject → rejected)
CREATE OR REPLACE FUNCTION update_change_request_status() RETURNS TRIGGER AS $$
DECLARE
  n_approve INTEGER;
  n_reject  INTEGER;
  cur_status TEXT;
BEGIN
  SELECT status INTO cur_status FROM agent_change_requests WHERE request_id = NEW.request_id;
  IF cur_status NOT IN ('pending') THEN
    RETURN NEW;  -- já decidido; não sobrescreve
  END IF;

  SELECT
    COUNT(*) FILTER (WHERE decision='approve'),
    COUNT(*) FILTER (WHERE decision='reject')
  INTO n_approve, n_reject
  FROM agent_change_reviews
  WHERE request_id = NEW.request_id;

  IF n_reject >= 1 THEN
    UPDATE agent_change_requests SET status='rejected'
     WHERE request_id = NEW.request_id;
  ELSIF n_approve >= 2 THEN
    UPDATE agent_change_requests SET status='approved'
     WHERE request_id = NEW.request_id;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_change_review ON agent_change_reviews;
CREATE TRIGGER trg_change_review
  AFTER INSERT OR UPDATE ON agent_change_reviews
  FOR EACH ROW EXECUTE FUNCTION update_change_request_status();

-- View pronta pro dashboard de aprovação
CREATE OR REPLACE VIEW v_change_requests_open AS
SELECT
  r.request_id,
  r.change_type,
  r.target_slug,
  r.proposed_by,
  r.proposed_at,
  r.status,
  COALESCE((SELECT COUNT(*) FROM agent_change_reviews rv
             WHERE rv.request_id=r.request_id AND rv.decision='approve'),0) AS n_approvals,
  COALESCE((SELECT COUNT(*) FROM agent_change_reviews rv
             WHERE rv.request_id=r.request_id AND rv.decision='reject'),0)  AS n_rejects,
  ARRAY(SELECT rv.reviewer FROM agent_change_reviews rv
         WHERE rv.request_id=r.request_id ORDER BY rv.reviewed_at) AS reviewers,
  r.justification
FROM agent_change_requests r
WHERE r.status IN ('pending','approved')
ORDER BY r.proposed_at DESC;

COMMIT;

-- =====================================================================
-- ROLLBACK
-- =====================================================================
-- BEGIN;
--
-- -- #13
-- DROP VIEW    IF EXISTS v_change_requests_open;
-- DROP TRIGGER IF EXISTS trg_change_review ON agent_change_reviews;
-- DROP FUNCTION IF EXISTS update_change_request_status();
-- DROP TABLE   IF EXISTS agent_change_reviews;
-- DROP TABLE   IF EXISTS agent_change_requests;
--
-- -- #10
-- DROP FUNCTION IF EXISTS promote_gaps_to_backlog(INTEGER, FLOAT);
-- DROP TABLE    IF EXISTS akp_curation_backlog;
--
-- -- #8
-- DROP TRIGGER  IF EXISTS trg_academic_theses_snapshot ON academic_theses;
-- DROP FUNCTION IF EXISTS academic_theses_snapshot();
-- DROP TABLE    IF EXISTS academic_theses_history;
-- ALTER TABLE academic_theses DROP COLUMN IF EXISTS revision;
--
-- -- #7
-- DROP VIEW  IF EXISTS v_akp_contradictions;
-- ALTER TABLE academic_knowledge_elements DROP COLUMN IF EXISTS related_kes;
--
-- COMMIT;
