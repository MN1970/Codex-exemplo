# Codex-exemplo — Manta Maestro Agent Registry

Repositório de referência do sistema **Manta Maestro** de agentes IA da
Manta Associados. Versiona:

- `CLAUDE.md` — registro mestre **operacional** dos agentes (horizontais +
  verticais por segmento + ciclo de vida). v4.2 — S6–S10.
- `.claude/agents/*.md` — definições canônicas dos agentes verticais
  operacionais (S6–S10) **e** propostas ainda não promovidas (ex.:
  `agente-performance.md`, ver seção "Proposta v4.3" abaixo).
- `docs/` — runbooks de deploy manual (Supabase + SharePoint) e notas de
  integração (Cowork).
- `sharepoint/` — mirror versionado do conteúdo que também vive no SP
  (`ARQUITETURA-AGENTES-IA.md`, `SKILL.md`/README/prompts por agente).
- `supabase/` — migrações candidatas (ainda não aplicadas em produção).
- `src/router/`, `tests/router/`, `tests/routing/` — protótipo isolado do
  Roteador Maestro v2 (ver seção "Proposta v4.3" abaixo). **Não é** o
  sistema de produção (`src/maestro/*.py`, em `main`, fora deste repo de
  registro).

## Estrutura

```
.
├── CLAUDE.md                         # master registry (operacional, v4.2)
├── README.md
├── package.json                      # scripts para rodar os testes do protótipo router v2
├── .claude/
│   └── agents/
│       ├── agente-portos.md          # S6 (operacional)
│       ├── agente-aeroportos.md      # S7 (operacional)
│       ├── agente-saneamento.md      # S8 — PRIORIDADE AySA (operacional)
│       ├── agente-energia.md         # S9 — ANEEL/State Grid (operacional)
│       ├── agente-barragens.md       # S10 (operacional)
│       └── agente-performance.md     # PROPOSTA v4.3 — pendente aprovação MN
├── docs/                             # runbooks de deploy + integração Cowork
├── sharepoint/                       # mirror versionado do conteúdo do SP
├── supabase/                         # migrações candidatas (não aplicadas)
├── scripts/
│   └── demo-router.ts                # driver de linha de comando do protótipo router v2
├── src/router/
│   └── maestro-router-v2.ts          # PROPOSTA v4.3 — protótipo isolado, não operacional
└── tests/
    ├── router/maestro-router-v2.test.ts
    └── routing/prompts.md            # smoke tests de routing (fonte para o autoteste)
```

## Versão atual

**v4.2** — 2026-07-05 — expansão S6–S10 (**operacional**, registrada no
`CLAUDE.md` master).

### Proposta v4.3 (não operacional, draft PR [#60](https://github.com/MN1970/Codex-exemplo/pull/60))

- `agente-performance.md` (Manta 03-PERF) — minuta de agente transversal
  de telemetria/desempenho. Não consta no `CLAUDE.md` master; o próprio
  arquivo se declara pendente de aprovação MN antes de qualquer registro,
  coleção RAG ou routing rule.
- `src/router/maestro-router-v2.ts` — protótipo isolado (zero dependências
  externas) do roteador Maestro: classificador de keywords ponderadas,
  seletor de agente com política de desambiguação, orquestrador de steps
  e autoteste contra `tests/routing/prompts.md`. **Validado nesta versão**:
  16/16 testes (`tests/router/maestro-router-v2.test.ts`) e 14/14 casos do
  autoteste passam. Este módulo **não** substitui nem se integra ao
  sistema de produção `src/maestro/*.py` (branch `main`) — três taxonomias
  de segmento incompatíveis coexistem hoje no repositório operacional (ver
  comentário no topo do arquivo de teste); reconciliá-las é uma decisão de
  arquitetura separada, não coberta por este protótipo.

Rodar a suíte do protótipo:

```bash
npm install
npm run test:router   # suíte node:test — 16 casos
npm run demo:router    # autoteste + exemplo de caso ambíguo + orquestração mock
```

## Como usar

Este repositório é **read-only** para o Maestro em runtime. Alterações
seguem gate humano (MN) e são replicadas para:

1. `manta-hub` — `.claude/agents/` (mirror dos agentes verticais)
2. SharePoint — `01-agentes-fundamentais/` (upload dos SKILL.md)
3. Supabase — coleções RAG e tabela `sp_agent_routing`

Ver checklist completo de deploy no `CLAUDE.md` e o runbook detalhado em
`docs/DEPLOY-v4.2.md` (itens de Supabase/SharePoint permanecem **bloqueados
por acesso** — não há credenciais de produção configuradas nesta sessão).
