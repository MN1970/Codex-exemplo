#!/usr/bin/env node
'use strict';

/**
 * heartbeat-service.js
 * ---------------------------------------------------------------------
 * Agent Heartbeat Service for Manta Maestro.
 *
 * Provides three composable pieces in a single file:
 *
 *   1. HeartbeatClient  — runs inside every agent process. Every
 *      `intervalMs` (default 5 min) it collects a status snapshot and
 *      POSTs it to the registry. Never throws into the host agent: any
 *      send failure is logged and retried on the next tick.
 *
 *   2. HealthRegistry    — the source of truth for agent health. Holds
 *      an in-memory "health view" (always authoritative and fast),
 *      write-through-persists it to Postgres (`agent_health` table),
 *      and falls back to a local disk cache whenever Postgres is
 *      unreachable ("graceful degradation"). Exposes `isRoutable()`
 *      so the Maestro router can make a synchronous yes/no decision
 *      without ever blocking on a DB round-trip.
 *
 *   3. HTTP server        — thin core-`http` layer (no external web
 *      framework dependency) exposing the registry over HTTP so
 *      agents and the Maestro router can be separate processes.
 *
 * Routing rule implemented (per spec):
 *   Maestro never routes to an agent whose status has been
 *   "unhealthy" for more than UNHEALTHY_GRACE_MS (default 10 min).
 *   An agent that simply stops sending heartbeats is treated as
 *   having gone unhealthy at the moment it became stale
 *   (STALE_AFTER_MS, default 2x the heartbeat interval).
 *
 * Run directly for a local demo:
 *   node heartbeat-service.js
 *
 * See README section at the bottom of this file (SETUP INSTRUCTIONS)
 * for environment variables, the SQL schema, and integration snippets.
 * ---------------------------------------------------------------------
 */

const http = require('http');
const https = require('https');
const fs = require('fs');
const path = require('path');
const { URL } = require('url');
const EventEmitter = require('events');

// ---------------------------------------------------------------------
// Config (all overridable via env vars)
// ---------------------------------------------------------------------

const CONFIG = {
  PORT: parseInt(process.env.HEARTBEAT_PORT || '8787', 10),
  HOST: process.env.HEARTBEAT_HOST || '0.0.0.0',
  DATABASE_URL: process.env.DATABASE_URL || process.env.SUPABASE_DB_URL || '',
  API_KEY: process.env.HEARTBEAT_API_KEY || '', // optional shared-secret auth
  HEARTBEAT_INTERVAL_MS: parseInt(process.env.HEARTBEAT_INTERVAL_MS || String(5 * 60 * 1000), 10), // 5 min
  // An agent that hasn't been heard from in this long is treated as stale/unhealthy.
  STALE_AFTER_MS: parseInt(
    process.env.HEARTBEAT_STALE_AFTER_MS || String(2 * 5 * 60 * 1000), // 2x interval = 10 min
    10
  ),
  // Grace period: an agent must be continuously unhealthy for this long
  // before the router is told to stop sending it traffic.
  UNHEALTHY_GRACE_MS: parseInt(process.env.HEARTBEAT_UNHEALTHY_GRACE_MS || String(10 * 60 * 1000), 10), // 10 min
  CACHE_FILE: process.env.HEARTBEAT_CACHE_FILE || path.join(__dirname, '.cache', 'agent-health-cache.json'),
  CACHE_FLUSH_INTERVAL_MS: parseInt(process.env.HEARTBEAT_CACHE_FLUSH_INTERVAL_MS || '30000', 10), // 30s
  DB_RETRY_BACKOFF_MS: parseInt(process.env.HEARTBEAT_DB_RETRY_BACKOFF_MS || '5000', 10),
  DB_RETRY_BACKOFF_MAX_MS: parseInt(process.env.HEARTBEAT_DB_RETRY_BACKOFF_MAX_MS || '120000', 10),
};

const VALID_STATUSES = new Set(['healthy', 'degraded', 'unhealthy']);

// ---------------------------------------------------------------------
// Logger — tiny structured logger, no dependency needed.
// ---------------------------------------------------------------------

