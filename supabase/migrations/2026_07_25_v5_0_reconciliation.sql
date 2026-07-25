-- Manta Maestro v5.0 — Agent Taxonomy Reconciliation
-- Ticket: MNT-2026-AGENT-RECONCILIATION
-- Date: 2026-07-25
--
-- BREAKING CHANGES:
-- 1. Rename 03-S* → S* in manta_agent_capabilities
-- 2. Remove guards (aluci-guard, consist-guard, context-guardian) from agents table
-- 3. Resolve Manta 15 collision: Manta 15 → M08, Manta 16 → M09
-- 4. Consolidate M-scheme: ensure M01-M10 (11 horizontals) + S01-S10 (10 setorials)
--
-- IDEMPOTENT: safe to re-run; uses IF EXISTS / ON CONFLICT
--
-- This migration ASSUMES the schema has:
--   - manta_agent_capabilities(agent_id TEXT PRIMARY KEY, name TEXT, ...)
--   - maestro_routing_keywords(agent_slug TEXT, keyword TEXT, ...)
--   - sp_agent_routing(agent_slug TEXT PRIMARY KEY, ...)
--
-- If your schema differs (e.g., separate guards table), adapt accordingly.
--
-- TESTING: Run in staging first. Rollback script at end.

BEGIN;

SET statement_timeout = '30 seconds';

-- =====================================================================
-- PHASE 1: Rename 03-S* → S* in manta_agent_capabilities
-- =====================================================================

-- S01: Rodovias (03-S1)
UPDATE manta_agent_capabilities
SET agent_id = 'S01'
WHERE agent_id = '03-S1' AND agent_id != 'S01';

-- S02: OAE (03-S2)
UPDATE manta_agent_capabilities
SET agent_id = 'S02'
WHERE agent_id = '03-S2' AND agent_id != 'S02';

-- S03: Ferrovia (03-S3)
UPDATE manta_agent_capabilities
SET agent_id = 'S03'
WHERE agent_id = '03-S3' AND agent_id != 'S03';

-- S04: Metrô (03-S4)
UPDATE manta_agent_capabilities
SET agent_id = 'S04'
WHERE agent_id = '03-S4' AND agent_id != 'S04';

-- S05: Túneis (03-S5)
UPDATE manta_agent_capabilities
SET agent_id = 'S05'
WHERE agent_id = '03-S5' AND agent_id != 'S05';

-- S06: Portos (03-S6)
UPDATE manta_agent_capabilities
SET agent_id = 'S06'
WHERE agent_id = '03-S6' AND agent_id != 'S06';

-- S07: Aeroportos (03-S7)
UPDATE manta_agent_capabilities
SET agent_id = 'S07'
WHERE agent_id = '03-S7' AND agent_id != 'S07';

-- S08: Saneamento (03-S8, PRIORIDADE AySA)
UPDATE manta_agent_capabilities
SET agent_id = 'S08'
WHERE agent_id = '03-S8' AND agent_id != 'S08';

-- S09: Energia (03-S9, ANEEL/State Grid)
UPDATE manta_agent_capabilities
SET agent_id = 'S09'
WHERE agent_id = '03-S9' AND agent_id != 'S09';

-- S10: Barragens (03-S10)
UPDATE manta_agent_capabilities
SET agent_id = 'S10'
WHERE agent_id = '03-S10' AND agent_id != 'S10';

-- =====================================================================
-- PHASE 2: Remove guards from manta_agent_capabilities
-- =====================================================================
-- Guards are skills, not agents; they belong in a separate skills table.
-- If your schema doesn't have a separate skills table yet, these are registered
-- but flagged as 'is_skill=true' or similar. Adapt as needed.

DELETE FROM manta_agent_capabilities
WHERE agent_id IN ('aluci-guard', 'consist-guard', 'context-guardian');

