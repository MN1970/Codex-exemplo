# Deploy Checklist — Manta Maestro v5.0

Ticket: **MNT-2026-CONSOLIDATE-15-SONNETS**
Data de referência: 2026-07-31
Autor: Sonnet 15 (consolidação v5.0)

Este checklist consolida (1) o estado herdado da v4.2 — que segue com
pendências reais, não resolvidas apenas por este documento — e (2) o
checklist novo da v5.0, referente à rodada de consolidação dos 15
Sonnets disparada hoje (31/07/2026) e ao deploy operacional que se
segue a ela.

---

## 1. Estado herdado — Checklist v4.2

Snapshot do estado real do código/repositório nesta data. Os itens
marcados `[x]` estão confirmados no repositório `Codex-exemplo`; os
`[ ]` continuam pendentes de ação fora do git (Supabase, SharePoint,
skill registry, testes, aprovação humana) — ver `docs/DEPLOY-v4.2.md`
para o runbook detalhado de cada um.

- [x] Copiar 5 agent `.md` para `.claude/agents/` (portos, aeroportos,
  saneamento, energia, barragens)
- [x] Aplicar patch no `CLAUDE.md` master (seção de agentes, routing,
  RAG, SharePoint routing)
- [ ] Criar 5 coleções RAG em Supabase (`rag_chunks` / `rag_collections`) — **PENDING**
- [ ] Inserir 5 routing rules em `sp_agent_routing` — **PENDING**
- [ ] Criar pastas SharePoint para os novos segmentos — **PENDING**
- [ ] Registrar skills no catálogo (skill registry) — **PENDING**
- [ ] Testar routing do Maestro com prompts de cada segmento — **PENDING**
- [ ] Upload dos `SKILL.md` para SP em `01-agentes-fundamentais/` — **PENDING**
- [ ] Atualizar `ARQUITETURA-AGENTES-IA.md` no SP (v1.0.0 → v2.0.0) — **PENDING**
- [ ] Gate humano: aprovação MN antes de merge — **PENDING**

> **Nota**: 8 de 10 itens da v4.2 seguem pendentes. A v5.0 não os
> substitui — ela herda essas pendências e adiciona o trabalho de
> consolidação/validação necessário para fechá-las com segurança.

---

## 2. Checklist novo — v5.0

Sequência operacional para a consolidação de hoje e o deploy que dela
decorre.

- [ ] Rodar 15 Sonnets de consolidação (HOJE 31/07) ← **este commit**
- [ ] Consolidar outputs dos 15 Sonnets
- [ ] Validar com `aluci-guard` (referências — normas, SICRO, URLs, DOIs)
- [ ] Validar com `consist-guard` (consistência interna do documento)
- [ ] Testar 10 casos de routing (S1–S10)
- [ ] Upload consolidado para SharePoint
- [ ] Merge PR em `Codex-exemplo`
- [ ] Merge PR em `manta-hub`
- [ ] Apply Supabase migration
- [ ] Create 10 SharePoint folders (5 agent + 5 project)
- [ ] Upload `SKILL.md` files to SP
- [ ] Execute routing smoke tests
- [ ] Deploy MCP to production
- [ ] Final gate MN approval

---

## 3. Dependências

A ordem acima não é arbitrária — cada item depende do fechamento do(s)
anterior(es):

| # | Item | Depende de |
|---|------|------------|
| 1 | Rodar 15 Sonnets | — (ponto de partida) |
| 2 | Consolidar outputs | (1) concluído |
| 3 | `aluci-guard` | (2) — precisa do documento consolidado |
| 4 | `consist-guard` | (2) — pode rodar em paralelo com (3) |
| 5 | Testar 10 casos de routing (S1–S10) | (3) e (4) aprovados sem pendências críticas |
| 6 | Upload consolidado para SP | (5) aprovado |
| 7 | Merge PR em `Codex-exemplo` | (3), (4), (5) aprovados + gate humano preliminar |
| 8 | Merge PR em `manta-hub` | (7) — mirror deve seguir o canônico |
| 9 | Apply Supabase migration | (7) e (8) mergeados (schema e conteúdo já no `main`) |
| 10 | Create 10 SharePoint folders | pode rodar em paralelo com (9), após (7)/(8) |
| 11 | Upload `SKILL.md` files to SP | (10) — pastas precisam existir |
| 12 | Execute routing smoke tests | (9), (10), (11) — ambiente de produção completo |
| 13 | Deploy MCP to produção | (12) aprovado sem falhas |
| 14 | Final gate MN approval | todos os itens (1)–(13) concluídos |

Regra geral: **nenhum item de infraestrutura (Supabase/SharePoint/MCP)
roda antes do merge dos PRs**, e **nenhum merge acontece antes das
validações de `aluci-guard` + `consist-guard` + testes de routing**.

---

## 4. Critérios de aceitação

- **Consolidação dos 15 Sonnets**: todos os 15 outputs recebidos e
  sem conflito de conteúdo não resolvido (divergências marcadas e
  decididas antes de seguir).
- **`aluci-guard`**: zero referências fabricadas (normas ABNT/leis,
  URLs, DOIs, códigos SICRO) no documento consolidado. Qualquer achado
  crítico bloqueia o avanço para (5).
- **`consist-guard`**: estrutura HTML/Markdown íntegra, numeração
  sequencial correta, sem pendências abertas (`a cargar`, `a
  confirmar`, campos em branco) no material a ser publicado.
- **Testes de routing (S1–S10)**: ≥ 90% dos 10 prompts de teste caem
  no agente vertical esperado; casos ambíguos documentados e decididos
  explicitamente (não apenas ignorados).
- **Upload SharePoint**: os 5 `SKILL.md` e o material consolidado
  presentes nas pastas corretas, com nomenclatura e metadados
  consistentes com os demais agentes.
- **Merges (`Codex-exemplo` e `manta-hub`)**: ambos os PRs revisados e
  aprovados, sem merge de um sem o outro (os dois repositórios devem
  ficar em sincronia — canônico + mirror).
- **Supabase migration**: 5 coleções RAG e 5 routing rules confirmadas
  via query pós-deploy (ver `docs/DEPLOY-v4.2.md`, seção 2.3); rollback
  testado e disponível antes de aplicar em produção.
- **SharePoint folders**: as 10 pastas (5 `01-agentes-fundamentais/*`
  + 5 `03_Projetos/*`) existentes e com a estrutura padrão
  (`SKILL.md`, `README.md`, `refs/`, `prompts/` onde aplicável).
- **Routing smoke tests**: execução em ambiente de produção (não
  apenas staging/local) com resultado registrado.
- **Deploy MCP em produção**: sem erros de inicialização, ferramentas
  respondendo, sem regressão nos agentes horizontais existentes
  (Manta 00–16).
- **Gate humano final (MN)**: aprovação explícita registrada antes de
  considerar a v5.0 encerrada — nenhum item acima substitui essa
  aprovação.

---

## Referências

- `CLAUDE.md` (raiz) — registro mestre v4.2, mapa de agentes e routing.
- `docs/DEPLOY-v4.2.md` — runbook detalhado das pendências herdadas
  (Supabase, SharePoint, testes de routing, rollback).
- `.claude/agents/agente-{portos,aeroportos,saneamento,energia,barragens}.md`
  — definições dos 5 agentes verticais S6–S10.
- `tests/routing/prompts.md` — prompts de teste de routing usados na
  v4.2, base para os 10 casos S1–S10 da v5.0.
