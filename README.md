# Codex-exemplo — Manta Maestro Agent Registry

Repositório de referência do sistema **Manta Maestro** de agentes IA da
Manta Associados. Versiona:

- `CLAUDE.md` — registro mestre dos 20 agentes (horizontais + verticais
  por segmento + ciclo de vida).
- `.claude/agents/*.md` — definições canônicas dos agentes verticais
  novos (S6–S10 adicionados na v4.2).
- `docs/MODELO-MESTRE-PROPOSTA.md` — análise e recomendação sobre modelo
  mestre de proposta técnico-comercial (v4.2.1).
- `docs/CATALOGO-ARTEFATOS-PORTAL-MANTA.md` — catálogo de artefatos-modelo
  de portal e protocolo de reuso (v4.2.2).
- `templates/portal-manta-modelo-padrao/` — modelo funcional (HTML)
  do padrão "Orçamentação Paramétrica".

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

**v4.2.2** — 2026-09-04 — expansão S6–S10 (v4.2) + modelo mestre de proposta + catálogo de artefatos-modelo de portal.

## Como usar

Este repositório é **read-only** para o Maestro em runtime. Alterações
seguem gate humano (MN) e são replicadas para:

1. `manta-hub` — `.claude/agents/` (mirror dos agentes verticais)
2. SharePoint — `01-agentes-fundamentais/` (upload dos SKILL.md)
3. Supabase — coleções RAG e tabela `sp_agent_routing`

Ver checklist completo de deploy no `CLAUDE.md`.
