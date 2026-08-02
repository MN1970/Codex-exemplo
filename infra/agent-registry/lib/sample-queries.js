'use strict';

const fs = require('fs');
const path = require('path');

/**
 * Produces the 5 sample queries used by the self-test step.
 *
 * Preference order:
 *   1. sharepoint/01-agentes-fundamentais/<agent-id>/prompts/starters.md
 *      if it exists (Manta's real curated prompts, one per quoted
 *      bullet — see e.g. agente-saneamento/prompts/starters.md).
 *   2. Synthesized from `expertise_primary` keywords, so a brand-new
 *      agent with no curated starters.md can still self-test.
 */
function loadSampleQueries(agentRecord, { repoRoot, count = 5 } = {}) {
  const starters = findCuratedStarters(agentRecord.id, repoRoot);
  if (starters.length >= count) return starters.slice(0, count);
  if (starters.length > 0) {
    return starters.concat(synthesize(agentRecord, count - starters.length));
  }
  return synthesize(agentRecord, count);
}

function findCuratedStarters(agentId, repoRoot) {
  if (!repoRoot) return [];
  const starterPath = path.join(
    repoRoot,
    'sharepoint',
    '01-agentes-fundamentais',
    agentId,
    'prompts',
    'starters.md'
  );
  if (!fs.existsSync(starterPath)) return [];

  const raw = fs.readFileSync(starterPath, 'utf8');
  const quoted = [...raw.matchAll(/"([^"]+)"/g)].map((m) => m[1].replace(/\s+/g, ' ').trim());
  return quoted;
}

function synthesize(agentRecord, count) {
  const keywords = (agentRecord.expertise_primary || []).filter(Boolean);
  const pool = keywords.length ? keywords : [agentRecord.name || agentRecord.id];
  const queries = [];
  for (let i = 0; i < count; i += 1) {
    const kw = pool[i % pool.length];
    queries.push(`Preciso de apoio técnico sobre ${kw}. Pode orientar os próximos passos?`);
  }
  return queries;
}

module.exports = { loadSampleQueries };
