# ARQUITETURA-AGENTES-IA v6.1.0

**Manta Maestro** — Sistema de Agentes IA da Manta Associados

**Versao:** 6.1.0 (2026-08-01)
**Status:** Operacional (taxonomia unificada S1..S14 + A1..A11 + F1..F10)
**Substitui:** v5.2.0 (2026-07-29 reconciliacao de trilhas)
**Mantido por:** mneves@mantaassociados.com

---

## Sumario Executivo

A v6.1.0 **encerra a divergencia** Codex-exemplo × SP-native, adotando a
taxonomia S1..S14 do Maestro operacional como codigo canonico unico em
ambos os lados. A entrega de v6.1 se deu em 4 fases (T1..T4):

| Fase | Entrega                                          | Status               |
|------|--------------------------------------------------|----------------------|
| T1   | Portar 4 SP-only skills (A9/A10/A11/F10) para repo | ✅ commit `ad98925`  |
| T2   | Criar pastas SP `S12-tuneis / S13-mineracao / S14-oleogas` | ✅ 2026-08-01      |
| T3   | Renumerar 9 agent files repo + migracao candidata | ✅ commit `48412d1`  |
| T4   | Publicar consolidacao SP (este doc)               | 🔄 em curso          |

O prefixo legado `Manta 03-S{n}` foi aposentado. Documentos e PRs
anteriores a v6.1 podem ser interpretados via legenda historica em
`Codex-exemplo/CLAUDE.md` §RECONCILIACAO.

---

## 1. Taxonomia unificada S/A/D/F v6.1

### 1.1 Segmentos verticais — S1..S14 (14 codigos)

| Codigo v6.1 | Segmento    | Agente               | Origem                     |
|-------------|-------------|----------------------|----------------------------|
| S1          | Rodovias    | agente-infraestrutura (S1) | ambos                     |
| S2          | OAE         | agente-infraestrutura (S2) | ambos                     |
| S3          | Ferrovia    | agente-infraestrutura (S3) | ambos                     |
| S4          | Metro       | agente-infraestrutura (S4) | ambos                     |
| S5          | Imobiliario | (SP-native, `manta-04`)    | SP                        |
| S6          | Edificacoes | agente-edificacoes         | v6.1 unificado (era S13)  |
| S7          | Portos      | agente-portos              | v6.1 (era S6)             |
| S8          | Aeroportos  | agente-aeroportos          | v6.1 (era S7)             |
| S9          | Saneamento  | agente-saneamento          | v6.1 (era S8) — AySA      |
| S10         | Energia     | agente-energia             | v6.1 (era S9)             |
| S11         | Barragens   | agente-barragens           | v6.1 (era S10)            |
| S12         | Tuneis      | agente-tuneis              | v6.1 (era S5 — novo no SP) |
| S13         | Mineracao   | agente-mineracao           | v6.1 (era S11 — novo no SP) |
| S14         | Oleo & Gas  | agente-oleo-gas            | v6.1 (era S12 — novo no SP) |

### 1.2 Atividades horizontais — A1..A11 (11 codigos)

Adotada taxonomia SP integral (mais rica que o repo). Repo em v6.1 T1
recebeu A9-regulatorio, A10-risco e A11-fiscalizacao portados do SP.

| Codigo | Atividade                                     | Status   |
|--------|-----------------------------------------------|----------|
| A1     | Proposta tecnica-economica                    | ambos    |
| A2     | Levantamento de quantidades                   | ambos    |
| A3     | Orcamentacao (SICRO/SINAPI, BDI)              | ambos    |
| A4     | Modelagem financeira (VPL/TIR/WACC)           | ambos    |
| A5     | Cronograma e gestao                           | ambos    |
| A6     | Administracao contratual                      | ambos    |
| A7     | Claims / pleitos                              | ambos    |
| A8     | Advisory                                      | ambos    |
| A9     | Regulatorio (ART/RRT/licenciamento)           | v6.1 T1  |
| A10    | Risco (Monte Carlo, HAZOP)                    | v6.1 T1  |
| A11    | Fiscalizacao (RDO, medicao, NC)               | v6.1 T1  |

### 1.3 Funcionais — F1..F10 (10 codigos)

