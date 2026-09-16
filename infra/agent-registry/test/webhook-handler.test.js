'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const crypto = require('node:crypto');

const { extractAgentFileChanges, verifySignature, agentIdFromPath } = require('../webhook-handler');

test('extractAgentFileChanges finds only .claude/agents/*.md across commits', () => {
  const payload = {
    commits: [
      {
        added: ['.claude/agents/agente-novo.md', 'README.md'],
        modified: ['CLAUDE.md'],
        removed: [],
      },
      {
        added: [],
        modified: ['.claude/agents/agente-saneamento.md'],
        removed: ['.claude/agents/agente-legado.md'],
      },
    ],
  };

  const changes = extractAgentFileChanges(payload);
  assert.deepEqual(changes.added.sort(), ['.claude/agents/agente-novo.md']);
  assert.deepEqual(changes.modified.sort(), ['.claude/agents/agente-saneamento.md']);
  assert.deepEqual(changes.removed.sort(), ['.claude/agents/agente-legado.md']);
});

test('extractAgentFileChanges treats add-then-remove in the same push as a removal', () => {
  const payload = {
    commits: [
      {
        added: ['.claude/agents/agente-efemero.md'],
        modified: [],
        removed: [],
      },
      {
        added: [],
        modified: [],
        removed: ['.claude/agents/agente-efemero.md'],
      },
    ],
  };

  const changes = extractAgentFileChanges(payload);
  assert.deepEqual(changes.added, []);
  assert.deepEqual(changes.removed, ['.claude/agents/agente-efemero.md']);
});

test('verifySignature accepts a correctly-signed body and rejects a tampered one', () => {
  const secret = 'test-secret';
  const body = Buffer.from(JSON.stringify({ hello: 'world' }));
  const goodSig = 'sha256=' + crypto.createHmac('sha256', secret).update(body).digest('hex');

  assert.equal(verifySignature(secret, body, goodSig), true);
  assert.equal(verifySignature(secret, Buffer.from('{"hello":"tampered"}'), goodSig), false);
  assert.equal(verifySignature(secret, body, undefined), false);
  assert.equal(verifySignature(secret, body, 'sha1=deadbeef'), false);
});

test('agentIdFromPath strips directory and extension', () => {
  assert.equal(agentIdFromPath('.claude/agents/agente-energia.md'), 'agente-energia');
});
