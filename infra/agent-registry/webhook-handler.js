'use strict';

/**
 * webhook-handler.js
 * ------------------------------------------------------------------
 * GitHub webhook receiver for the auto-registration pipeline.
 *
 * Wiring (per docs/MANTA-MAESTRO-ECOSYSTEM-v5-UPGRADE.md §3.1):
 *   GitHub push/PR-merge on `main`
 *     → POST /webhooks/github/agent-registry
 *     → verify HMAC signature
 *     → diff the commits for added/modified/removed
 *       `.claude/agents/*.md` files
 *     → for each added/modified file: registerAgentFromFile()
 *       (upsert → self-test → start A/B test)
 *     → for each removed file: deregisterAgentById()
 *
 * GitHub signs payloads with HMAC-SHA256 over the raw body using the
 * webhook secret (X-Hub-Signature-256 header) — verify BEFORE parsing
 * JSON, and respond 202 immediately since registration + self-test can
 * take longer than GitHub's webhook timeout.
 */

const crypto = require('crypto');
const path = require('path');
const express = require('express');

const { registerAgentFromFile, deregisterAgentById } = require('./auto-registration-service');

const AGENTS_DIR_PREFIX = '.claude/agents/';
const AGENT_FILE_RE = /^\.claude\/agents\/[\w-]+\.md$/;

function verifySignature(secret, rawBody, signatureHeader) {
  if (!signatureHeader || !signatureHeader.startsWith('sha256=')) return false;
  const expected =
    'sha256=' + crypto.createHmac('sha256', secret).update(rawBody).digest('hex');
  const a = Buffer.from(expected);
  const b = Buffer.from(signatureHeader);
  return a.length === b.length && crypto.timingSafeEqual(a, b);
}

/** Extracts { added, modified, removed } agent .md paths from a GitHub push payload. */
function extractAgentFileChanges(pushPayload) {
  const added = new Set();
  const modified = new Set();
  const removed = new Set();

  for (const commit of pushPayload.commits || []) {
    for (const f of commit.added || []) if (AGENT_FILE_RE.test(f)) added.add(f);
    for (const f of commit.modified || []) if (AGENT_FILE_RE.test(f)) modified.add(f);
    for (const f of commit.removed || []) if (AGENT_FILE_RE.test(f)) removed.add(f);
  }

  // A file added then later modified (or vice versa) within the same
  // push should only be treated once, as "modified" wins ambiguity in
  // favor of a safe re-registration rather than assuming brand-new.
  for (const f of modified) added.delete(f);
  // If it was both added/modified AND removed in the same push, the
  // net effect is removal.
  for (const f of removed) {
    added.delete(f);
    modified.delete(f);
  }

  return {
    added: [...added],
    modified: [...modified],
    removed: [...removed],
  };
}

function agentIdFromPath(relPath) {
  return path.basename(relPath, path.extname(relPath));
}

/**
 * Builds the Express app. Kept as a factory (not a bare top-level
 * `app.listen`) so tests / the CLI can mount it however they like,
 * and so `repoRoot` + `agentInvoker` are injectable.
 *
 * @param {object} opts
 * @param {string} opts.webhookSecret shared secret configured on the GitHub webhook
 * @param {string} opts.repoRoot local checkout root containing `.claude/agents/`
 * @param {function} [opts.resolveFileContent] async (relPath, commitSha) => absolute local path
 *        Defaults to reading straight from the local checkout at HEAD
 *        (assumes CI/deploy already synced `main` before firing the
 *        webhook). Override to fetch a specific blob via the GitHub
 *        API instead if the receiver isn't co-located with a checkout.
 * @param {function} [opts.agentInvoker] passed through to the self-test step
 */