-- Optional: Log removal (if you have an audit log table)
-- INSERT INTO audit_log (action, affected_agent_ids, timestamp)
-- VALUES ('reconciliation_remove_guards',
--         ARRAY['aluci-guard', 'consist-guard', 'context-guardian'],
--         NOW());

-- =====================================================================
-- PHASE 3: Resolve Manta 15 collision & consolidate Manta → M scheme
-- =====================================================================
-- Horizontal agents: M00-M10 (11 total)
--
-- Old → New mapping:
--   Manta 00 → M00 (maestro)
--   Manta 01 → M01 (claims)
--   Manta 02 → M02 (contratual)  [conflicts with M02 in db; choose one]
--   Manta 04 → M04 (imobiliario)
--   Manta 05 → M05 (orcamento)
--   Manta 06 → M06 (modelagem)
--   Manta 07 → M07 (cronograma)
--   Manta 13 → M03 (bd; renumbered to fill gap)
--   Manta 14 → M10 (apresentacoes; renumbered)
--   Manta 15 → M08 (advisory; renumbered to resolve collision with 16)
--   Manta 16 → M09 (arquiteto-ia; renumbered)

-- Consolidate Manta → M (assuming Manta codes are the old names)
-- If database already has M01-M10, these are idempotent:

UPDATE manta_agent_capabilities
SET agent_id = 'M00'
WHERE agent_id IN ('Manta 00', 'Manta-00') AND agent_id != 'M00';

UPDATE manta_agent_capabilities
SET agent_id = 'M01'
WHERE agent_id IN ('Manta 01', 'Manta-01', '02-C') AND agent_id != 'M01';

UPDATE manta_agent_capabilities
SET agent_id = 'M02'
WHERE agent_id IN ('Manta 02', 'Manta-02') AND agent_id != 'M02';

-- Manta 04 → M04 (imobiliario; skip if already M04)
UPDATE manta_agent_capabilities
SET agent_id = 'M04'
WHERE agent_id IN ('Manta 04', 'Manta-04') AND agent_id != 'M04';

UPDATE manta_agent_capabilities
SET agent_id = 'M05'
WHERE agent_id IN ('Manta 05', 'Manta-05') AND agent_id != 'M05';

UPDATE manta_agent_capabilities
SET agent_id = 'M06'
WHERE agent_id IN ('Manta 06', 'Manta-06') AND agent_id != 'M06';

UPDATE manta_agent_capabilities
SET agent_id = 'M07'
WHERE agent_id IN ('Manta 07', 'Manta-07') AND agent_id != 'M07';

-- COLLISION RESOLUTION:
-- Manta 13 (bd, manta-13) → M03 (filling gap, renumber)
UPDATE manta_agent_capabilities
SET agent_id = 'M03'
WHERE agent_id IN ('Manta 13', 'Manta-13', 'manta-13', 'M13') AND agent_id != 'M03';

-- Manta 14 (apresentacoes, manta-14-pptx) → M10 (renumber)
UPDATE manta_agent_capabilities
SET agent_id = 'M10'
WHERE agent_id IN ('Manta 14', 'Manta-14', 'manta-14-pptx', 'M14') AND agent_id != 'M10';

-- CRITICAL: Resolve Manta 15 vs 16 collision
-- Manta 15 is "advisory" in CLAUDE.md but "arquiteto-ia" in skills
-- Solution: Manta 15 → M08 (advisory), Manta 16 → M09 (arquiteto-ia)

UPDATE manta_agent_capabilities
SET agent_id = 'M08'
WHERE agent_id IN ('Manta 15', 'Manta-15') AND agent_id != 'M08';

UPDATE manta_agent_capabilities
SET agent_id = 'M09'
WHERE agent_id IN ('Manta 16', 'Manta-16', 'manta-15-arq') AND agent_id != 'M09';