function makeLogger(scope) {
  const fmt = (level, msg, extra) => {
    const line = {
      ts: new Date().toISOString(),
      level,
      scope,
      msg,
      ...(extra ? { extra } : {}),
    };
    return JSON.stringify(line);
  };
  return {
    info: (msg, extra) => console.log(fmt('info', msg, extra)),
    warn: (msg, extra) => console.warn(fmt('warn', msg, extra)),
    error: (msg, extra) => console.error(fmt('error', msg, extra)),
    debug: (msg, extra) => {
      if (process.env.HEARTBEAT_DEBUG) console.log(fmt('debug', msg, extra));
    },
  };
}

// ---------------------------------------------------------------------
// Disk-backed cache (graceful degradation store)
// ---------------------------------------------------------------------
// Survives process restarts even if Postgres/Supabase is unreachable
// for the entire lifetime of the process. Written atomically (write to
// tmp file + rename) so a crash mid-write can't corrupt it.

class DiskCache {
  constructor(filePath, logger) {
    this.filePath = filePath;
    this.logger = logger;
  }

  ensureDir() {
    const dir = path.dirname(this.filePath);
    fs.mkdirSync(dir, { recursive: true });
  }

  load() {
    try {
      const raw = fs.readFileSync(this.filePath, 'utf8');
      return JSON.parse(raw);
    } catch (err) {
      if (err.code !== 'ENOENT') {
        this.logger.warn('disk cache load failed, starting empty', { error: err.message });
      }
      return {};
    }
  }

  save(dataObj) {
    try {
      this.ensureDir();
      const tmp = `${this.filePath}.tmp-${process.pid}`;
      fs.writeFileSync(tmp, JSON.stringify(dataObj, null, 2), 'utf8');
      fs.renameSync(tmp, this.filePath);
    } catch (err) {
      this.logger.error('disk cache save failed', { error: err.message });
    }
  }
}

// ---------------------------------------------------------------------
// Postgres store (optional — service degrades gracefully without it)
// ---------------------------------------------------------------------
// Uses `pg` if it's installed. Lazily required so this file still runs
// (in cache-only / degraded mode) even if `pg` was never `npm install`ed.

const AGENT_HEALTH_TABLE_DDL = `
CREATE TABLE IF NOT EXISTS agent_health (
  agent_id           TEXT PRIMARY KEY,
  status             TEXT NOT NULL CHECK (status IN ('healthy','degraded','unhealthy')),
  queue_depth        INTEGER NOT NULL DEFAULT 0,
  error_rate_5m      NUMERIC NOT NULL DEFAULT 0,
  last_heartbeat_at  TIMESTAMPTZ NOT NULL,
  unhealthy_since    TIMESTAMPTZ,
  routable           BOOLEAN NOT NULL DEFAULT TRUE,
  updated_at         TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_agent_health_status ON agent_health (status);
`;

class PostgresStore {
  constructor(databaseUrl, logger) {
    this.databaseUrl = databaseUrl;
    this.logger = logger;
    this.pool = null;
    this.available = false;
  }

  async init() {
    if (!this.databaseUrl) {
      this.logger.warn('DATABASE_URL not set — running in cache-only (degraded) mode by design');
      return;
    }
    let PgPool;
    try {
      // eslint-disable-next-line global-require
      ({ Pool: PgPool } = require('pg'));
    } catch (err) {
      this.logger.warn('`pg` package not installed — running in cache-only (degraded) mode', {
        hint: 'npm install pg',
      });
      return;
    }
    try {
      this.pool = new PgPool({ connectionString: this.databaseUrl, max: 5, connectionTimeoutMillis: 5000 });
      await this.pool.query(AGENT_HEALTH_TABLE_DDL);
      this.available = true;
      this.logger.info('Postgres store ready (agent_health table ensured)');
    } catch (err) {
      this.logger.error('Postgres init failed — falling back to cache-only mode', { error: err.message });
      this.available = false;
    }
  }

