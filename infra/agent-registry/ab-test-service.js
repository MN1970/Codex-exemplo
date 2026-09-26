'use strict';

/**
 * ab-test-service.js
 * ------------------------------------------------------------------
 * Implements the A/B test + promotion half of Fase 3.1:
 *
 *   - A new agent that passes self-test starts at 5% traffic for
 *     AB_TEST_DURATION_DAYS (default 7).
 *   - `getTrafficAssignment()` gives the Maestro a deterministic yes/no
 *     for "should THIS request be routed to the new agent" so the same
 *     requester/session sees consistent behavior during the test.
 *   - `runPromotionSweep()` is meant to run on a schedule (cron / Edge
 *     Function). For every agent whose A/B window has ended it checks
 *     health + self-test history and either promotes to 100% traffic
 *     (lifecycle='prod') or rolls back to 0% (promotion_status=
 *     'rolled_back'), logging the decision either way.
 */

const crypto = require('crypto');
const { getSupabaseClient } = require('./lib/supabase-client');
const { logPromotionEvent } = require('./lib/events');

const AB_TEST_TRAFFIC_PERCENT = Number(process.env.AB_TEST_TRAFFIC_PERCENT || 5);
const AB_TEST_DURATION_DAYS = Number(process.env.AB_TEST_DURATION_DAYS || 7);

// Promotion gate thresholds — tune per docs/MANTA-MAESTRO-ECOSYSTEM-v5-UPGRADE.md §8
const PROMOTION_MIN_SUCCESS_RATE = Number(process.env.PROMOTION_MIN_SUCCESS_RATE || 0.9);
const PROMOTION_MAX_ERROR_RATE = Number(process.env.PROMOTION_MAX_ERROR_RATE || 0.1);
const PROMOTION_MAX_AVG_LATENCY_MS = Number(process.env.PROMOTION_MAX_AVG_LATENCY_MS || 30000);

/** Starts the A/B test window for an agent that just passed self-test. */
async function startAbTest(agentId, { trafficPercentage = AB_TEST_TRAFFIC_PERCENT, durationDays = AB_TEST_DURATION_DAYS } = {}) {
  const supabase = getSupabaseClient();
  const startedAt = new Date();
  const endsAt = new Date(startedAt.getTime() + durationDays * 24 * 60 * 60 * 1000);

  const { data, error } = await supabase
    .from('agents')
    .update({
      lifecycle: 'beta',
      promotion_status: 'ab_testing',
      traffic_percentage: trafficPercentage,
      ab_test_started_at: startedAt.toISOString(),
      ab_test_ends_at: endsAt.toISOString(),
      updated_at: startedAt.toISOString(),
    })
    .eq('id', agentId)
    .select()
    .single();

  if (error) throw new Error(`Failed to start A/B test for "${agentId}": ${error.message}`);

  await logPromotionEvent(agentId, 'ab_test_started', {
    before: 0,
    after: trafficPercentage,
    reason: `self-test passed — ${durationDays}d window @ ${trafficPercentage}% traffic`,
  });

  return { agent: data, startedAt, endsAt, trafficPercentage };
}

/**
 * Deterministic bucketing: same requestKey always gets the same
 * in/out decision for a given agent, so a user isn't flip-flopped
 * between old and new agent mid-conversation.
 *
 * @param {string} agentId
 * @param {number} trafficPercentage 0-100
 * @param {string} requestKey any stable per-request/session identifier
 */
function getTrafficAssignment(agentId, trafficPercentage, requestKey) {
  if (trafficPercentage <= 0) return false;
  if (trafficPercentage >= 100) return true;

  const hash = crypto.createHash('sha256').update(`${agentId}:${requestKey}`).digest();
  const bucket = hash.readUInt32BE(0) % 100; // 0-99
  return bucket < trafficPercentage;
}

/** Pulls the metrics needed to decide promote vs. rollback. */
async function collectAbTestMetrics(agentId) {
  const supabase = getSupabaseClient();

  const [{ data: health, error: healthErr }, { data: selfTests, error: stErr }] = await Promise.all([
    supabase
      .from('agent_health')
      .select('status, avg_latency_ms, error_rate_24h, success_count, error_count')
      .eq('agent_id', agentId)
      .order('recorded_at', { ascending: false })
      .limit(20),
    supabase
      .from('agent_self_test_results')
      .select('passed, latency_ms')
      .eq('agent_id', agentId),
  ]);

  if (healthErr) throw new Error(`Failed to read agent_health for "${agentId}": ${healthErr.message}`);
  if (stErr) throw new Error(`Failed to read agent_self_test_results for "${agentId}": ${stErr.message}`);

  const successCount = (health || []).reduce((acc, h) => acc + (h.success_count || 0), 0);
  const errorCount = (health || []).reduce((acc, h) => acc + (h.error_count || 0), 0);
  const totalCalls = successCount + errorCount;

  const successRate = totalCalls > 0 ? successCount / totalCalls : selfTestPassRate(selfTests);
  const errorRate = totalCalls > 0 ? errorCount / totalCalls : 1 - selfTestPassRate(selfTests);
  const avgLatency =
    (health || []).length > 0
      ? average((health || []).map((h) => h.avg_latency_ms).filter((v) => typeof v === 'number'))
      : average((selfTests || []).map((s) => s.latency_ms).filter((v) => typeof v === 'number'));

  return {
    successRate,
    errorRate,
    avgLatencyMs: avgLatency,
    sampleSize: totalCalls > 0 ? totalCalls : (selfTests || []).length,
    source: totalCalls > 0 ? 'agent_health' : 'self_test_fallback',
  };
}

