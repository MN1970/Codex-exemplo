# WF-MCP-001 — Manta Cases Pipeline (Arquitetura)

**Ticket:** WF-MCP-001
**Autor:** ecossistema Manta Maestro (Vetor 3)
**Data:** 2026-07-12
**Status:** proposta técnica (candidata a v4.6 do CLAUDE.md master)

---

## 1. Motivação — por que casos > teses

O ecossistema Maestro já opera a coleção `academic-knowledge`
(WF-AKP-001) com 36 teses + 52 KEs, priority=100 nos verticais S1-S13.
Teses são um ótimo *floor* de estado da arte, mas têm dois limites
estruturais para responder as perguntas de projeto real:

1. **Contexto brasileiro é raso**: a maioria das teses cobre problemas
   genéricos (dimensionamento, dragagem, ETA); poucas discutem
   *decisões de projeto Manta* como "usar barreira artificial Brückner
   no km 594+300 para forçar compensação dentro da faixa" ou
   "argumentar variação de aço CA-50 como fato imprevisível fora da
   fórmula paramétrica do contrato".
2. **Voltagem executiva zero**: teses não são pleitos, não são
   memoriais executados, não passaram por auditoria de obra.

Os memoriais reais Manta — DDs, EVTEs, projetos executivos, laudos
periciais, pleitos de reequilíbrio, auditorias — codificam DECISÕES
tomadas por MN e pela equipe com contexto, restrições reais, negociação
com cliente, validação em obra. É ouro para RAG: cada memorial é um par
(pergunta técnica implícita → resposta especializada Manta) de altíssima
qualidade.

**Portanto, `manta-cases` roda em priority=120 nos bindings dos agentes
verticais e horizontais estratégicos**, acima de `academic-knowledge`
(priority=100). Em qualquer resolução de contexto (top-N retrieval), um
KE de caso Manta vale mais que um KE acadêmico.

---

## 2. Escopo

- **Coleção RAG:** `manta-cases` (slug), prefixo storage `mcs:`.
- **Escala inicial:** batch piloto de 5-20 projetos ao longo dos 6 meses
  após aprovação. Escala natural: ~5 KEs por memorial em média → 100–500
  KEs no primeiro ano.
- **Cobertura por segmento:** obrigatoriamente cross-vertical S1-S13.
- **Consumidores primários:** todos os agentes verticais (S1-S13) +
  horizontais estratégicos (advisory Manta 15, arquiteto-ia Manta 16).
- **Consumidores secundários (fase 2):** agente-claims (Manta 01) e
  agente-contratual (Manta 02) recebem hooks explícitos para pleitos.

Fora do escopo desta fase:
- Ingestor automatizado no Supabase (fica no TODO — espelho do
  `akp_ingest.py`).
- Reindexação incremental por webhook (fase 2, junto com Manta 17
  Telemetry).
- Redação automática de memorial a partir de KE (é o AVESSO do
  pipeline; não vai acontecer no v4.6).

---

## 3. Stages 1-6 (espelho do WF-AKP-001)

| Stage | Descrição                                          | Executor            | Status v4.6 |
|-------|----------------------------------------------------|---------------------|-------------|
| 1     | Curadoria de memorial (seleção + tagging)          | MN + equipe         | contínuo    |
| 2     | Extração de KEs (`manta_cases_extract.py`)         | script + Sonnet 4.6 | entregue    |
| 3     | Revisão + metadata + `nda_level` explícito         | MN + revisor        | contínuo    |
| 4     | pgvector ingestion (schema + índices + hybrid)     | migração SQL        | entregue    |
| 5     | SharePoint indexing (`08_Casos_Manta/`)            | ops (crawler)       | scaffold    |
| 6     | Agent activation (bindings priority=120)           | migração SQL        | entregue    |

Os deliverables desta versão (v4.6):

- Migração: `supabase/migrations/2026_07_12_manta_cases_v4_6.sql`
- Folder SharePoint: `sharepoint/03-manta-cases/`
- Extrator CLI: `manta-hub/scripts/manta_cases_extract.py`
- Doc de arquitetura: este arquivo.

---

## 4. Schema pgvector

Duas tabelas + uma função híbrida (RRF FTS+Vector) + filtro NDA.

### 4.1 `manta_projects`

Metadata dos projetos que originam casos. Um projeto pode gerar N casos.
Campos-chave:

- `id` slug estável (ex.: `epr-br365`).
- `segmento` (mesmo domínio S1-S13 + `transversal`).
- `nda_level` (`publico` < `interno` < `confidencial` < `restrito`).
- `disciplinas TEXT[]`, `equipe_manta TEXT[]`.
- `sp_path` (path SharePoint canônico).

### 4.2 `manta_cases_elements`

Um KE = trecho autocontido + metadata do memorial. Campos essenciais
espelham `academic_knowledge_elements` (v4.3), com semântica adaptada:

- `tipo` ∈ {`lição_aprendida`, `decisão_projeto`, `memória_calculo`,
  `pleito_claim`, `risco_mitigado`, `padrão_aplicado`, `contra_exemplo`,
  `recomendação`}.
- `citacao_interna` — referência interna (não é BibTeX; é
  `[MN 2024, memorial-EPR-BR365-DD, §4.2]`).
- `nda_level` — herda do projeto, PODE ser mais restritivo (nunca menos).
- `provenance` JSONB carrega o log das stages 1-3, inclusive
  `cost_usd` da extração LLM.

Índices: `projeto`, `tipo`, `segmento`, GIN em `agentes_alvo` /
`disciplinas` / `fase_ciclo_vida`, HNSW em `embedding`, GIN em
`search_tsv`.

### 4.3 `match_manta_cases_hybrid`

