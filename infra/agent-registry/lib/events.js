'use strict';

/**
 * Shared helper to append a row to `agent_promotion_events`.
 * Pulled out of auto-registration-service.js so that module and
 * ab-test-service.js can both log events without a circular
 * require between them (auto-registration-service depends on
 * ab-test-service to kick off the A/B test after a passing
 * self-test; ab-test-service must not depend back on it).
 */

const { getSupabaseClient } = require('./supabase-client');

async function logPromotionEvent(agentId, event, { reason, metrics, before, after } = {}) {
  const supabase = getSupabaseClient();
  const { error } = await supabase.from('agent_promotion_events').insert({
    agent_id: agentId,
    event,
    reason: reason || null,
    metrics: metrics || null,
    traffic_percentage_before: before ?? null,
    traffic_percentage_after: after ?? null,
  });
  if (error) {
    // Non-fatal: telemetry shouldn't block registration/promotion.
    // eslint-disable-next-line no-console
    console.error(`[agent-registry] failed to log event "${event}" for ${agentId}:`, error.message);
  }
}

module.exports = { logPromotionEvent };