| Codigo | Funcional               | Papel                                  | Status  |
|--------|-------------------------|----------------------------------------|---------|
| F1     | IA                      | Model management, tiering              | ambos   |
| F2     | SharePoint              | F2 fallback chain (v4.6.1)             | ambos   |
| F3     | Portal                  | Portal de cliente                       | ambos   |
| F4     | Extracao                | Leitura de fontes                       | ambos   |
| F5     | Notificacao             | Alertas Slack/email                     | ambos   |
| F6     | Trace                   | Rastreabilidade R1                      | ambos   |
| F7     | Guardrails              | R1-R5, aluci-guard, consist-guard       | ambos   |
| F8     | Padronizacao            | Templates, output formatacao            | ambos   |
| F9     | Meta                    | Auto-projeto (F9 meta-kernel)           | ambos   |
| F10    | Pesquisa Evolutiva      | Scout (active learning + RAG incremental) | v6.1 T1 |

### 1.4 Disciplinas — D01..D23 (23 codigos)

Adotada taxonomia SP integral. Referencia em
`sharepoint/03-funcionais/F10-pesquisa-evolutiva/refs/disciplinas.md`
(pendente de expansao).

---

## 2. Duas trilhas Supabase — inalterado desde v5.2

- **`ogxxgvgtulrbbppshjie`** (sa-east-1) — Maestro core, Learning Loop,
  agent_episodes, akp_curation_backlog, LLM-as-a-judge. Este e o project
  que recebera a migracao candidata `2026_08_01_v6_1_taxonomy_reconciliation.sql`.
- **`xgluoaaymbdzbbudnwrh`** (us-east-2) — KB rodovias (dispositivos, sinais
  verticais/horizontais, elementos rodoviarios). Acesso pendente de gate
  MN.

---

## 3. Camadas do Maestro (v4.7 → v4.9 → v6.1)

Preservadas integralmente da v3.0.0/v5.2.0:

1. **Complexity Detection** (Q0 intake) — star1/star2/star3
2. **Reflexion Loop** — auto-critica pre-entrega (gating star2/star3)
3. **Consensus 3/5** — LLM-as-a-judge (Sonnet 4.6), 5 criterios 0-5
4. **Aggregation** — Weighted RRF (hybrid BM25 + vector)
5. **ML Intelligence** — MLP 384→128 sobre embeddings (learned router)
6. **Episodic Memory** — agent_episodes com HNSW + consolidate_old_episodes cron
7. **Learning Loop v4.9** — judge_feedback → akp_curation_backlog (aplicado em prod 2026-07-19)

---

## 4. Migracao pendente v6.1 T3 (gate MN duro)

`Codex-exemplo/supabase/migrations/2026_08_01_v6_1_taxonomy_reconciliation.sql`

- UPDATE `manta_agent_capabilities.agent_id` de `03-S{n}` para `S{n}` unificado
- UPDATE `rag_collections.codigo` de forma equivalente
- INSERT 3 atividades + 1 funcional novas
- Stage-rename para evitar colisao S6/S7/S8/S9/S10/S11
- Bloco DOWN de rollback incluso

Depende de: backup logico completo (pg_dump) + M-A ja aplicada + m_e_manta_cases
ja aplicada. Idempotente. Roda em transacao.

---

## 5. Fixes prioritarios pos-v6.1

1. **Router SKILL v1.1.0** — hoje aponta para pasta fantasma
   `01-agentes-fundamentais/` no SP. Fix: publicar `manta-maestro v6.1.0`
   com fanout via `list_folders` em `01-segmentos/`, `02-atividades/`,
   `03-funcionais/`.
2. **RLS advisor critical** — 3 tabelas com RLS disabled em prod
   (`rag_collections`, `sp_agent_routing`, `maestro_routing_keywords`).
   Fix planejado: enable RLS + politica read-only publica + write role
   restrita a service_role.
3. **LLM judge ativo em 0/30d** — nenhum registro em `agent_query_log`
   com `judge_score` populado nos ultimos 30 dias. Investigar se o cron
   quebrou ou se o backend nao esta emitindo `judge_score`.

---

## 6. Changelog v6.1.0

- **2026-08-01** — v6.1.0 T1+T2+T3 (repo) publicado.
- **2026-07-29** — v5.2.0 reconciliacao de trilhas.
- **2026-07-28** — v5.1.0 KB rodovias.
- **2026-07-19** — v3.0.0 Learning Loop v4.9 aplicado em prod.
- **2026-07-13** — v3.0.0 Agentic Intelligence Layer (v4.7).

---

**Autor:** Maestro · Manta Associados · 2026-08-01
**Sessao:** v6.1 T1→T4 sprint