  async upsert(record) {
    if (!this.available) throw new Error('postgres store unavailable');
    const sql = `
      INSERT INTO agent_health
        (agent_id, status, queue_depth, error_rate_5m, last_heartbeat_at, unhealthy_since, routable, updated_at)
      VALUES ($1,$2,$3,$4,$5,$6,$7, NOW())
      ON CONFLICT (agent_id) DO UPDATE SET
        status = EXCLUDED.status,
        queue_depth = EXCLUDED.queue_depth,
        error_rate_5m = EXCLUDED.error_rate_5m,
        last_heartbeat_at = EXCLUDED.last_heartbeat_at,
        unhealthy_since = EXCLUDED.unhealthy_since,
        routable = EXCLUDED.routable,
        updated_at = NOW();
    `;
    await this.pool.query(sql, [
      record.agent_id,
      record.status,
      record.queue_depth,
      record.error_rate_5m,
      record.last_heartbeat_at,
      record.unhealthy_since,
      record.routable,
    ]);
  }

  async listAll() {
    if (!this.available) throw new Error('postgres store unavailable');
    const { rows } = await this.pool.query('SELECT * FROM agent_health ORDER BY agent_id');
    return rows;
  }

  async close() {
    if (this.pool) await this.pool.end().catch(() => {});
  }
}

// ---------------------------------------------------------------------
// HealthRegistry — the authoritative, always-available health view.
// ---------------------------------------------------------------------

class HealthRegistry extends EventEmitter {
  constructor(opts = {}) {
    super();
    this.logger = opts.logger || makeLogger('registry');
    this.staleAfterMs = opts.staleAfterMs ?? CONFIG.STALE_AFTER_MS;
    this.unhealthyGraceMs = opts.unhealthyGraceMs ?? CONFIG.UNHEALTHY_GRACE_MS;
    this.diskCache = new DiskCache(opts.cacheFile || CONFIG.CACHE_FILE, this.logger);
    this.pg = new PostgresStore(opts.databaseUrl ?? CONFIG.DATABASE_URL, this.logger);

    // In-memory authoritative view: agent_id -> record
    this.view = new Map();
    // Records that failed to persist to Postgres and need a retry.
    this.pendingWrites = new Map();
    this.dbDegraded = false;
    this._staleSweepTimer = null;
    this._flushTimer = null;
  }

  async init() {
    // 1) Load whatever we had cached on disk from a previous run so
    //    routing decisions are sane even before the first Postgres query.
    const cached = this.diskCache.load();
    for (const [agentId, record] of Object.entries(cached)) {
      this.view.set(agentId, record);
    }

    // 2) Try Postgres. If it fails, we simply keep running off the cache.
    await this.pg.init();
    if (this.pg.available) {
      try {
        const rows = await this.pg.listAll();
        for (const row of rows) {
          this.view.set(row.agent_id, this._rowToRecord(row));
        }
        this.logger.info('hydrated health view from Postgres', { agents: rows.length });
      } catch (err) {
        this.logger.warn('initial Postgres hydration failed, using disk cache only', { error: err.message });
        this.dbDegraded = true;
      }
    } else {
      this.dbDegraded = true;
    }

    // 3) Periodically re-evaluate staleness (agents that stopped
    //    heartbeating without ever reporting "unhealthy" explicitly).
    this._staleSweepTimer = setInterval(() => this._sweepStale(), Math.min(this.staleAfterMs, 60000));
    this._staleSweepTimer.unref?.();

    // 4) Periodically retry flushing anything Postgres rejected while degraded.
    this._flushTimer = setInterval(() => this._flushPending(), CONFIG.CACHE_FLUSH_INTERVAL_MS);
    this._flushTimer.unref?.();
  }

  _rowToRecord(row) {
    return {
      agent_id: row.agent_id,
      status: row.status,
      queue_depth: Number(row.queue_depth),
      error_rate_5m: Number(row.error_rate_5m),
      last_heartbeat_at: new Date(row.last_heartbeat_at).toISOString(),
      unhealthy_since: row.unhealthy_since ? new Date(row.unhealthy_since).toISOString() : null,
      routable: !!row.routable,
    };
  }

