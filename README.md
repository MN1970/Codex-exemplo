# Codex-exemplo — Manta Maestro Agent Registry

Repositório de referência do sistema **Manta Maestro** de agentes IA da
Manta Associados. Versiona:

- `CLAUDE.md` — registro mestre dos 21 agentes (horizontais + verticais
  por segmento + ciclo de vida).
- `.claude/agents/*.md` — definições canônicas dos agentes verticais
  novos (S6–S10 adicionados na v4.2) e do agente horizontal
  leitor-documental (Manta 08, draft v4.3).
- `docs/MODELO-MESTRE-PROPOSTA.md` — análise e recomendação sobre modelo
  mestre de proposta técnico-comercial (v4.2.1).
- `docs/DEPLOY-v4.3.md` — runbook do draft de arquitetura do
  leitor-documental (ingestão multi-formato PDF/Excel/DWG/Word/PPTX/
  BIM/cronograma).

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
        ├── agente-barragens.md       # S10
        └── agente-leitor-documental.md  # Manta 08 — ingestão multi-formato (draft v4.3)
```

## Versão atual

**v4.3.0** — 2026-09-14 — draft do agente-leitor-documental (v4.3),
sobre a expansão S6–S10 (v4.2) + modelo mestre de proposta (v4.2.x).

## Como usar

Este repositório é **read-only** para o Maestro em runtime. Alterações
seguem gate humano (MN) e são replicadas para:

1. `manta-hub` — `.claude/agents/` (mirror dos agentes verticais)
2. SharePoint — `01-agentes-fundamentais/` (upload dos SKILL.md)
3. Supabase — coleções RAG e tabela `sp_agent_routing`

Ver checklist completo de deploy no `CLAUDE.md`.