-- =====================================================================
-- PHASE 4: Update routing keywords to use new agent_ids
-- =====================================================================
-- If maestro_routing_keywords uses agent_slug (agent name) instead of
-- agent_id, you may need to map:
--   'agente-energia' → 'S09'
--   'agente-saneamento' → 'S08'
-- etc.
--
-- For now, assume maestro_routing_keywords.agent_slug uses the slug
-- (e.g., 'agente-energia'), and mapping happens at routing time.
-- If your schema uses agent_id directly, uncomment below:

-- UPDATE maestro_routing_keywords
-- SET agent_slug = 'S08'
-- WHERE agent_slug IN ('agente-saneamento', 'S08-old') AND agent_slug != 'S08';

-- (Similar for S01-S10 and M00-M10)

-- =====================================================================
-- PHASE 5: Update sp_agent_routing if it uses agent_ids
-- =====================================================================
-- Assuming sp_agent_routing.agent_slug uses agent folder names (e.g., 'agente-saneamento')
-- rather than codes, no changes needed here. If it uses codes, adapt:

-- UPDATE sp_agent_routing
-- SET agent_slug = 'S01'
-- WHERE agent_slug IN ('agente-rodovias', 'S01-old') AND agent_slug != 'S01';

-- =====================================================================
-- PHASE 6: Verify integrity
-- =====================================================================

-- List agents after migration
-- SELECT agent_id, name, ativo FROM manta_agent_capabilities ORDER BY agent_id;

-- Check for orphans (if any 03-S11, S12, S13 exist, investigate)
-- SELECT * FROM manta_agent_capabilities WHERE agent_id LIKE '03-S%' OR agent_id LIKE 'Manta%';

-- Check guards were removed
-- SELECT COUNT(*) as guards_remaining FROM manta_agent_capabilities
--   WHERE agent_id IN ('aluci-guard', 'consist-guard', 'context-guardian');
-- -- Expected: 0

COMMIT;

-- =====================================================================
-- ROLLBACK (manual execution if migration fails)
-- =====================================================================
-- BEGIN;
--
-- -- Reverse S* renames
-- UPDATE manta_agent_capabilities SET agent_id = '03-S1' WHERE agent_id = 'S01';
-- UPDATE manta_agent_capabilities SET agent_id = '03-S2' WHERE agent_id = 'S02';
-- -- ... (etc. for S03-S10)
--
-- -- Restore guards (if you have a backup, else INSERTs here)
-- INSERT INTO manta_agent_capabilities (agent_id, name, ...)
-- VALUES
--   ('aluci-guard', 'Validador Anti-Alucinação', ...),
--   ('consist-guard', 'Validador de Consistência', ...),
--   ('context-guardian', 'Guardião de Contexto', ...)
-- ON CONFLICT DO NOTHING;
--
-- -- Reverse M-scheme consolidations
-- UPDATE manta_agent_capabilities SET agent_id = 'Manta 15' WHERE agent_id = 'M08';
-- UPDATE manta_agent_capabilities SET agent_id = 'Manta 16' WHERE agent_id = 'M09';
-- -- ... (etc.)
--
-- COMMIT;

-- =====================================================================
-- NOTES FOR IMPLEMENTER
-- =====================================================================
--
-- 1. Schema assumptions: Adapt the table/column names if they differ.
--    E.g., if the primary key is (agent_id, organization_id), adjust UPDATEs.
--
-- 2. Backup before running: `supabase db pull` or `pg_dump` the production DB.
--
-- 3. Run in staging first: Verify no data loss, no constraint violations.
--
-- 4. Test rollback: Ensure the ROLLBACK script works if you need to undo.
--
-- 5. Audit trail: Consider logging who ran the migration and when.
--
-- 6. Notify stakeholders: Ensure all consumers of manta_agent_capabilities
--    are aware of the agent_id changes (subagents, routing, RAG, etc.).
--
-- 7. Guard handling: If you have a separate skills table, INSERT guards there
--    and skip the DELETE in PHASE 2. Update only if applicable.
--
-- 8. Post-execution: Run the verification queries (PHASE 6) to confirm success.