  /**
   * Ingest one heartbeat payload: {agent_id, status, queue_depth, error_rate_5m, timestamp}
   */
  async recordHeartbeat(payload) {
    const { agent_id, status, queue_depth, error_rate_5m, timestamp } = payload;

    if (!agent_id || typeof agent_id !== 'string') {
      throw new ValidationError('agent_id is required and must be a string');
    }
    if (!VALID_STATUSES.has(status)) {
      throw new ValidationError(`status must be one of: ${[...VALID_STATUSES].join(', ')}`);
    }
    if (queue_depth !== undefined && (typeof queue_depth !== 'number' || queue_depth < 0)) {
      throw new ValidationError('queue_depth must be a non-negative number');
    }
    if (error_rate_5m !== undefined && (typeof error_rate_5m !== 'number' || error_rate_5m < 0 || error_rate_5m > 1)) {
      throw new ValidationError('error_rate_5m must be a number between 0 and 1');
    }

    const now = new Date();
    const heartbeatAt = timestamp ? new Date(timestamp) : now;
    if (Number.isNaN(heartbeatAt.getTime())) {
      throw new ValidationError('timestamp is not a valid date');
    }

    const previous = this.view.get(agent_id);
    const wasUnhealthy = previous?.status === 'unhealthy';
    const isUnhealthy = status === 'unhealthy';

    // Track how long the agent has been continuously unhealthy so we can
    // apply the 10-minute grace period, rather than yanking it out of
    // rotation on a single bad report.
    let unhealthySince = null;
    if (isUnhealthy) {
      unhealthySince = wasUnhealthy && previous.unhealthy_since ? previous.unhealthy_since : heartbeatAt.toISOString();
    }

    const record = {
      agent_id,
      status,
      queue_depth: queue_depth ?? 0,
      error_rate_5m: error_rate_5m ?? 0,
      last_heartbeat_at: heartbeatAt.toISOString(),
      unhealthy_since: unhealthySince,
      routable: true, // recomputed below
    };
    record.routable = this._computeRoutable(record, now);

    // Write-through: the in-memory view is authoritative and updated
    // synchronously so isRoutable() never blocks on I/O.
    this.view.set(agent_id, record);
    this._persistCacheSnapshot();

    // Best-effort async persistence to Postgres. Failures degrade
    // gracefully: the record stays valid in `view`/disk cache and is
    // queued for retry.
    await this._tryPersist(record);

    this.emit('heartbeat', record);
    return record;
  }

  async _tryPersist(record) {
    if (!this.pg.available) {
      this.pendingWrites.set(record.agent_id, record);
      return;
    }
    try {
      await this.pg.upsert(record);
      this.pendingWrites.delete(record.agent_id);
      if (this.dbDegraded) {
        this.logger.info('Postgres connectivity restored');
        this.dbDegraded = false;
      }
    } catch (err) {
      this.dbDegraded = true;
      this.pendingWrites.set(record.agent_id, record);
      this.logger.warn('failed to persist heartbeat to Postgres, using cache fallback', {
        agent_id: record.agent_id,
        error: err.message,
      });
    }
  }

  async _flushPending() {
    if (!this.pg.available || this.pendingWrites.size === 0) return;
    for (const [agentId, record] of this.pendingWrites) {
      try {
        await this.pg.upsert(record);
        this.pendingWrites.delete(agentId);
      } catch (err) {
        this.logger.warn('retry flush to Postgres still failing', { agent_id: agentId, error: err.message });
        break; // stop this pass; try again next tick
      }
    }
    if (this.pendingWrites.size === 0) this.dbDegraded = false;
  }

  _persistCacheSnapshot() {
    const obj = {};
    for (const [agentId, record] of this.view) obj[agentId] = record;
    this.diskCache.save(obj);
  }

