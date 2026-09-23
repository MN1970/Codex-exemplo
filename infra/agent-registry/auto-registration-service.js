'use strict';

/**
 * auto-registration-service.js
 * ------------------------------------------------------------------
 * Implements Fase 3.1 "Agent self-registration" from
 * docs/MANTA-MAESTRO-ECOSYSTEM-v5-UPGRADE.md:
 *
 *   1. Novo agente = apenas um arquivo .claude/agents/meu-agente.md
 *      com frontmatter (name, description, tools, model, e
 *      opcionalmente expertise/rag_collections/handoffs_to).
 *   2. Este serviço lê esse metadata e faz upsert em `agents`
 *      (Supabase) — o Maestro passa a "ver" o agente na próxima
 *      query, sem precisar de deploy.
 *   3. Roda um self-test de 5 sample queries, exigindo latência
 *      < 30s (SELF_TEST_LATENCY_THRESHOLD_MS) e ausência de erro.
 *   4. Se o self-test passar, delega ao ab-test-service para iniciar
 *      o A/B test (5% do tráfego por 1 semana); se falhar, marca
 *      `promotion_status = 'self_test_failed'` e NÃO expõe o agente
 *      ao Maestro em produção.
 *
 * Webhook handler and CLI both call `registerAgentFromFile()` — the
 * single entrypoint of this module.
 */

const crypto = require('crypto');
const { getSupabaseClient } = require('./lib/supabase-client');
const { parseAgentMarkdown } = require('./lib/parse-agent-md');
const { loadSampleQueries } = require('./lib/sample-queries');
const { logPromotionEvent } = require('./lib/events');
const { startAbTest } = require('./ab-test-service');

const SELF_TEST_LATENCY_THRESHOLD_MS = Number(
  process.env.SELF_TEST_LATENCY_THRESHOLD_MS || 30000
);
const SELF_TEST_SAMPLE_SIZE = Number(process.env.SELF_TEST_SAMPLE_SIZE || 5);

/**
 * Default invoker is a stub that just proves the plumbing works.
 * In production this is injected by the caller (webhook handler /
 * Maestro deploy pipeline) and should actually dispatch the query to
 * the new agent (e.g. spin up a Claude Code subagent run) so latency
 * and correctness are measured for real.
 */
async function defaultAgentInvoker(agentRecord, query) {
  throw new Error(
    `No agentInvoker configured — cannot self-test "${agentRecord.id}" for real. ` +
      'Pass { agentInvoker } to registerAgentFromFile()/runSelfTest().'
  );
}

/** Upserts the parsed agent metadata into the `agents` table. */
async function upsertAgent(record, { commitSha } = {}) {
  const supabase = getSupabaseClient();
  const now = new Date().toISOString();

  const existing = await supabase
    .from('agents')
    .select('id, lifecycle, promotion_status')
    .eq('id', record.id)
    .maybeSingle();

  const isNew = !existing.data;

  const row = {
    id: record.id,
    name: record.name,
    description: record.description,
    expertise_primary: record.expertise_primary,
    expertise_secondary: record.expertise_secondary,
    keywords: record.keywords,
    model: record.model,
    skills: record.skills,
    tools: record.tools,
    rag_collections: record.rag_collections,
    handoffs_to: record.handoffs_to,
    version: record.version,
    source_path: record.source_path,
    source_commit: commitSha || null,
    registered_at: now,
    updated_at: now,
    // Only reset the rollout state for a brand-new agent; a
    // re-registration of an already-promoted agent (e.g. doc tweak)
    // should not restart its A/B test from zero.
    ...(isNew
      ? {
          lifecycle: 'alpha',
          traffic_percentage: 0,
          promotion_status: 'pending',
          created_at: now,
        }
      : {}),
  };

  const { data, error } = await supabase
    .from('agents')
    .upsert(row, { onConflict: 'id' })
    .select()
    .single();

  if (error) throw new Error(`Failed to upsert agent "${record.id}": ${error.message}`);

  await logPromotionEvent(record.id, isNew ? 'registered' : 'registered', {
    reason: isNew ? 'new agent file detected' : 're-registration (file updated)',
  });

  return { agent: data, isNew };
}

/**
 * Runs the 5-sample-query self-test and persists each result.
 * Passes only if every query both succeeds and responds within the
 * latency threshold.
 */
