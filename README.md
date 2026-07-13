# Codex-exemplo — Manta Maestro Agent Registry

Repositório de referência do sistema **Manta Maestro** de agentes IA da
Manta Associados. Versiona:

- `CLAUDE.md` — registro mestre dos 20 agentes (horizontais + verticais
  por segmento + ciclo de vida).
- `.claude/agents/*.md` — definições canônicas dos agentes verticais
  novos (S6–S10 adicionados na v4.2).

## Estrutura

```
.
├── CLAUDE.md                         # master registry
└── .claude/
    └── agents/
        ├── agente-portos.md          # S6
        ├── agente-aeroportos.md      # S7
        ├── agente-saneamento.md      # S8 — PRIORIDADE AySA
        ├── agente-energia.md         # S9 — ANEEL/State Grid
        └── agente-barragens.md       # S10
```

## Versão atual

**v4.2** — 2026-07-05 — expansão S6–S10.

## Como usar

Este repositório é **read-only** para o Maestro em runtime. Alterações
seguem gate humano (MN) e são replicadas para:

1. `manta-hub` — `.claude/agents/` (mirror dos agentes verticais)
2. SharePoint — `01-agentes-fundamentais/` (upload dos SKILL.md)
3. Supabase — coleções RAG e tabela `sp_agent_routing`

Ver checklist completo de deploy no `CLAUDE.md`.
