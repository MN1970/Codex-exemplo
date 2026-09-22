# Pendencias SharePoint — pos-v3.1

> Snapshot v2.0 (fila 2026-06-20 aguardando MCP sharepoint-write) **encerrada**: canonical foi ativado via OneDrive sync em 2026-07-11 e itens da fila legada ja estao propagados.
> Documento agora rastreia pendencias forward de v3.1.
> [2026-09-22] Status atualizado pela auditoria do Manta Maestro — ver `09-base-conhecimento/INDICE-CANONICAL.md` §14. Fonte de edicao deste arquivo: repositorio GitHub (`sharepoint/Manta-Maestro/00-arquitetura/PENDENTE-SHAREPOINT.md`).

## Bloqueadores ativos

| # | Item | Impacto | Ativacao |
|---|---|---|---|
| 1 | ~~MCP `sharepoint-write` nao conectado~~ | [2026-09-22] **Resolvido na pratica**: sessoes de agente escrevem via conector `SharePoint_Manta` (leitura/escrita) desde 2026-09-07. Continua valendo: ha varios escritores em paralelo (sessoes, Routine, `Sync-MantaMaestro.ps1`, OneDrive) — reler antes de sobrescrever | — |
| 2 | Drive B `Manta-Maestro/` staging paralelo | [2026-09-22] `_DEPRECATED.md` colocado em `04_IA/Manta-Maestro/` e `04_IA/01-agentes-fundamentais/`; `04_IA/02-agentes-horizontais/` (9 pastas vazias) para a lixeira. Falta a aposentadoria completa do conteudo restante (revisao humana) | Revisao humana do conteudo restante do Drive B |
| 3 | Naming remoto pre-v3.1 (`S7- Portos` etc) | Normalizado 2026-07-11 para kebab-case; verificar se dashboards/portais que referencia paths antigos foram atualizados | Grep `portal-manta-*/src/` por strings `S7-Portos`, `S-11 Barragens` etc |

## Pendencias v3.2 (herdadas da v3.0 §13 + v3.1)

1. Densificar S7-S11 no padrao S3-ferrovia — cada segmento com triade `SKILL.md + README.md + ROADMAP.md` + N subpastas sub-agente + `_agent-types/` + `_referencias/`. Estimativa: 1 sessao dedicada por segmento (5 sessoes). [2026-09-22: S7–S11 ja constam como "denso" no `INDICE-CANONICAL.md` §2; conferir se a triade esta completa em cada um.]
2. Escrever 43 SKILL.md restantes (segmentos S7-S11 densos, atividades A1-A10 densificacao, funcionais F1-F9, disciplinas D01-D20) — pipeline Batch API sob `agente-projeto-claude`.
3. ~~Rubricas de auto-juiz por A e por D em `08-rubricas/`.~~ [2026-09-22: 41 rubricas ativas (A1–A10, S1–S11, D01–D20); faltam A11, D21, D22, S12, S13, S14 — `INDICE-CANONICAL.md` §9.]
4. Implantar Supabase L2. [2026-09-22: projeto `manta-maestro` ativo com RAG, routing e bases de custo; RLS e views revisadas na auditoria.]
5. ~~Escolher embedder definitivo (base L0.5).~~ [Decidido em 2026-07-26: `bge-small-en-v1.5` (384-d) — `09-base-conhecimento/RAG_ARQUITETURA_CANONICA.md`.]
6. Popular exemplares L3 em `06-exemplares/S{n}.A{m}/`.
7. Definir retencao L2.
8. ~~Consolidar duplicacoes vestigiais (02-sub-skills vs 05-sub-skills; 03-exemplares vs 06-exemplares; 04-rubricas vs 08-rubricas; 05-execucoes vs 07-execucoes) — arqueologia pos-v3.0.~~ [2026-09-22: as quatro tem `_DEPRECATED.md`; `03-exemplares/` foi esvaziado e o conteudo movido para `06-exemplares/`.]
9. Merge `SKILL-manta-<slug>-<codigo>.md` naming em skills legadas.
10. Atualizar CLAUDE.md do projeto se S9 saneamento tiver projeto ativo (mover prioridade de cliente para la — R1).
11. [2026-09-22, novo] Corrigir o campo legado `manta_code` nos `SKILL.md` de S12–S14 (colide com o codigo de outro segmento) e confirmar keywords/escopo dos itens "a confirmar" do indice (S12–S14, A11, D21–D22, F9–F10).

## Historico (v2.0, 2026-06-20)

Fila original de 10 itens (agentes fundamentais imobiliario, exemplar re-dashboard, pastas espelhadas) — concluida em 2026-07-11 quando sync ativou. Documentacao preservada para auditoria.

---

*Ultima revisao: 2026-09-22 (anterior: 2026-07-11).*