async function runSelfTest(agentRecord, { repoRoot, agentInvoker = defaultAgentInvoker } = {}) {
  const queries = loadSampleQueries(agentRecord, { repoRoot, count: SELF_TEST_SAMPLE_SIZE });
  const runId = crypto.randomUUID();
  const supabase = getSupabaseClient();
  const results = [];

  for (const query of queries) {
    const startedAt = Date.now();
    let passed = false;
    let error = null;

    try {
      await agentInvoker(agentRecord, query);
      const latencyMs = Date.now() - startedAt;
      passed = latencyMs < SELF_TEST_LATENCY_THRESHOLD_MS;
      if (!passed) error = `latency ${latencyMs}ms >= threshold ${SELF_TEST_LATENCY_THRESHOLD_MS}ms`;
      results.push({ query, latencyMs, passed, error });
    } catch (err) {
      results.push({
        query,
        latencyMs: Date.now() - startedAt,
        passed: false,
        error: err.message,
      });
    }
  }

  const rows = results.map((r) => ({
    agent_id: agentRecord.id,
    run_id: runId,
    query: r.query,
    passed: r.passed,
    latency_ms: r.latencyMs,
    latency_threshold_ms: SELF_TEST_LATENCY_THRESHOLD_MS,
    error: r.error,
  }));

  const { error: insertError } = await supabase.from('agent_self_test_results').insert(rows);
  if (insertError) {
    // eslint-disable-next-line no-console
    console.error('[agent-registry] failed to persist self-test results:', insertError.message);
  }

  const allPassed = results.every((r) => r.passed);
  return { runId, results, allPassed, sampleSize: queries.length };
}

/**
 * Full pipeline for one agent file: parse → upsert → self-test →
 * (start A/B test | mark failed).
 *
 * @param {string} filePath absolute path to .claude/agents/*.md
 * @param {object} [opts]
 * @param {string} [opts.repoRoot] repo root, used to find prompts/starters.md
 * @param {string} [opts.commitSha] git sha that introduced/changed the file
 * @param {function} [opts.agentInvoker] (agentRecord, query) => Promise — actually dispatches to the agent
 */
async function registerAgentFromFile(filePath, opts = {}) {
  const parsed = parseAgentMarkdown(filePath);
  const { agent, isNew } = await upsertAgent(parsed, { commitSha: opts.commitSha });

  const selfTest = await runSelfTest(agent, {
    repoRoot: opts.repoRoot,
    agentInvoker: opts.agentInvoker,
  });

  const supabase = getSupabaseClient();

  if (selfTest.allPassed) {
    await logPromotionEvent(agent.id, 'self_test_passed', {
      metrics: { sample_size: selfTest.sampleSize, run_id: selfTest.runId },
    });
    await supabase.from('agents').update({ promotion_status: 'ab_testing' }).eq('id', agent.id);
    const abTest = await startAbTest(agent.id);
    return { agent, isNew, selfTest, abTest, status: 'ab_testing' };
  }

  await logPromotionEvent(agent.id, 'self_test_failed', {
    metrics: { sample_size: selfTest.sampleSize, run_id: selfTest.runId, results: selfTest.results },
    reason: 'one or more sample queries failed or exceeded the latency threshold',
  });
  await supabase
    .from('agents')
    .update({ promotion_status: 'self_test_failed', lifecycle: 'alpha', traffic_percentage: 0 })
    .eq('id', agent.id);

  return { agent, isNew, selfTest, abTest: null, status: 'self_test_failed' };
}

/** Marks an agent deprecated when its source .md file is deleted. */
async function deregisterAgentById(agentId, { reason } = {}) {
  const supabase = getSupabaseClient();
  const { error } = await supabase
    .from('agents')
    .update({ lifecycle: 'deprecated', traffic_percentage: 0, updated_at: new Date().toISOString() })
    .eq('id', agentId);
  if (error) throw new Error(`Failed to deregister agent "${agentId}": ${error.message}`);
  await logPromotionEvent(agentId, 'rolled_back', { reason: reason || 'source file removed' });
}

module.exports = {
  registerAgentFromFile,
  runSelfTest,
  upsertAgent,
  deregisterAgentById,
  logPromotionEvent,
  SELF_TEST_LATENCY_THRESHOLD_MS,
  SELF_TEST_SAMPLE_SIZE,
};

// ---------------------------------------------------------------------
// CLI: node auto-registration-service.js .claude/agents/agente-x.md
// ---------------------------------------------------------------------
if (require.main === module) {
  const filePath = process.argv[2];
  if (!filePath) {
    // eslint-disable-next-line no-console
    console.error('Usage: node auto-registration-service.js <path-to-agent.md>');
    process.exit(1);
  }
  const path = require('path');
  registerAgentFromFile(path.resolve(filePath), { repoRoot: path.resolve(__dirname, '..', '..') })
    .then((result) => {
      // eslint-disable-next-line no-console
      console.log(JSON.stringify(result, null, 2));
    })
    .catch((err) => {
      // eslint-disable-next-line no-console
      console.error('[agent-registry] registration failed:', err);
      process.exit(1);
    });
}
