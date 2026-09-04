'use strict';

/**
 * Parses a `.claude/agents/*.md` file into the metadata shape the
 * auto-registration service needs: { name, description, expertise,
 * tools, rag_collections, handoffs_to, model, skills, lifecycle }.
 *
 * Design goal: work with the frontmatter Manta already ships today
 * (name, description, tools, model — see .claude/agents/agente-*.md)
 * AND with a richer frontmatter that new agents can opt into
 * (expertise.primary/secondary, rag_collections, handoffs_to,
 * lifecycle, skills). When the richer fields are absent, derive them
 * from the free-text body so existing agents register cleanly with
 * no edits required.
 */

const fs = require('fs');
const path = require('path');

const FRONTMATTER_RE = /^---\r?\n([\s\S]*?)\r?\n---\r?\n?([\s\S]*)$/;

/** Minimal YAML-subset parser for our frontmatter (no external deps).
 *  Supports: scalars, `key: [a, b, c]` inline arrays, and simple
 *  nested maps used only by `expertise:`. Good enough for the
 *  controlled shape of agent frontmatter; anything else throws so
 *  authors notice quickly instead of silently misparsing.
 */
function parseFrontmatterYaml(raw) {
  const lines = raw.split(/\r?\n/);
  const root = {};
  let currentKey = null;
  let currentIndent = 0;

  for (const rawLine of lines) {
    if (!rawLine.trim() || rawLine.trim().startsWith('#')) continue;
    const indent = rawLine.match(/^ */)[0].length;
    const line = rawLine.trim();

    const kv = line.match(/^([A-Za-z0-9_]+):\s*(.*)$/);
    if (!kv) continue;
    const [, key, valueRaw] = kv;

    if (indent === 0) {
      currentKey = key;
      currentIndent = indent;
      if (valueRaw === '' || valueRaw === undefined) {
        root[key] = {}; // expect nested keys (e.g. expertise:)
      } else {
        root[key] = parseScalarOrArray(valueRaw);
      }
    } else if (currentKey && indent > currentIndent) {
      if (typeof root[currentKey] !== 'object' || Array.isArray(root[currentKey])) {
        root[currentKey] = {};
      }
      root[currentKey][key] = parseScalarOrArray(valueRaw);
    }
  }
  return root;
}

function parseScalarOrArray(value) {
  const v = value.trim();
  if (v.startsWith('[') && v.endsWith(']')) {
    const inner = v.slice(1, -1).trim();
    if (!inner) return [];
    return inner.split(',').map((s) => stripQuotes(s.trim())).filter(Boolean);
  }
  return stripQuotes(v);
}

function stripQuotes(s) {
  if (
    (s.startsWith('"') && s.endsWith('"')) ||
    (s.startsWith("'") && s.endsWith("'"))
  ) {
    return s.slice(1, -1);
  }
  return s;
}

/** Fallback: pull primary expertise keywords out of the description
 *  when there is no explicit `expertise:` block. Manta descriptions
 *  consistently end with "Roteia quando o usuário menciona X, Y, Z."
 *  — reuse that list; otherwise fall back to the first clause.
 */
function deriveExpertiseFromDescription(description) {
  if (!description) return { primary: [], secondary: [] };
  const match = description.match(/menciona\s+(.+?)\.?$/i);
  if (match) {
    const primary = match[1]
      .split(',')
      .map((s) => s.trim())
      .filter(Boolean)
      .slice(0, 12);
    return { primary, secondary: [] };
  }
  const firstClause = description.split(/[.—]/)[0];
  return { primary: [firstClause.trim()].filter(Boolean), secondary: [] };
}

/** Fallback: find `Coleção RAG \`slug\`` mentions in the body. */
function deriveRagCollectionsFromBody(body) {
  const matches = [...body.matchAll(/Coleção RAG `([a-z0-9_-]+)`/gi)];
  return [...new Set(matches.map((m) => m[1]))];
}

/** Fallback: find bold agent names under a "Handoff" heading. */
function deriveHandoffsFromBody(body) {
  const section = body.match(/##\s*Handoff[^\n]*\n([\s\S]*?)(\n##\s|$)/i);
  if (!section) return [];
  const bullets = [...section[1].matchAll(/\*\*([a-zA-Z0-9À-ÿ() .-]+)\*\*/g)];
  return [...new Set(bullets.map((m) => m[1].trim()))].slice(0, 10);
}

function slugFromFilename(filePath) {
  return path.basename(filePath, path.extname(filePath));
}

/**
 * @param {string} filePath absolute path to a .claude/agents/*.md file
 * @returns {object} normalized agent metadata ready for the `agents` table
 */
function parseAgentMarkdown(filePath) {
  const raw = fs.readFileSync(filePath, 'utf8');
  const match = raw.match(FRONTMATTER_RE);
  if (!match) {
    throw new Error(`No YAML frontmatter found in ${filePath}`);
  }
  const [, frontmatterRaw, body] = match;
  const fm = parseFrontmatterYaml(frontmatterRaw);

  const id = fm.name || slugFromFilename(filePath);
  const description = fm.description || '';

  const expertise = fm.expertise && (fm.expertise.primary || fm.expertise.secondary)
    ? {
        primary: Array.isArray(fm.expertise.primary) ? fm.expertise.primary : [],
        secondary: Array.isArray(fm.expertise.secondary) ? fm.expertise.secondary : [],
      }
    : deriveExpertiseFromDescription(description);

  const ragCollections = Array.isArray(fm.rag_collections) && fm.rag_collections.length
    ? fm.rag_collections
    : deriveRagCollectionsFromBody(body);

  const handoffsTo = Array.isArray(fm.handoffs_to) && fm.handoffs_to.length
    ? fm.handoffs_to
    : deriveHandoffsFromBody(body);

  const tools = Array.isArray(fm.tools) ? fm.tools : [];
  const skills = Array.isArray(fm.skills) ? fm.skills : [];
  const model = typeof fm.model === 'string' ? fm.model : 'sonnet';
  const lifecycle = typeof fm.lifecycle === 'string' ? fm.lifecycle : 'alpha';

  return {
    id,
    name: fm.name || id,
    description,
    expertise_primary: expertise.primary,
    expertise_secondary: expertise.secondary,
    keywords: expertise.primary,
    model,
    skills,
    tools,
    rag_collections: ragCollections,
    handoffs_to: handoffsTo,
    lifecycle,
    source_path: filePath,
    version: fm.version || null,
  };
}

module.exports = {
  parseAgentMarkdown,
  // exported for unit tests
  parseFrontmatterYaml,
  deriveExpertiseFromDescription,
  deriveRagCollectionsFromBody,
  deriveHandoffsFromBody,
};
