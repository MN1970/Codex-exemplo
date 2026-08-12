# Changelog — Manta Maestro (Agent Registry)

Histórico de versões do `CLAUDE.md` master. Movido para este arquivo
em 2026-08-12 para manter o `CLAUDE.md` enxuto (é carregado inteiro em
toda sessão do Claude Code neste repositório).

## v4.2.1 (2026-08-12)

QA de routing: smoke test dos 30 prompts de `tests/routing/prompts.md`
simulado com 5 agentes Sonnet aplicando literalmente o bloco de regras
do `CLAUDE.md` — ~20% de falha de match (PIANC/quebra-mar, RBAC/PCN,
PMSB, ampacidade/ACSR, dam breach/SIGBM/ANM). Corrigido:
- Adicionadas 13 keywords faltantes ao bloco `ROUTING` do `CLAUDE.md`
  e replicadas em `maestro_routing_keywords`
  (`supabase/migrations/2026_07_05_v4_2_agents_s6_s10.sql`).
- Adicionada regra de desempate explícita para múltiplos matches
  (estrutura principal = primário; suporte/interligação = handoff),
  resolvendo os 4 "casos ambíguos" de `tests/routing/prompts.md`.
- `ARQUITETURA-AGENTES-IA.md` §6 não duplica mais o bloco de regras —
  aponta para `CLAUDE.md` como fonte única.

## v4.2 (2026-07-05)

Expansão S6–S10 (Portos, Aeroportos, Saneamento, Energia, Barragens).
5 novos agentes verticais + 5 coleções RAG + 5 pastas SharePoint.
Ticket MNT-2026-UPGRADE-AGENTS-S6S10.

## v4.1 (anterior)

15 agentes: horizontais + S1–S4.
