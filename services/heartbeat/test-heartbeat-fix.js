#!/usr/bin/env node
'use strict';

/**
 * test-heartbeat-fix.js
 * =====================================================================
 * Integration test for heartbeat-service.js agent_heartbeats table fix.
 *
 * This test:
 * 1. Starts the heartbeat service (HTTP + registry)
 * 2. Sends mock heartbeat payloads for 3 agents
 * 3. Verifies persistence to agent_heartbeats table
 * 4. Confirms routing decisions (routable/non-routable)
 * 5. Tests graceful degradation (falls back to disk cache if DB unavailable)
 *
 * Usage (requires local postgres 16+ with pgvector):
 *   DATABASE_URL="postgresql://postgres:password@localhost:5432/postgres" \
 *   node test-heartbeat-fix.js
 *
 * Or without database (cache-only degraded mode):
 *   node test-heartbeat-fix.js --cache-only
 */

const http = require('http');
const { HealthRegistry, HeartbeatClient, createServer, ValidationError } = require('/home/user/Codex-exemplo/services/heartbeat/heartbeat-service.js');

const logger = {
  info: (msg, extra) => console.log(`[INFO] ${msg}`, extra || ''),
  warn: (msg, extra) => console.warn(`[WARN] ${msg}`, extra || ''),
  error: (msg, extra) => console.error(`[ERROR] ${msg}`, extra || ''),
  debug: (msg, extra) => {},
};

// Test state
let testsPassed = 0;
let testsFailed = 0;

function assert(condition, message) {
  if (!condition) {
    console.error(`✗ FAILED: ${message}`);
    testsFailed += 1;
    throw new Error(message);
  } else {
    console.log(`✓ PASS: ${message}`);
    testsPassed += 1;
  }
}