function createWebhookApp({ webhookSecret, repoRoot, resolveFileContent, agentInvoker } = {}) {
  if (!webhookSecret) {
    throw new Error('createWebhookApp requires { webhookSecret } (GITHUB_WEBHOOK_SECRET)');
  }
  if (!repoRoot) {
    throw new Error('createWebhookApp requires { repoRoot } pointing at a local checkout');
  }

  const resolvePath =
    resolveFileContent || (async (relPath) => path.join(repoRoot, relPath));

  const app = express();

  // Keep the raw body around for signature verification — do not use
  // express.json() directly, it discards the exact bytes GitHub signed.
  app.use(
    express.json({
      verify: (req, _res, buf) => {
        req.rawBody = buf;
      },
    })
  );

  app.post('/webhooks/github/agent-registry', async (req, res) => {
    const signature = req.get('X-Hub-Signature-256');
    if (!verifySignature(webhookSecret, req.rawBody, signature)) {
      return res.status(401).json({ error: 'invalid signature' });
    }

    const event = req.get('X-GitHub-Event');
    if (event === 'ping') {
      return res.status(200).json({ pong: true });
    }
    if (event !== 'push') {
      return res.status(202).json({ ignored: true, reason: `unhandled event "${event}"` });
    }

    const payload = req.body;
    const branch = (payload.ref || '').replace('refs/heads/', '');
    if (payload.ref && branch !== 'main') {
      return res.status(202).json({ ignored: true, reason: `push to "${branch}", not main` });
    }

    const changes = extractAgentFileChanges(payload);
    const totalChanges = changes.added.length + changes.modified.length + changes.removed.length;
    if (totalChanges === 0) {
      return res.status(202).json({ ignored: true, reason: 'no .claude/agents/*.md changes' });
    }

    // Acknowledge immediately; registration + self-test (5 sample
    // queries, up to 30s each) can comfortably exceed GitHub's ~10s
    // webhook timeout.
    res.status(202).json({ accepted: true, changes });

    const commitSha = payload.after;
    processChanges(changes, { repoRoot, resolvePath, agentInvoker, commitSha }).catch((err) => {
      // eslint-disable-next-line no-console
      console.error('[agent-registry] webhook processing failed:', err);
    });
  });

  app.get('/webhooks/github/agent-registry/health', (_req, res) => {
    res.status(200).json({ ok: true });
  });

  return app;
}

async function processChanges(changes, { repoRoot, resolvePath, agentInvoker, commitSha }) {
  const results = { registered: [], deregistered: [], errors: [] };

  for (const relPath of [...changes.added, ...changes.modified]) {
    try {
      const absPath = await resolvePath(relPath, commitSha);
      const result = await registerAgentFromFile(absPath, { repoRoot, commitSha, agentInvoker });
      results.registered.push({ relPath, agentId: result.agent.id, status: result.status });
      // eslint-disable-next-line no-console
      console.log(`[agent-registry] ${relPath} → ${result.agent.id}: ${result.status}`);
    } catch (err) {
      results.errors.push({ relPath, error: err.message });
      // eslint-disable-next-line no-console
      console.error(`[agent-registry] failed to register ${relPath}:`, err.message);
    }
  }

  for (const relPath of changes.removed) {
    const agentId = agentIdFromPath(relPath);
    try {
      await deregisterAgentById(agentId, { reason: `${relPath} removed in ${commitSha}` });
      results.deregistered.push({ relPath, agentId });
      // eslint-disable-next-line no-console
      console.log(`[agent-registry] ${relPath} removed → ${agentId} deprecated`);
    } catch (err) {
      results.errors.push({ relPath, error: err.message });
      // eslint-disable-next-line no-console
      console.error(`[agent-registry] failed to deregister ${agentId}:`, err.message);
    }
  }

  return results;
}

module.exports = {
  createWebhookApp,
  extractAgentFileChanges,
  verifySignature,
  agentIdFromPath,
  AGENTS_DIR_PREFIX,
};

// ---------------------------------------------------------------------
// Standalone server: node webhook-handler.js
// ---------------------------------------------------------------------
if (require.main === module) {
  const port = Number(process.env.PORT || 8787);
  const app = createWebhookApp({
    webhookSecret: process.env.GITHUB_WEBHOOK_SECRET,
    repoRoot: process.env.AGENTS_REPO_ROOT || path.resolve(__dirname, '..', '..'),
  });
  app.listen(port, () => {
    // eslint-disable-next-line no-console
    console.log(`[agent-registry] webhook listening on :${port}`);
  });
}
