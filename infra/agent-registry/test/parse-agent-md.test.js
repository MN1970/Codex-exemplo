'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const path = require('node:path');

const { parseAgentMarkdown } = require('../lib/parse-agent-md');

const REPO_ROOT = path.resolve(__dirname, '..', '..', '..');

test('parses today\'s minimal frontmatter (agente-saneamento.md) and derives the rest', () => {
  const filePath = path.join(REPO_ROOT, '.claude', 'agents', 'agente-saneamento.md');
  const agent = parseAgentMarkdown(filePath);

  assert.equal(agent.id, 'agente-saneamento');
  assert.equal(agent.model, 'sonnet');
  assert.ok(Array.isArray(agent.tools) && agent.tools.includes('WebSearch'));

  // Derived from "Roteia quando o usuário menciona X, Y, Z." in the description.
  assert.ok(agent.expertise_primary.length > 5);
  assert.ok(agent.expertise_primary.some((k) => k.toLowerCase().includes('aysa')));

  // Derived from "Coleção RAG `saneamento`" in the body.
  assert.ok(agent.rag_collections.includes('saneamento'));

  // Derived from the "## Handoff com outros agentes" section.
  assert.ok(agent.handoffs_to.length > 0);
});

test('parses all five S6-S10 agent files without throwing', () => {
  const dir = path.join(REPO_ROOT, '.claude', 'agents');
  const files = [
    'agente-portos.md',
    'agente-aeroportos.md',
    'agente-saneamento.md',
    'agente-energia.md',
    'agente-barragens.md',
  ];
  for (const f of files) {
    const agent = parseAgentMarkdown(path.join(dir, f));
    assert.equal(agent.id, path.basename(f, '.md'));
    assert.ok(agent.description.length > 0, `${f} should have a non-empty description`);
  }
});