function selfTestPassRate(selfTests) {
  if (!selfTests || selfTests.length === 0) return 0;
  return selfTests.filter((s) => s.passed).length / selfTests.length;
}

function average(values) {
  if (!values.length) return null;
  return values.reduce((a, b) => a + b, 0) / values.length;
}

/** Promotes a single agent to 100% traffic / prod lifecycle. */
async function promoteAgent(agentId, metrics) {
  const supabase = getSupabaseClient();
  const now = new Date().toISOString();

  const { data: before } = await supabase.from('agents').select('traffic_percentage').eq('id', agentId).single();

  const { data, error } = await supabase
    .from('agents')
    .update({
      lifecycle: 'prod',
      promotion_status: 'promoted',
      traffic_percentage: 100,
      promoted_at: now,
      updated_at: now,
    })
    .eq('id', agentId)
    .select()
    .single();

  if (error) throw new Error(`Failed to promote "${agentId}": ${error.message}`);

  await logPromotionEvent(agentId, 'promoted', {
    before: before ? before.traffic_percentage : null,
    after: 100,
    metrics,
    reason: 'A/B test window ended — metrics met promotion thresholds',
  });

  return data;
}

/** Rolls an agent back to 0% traffic after a failed A/B test. */
async function rollbackAgent(agentId, metrics) {
  const supabase = getSupabaseClient();
  const now = new Date().toISOString();

  const { data: before } = await supabase.from('agents').select('traffic_percentage').eq('id', agentId).single();

  const { data, error } = await supabase
    .from('agents')
    .update({
      promotion_status: 'rolled_back',
      traffic_percentage: 0,
      lifecycle: 'alpha',
      updated_at: now,
    })
    .eq('id', agentId)
    .select()
    .single();

  if (error) throw new Error(`Failed to roll back "${agentId}": ${error.message}`);

  await logPromotionEvent(agentId, 'rolled_back', {
    before: before ? before.traffic_percentage : null,
    after: 0,
    metrics,
    reason: 'A/B test window ended — metrics did not meet promotion thresholds',
  });

  return data;
}

/** Decides promote vs. rollback for metrics already collected. */
function isEligibleForPromotion(metrics) {
  if (!metrics) return false;
  if (metrics.successRate < PROMOTION_MIN_SUCCESS_RATE) return false;
  if (metrics.errorRate > PROMOTION_MAX_ERROR_RATE) return false;
  if (metrics.avgLatencyMs != null && metrics.avgLatencyMs > PROMOTION_MAX_AVG_LATENCY_MS) return false;
  return true;
}

/**
 * Scheduled sweep: find every agent whose A/B window has closed and
 * promote/roll back accordingly. Intended to be invoked hourly/daily
 * by a cron trigger (Routine) or Supabase Edge Function.
 */
async function runPromotionSweep() {
  const supabase = getSupabaseClient();
  const nowIso = new Date().toISOString();

  const { data: dueAgents, error } = await supabase
    .from('agents')
    .select('id, ab_test_ends_at')
    .eq('promotion_status', 'ab_testing')
    .lte('ab_test_ends_at', nowIso);

  if (error) throw new Error(`Failed to query due A/B tests: ${error.message}`);

  const outcomes = [];
  for (const row of dueAgents || []) {
    const metrics = await collectAbTestMetrics(row.id);
    if (isEligibleForPromotion(metrics)) {
      const agent = await promoteAgent(row.id, metrics);
      outcomes.push({ agentId: row.id, decision: 'promoted', metrics, agent });
    } else {
      const agent = await rollbackAgent(row.id, metrics);
      outcomes.push({ agentId: row.id, decision: 'rolled_back', metrics, agent });
    }
  }
  return outcomes;
}

module.exports = {
  startAbTest,
  getTrafficAssignment,
  collectAbTestMetrics,
  promoteAgent,
  rollbackAgent,
  isEligibleForPromotion,
  runPromotionSweep,
  AB_TEST_TRAFFIC_PERCENT,
  AB_TEST_DURATION_DAYS,
  PROMOTION_MIN_SUCCESS_RATE,
  PROMOTION_MAX_ERROR_RATE,
  PROMOTION_MAX_AVG_LATENCY_MS,
};

// ---------------------------------------------------------------------
// CLI: node ab-test-service.js sweep
// ---------------------------------------------------------------------
if (require.main === module) {
  const cmd = process.argv[2];
  if (cmd === 'sweep') {
    runPromotionSweep()
      .then((outcomes) => {
        // eslint-disable-next-line no-console
        console.log(JSON.stringify(outcomes, null, 2));
      })
      .catch((err) => {
        // eslint-disable-next-line no-console
        console.error('[ab-test-service] sweep failed:', err);
        process.exit(1);
      });
  } else {
    // eslint-disable-next-line no-console
    console.error('Usage: node ab-test-service.js sweep');
    process.exit(1);
  }
}