  /** Re-evaluate every agent for staleness (missed heartbeats). */
  _sweepStale() {
    const now = new Date();
    let changed = false;
    for (const [agentId, record] of this.view) {
      const routableBefore = record.routable;
      const lastSeen = new Date(record.last_heartbeat_at).getTime();
      const isStale = now.getTime() - lastSeen > this.staleAfterMs;

      if (isStale && record.status !== 'unhealthy') {
        record.status = 'unhealthy';
        record.unhealthy_since = record.unhealthy_since || new Date(lastSeen + this.staleAfterMs).toISOString();
        this.logger.warn('agent marked unhealthy due to missed heartbeats', { agent_id: agentId });
        changed = true;
      }

      record.routable = this._computeRoutable(record, now);
      if (record.routable !== routableBefore) changed = true;
    }
    if (changed) {
      this._persistCacheSnapshot();
      // Fire-and-forget persistence of the recomputed rows.
      for (const record of this.view.values()) this._tryPersist(record).catch(() => {});
    }
  }

  /**
   * Core routing rule: an agent is NOT routable once it has been
   * continuously "unhealthy" for longer than `unhealthyGraceMs`
   * (default 10 minutes). Anything else (healthy, degraded, or a
   * brand-new unhealthy report still inside the grace window) is
   * routable.
   */
  _computeRoutable(record, now = new Date()) {
    if (record.status !== 'unhealthy') return true;
    if (!record.unhealthy_since) return true;
    const downForMs = now.getTime() - new Date(record.unhealthy_since).getTime();
    return downForMs <= this.unhealthyGraceMs;
  }

  /** Synchronous, allocation-light check used by the Maestro router. */
  isRoutable(agentId) {
    const record = this.view.get(agentId);
    if (!record) return false; // unknown agent = never seen a heartbeat = not routable
    return this._computeRoutable(record);
  }

  getAgent(agentId) {
    const record = this.view.get(agentId);
    if (!record) return null;
    return { ...record, routable: this._computeRoutable(record) };
  }

  listAgents() {
    const now = new Date();
    return [...this.view.values()].map((r) => ({ ...r, routable: this._computeRoutable(r, now) }));
  }

  listRoutable() {
    return this.listAgents()
      .filter((r) => r.routable)
      .map((r) => r.agent_id);
  }

  status() {
    return {
      mode: this.dbDegraded ? 'degraded (cache fallback)' : 'nominal (postgres)',
      postgres_available: this.pg.available,
      pending_writes: this.pendingWrites.size,
      agents_tracked: this.view.size,
    };
  }

  async close() {
    clearInterval(this._staleSweepTimer);
    clearInterval(this._flushTimer);
    this._persistCacheSnapshot();
    await this.pg.close();
  }
}

class ValidationError extends Error {
  constructor(message) {
    super(message);
    this.name = 'ValidationError';
    this.statusCode = 400;
  }
}

// ---------------------------------------------------------------------
// HTTP layer (core `http`, zero web-framework dependency)
// ---------------------------------------------------------------------

function readJsonBody(req, limitBytes = 1024 * 64) {
  return new Promise((resolve, reject) => {
    let size = 0;
    const chunks = [];
    req.on('data', (chunk) => {
      size += chunk.length;
      if (size > limitBytes) {
        reject(new ValidationError('request body too large'));
        req.destroy();
        return;
      }
      chunks.push(chunk);
    });
    req.on('end', () => {
      if (chunks.length === 0) return resolve({});
      try {
        resolve(JSON.parse(Buffer.concat(chunks).toString('utf8')));
      } catch (err) {
        reject(new ValidationError('invalid JSON body'));
      }
    });
    req.on('error', reject);
  });
}

function sendJson(res, statusCode, payload) {
  const body = JSON.stringify(payload);
  res.writeHead(statusCode, {
    'Content-Type': 'application/json; charset=utf-8',
    'Content-Length': Buffer.byteLength(body),
  });
  res.end(body);
}

function authorized(req) {
  if (!CONFIG.API_KEY) return true; // auth disabled
  const header = req.headers['x-api-key'] || '';
  return header === CONFIG.API_KEY;
}

