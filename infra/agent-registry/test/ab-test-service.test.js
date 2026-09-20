'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');

const { getTrafficAssignment, isEligibleForPromotion } = require('../ab-test-service');

test('getTrafficAssignment is deterministic per (agentId, requestKey)', () => {
  const a = getTrafficAssignment('agente-saneamento', 5, 'session-123');
  const b = getTrafficAssignment('agente-saneamento', 5, 'session-123');
  assert.equal(a, b);
});

test('getTrafficAssignment respects the 0 and 100 edges without hashing', () => {
  assert.equal(getTrafficAssignment('x', 0, 'anything'), false);
  assert.equal(getTrafficAssignment('x', 100, 'anything'), true);
});

test('getTrafficAssignment roughly matches the requested percentage over many keys', () => {
  const trials = 5000;
  let inBucket = 0;
  for (let i = 0; i < trials; i += 1) {
    if (getTrafficAssignment('agente-x', 5, `req-${i}`)) inBucket += 1;
  }
  const rate = inBucket / trials;
  // 5% target — allow generous tolerance since this is a hash-bucket
  // approximation, not a true RNG.
  assert.ok(rate > 0.02 && rate < 0.09, `expected ~5% assignment, got ${rate}`);
});

test('isEligibleForPromotion enforces success/error/latency thresholds', () => {
  assert.equal(
    isEligibleForPromotion({ successRate: 0.95, errorRate: 0.05, avgLatencyMs: 5000 }),
    true
  );
  assert.equal(
    isEligibleForPromotion({ successRate: 0.5, errorRate: 0.5, avgLatencyMs: 5000 }),
    false
  );
  assert.equal(
    isEligibleForPromotion({ successRate: 0.95, errorRate: 0.05, avgLatencyMs: 45000 }),
    false
  );
  assert.equal(isEligibleForPromotion(null), false);
});