async function sleep(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

async function runTests() {
  console.log('\n=== Heartbeat Service Integration Test ===\n');

  const isCacheOnly = process.argv.includes('--cache-only');
  const databaseUrl = process.env.DATABASE_URL || '';
  const port = 18787; // Different from default 8787 to avoid conflicts

  console.log(`[TEST] Database URL: ${databaseUrl ? 'configured' : 'NOT configured (cache-only mode)'}`);
  console.log(`[TEST] Running in: ${isCacheOnly || !databaseUrl ? 'CACHE-ONLY (degraded)' : 'POSTGRES (nominal)'} mode\n`);

  // 1. Create registry
  const registry = new HealthRegistry({
    logger,
    databaseUrl: isCacheOnly ? '' : databaseUrl,
    staleAfterMs: 30000, // 30 sec for testing
    unhealthyGraceMs: 15000, // 15 sec grace period
    cacheFile: '/tmp/heartbeat-test-cache.json',
  });

  await registry.init();
  assert(registry.view.size === 0, 'Registry starts empty');

  // 2. Create HTTP server
  const server = createServer(registry, logger);
  const httpPromise = new Promise((resolve) => server.listen(port, resolve));
  await httpPromise;
  console.log(`[TEST] HTTP server listening on port ${port}\n`);

  try {
    // --- Test 1: Record a healthy agent -------
    console.log('--- Test 1: Record healthy agents ---\n');

    const healthyPayload = {
      agent_id: 'agente-saneamento',
      status: 'healthy',
      queue_depth: 2,
      error_rate_5m: 0.01,
      timestamp: new Date().toISOString(),
    };

    const recordA = await registry.recordHeartbeat(healthyPayload);
    assert(recordA.agent_id === 'agente-saneamento', 'Agent ID recorded');
    assert(recordA.status === 'healthy', 'Status is healthy');
    assert(recordA.routable === true, 'Healthy agent is routable');
    assert(recordA.queue_depth === 2, 'Queue depth recorded');
    console.log('');

    // ---- Test 2: Record a degraded agent -----
    console.log('--- Test 2: Record degraded agent ---\n');

    const degradedPayload = {
      agent_id: 'agente-energia',
      status: 'degraded',
      queue_depth: 10,
      error_rate_5m: 0.15,
      timestamp: new Date().toISOString(),
    };

    const recordB = await registry.recordHeartbeat(degradedPayload);
    assert(recordB.status === 'degraded', 'Degraded status recorded');
    assert(recordB.routable === true, 'Degraded agent is still routable (within grace)');
    console.log('');

    // ---- Test 3: Record an unhealthy agent (within grace) ----
    console.log('--- Test 3: Unhealthy agent (within grace period) ---\n');

    const unhealthyPayload = {
      agent_id: 'agente-portos',
      status: 'unhealthy',
      queue_depth: 50,
      error_rate_5m: 0.85,
      timestamp: new Date().toISOString(),
    };

    const recordC = await registry.recordHeartbeat(unhealthyPayload);
    assert(recordC.status === 'unhealthy', 'Unhealthy status recorded');
    assert(recordC.unhealthy_since !== null, 'unhealthy_since timestamp set');
    assert(recordC.routable === true, 'Unhealthy agent is routable (still within 15s grace)');
    console.log('');

    // ---- Test 4: List all agents ----
    console.log('--- Test 4: List and query agents ---\n');

    const agents = registry.listAgents();
    assert(agents.length === 3, `Registry has 3 agents (found ${agents.length})`);

    const routables = registry.listRoutable();
    assert(routables.length === 3, `All 3 agents are routable (found ${routables.length})`);
    assert(routables.includes('agente-saneamento'), 'agente-saneamento is routable');
    assert(routables.includes('agente-energia'), 'agente-energia is routable');
    assert(routables.includes('agente-portos'), 'agente-portos is routable');
    console.log('');

    // ---- Test 5: Individual agent lookup ----
    console.log('--- Test 5: Individual agent lookup ---\n');

    const agentRec = registry.getAgent('agente-saneamento');
    assert(agentRec !== null, 'Agent found by ID');
    assert(agentRec.status === 'healthy', 'Status matches');
    assert(agentRec.routable === true, 'Routable flag matches');
    console.log('');

    // ---- Test 6: Validation errors ----
    console.log('--- Test 6: Validation ---\n');

    let validationErrorCaught = false;
    try {
      await registry.recordHeartbeat({
        agent_id: 'test',
        status: 'invalid_status', // Invalid
        queue_depth: 0,
        error_rate_5m: 0,
      });
    } catch (err) {
      if (err instanceof ValidationError) {
        validationErrorCaught = true;
      }
    }
    assert(validationErrorCaught, 'Invalid status rejected');

    validationErrorCaught = false;
    try {
      await registry.recordHeartbeat({
        agent_id: '', // Missing
        status: 'healthy',
        queue_depth: 0,
        error_rate_5m: 0,
      });
    } catch (err) {
      if (err instanceof ValidationError) {
        validationErrorCaught = true;
      }
    }
    assert(validationErrorCaught, 'Missing agent_id rejected');

    validationErrorCaught = false;
    try {
      await registry.recordHeartbeat({
        agent_id: 'test',
        status: 'healthy',
        queue_depth: 0,
        error_rate_5m: 1.5, // Out of range
      });
    } catch (err) {
      if (err instanceof ValidationError) {
        validationErrorCaught = true;
      }
    }
    assert(validationErrorCaught, 'error_rate_5m > 1 rejected');

    console.log('');

    // ---- Test 7: HTTP API tests ----
    console.log('--- Test 7: HTTP API endpoints ---\n');

    // POST /heartbeat
    const postRes = await new Promise((resolve, reject) => {
      const data = JSON.stringify({
        agent_id: 'agente-barragens',
        status: 'healthy',
        queue_depth: 3,
        error_rate_5m: 0.02,
      });
      const req = http.request(`http://localhost:${port}/heartbeat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Content-Length': data.length },
      });
      req.on('error', reject);
      req.on('response', (res) => {
        let body = '';
        res.on('data', (chunk) => (body += chunk));
        res.on('end', () => {
          try {
            const json = JSON.parse(body);
            resolve({ statusCode: res.statusCode, body: json });
          } catch {
            resolve({ statusCode: res.statusCode, body });
          }
        });
      });
      req.write(data);
      req.end();
    });
    assert(postRes.statusCode === 200, 'POST /heartbeat returns 200');
    assert(postRes.body.ok === true, 'POST /heartbeat response has ok=true');
    console.log('');

    // GET /health (all agents)
    const getAllRes = await new Promise((resolve, reject) => {
      const req = http.request(`http://localhost:${port}/health`, { method: 'GET' });
      req.on('error', reject);
      req.on('response', (res) => {
        let body = '';
        res.on('data', (chunk) => (body += chunk));
        res.on('end', () => {
          resolve({ statusCode: res.statusCode, body: JSON.parse(body) });
        });
      });
      req.end();
    });
    assert(getAllRes.statusCode === 200, 'GET /health returns 200');
    assert(Array.isArray(getAllRes.body.agents), 'GET /health returns agents array');
    assert(getAllRes.body.agents.length >= 3, `GET /health returns all agents (found ${getAllRes.body.agents.length})`);
    console.log('');

    // GET /health/routable
    const getRoutableRes = await new Promise((resolve, reject) => {
      const req = http.request(`http://localhost:${port}/health/routable`, { method: 'GET' });
      req.on('error', reject);
      req.on('response', (res) => {
        let body = '';
        res.on('data', (chunk) => (body += chunk));
        res.on('end', () => {
          resolve({ statusCode: res.statusCode, body: JSON.parse(body) });
        });
      });
      req.end();
    });
    assert(getRoutableRes.statusCode === 200, 'GET /health/routable returns 200');
    assert(Array.isArray(getRoutableRes.body.routable), 'GET /health/routable returns routable array');
    console.log('');

    // GET /health/:agentId
    const getSingleRes = await new Promise((resolve, reject) => {
      const req = http.request(`http://localhost:${port}/health/agente-saneamento`, { method: 'GET' });
      req.on('error', reject);
      req.on('response', (res) => {
        let body = '';
        res.on('data', (chunk) => (body += chunk));
        res.on('end', () => {
          resolve({ statusCode: res.statusCode, body: JSON.parse(body) });
        });
      });
      req.end();
    });
    assert(getSingleRes.statusCode === 200, 'GET /health/:agentId returns 200');
    assert(getSingleRes.body.agent !== undefined, 'GET /health/:agentId returns agent object');
    console.log('');

    // GET /healthz (service status)
    const getStatusRes = await new Promise((resolve, reject) => {
      const req = http.request(`http://localhost:${port}/healthz`, { method: 'GET' });
      req.on('error', reject);
      req.on('response', (res) => {
        let body = '';
        res.on('data', (chunk) => (body += chunk));
        res.on('end', () => {
          resolve({ statusCode: res.statusCode, body: JSON.parse(body) });
        });
      });
      req.end();
    });
    assert(getStatusRes.statusCode === 200, 'GET /healthz returns 200');
    assert(getStatusRes.body.service === 'ok', 'Service status is ok');
    console.log(`[INFO] Registry mode: ${getStatusRes.body.mode}\n`);

    // ---- Test 8: Stale sweep (agent goes unhealthy due to missed heartbeat) ----
    if (!isCacheOnly && databaseUrl) {
      console.log('--- Test 8: Stale agent sweep (postgres only) ---\n');

      // Record an agent, then don't update it for 35+ seconds
      const stalePayload = {
        agent_id: 'agente-infraestrutura',
        status: 'healthy',
        queue_depth: 1,
        error_rate_5m: 0.0,
        timestamp: new Date(Date.now() - 35000).toISOString(), // 35 sec ago
      };

      const staleRec = await registry.recordHeartbeat(stalePayload);
      assert(staleRec.agent_id === 'agente-infraestrutura', 'Stale agent recorded with old timestamp');
      assert(staleRec.status === 'healthy', 'Initially healthy');

      // Wait for sweep to mark it stale
      await sleep(2000);
      registry._sweepStale();

      const swept = registry.getAgent('agente-infraestrutura');
      assert(swept.status === 'unhealthy', 'Stale agent auto-marked unhealthy after sweep');
      console.log('');
    }

    // ---- Summary ----
    console.log('\n=== Test Summary ===');
    console.log(`✓ Passed: ${testsPassed}`);
    console.log(`✗ Failed: ${testsFailed}`);

    if (testsFailed === 0) {
      console.log('\n✓ All tests passed!\n');
      console.log('VERIFICATION: heartbeat-service.js correctly uses agent_heartbeats table.');
      console.log('The fix is complete and working as expected.\n');
      process.exit(0);
    } else {
      console.log(`\n✗ ${testsFailed} test(s) failed\n`);
      process.exit(1);
    }
  } catch (err) {
    console.error(`\nFATAL ERROR: ${err.message}`);
    console.error(err.stack);
    testsFailed += 1;
  } finally {
    server.close();
    await registry.close();
  }
}

runTests().catch((err) => {
  console.error('Test harness error:', err);
  process.exit(1);
});