function createServer(registry, logger) {
  return http.createServer(async (req, res) => {
    const url = new URL(req.url, `http://${req.headers.host || 'localhost'}`);
    logger.debug('request', { method: req.method, path: url.pathname });

    try {
      if (!authorized(req)) {
        return sendJson(res, 401, { error: 'unauthorized' });
      }

      if (req.method === 'POST' && url.pathname === '/heartbeat') {
        const body = await readJsonBody(req);
        const record = await registry.recordHeartbeat(body);
        return sendJson(res, 200, { ok: true, record });
      }

      if (req.method === 'GET' && url.pathname === '/health') {
        return sendJson(res, 200, { agents: registry.listAgents() });
      }

      if (req.method === 'GET' && url.pathname === '/health/routable') {
        return sendJson(res, 200, { routable: registry.listRoutable() });
      }

      const singleMatch = url.pathname.match(/^\/health\/([^/]+)$/);
      if (req.method === 'GET' && singleMatch) {
        const agentId = decodeURIComponent(singleMatch[1]);
        const record = registry.getAgent(agentId);
        if (!record) return sendJson(res, 404, { error: 'unknown agent_id', agent_id: agentId });
        return sendJson(res, 200, { agent: record });
      }

      if (req.method === 'GET' && url.pathname === '/healthz') {
        return sendJson(res, 200, { service: 'ok', ...registry.status() });
      }

      return sendJson(res, 404, { error: 'not found' });
    } catch (err) {
      const statusCode = err.statusCode || 500;
      if (statusCode >= 500) logger.error('request handler error', { error: err.message });
      return sendJson(res, statusCode, { error: err.message });
    }
  });
}

// ---------------------------------------------------------------------
// HeartbeatClient — runs inside each agent process.
// ---------------------------------------------------------------------

class HeartbeatClient {
  /**
   * @param {object} opts
   * @param {string} opts.agentId          e.g. "agente-saneamento"
   * @param {string} [opts.registryUrl]    e.g. "http://localhost:8787"
   * @param {function} [opts.statusProvider] async () => {status, queue_depth, error_rate_5m}
   *   Defaults to always reporting healthy/0/0 — replace with real
   *   agent introspection (queue length, rolling error rate, etc).
   * @param {number} [opts.intervalMs]     default 5 minutes
   * @param {string} [opts.apiKey]
   */
  constructor(opts) {
    if (!opts || !opts.agentId) throw new Error('HeartbeatClient requires { agentId }');
    this.agentId = opts.agentId;
    this.registryUrl = (opts.registryUrl || `http://localhost:${CONFIG.PORT}`).replace(/\/+$/, '');
    this.apiKey = opts.apiKey || CONFIG.API_KEY;
    this.intervalMs = opts.intervalMs || CONFIG.HEARTBEAT_INTERVAL_MS;
    this.statusProvider = opts.statusProvider || (async () => ({ status: 'healthy', queue_depth: 0, error_rate_5m: 0 }));
    this.logger = opts.logger || makeLogger(`client:${this.agentId}`);
    this._timer = null;
    this._sending = false;
  }

  start() {
    if (this._timer) return;
    this.logger.info('heartbeat loop starting', { intervalMs: this.intervalMs, registryUrl: this.registryUrl });
    // Send immediately, then on the fixed interval.
    this._tick();
    this._timer = setInterval(() => this._tick(), this.intervalMs);
    this._timer.unref?.();
  }

  stop() {
    if (this._timer) {
      clearInterval(this._timer);
      this._timer = null;
      this.logger.info('heartbeat loop stopped');
    }
  }

  async _tick() {
    if (this._sending) return; // don't overlap if a send is still in flight
    this._sending = true;
    try {
      await this.sendHeartbeat();
    } catch (err) {
      // Never let a failed heartbeat crash the host agent process.
      this.logger.warn('heartbeat send failed, will retry next cycle', { error: err.message });
    } finally {
      this._sending = false;
    }
  }

  async sendHeartbeat(retries = 2) {
    const status = await this.statusProvider();
    const payload = {
      agent_id: this.agentId,
      status: status.status,
      queue_depth: status.queue_depth ?? 0,
      error_rate_5m: status.error_rate_5m ?? 0,
      timestamp: new Date().toISOString(),
    };

    let lastErr;
    for (let attempt = 0; attempt <= retries; attempt += 1) {
      try {
        await this._post('/heartbeat', payload);
        this.logger.debug('heartbeat sent', payload);
        return payload;
      } catch (err) {
        lastErr = err;
        if (attempt < retries) {
          const backoffMs = 500 * 2 ** attempt;
          await new Promise((r) => setTimeout(r, backoffMs));
        }
      }
    }
    throw lastErr;
  }