RRF (k=60 default) sobre BM25-like FTS (config `portuguese`) + pgvector
cosine. Assinatura estável para o agente:

```sql
SELECT * FROM match_manta_cases_hybrid(
  query_text       := 'compensação de terra em duplicação apertada',
  query_embedding  := '[...]'::vector(1536),
  match_count      := 5,
  filter_segmento  := 'rodovias',
  filter_nda_level := 'interno'
);
```

`filter_nda_level` = teto autorizado do consumidor (default `interno`).
A função só retorna KEs com `nda_level ≤ teto` (ordem lexicográfica de
sensibilidade via função interna `_nda_rank`).

---

## 5. NDA compliance

Cada projeto e cada KE carregam `nda_level` **explícito e obrigatório**.
Não há default silencioso — o revisor da stage 3 confirma nível caso a
caso.

Ordem de sensibilidade:

```
publico(0) < interno(1) < confidencial(2) < restrito(3)
```

**Regra de herança:** `KE.nda_level` NUNCA pode ser MENOS restritivo
que `projeto.nda_level`. O ingestor rejeita a inserção nesse caso (a
migração garante isso via lógica no ingestor + code review; não é
enforçado por CHECK cross-table para não travar imports em ordem
arbitrária, mas o ingestor faz o assert antes do UPSERT).

**Consumo pelos agentes:**
- Maestro (Manta 00) roda com teto `interno` por padrão.
- Agente-advisory (Manta 15) roda com teto `confidencial` quando o
  autor da sessão é MN ou tech lead.
- Nível `restrito` só é aberto por MN via override manual na sessão.

**Retenção e reclassificação automática (decisão a MN — v4.7):**
- Proposta: memoriais de projetos com `status='encerrado'` e
  `ano_conclusao < NOW() - 5 anos` migram automaticamente de
  `interno` para `publico`.
- Não fazemos isso via trigger pgvector neste v4.6. Fica como TODO:
  gerar tickets em `akp_curation_backlog` (reaproveitando a
  infraestrutura de v4.5) pedindo revisão manual de reclassificação.
- **Decisão a MN**: aprovar ou vetar a proposta antes de habilitar a
  automação.

---

## 6. Integração com Telemetria (v4.3 `agent_query_log`)

O schema de telemetria WF-AKP-001 (`agent_query_log` +
`agent_ke_hits`) foi desenhado inicialmente para a coleção
`academic-knowledge`, mas o campo `collection_slug` já é genérico. Duas
extensões TODO para cobrir `manta-cases`:

1. **`matched_ke_ids TEXT[]`** já suporta IDs `MCS-NNNNN` — nada a fazer
   no schema.
2. Adicionar uma view `v_mcs_top_kes` espelhando o padrão de
   `v_akp_top_kes` (top KEs mais consumidos por agente, filtrando
   `collection_slug='manta-cases'`).
3. Adicionar métrica de "nda_level distribution per agent" — quanto
   cada agente consome de KEs `interno` vs `confidencial`, para
   auditoria trimestral.

Esses três TODOs vão junto com o merge do agente Manta 17 Telemetry
(backlog separado).

---

## 7. Handoffs cross-agent (extensão do playbook v4.5)

O playbook em `docs/HANDOFFS-CROSS-AGENT.md` (v4.5) precisa ganhar 2
cenários novos com priority=120 explícito:

- **Cenário 9 — Pleito derivado de caso Manta**: agente-claims
  descobre KE `tipo=pleito_claim` no manta-cases → cita a
  argumentação, aponta a citacao_interna e propõe a mesma linha de
  raciocínio.
- **Cenário 10 — Contra-exemplo Manta**: agente vertical descobre KE
  `tipo=contra_exemplo` → obrigatoriamente cita antes de propor solução
  parecida, evitando reincidência do erro.

Esses cenários entram no playbook em ticket separado (fora do escopo
desta migração).

---

## 8. Decisões pendentes (para MN)

1. **Priority delta**: 120 é agressivo. Alternativas:
   - 110 (só 10 pts acima de AKP) → conservador, force mix.
   - 130 (30 pts acima) → forte dominância Manta em qualquer conflito.
   O valor atual (**120**) foi escolhido como "claramente acima" sem
   sepultar o AKP. Revisar após 3 meses de telemetria.
2. **Retenção automática 5 anos**: aprovar (`publico` após 5 anos) ou
   manter revisão manual sempre?
3. **Extrator com LLM em memoriais confidenciais**: usar Claude
   Sonnet 4.6 (Anthropic) em memoriais nível `confidencial` viola o
   compromisso de "nada do projeto sai do perímetro Manta"? Alternativa:
   rodar Sonnet on-prem via Bedrock/self-hosted. Decisão MN antes do
   primeiro batch confidencial.

---

## 9. Referências cruzadas

- `supabase/migrations/2026_07_12_manta_cases_v4_6.sql` — schema.
- `sharepoint/03-manta-cases/README.md` — folder SP.
- `sharepoint/03-manta-cases/runbook.md` — passos operacionais.
- `manta-hub/scripts/manta_cases_extract.py` — extrator CLI.
- `docs/HANDOFFS-CROSS-AGENT.md` — playbook (a estender).
- `supabase/migrations/2026_07_12_akp_stages_4_6.sql` — schema espelho
  do AKP.
- `supabase/migrations/2026_07_12_akp_hybrid_search.sql` — padrão híbrido
  FTS+Vector RRF.
- `supabase/migrations/2026_07_12_akp_telemetry.sql` — telemetria a
  estender.
- `supabase/migrations/2026_07_12_akp_governance_v4_5.sql` — camada de
  governança a reaproveitar (curation backlog).