  _post(pathName, body) {
    return new Promise((resolve, reject) => {
      const target = new URL(this.registryUrl + pathName);
      const lib = target.protocol === 'https:' ? https : http;
      const data = JSON.stringify(body);
      const req = lib.request(
        target,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Content-Length': Buffer.byteLength(data),
            ...(this.apiKey ? { 'x-api-key': this.apiKey } : {}),
          },
          timeout: 5000,
        },
        (res) => {
          let raw = '';
          res.on('data', (c) => (raw += c));
          res.on('end', () => {
            if (res.statusCode >= 200 && res.statusCode < 300) {
              resolve(raw ? JSON.parse(raw) : {});
            } else {
              reject(new Error(`registry responded ${res.statusCode}: ${raw}`));
            }
          });
        }
      );
      req.on('timeout', () => req.destroy(new Error('registry request timed out')));
      req.on('error', reject);
      req.write(data);
      req.end();
    });
  }
}

// ---------------------------------------------------------------------
// Bootstrapping helper: start registry + HTTP server together.
// ---------------------------------------------------------------------

async function startService(overrides = {}) {
  const logger = makeLogger('heartbeat-service');
  const registry = new HealthRegistry({ logger, ...overrides });
  await registry.init();

  const server = createServer(registry, logger);
  await new Promise((resolve) => server.listen(CONFIG.PORT, CONFIG.HOST, resolve));
  logger.info(`heartbeat-service listening`, { host: CONFIG.HOST, port: CONFIG.PORT });

  const shutdown = async (signal) => {
    logger.info('shutting down', { signal });
    server.close();
    await registry.close();
    process.exit(0);
  };
  process.on('SIGINT', () => shutdown('SIGINT'));
  process.on('SIGTERM', () => shutdown('SIGTERM'));

  return { server, registry, logger };
}

// ---------------------------------------------------------------------
// Demo mode: `node heartbeat-service.js` starts the registry + server
// and spins up two fake agents, one of which fails after a while, so
// you can watch the routable list change in real time.
// ---------------------------------------------------------------------

async function runDemo() {
  const { registry, logger } = await startService();

  const clientA = new HeartbeatClient({
    agentId: 'agente-saneamento',
    intervalMs: 5000, // fast, for the demo only — real usage is 5 min
    statusProvider: async () => ({ status: 'healthy', queue_depth: 2, error_rate_5m: 0.01 }),
  });

  let demoTicks = 0;
  const clientB = new HeartbeatClient({
    agentId: 'agente-energia',
    intervalMs: 5000,
    statusProvider: async () => {
      demoTicks += 1;
      // Goes unhealthy after a few ticks to demonstrate the grace window.
      return demoTicks > 3
        ? { status: 'unhealthy', queue_depth: 40, error_rate_5m: 0.9 }
        : { status: 'healthy', queue_depth: 3, error_rate_5m: 0.02 };
    },
  });

  clientA.start();
  clientB.start();

  setInterval(() => {
    logger.info('current routable agents', { routable: registry.listRoutable() });
  }, 5000).unref?.();
}

// ---------------------------------------------------------------------
// Exports (for use as a library from other agent processes / Maestro)
// ---------------------------------------------------------------------

module.exports = {
  CONFIG,
  HealthRegistry,
  HeartbeatClient,
  createServer,
  startService,
  ValidationError,
};

// Only auto-run when executed directly (`node heartbeat-service.js`),
// never when required as a module.
if (require.main === module) {
  const isDemo = process.argv.includes('--demo');
  (isDemo ? runDemo() : startService()).catch((err) => {
    // eslint-disable-next-line no-console
    console.error('fatal error starting heartbeat-service:', err);
    process.exit(1);
  });
}
