# SKILL.md — Manta Maestro v5.0 (20 Agentes)

Registro consolidado de capabilities, routing, tiering e exemplos para todos os 20 agentes da Manta Associados.

**Versão:** v5.0 (2026-07-25)
**Gerado:** 2026-07-25T02:18:26.534917
**Fonte:** CLAUDE.md + VERSIONS.json
**Total de agentes:** 11 horizontais + 9 verticais (S1–S4, S6–S10)
**Status:** Completo e validado

---

## Índice Rápido

### Tier 1 — Agentes Horizontais (11)

| # | Agente | Tier default | Status | RAG |
|----|--------|--------------|--------|-----|
| Manta 15 | advisory | Sonnet | Prod | N/A |
| Manta 14 | apresentacoes | Sonnet | Prod | N/A |
| Manta 16 | arquiteto-ia | Opus | Prod | N/A |
| Manta 13 | bd | Sonnet | Prod | N/A |
| Manta 01 | claims | Opus | Prod | N/A |
| Manta 02 | contratual | Sonnet | Prod | N/A |
| Manta 07 | cronograma | Sonnet | Prod | N/A |
| Manta 04 | imobiliario | Sonnet | Prod | N/A |
| Manta 00 | maestro | Haiku→Sonnet | Prod | N/A |
| Manta 06 | modelagem | Sonnet | Prod | N/A |
| Manta 05 | orcamento | Sonnet | Prod | N/A |

### Tier 2–3 — Agentes Verticais (9)

| # | Segmento | Agente | Tier default | RAG | Status |
|----|----|--------|--------------|-----|--------|
| Manta 03-S7 | aeroportos | agente-aeroportos | Sonnet | aer:v5.0:* | Prod |
| Manta 03-S10 | barragens | agente-barragens | Sonnet | bar:v5.0:* | Prod |
| Manta 03-S9 | energia | agente-energia | Sonnet | ene:v5.0:* | Prod |
| Manta 03-S3 | ferrovia | agente-ferrovia | Sonnet | fer:v5.0:* | Prod |
| Manta 03-S4 | metro | agente-metro | Sonnet | met:v5.0:* | Prod |
| Manta 03-S2 | oae | agente-oae | Sonnet | oae:v5.0:* | Prod |
| Manta 03-S6 | portos | agente-portos | Sonnet | por:v5.0:* | Prod |
| Manta 03-S1 | rodovias | agente-rodovias | Sonnet | rod:v5.0:* | Prod |
| Manta 03-S8 | saneamento | agente-saneamento | Sonnet | san:v5.0:* | Prod |


---

## AGENTES HORIZONTAIS (Tier 1)

## Manta 15 — ADVISORY

**Categoria:** horizontal | **Status:** Prod | **Tier default:** Sonnet

Especialista em assessoria estratégica e governança — recomendações, estudos de viabilidade, benchmarking.

### Aliases & Roteamento

Roteia automaticamente para este agente se o usuário menciona:
- **Aliases principais:** advisory-board, manta-15
- **Confidence score:** Maestro calcula via keyword matching + embedding similarity
- **RAG collection:** N/A (horizontal)

### Skill & Versionamento

- **Skill file:** `advisory.v5.0.md`
- **Checksum v5.0:** `a5d2f3c1b4e7`
- **Skill versionamento:** MD5 pinned em `settings.json` → auto-fallback se divergência
- **Compatibilidade:** Python 3.10+ | Claude API Opus/Sonnet/Haiku

### Capabilities

**Tools disponíveis:**
- Read (ler arquivos do workspace)
- Grep (buscar padrões em código/docs)
- Glob (encontrar arquivos por pattern)
- Bash (executar comandos — conforme permissão)
- WebSearch / WebFetch (pesquisa online)


**Skills/Plugins:**
- autodesk-toolkit (processamento CAD/BIM — conforme segmento)
- cronograma-toolkit (Gantt/XER/MSP)
- docx/xlsx/pptx (edição de documentos)
- sicro-composicoes (SICRO para orçamento — rodovias/OAE)
- pdf (processamento de PDFs estruturados)

### Ciclo de Vida (8 fases)


Este agente é **horizontal** (transversal) e não suporta ciclo de vida específico.


### Trigger Phrases (Maestro Routing)

Palavras-chave que acionam este agente automaticamente:
```
N/A
```

### Exemplos de Prompts (Golden Set)

**Adequado para este agente:**


- "Exemplo de prompt para advisory"


**Não adequado (roteado a outro agente):**
- Prompts sobre projetos de infraestrutura específicos (rodovia, ETA, etc.)

### Tiering Automático (R7)

- **Entrada típica:** 4000 tokens
- **Complexity score típica:** 4.0
- **Fallback:** Sonnet → Sonnet → Opus (se timeout > 60s)
- **Custo estimado:** ~$3/1M tokens

### Observabilidade

Todos os runs são tracked em Supabase (`agent_runs` table):
- `run_id` (UUID único)
- `input_tokens`, `output_tokens`, `cost_usd`
- `latency_ms`, `status` (success|timeout|error)
- `feedback_score` (0–5, coletado pós-run)

Dashboard Grafana: `manta 15-dashboard` (custo/dia, latência p50/p95/p99, taxa de erro).

### Fallback Inteligente (R8)

Se timeout em Sonnet:
1. Log em `agent_runs` com `timeout=true`
2. Resubmit com próximo tier (Sonnet ou Opus)
3. Reinjetar contexto (RAG results, partial output)
4. Max tokens reduzido a 1500 (evitar timeout novamente)

### SharePoint Routing

Este agente roteia automaticamente para pasta no SharePoint:
- **Site:** Manta.net
- **Drive:** Projetos
- **Pasta sugerida:** 03_Projetos/Advisory ou 05_Advisory
- **Tier acesso:** Viewer

### Feedback Loop (R9)

1. Após cada run, coletar `feedback_score` (0–5 estrellas)
2. Persistir em `agent_feedback` (Supabase)
3. Semanal: calcular embedding de prompts com score >= 4
4. Treinar reranker com high-scoring queries
5. Redeploy checksum atualizado em VERSIONS.json

---


## Manta 14 — APRESENTACOES

**Categoria:** horizontal | **Status:** Prod | **Tier default:** Sonnet

Especialista em criação de apresentações executivas (PowerPoint) — slides, storytelling, visualizações.

### Aliases & Roteamento

Roteia automaticamente para este agente se o usuário menciona:
- **Aliases principais:** pptx, slides, manta-14
- **Confidence score:** Maestro calcula via keyword matching + embedding similarity
- **RAG collection:** N/A (horizontal)

### Skill & Versionamento

- **Skill file:** `apresentacoes.v5.0.md`
- **Checksum v5.0:** `b4e3c1a2f6d5`
- **Skill versionamento:** MD5 pinned em `settings.json` → auto-fallback se divergência
- **Compatibilidade:** Python 3.10+ | Claude API Opus/Sonnet/Haiku

### Capabilities

**Tools disponíveis:**
- Read (ler arquivos do workspace)
- Grep (buscar padrões em código/docs)
- Glob (encontrar arquivos por pattern)
- Bash (executar comandos — conforme permissão)
- WebSearch / WebFetch (pesquisa online)


**Skills/Plugins:**
- autodesk-toolkit (processamento CAD/BIM — conforme segmento)
- cronograma-toolkit (Gantt/XER/MSP)
- docx/xlsx/pptx (edição de documentos)
- sicro-composicoes (SICRO para orçamento — rodovias/OAE)
- pdf (processamento de PDFs estruturados)

### Ciclo de Vida (8 fases)


Este agente é **horizontal** (transversal) e não suporta ciclo de vida específico.


### Trigger Phrases (Maestro Routing)

Palavras-chave que acionam este agente automaticamente:
```
N/A
```

### Exemplos de Prompts (Golden Set)

**Adequado para este agente:**


- "Exemplo de prompt para apresentacoes"


**Não adequado (roteado a outro agente):**
- Prompts sobre projetos de infraestrutura específicos (rodovia, ETA, etc.)

### Tiering Automático (R7)

- **Entrada típica:** 4000 tokens
- **Complexity score típica:** 4.0
- **Fallback:** Sonnet → Sonnet → Opus (se timeout > 60s)
- **Custo estimado:** ~$3/1M tokens

### Observabilidade

Todos os runs são tracked em Supabase (`agent_runs` table):
- `run_id` (UUID único)
- `input_tokens`, `output_tokens`, `cost_usd`
- `latency_ms`, `status` (success|timeout|error)
- `feedback_score` (0–5, coletado pós-run)

Dashboard Grafana: `manta 14-dashboard` (custo/dia, latência p50/p95/p99, taxa de erro).

### Fallback Inteligente (R8)

Se timeout em Sonnet:
1. Log em `agent_runs` com `timeout=true`
2. Resubmit com próximo tier (Sonnet ou Opus)
3. Reinjetar contexto (RAG results, partial output)
4. Max tokens reduzido a 1500 (evitar timeout novamente)

### SharePoint Routing

Este agente roteia automaticamente para pasta no SharePoint:
- **Site:** Manta.net
- **Drive:** Projetos
- **Pasta sugerida:** 03_Projetos/Apresentacoes ou 05_Apresentacoes
- **Tier acesso:** Viewer

### Feedback Loop (R9)

1. Após cada run, coletar `feedback_score` (0–5 estrellas)
2. Persistir em `agent_feedback` (Supabase)
3. Semanal: calcular embedding de prompts com score >= 4
4. Treinar reranker com high-scoring queries
5. Redeploy checksum atualizado em VERSIONS.json

---


## Manta 16 — ARQUITETO-IA

**Categoria:** horizontal | **Status:** Prod | **Tier default:** Opus

Especialista em arquitetura e governança de agentes IA — design de agents, orquestração, RAG, observabilidade.

### Aliases & Roteamento

Roteia automaticamente para este agente se o usuário menciona:
- **Aliases principais:** ai-arch, manta-16-arq
- **Confidence score:** Maestro calcula via keyword matching + embedding similarity
- **RAG collection:** N/A (horizontal)

### Skill & Versionamento

- **Skill file:** `arquiteto-ia.v5.0.md`
- **Checksum v5.0:** `f6b1e3d5a2c4`
- **Skill versionamento:** MD5 pinned em `settings.json` → auto-fallback se divergência
- **Compatibilidade:** Python 3.10+ | Claude API Opus/Sonnet/Haiku

### Capabilities

**Tools disponíveis:**
- Read (ler arquivos do workspace)
- Grep (buscar padrões em código/docs)
- Glob (encontrar arquivos por pattern)
- Bash (executar comandos — conforme permissão)
- WebSearch / WebFetch (pesquisa online)


**Skills/Plugins:**
- autodesk-toolkit (processamento CAD/BIM — conforme segmento)
- cronograma-toolkit (Gantt/XER/MSP)
- docx/xlsx/pptx (edição de documentos)
- sicro-composicoes (SICRO para orçamento — rodovias/OAE)
- pdf (processamento de PDFs estruturados)

### Ciclo de Vida (8 fases)


Este agente é **horizontal** (transversal) e não suporta ciclo de vida específico.


### Trigger Phrases (Maestro Routing)

Palavras-chave que acionam este agente automaticamente:
```
N/A
```

### Exemplos de Prompts (Golden Set)

**Adequado para este agente:**


- "Exemplo de prompt para arquiteto-ia"


**Não adequado (roteado a outro agente):**
- Prompts sobre projetos de infraestrutura específicos (rodovia, ETA, etc.)

### Tiering Automático (R7)

- **Entrada típica:** 8000 tokens
- **Complexity score típica:** 6.0
- **Fallback:** Opus → Sonnet → Opus (se timeout > 60s)
- **Custo estimado:** ~$15/1M tokens

### Observabilidade

Todos os runs são tracked em Supabase (`agent_runs` table):
- `run_id` (UUID único)
- `input_tokens`, `output_tokens`, `cost_usd`
- `latency_ms`, `status` (success|timeout|error)
- `feedback_score` (0–5, coletado pós-run)

Dashboard Grafana: `manta 16-dashboard` (custo/dia, latência p50/p95/p99, taxa de erro).

### Fallback Inteligente (R8)

Se timeout em Opus:
1. Log em `agent_runs` com `timeout=true`
2. Resubmit com próximo tier (Sonnet ou Opus)
3. Reinjetar contexto (RAG results, partial output)
4. Max tokens reduzido a 1500 (evitar timeout novamente)

### SharePoint Routing

Este agente roteia automaticamente para pasta no SharePoint:
- **Site:** Manta.net
- **Drive:** Projetos
- **Pasta sugerida:** 03_Projetos/Arquiteto-Ia ou 05_Arquiteto-Ia
- **Tier acesso:** Viewer

### Feedback Loop (R9)

1. Após cada run, coletar `feedback_score` (0–5 estrellas)
2. Persistir em `agent_feedback` (Supabase)
3. Semanal: calcular embedding de prompts com score >= 4
4. Treinar reranker com high-scoring queries
5. Redeploy checksum atualizado em VERSIONS.json

---


## Manta 13 — BD

**Categoria:** horizontal | **Status:** Prod | **Tier default:** Sonnet

Especialista em business development e estratégia comercial — prospecção, negociações, estruturas comerciais.

### Aliases & Roteamento

Roteia automaticamente para este agente se o usuário menciona:
- **Aliases principais:** business-dev, manta-13
- **Confidence score:** Maestro calcula via keyword matching + embedding similarity
- **RAG collection:** N/A (horizontal)

### Skill & Versionamento

- **Skill file:** `bd.v5.0.md`
- **Checksum v5.0:** `c3f2a1d5e4b6`
- **Skill versionamento:** MD5 pinned em `settings.json` → auto-fallback se divergência
- **Compatibilidade:** Python 3.10+ | Claude API Opus/Sonnet/Haiku

### Capabilities

**Tools disponíveis:**
- Read (ler arquivos do workspace)
- Grep (buscar padrões em código/docs)
- Glob (encontrar arquivos por pattern)
- Bash (executar comandos — conforme permissão)
- WebSearch / WebFetch (pesquisa online)


**Skills/Plugins:**
- autodesk-toolkit (processamento CAD/BIM — conforme segmento)
- cronograma-toolkit (Gantt/XER/MSP)
- docx/xlsx/pptx (edição de documentos)
- sicro-composicoes (SICRO para orçamento — rodovias/OAE)
- pdf (processamento de PDFs estruturados)

### Ciclo de Vida (8 fases)


Este agente é **horizontal** (transversal) e não suporta ciclo de vida específico.


### Trigger Phrases (Maestro Routing)

Palavras-chave que acionam este agente automaticamente:
```
N/A
```

### Exemplos de Prompts (Golden Set)

**Adequado para este agente:**


- "Exemplo de prompt para bd"


**Não adequado (roteado a outro agente):**
- Prompts sobre projetos de infraestrutura específicos (rodovia, ETA, etc.)

### Tiering Automático (R7)

- **Entrada típica:** 4000 tokens
- **Complexity score típica:** 4.0
- **Fallback:** Sonnet → Sonnet → Opus (se timeout > 60s)
- **Custo estimado:** ~$3/1M tokens

### Observabilidade

Todos os runs são tracked em Supabase (`agent_runs` table):
- `run_id` (UUID único)
- `input_tokens`, `output_tokens`, `cost_usd`
- `latency_ms`, `status` (success|timeout|error)
- `feedback_score` (0–5, coletado pós-run)

Dashboard Grafana: `manta 13-dashboard` (custo/dia, latência p50/p95/p99, taxa de erro).

### Fallback Inteligente (R8)

Se timeout em Sonnet:
1. Log em `agent_runs` com `timeout=true`
2. Resubmit com próximo tier (Sonnet ou Opus)
3. Reinjetar contexto (RAG results, partial output)
4. Max tokens reduzido a 1500 (evitar timeout novamente)

### SharePoint Routing

Este agente roteia automaticamente para pasta no SharePoint:
- **Site:** Manta.net
- **Drive:** Projetos
- **Pasta sugerida:** 03_Projetos/Bd ou 05_Bd
- **Tier acesso:** Viewer

### Feedback Loop (R9)

1. Após cada run, coletar `feedback_score` (0–5 estrellas)
2. Persistir em `agent_feedback` (Supabase)
3. Semanal: calcular embedding de prompts com score >= 4
4. Treinar reranker com high-scoring queries
5. Redeploy checksum atualizado em VERSIONS.json

---


## Manta 01 — CLAIMS

**Categoria:** horizontal | **Status:** Prod | **Tier default:** Opus

Especialista em indenizações, sinistros e gestão de claims — análise de riscos, quantificação de danos, estruturação de sinistros complexos.

### Aliases & Roteamento

Roteia automaticamente para este agente se o usuário menciona:
- **Aliases principais:** manta-claims, claim-mgmt
- **Confidence score:** Maestro calcula via keyword matching + embedding similarity
- **RAG collection:** N/A (horizontal)

### Skill & Versionamento

- **Skill file:** `claims.v5.0.md`
- **Checksum v5.0:** `c1f4b7d3a2e6`
- **Skill versionamento:** MD5 pinned em `settings.json` → auto-fallback se divergência
- **Compatibilidade:** Python 3.10+ | Claude API Opus/Sonnet/Haiku

### Capabilities

**Tools disponíveis:**
- Read (ler arquivos do workspace)
- Grep (buscar padrões em código/docs)
- Glob (encontrar arquivos por pattern)
- Bash (executar comandos — conforme permissão)
- WebSearch / WebFetch (pesquisa online)


**Skills/Plugins:**
- autodesk-toolkit (processamento CAD/BIM — conforme segmento)
- cronograma-toolkit (Gantt/XER/MSP)
- docx/xlsx/pptx (edição de documentos)
- sicro-composicoes (SICRO para orçamento — rodovias/OAE)
- pdf (processamento de PDFs estruturados)

### Ciclo de Vida (8 fases)


Este agente é **horizontal** (transversal) e não suporta ciclo de vida específico.


### Trigger Phrases (Maestro Routing)

Palavras-chave que acionam este agente automaticamente:
```
N/A
```

### Exemplos de Prompts (Golden Set)

**Adequado para este agente:**


- "Exemplo de prompt para claims"


**Não adequado (roteado a outro agente):**
- Prompts sobre projetos de infraestrutura específicos (rodovia, ETA, etc.)

### Tiering Automático (R7)

- **Entrada típica:** 8000 tokens
- **Complexity score típica:** 6.0
- **Fallback:** Opus → Sonnet → Opus (se timeout > 60s)
- **Custo estimado:** ~$15/1M tokens

### Observabilidade

Todos os runs são tracked em Supabase (`agent_runs` table):
- `run_id` (UUID único)
- `input_tokens`, `output_tokens`, `cost_usd`
- `latency_ms`, `status` (success|timeout|error)
- `feedback_score` (0–5, coletado pós-run)

Dashboard Grafana: `manta 01-dashboard` (custo/dia, latência p50/p95/p99, taxa de erro).

### Fallback Inteligente (R8)

Se timeout em Opus:
1. Log em `agent_runs` com `timeout=true`
2. Resubmit com próximo tier (Sonnet ou Opus)
3. Reinjetar contexto (RAG results, partial output)
4. Max tokens reduzido a 1500 (evitar timeout novamente)

### SharePoint Routing

Este agente roteia automaticamente para pasta no SharePoint:
- **Site:** Manta.net
- **Drive:** Projetos
- **Pasta sugerida:** 03_Projetos/Claims ou 05_Claims
- **Tier acesso:** Viewer

### Feedback Loop (R9)

1. Após cada run, coletar `feedback_score` (0–5 estrellas)
2. Persistir em `agent_feedback` (Supabase)
3. Semanal: calcular embedding de prompts com score >= 4
4. Treinar reranker com high-scoring queries
5. Redeploy checksum atualizado em VERSIONS.json

---


## Manta 02 — CONTRATUAL

**Categoria:** horizontal | **Status:** Prod | **Tier default:** Sonnet

Especialista em contratos, análise legal e questões jurídicas — revisão de cláusulas, interpretação de jurisdição, litigância.

### Aliases & Roteamento

Roteia automaticamente para este agente se o usuário menciona:
- **Aliases principais:** manta-02, legal
- **Confidence score:** Maestro calcula via keyword matching + embedding similarity
- **RAG collection:** N/A (horizontal)

### Skill & Versionamento

- **Skill file:** `contratual.v5.0.md`
- **Checksum v5.0:** `b2e5c3a1f7d4`
- **Skill versionamento:** MD5 pinned em `settings.json` → auto-fallback se divergência
- **Compatibilidade:** Python 3.10+ | Claude API Opus/Sonnet/Haiku

### Capabilities

**Tools disponíveis:**
- Read (ler arquivos do workspace)
- Grep (buscar padrões em código/docs)
- Glob (encontrar arquivos por pattern)
- Bash (executar comandos — conforme permissão)
- WebSearch / WebFetch (pesquisa online)


**Skills/Plugins:**
- autodesk-toolkit (processamento CAD/BIM — conforme segmento)
- cronograma-toolkit (Gantt/XER/MSP)
- docx/xlsx/pptx (edição de documentos)
- sicro-composicoes (SICRO para orçamento — rodovias/OAE)
- pdf (processamento de PDFs estruturados)

### Ciclo de Vida (8 fases)


Este agente é **horizontal** (transversal) e não suporta ciclo de vida específico.


### Trigger Phrases (Maestro Routing)

Palavras-chave que acionam este agente automaticamente:
```
N/A
```

### Exemplos de Prompts (Golden Set)

**Adequado para este agente:**


- "Exemplo de prompt para contratual"


**Não adequado (roteado a outro agente):**
- Prompts sobre projetos de infraestrutura específicos (rodovia, ETA, etc.)

### Tiering Automático (R7)

- **Entrada típica:** 4000 tokens
- **Complexity score típica:** 4.0
- **Fallback:** Sonnet → Sonnet → Opus (se timeout > 60s)
- **Custo estimado:** ~$3/1M tokens

### Observabilidade

Todos os runs são tracked em Supabase (`agent_runs` table):
- `run_id` (UUID único)
- `input_tokens`, `output_tokens`, `cost_usd`
- `latency_ms`, `status` (success|timeout|error)
- `feedback_score` (0–5, coletado pós-run)

Dashboard Grafana: `manta 02-dashboard` (custo/dia, latência p50/p95/p99, taxa de erro).

### Fallback Inteligente (R8)

Se timeout em Sonnet:
1. Log em `agent_runs` com `timeout=true`
2. Resubmit com próximo tier (Sonnet ou Opus)
3. Reinjetar contexto (RAG results, partial output)
4. Max tokens reduzido a 1500 (evitar timeout novamente)

### SharePoint Routing

Este agente roteia automaticamente para pasta no SharePoint:
- **Site:** Manta.net
- **Drive:** Projetos
- **Pasta sugerida:** 03_Projetos/Contratual ou 05_Contratual
- **Tier acesso:** Viewer

### Feedback Loop (R9)

1. Após cada run, coletar `feedback_score` (0–5 estrellas)
2. Persistir em `agent_feedback` (Supabase)
3. Semanal: calcular embedding de prompts com score >= 4
4. Treinar reranker com high-scoring queries
5. Redeploy checksum atualizado em VERSIONS.json

---


## Manta 07 — CRONOGRAMA

**Categoria:** horizontal | **Status:** Prod | **Tier default:** Sonnet

Especialista em cronogramas, gestão de projetos e planejamento — Gantt, PERT/CPM, XER, MSP, desvios.

### Aliases & Roteamento

Roteia automaticamente para este agente se o usuário menciona:
- **Aliases principais:** schedule, manta-07
- **Confidence score:** Maestro calcula via keyword matching + embedding similarity
- **RAG collection:** N/A (horizontal)

### Skill & Versionamento

- **Skill file:** `cronograma.v5.0.md`
- **Checksum v5.0:** `d1a6f4c2b3e5`
- **Skill versionamento:** MD5 pinned em `settings.json` → auto-fallback se divergência
- **Compatibilidade:** Python 3.10+ | Claude API Opus/Sonnet/Haiku

### Capabilities

**Tools disponíveis:**
- Read (ler arquivos do workspace)
- Grep (buscar padrões em código/docs)
- Glob (encontrar arquivos por pattern)
- Bash (executar comandos — conforme permissão)
- WebSearch / WebFetch (pesquisa online)


**Skills/Plugins:**
- autodesk-toolkit (processamento CAD/BIM — conforme segmento)
- cronograma-toolkit (Gantt/XER/MSP)
- docx/xlsx/pptx (edição de documentos)
- sicro-composicoes (SICRO para orçamento — rodovias/OAE)
- pdf (processamento de PDFs estruturados)

### Ciclo de Vida (8 fases)


Este agente é **horizontal** (transversal) e não suporta ciclo de vida específico.


### Trigger Phrases (Maestro Routing)

Palavras-chave que acionam este agente automaticamente:
```
N/A
```

### Exemplos de Prompts (Golden Set)

**Adequado para este agente:**


- "Exemplo de prompt para cronograma"


**Não adequado (roteado a outro agente):**
- Prompts sobre projetos de infraestrutura específicos (rodovia, ETA, etc.)

### Tiering Automático (R7)

- **Entrada típica:** 4000 tokens
- **Complexity score típica:** 4.0
- **Fallback:** Sonnet → Sonnet → Opus (se timeout > 60s)
- **Custo estimado:** ~$3/1M tokens

### Observabilidade

Todos os runs são tracked em Supabase (`agent_runs` table):
- `run_id` (UUID único)
- `input_tokens`, `output_tokens`, `cost_usd`
- `latency_ms`, `status` (success|timeout|error)
- `feedback_score` (0–5, coletado pós-run)

Dashboard Grafana: `manta 07-dashboard` (custo/dia, latência p50/p95/p99, taxa de erro).

### Fallback Inteligente (R8)

Se timeout em Sonnet:
1. Log em `agent_runs` com `timeout=true`
2. Resubmit com próximo tier (Sonnet ou Opus)
3. Reinjetar contexto (RAG results, partial output)
4. Max tokens reduzido a 1500 (evitar timeout novamente)

### SharePoint Routing

Este agente roteia automaticamente para pasta no SharePoint:
- **Site:** Manta.net
- **Drive:** Projetos
- **Pasta sugerida:** 03_Projetos/Cronograma ou 05_Cronograma
- **Tier acesso:** Viewer

### Feedback Loop (R9)

1. Após cada run, coletar `feedback_score` (0–5 estrellas)
2. Persistir em `agent_feedback` (Supabase)
3. Semanal: calcular embedding de prompts com score >= 4
4. Treinar reranker com high-scoring queries
5. Redeploy checksum atualizado em VERSIONS.json

---


## Manta 04 — IMOBILIARIO

**Categoria:** horizontal | **Status:** Prod | **Tier default:** Sonnet

Especialista em projetos imobiliários — viabilidade, design, licenciamento, incorporação, PPP.

### Aliases & Roteamento

Roteia automaticamente para este agente se o usuário menciona:
- **Aliases principais:** real-estate, manta-04
- **Confidence score:** Maestro calcula via keyword matching + embedding similarity
- **RAG collection:** N/A (horizontal)

### Skill & Versionamento

- **Skill file:** `imobiliario.v5.0.md`
- **Checksum v5.0:** `a4d7f2c1b3e8`
- **Skill versionamento:** MD5 pinned em `settings.json` → auto-fallback se divergência
- **Compatibilidade:** Python 3.10+ | Claude API Opus/Sonnet/Haiku

### Capabilities

**Tools disponíveis:**
- Read (ler arquivos do workspace)
- Grep (buscar padrões em código/docs)
- Glob (encontrar arquivos por pattern)
- Bash (executar comandos — conforme permissão)
- WebSearch / WebFetch (pesquisa online)


**Skills/Plugins:**
- autodesk-toolkit (processamento CAD/BIM — conforme segmento)
- cronograma-toolkit (Gantt/XER/MSP)
- docx/xlsx/pptx (edição de documentos)
- sicro-composicoes (SICRO para orçamento — rodovias/OAE)
- pdf (processamento de PDFs estruturados)

### Ciclo de Vida (8 fases)


Este agente é **horizontal** (transversal) e não suporta ciclo de vida específico.


### Trigger Phrases (Maestro Routing)

Palavras-chave que acionam este agente automaticamente:
```
N/A
```

### Exemplos de Prompts (Golden Set)

**Adequado para este agente:**


- "Exemplo de prompt para imobiliario"


**Não adequado (roteado a outro agente):**
- Prompts sobre projetos de infraestrutura específicos (rodovia, ETA, etc.)

### Tiering Automático (R7)

- **Entrada típica:** 4000 tokens
- **Complexity score típica:** 4.0
- **Fallback:** Sonnet → Sonnet → Opus (se timeout > 60s)
- **Custo estimado:** ~$3/1M tokens

### Observabilidade

Todos os runs são tracked em Supabase (`agent_runs` table):
- `run_id` (UUID único)
- `input_tokens`, `output_tokens`, `cost_usd`
- `latency_ms`, `status` (success|timeout|error)
- `feedback_score` (0–5, coletado pós-run)

Dashboard Grafana: `manta 04-dashboard` (custo/dia, latência p50/p95/p99, taxa de erro).

### Fallback Inteligente (R8)

Se timeout em Sonnet:
1. Log em `agent_runs` com `timeout=true`
2. Resubmit com próximo tier (Sonnet ou Opus)
3. Reinjetar contexto (RAG results, partial output)
4. Max tokens reduzido a 1500 (evitar timeout novamente)

### SharePoint Routing

Este agente roteia automaticamente para pasta no SharePoint:
- **Site:** Manta.net
- **Drive:** Projetos
- **Pasta sugerida:** 03_Projetos/Imobiliario ou 05_Imobiliario
- **Tier acesso:** Viewer

### Feedback Loop (R9)

1. Após cada run, coletar `feedback_score` (0–5 estrellas)
2. Persistir em `agent_feedback` (Supabase)
3. Semanal: calcular embedding de prompts com score >= 4
4. Treinar reranker com high-scoring queries
5. Redeploy checksum atualizado em VERSIONS.json

---


## Manta 00 — MAESTRO

**Categoria:** horizontal | **Status:** Prod | **Tier default:** Haiku→Sonnet

Router canônico do Maestro (Manta 00) — orquestra roteamento determinístico, tiering automático e fallback inteligente para todos os 20 agentes v5.0.

### Aliases & Roteamento

Roteia automaticamente para este agente se o usuário menciona:
- **Aliases principais:** router, manta-router
- **Confidence score:** Maestro calcula via keyword matching + embedding similarity
- **RAG collection:** N/A (horizontal)

### Skill & Versionamento

- **Skill file:** `maestro.v5.0.md`
- **Checksum v5.0:** `d3a2f1c8e4b7`
- **Skill versionamento:** MD5 pinned em `settings.json` → auto-fallback se divergência
- **Compatibilidade:** Python 3.10+ | Claude API Opus/Sonnet/Haiku

### Capabilities

**Tools disponíveis:**
- Read (ler arquivos do workspace)
- Grep (buscar padrões em código/docs)
- Glob (encontrar arquivos por pattern)
- Bash (executar comandos — conforme permissão)
- WebSearch / WebFetch (pesquisa online)


**Skills/Plugins:**
- autodesk-toolkit (processamento CAD/BIM — conforme segmento)
- cronograma-toolkit (Gantt/XER/MSP)
- docx/xlsx/pptx (edição de documentos)
- sicro-composicoes (SICRO para orçamento — rodovias/OAE)
- pdf (processamento de PDFs estruturados)

### Ciclo de Vida (8 fases)


Este agente é **horizontal** (transversal) e não suporta ciclo de vida específico.


### Trigger Phrases (Maestro Routing)

Palavras-chave que acionam este agente automaticamente:
```
N/A
```

### Exemplos de Prompts (Golden Set)

**Adequado para este agente:**


- "Exemplo de prompt para maestro"


**Não adequado (roteado a outro agente):**
- Prompts sobre projetos de infraestrutura específicos (rodovia, ETA, etc.)

### Tiering Automático (R7)

- **Entrada típica:** 8000 tokens
- **Complexity score típica:** 6.0
- **Fallback:** Haiku→Sonnet → Sonnet → Opus (se timeout > 60s)
- **Custo estimado:** ~$15/1M tokens

### Observabilidade

Todos os runs são tracked em Supabase (`agent_runs` table):
- `run_id` (UUID único)
- `input_tokens`, `output_tokens`, `cost_usd`
- `latency_ms`, `status` (success|timeout|error)
- `feedback_score` (0–5, coletado pós-run)

Dashboard Grafana: `manta 00-dashboard` (custo/dia, latência p50/p95/p99, taxa de erro).

### Fallback Inteligente (R8)

Se timeout em Haiku→Sonnet:
1. Log em `agent_runs` com `timeout=true`
2. Resubmit com próximo tier (Sonnet ou Opus)
3. Reinjetar contexto (RAG results, partial output)
4. Max tokens reduzido a 1500 (evitar timeout novamente)

### SharePoint Routing

Este agente roteia automaticamente para pasta no SharePoint:
- **Site:** Manta.net
- **Drive:** Projetos
- **Pasta sugerida:** 03_Projetos/Maestro ou 05_Maestro
- **Tier acesso:** Viewer

### Feedback Loop (R9)

1. Após cada run, coletar `feedback_score` (0–5 estrellas)
2. Persistir em `agent_feedback` (Supabase)
3. Semanal: calcular embedding de prompts com score >= 4
4. Treinar reranker com high-scoring queries
5. Redeploy checksum atualizado em VERSIONS.json

---


## Manta 06 — MODELAGEM

**Categoria:** horizontal | **Status:** Prod | **Tier default:** Sonnet

Especialista em modelagem financeira, cenários e simulações — análise de sensibilidade, projeções, riscos.

### Aliases & Roteamento

Roteia automaticamente para este agente se o usuário menciona:
- **Aliases principais:** modeling, manta-06
- **Confidence score:** Maestro calcula via keyword matching + embedding similarity
- **RAG collection:** N/A (horizontal)

### Skill & Versionamento

- **Skill file:** `modelagem.v5.0.md`
- **Checksum v5.0:** `e2b5d3a1c4f7`
- **Skill versionamento:** MD5 pinned em `settings.json` → auto-fallback se divergência
- **Compatibilidade:** Python 3.10+ | Claude API Opus/Sonnet/Haiku

### Capabilities

**Tools disponíveis:**
- Read (ler arquivos do workspace)
- Grep (buscar padrões em código/docs)
- Glob (encontrar arquivos por pattern)
- Bash (executar comandos — conforme permissão)
- WebSearch / WebFetch (pesquisa online)


**Skills/Plugins:**
- autodesk-toolkit (processamento CAD/BIM — conforme segmento)
- cronograma-toolkit (Gantt/XER/MSP)
- docx/xlsx/pptx (edição de documentos)
- sicro-composicoes (SICRO para orçamento — rodovias/OAE)
- pdf (processamento de PDFs estruturados)

### Ciclo de Vida (8 fases)


Este agente é **horizontal** (transversal) e não suporta ciclo de vida específico.


### Trigger Phrases (Maestro Routing)

Palavras-chave que acionam este agente automaticamente:
```
N/A
```

### Exemplos de Prompts (Golden Set)

**Adequado para este agente:**


- "Exemplo de prompt para modelagem"


**Não adequado (roteado a outro agente):**
- Prompts sobre projetos de infraestrutura específicos (rodovia, ETA, etc.)

### Tiering Automático (R7)

- **Entrada típica:** 4000 tokens
- **Complexity score típica:** 4.0
- **Fallback:** Sonnet → Sonnet → Opus (se timeout > 60s)
- **Custo estimado:** ~$3/1M tokens

### Observabilidade

Todos os runs são tracked em Supabase (`agent_runs` table):
- `run_id` (UUID único)
- `input_tokens`, `output_tokens`, `cost_usd`
- `latency_ms`, `status` (success|timeout|error)
- `feedback_score` (0–5, coletado pós-run)

Dashboard Grafana: `manta 06-dashboard` (custo/dia, latência p50/p95/p99, taxa de erro).

### Fallback Inteligente (R8)

Se timeout em Sonnet:
1. Log em `agent_runs` com `timeout=true`
2. Resubmit com próximo tier (Sonnet ou Opus)
3. Reinjetar contexto (RAG results, partial output)
4. Max tokens reduzido a 1500 (evitar timeout novamente)

### SharePoint Routing

Este agente roteia automaticamente para pasta no SharePoint:
- **Site:** Manta.net
- **Drive:** Projetos
- **Pasta sugerida:** 03_Projetos/Modelagem ou 05_Modelagem
- **Tier acesso:** Viewer

### Feedback Loop (R9)

1. Após cada run, coletar `feedback_score` (0–5 estrellas)
2. Persistir em `agent_feedback` (Supabase)
3. Semanal: calcular embedding de prompts com score >= 4
4. Treinar reranker com high-scoring queries
5. Redeploy checksum atualizado em VERSIONS.json

---


## Manta 05 — ORCAMENTO

**Categoria:** horizontal | **Status:** Prod | **Tier default:** Sonnet

Especialista em orçamentação e gestão de custos — SICRO, composições, simulações de cenários, análise de desvios.

### Aliases & Roteamento

Roteia automaticamente para este agente se o usuário menciona:
- **Aliases principais:** budget, manta-05
- **Confidence score:** Maestro calcula via keyword matching + embedding similarity
- **RAG collection:** N/A (horizontal)

### Skill & Versionamento

- **Skill file:** `orcamento.v5.0.md`
- **Checksum v5.0:** `f3c8e1a4d2b6`
- **Skill versionamento:** MD5 pinned em `settings.json` → auto-fallback se divergência
- **Compatibilidade:** Python 3.10+ | Claude API Opus/Sonnet/Haiku

### Capabilities

**Tools disponíveis:**
- Read (ler arquivos do workspace)
- Grep (buscar padrões em código/docs)
- Glob (encontrar arquivos por pattern)
- Bash (executar comandos — conforme permissão)
- WebSearch / WebFetch (pesquisa online)


**Skills/Plugins:**
- autodesk-toolkit (processamento CAD/BIM — conforme segmento)
- cronograma-toolkit (Gantt/XER/MSP)
- docx/xlsx/pptx (edição de documentos)
- sicro-composicoes (SICRO para orçamento — rodovias/OAE)
- pdf (processamento de PDFs estruturados)

### Ciclo de Vida (8 fases)


Este agente é **horizontal** (transversal) e não suporta ciclo de vida específico.


### Trigger Phrases (Maestro Routing)

Palavras-chave que acionam este agente automaticamente:
```
N/A
```

### Exemplos de Prompts (Golden Set)

**Adequado para este agente:**


- "Exemplo de prompt para orcamento"


**Não adequado (roteado a outro agente):**
- Prompts sobre projetos de infraestrutura específicos (rodovia, ETA, etc.)

### Tiering Automático (R7)

- **Entrada típica:** 4000 tokens
- **Complexity score típica:** 4.0
- **Fallback:** Sonnet → Sonnet → Opus (se timeout > 60s)
- **Custo estimado:** ~$3/1M tokens

### Observabilidade

Todos os runs são tracked em Supabase (`agent_runs` table):
- `run_id` (UUID único)
- `input_tokens`, `output_tokens`, `cost_usd`
- `latency_ms`, `status` (success|timeout|error)
- `feedback_score` (0–5, coletado pós-run)

Dashboard Grafana: `manta 05-dashboard` (custo/dia, latência p50/p95/p99, taxa de erro).

### Fallback Inteligente (R8)

Se timeout em Sonnet:
1. Log em `agent_runs` com `timeout=true`
2. Resubmit com próximo tier (Sonnet ou Opus)
3. Reinjetar contexto (RAG results, partial output)
4. Max tokens reduzido a 1500 (evitar timeout novamente)

### SharePoint Routing

Este agente roteia automaticamente para pasta no SharePoint:
- **Site:** Manta.net
- **Drive:** Projetos
- **Pasta sugerida:** 03_Projetos/Orcamento ou 05_Orcamento
- **Tier acesso:** Viewer

### Feedback Loop (R9)

1. Após cada run, coletar `feedback_score` (0–5 estrellas)
2. Persistir em `agent_feedback` (Supabase)
3. Semanal: calcular embedding de prompts com score >= 4
4. Treinar reranker com high-scoring queries
5. Redeploy checksum atualizado em VERSIONS.json

---



---

## AGENTES VERTICAIS (Tier 2–3)

## Manta 03-S1 — AGENTE-RODOVIAS

**Categoria:** vertical | **Status:** Prod | **Tier default:** Sonnet

Especialista em infraestrutura rodoviária (Manta 03-S1) — pavimentos, drenagem, SICRO, DNIT, terraplenagem.

### Aliases & Roteamento

Roteia automaticamente para este agente se o usuário menciona:
- **Aliases principais:** Rodovias
- **Confidence score:** Maestro calcula via keyword matching + embedding similarity
- **RAG collection:** rod:v5.0:*

### Skill & Versionamento

- **Skill file:** `rodovias.v5.0.md`
- **Checksum v5.0:** `f7a3b2c1d4e6`
- **Skill versionamento:** MD5 pinned em `settings.json` → auto-fallback se divergência
- **Compatibilidade:** Python 3.10+ | Claude API Opus/Sonnet/Haiku

### Capabilities

**Tools disponíveis:**
- Read (ler arquivos do workspace)
- Grep (buscar padrões em código/docs)
- Glob (encontrar arquivos por pattern)
- Bash (executar comandos — conforme permissão)
- WebSearch / WebFetch (pesquisa online)

- RAG Query (rod:v5.0:*)


**Skills/Plugins:**
- autodesk-toolkit (processamento CAD/BIM — conforme segmento)
- cronograma-toolkit (Gantt/XER/MSP)
- docx/xlsx/pptx (edição de documentos)
- sicro-composicoes (SICRO para orçamento — rodovias/OAE)
- pdf (processamento de PDFs estruturados)

### Ciclo de Vida (8 fases)


Este agente suporta as seguintes fases de um projeto:

1. **Estudo prévio / EVTE** — Diagnóstico, benchmarking, análise preliminar
2. **Projeto básico** — Conceitos, layouts, orçamento order-of-magnitude
3. **Projeto executivo** — Detalhamento, especificações, cronograma vinculante
4. **Obra em execução** — Acompanhamento, desvios, revisões de escopo
5. **Operação & manutenção** — Gestão de ativo, indicadores, OPEX
6. **Processo competitivo / licitação** — Edital, termo de referência, avaliação
7. **Due diligence / M&A** — Auditoria financeira, ambiental, legal, riscos
8. **Encerramento / descomissionamento** — Final de vida útil, passivos, reabilitação

**Declaração de fase (recomendado):**
```json
{
  "phase": "projeto-executivo",
  "deliverables": ["projeto-estrutural.dwg", "memorial-descritivo.pdf"]
}
```



### Trigger Phrases (Maestro Routing)

Palavras-chave que acionam este agente automaticamente:
```
rodovia | pavimento | CBUQ | SICRO | DNIT | terraplenagem | drenagem-rodoviária | tráfego
```

### Exemplos de Prompts (Golden Set)

**Adequado para este agente:**


- "Qual a espessura de pavimento CBUQ para tráfego VDM=1500 veículos/dia?"

- "Elabore um orçamento SICRO para 50km de rodovia pavimentada"

- "Analise o projeto de drenagem rodoviária para corte de 8m"

- "Qual o custo de terraplenagem para aterro de 2m em solo arenoso?"


**Não adequado (roteado a outro agente):**
- Prompts sobre processos horizontais (contrato, claims, etc.)

### Tiering Automático (R7)

- **Entrada típica:** 4000 tokens
- **Complexity score típica:** 4.0
- **Fallback:** Sonnet → Sonnet → Opus (se timeout > 60s)
- **Custo estimado:** ~$3/1M tokens

### Observabilidade

Todos os runs são tracked em Supabase (`agent_runs` table):
- `run_id` (UUID único)
- `input_tokens`, `output_tokens`, `cost_usd`
- `latency_ms`, `status` (success|timeout|error)
- `feedback_score` (0–5, coletado pós-run)

Dashboard Grafana: `manta 03-s1-dashboard` (custo/dia, latência p50/p95/p99, taxa de erro).

### Fallback Inteligente (R8)

Se timeout em Sonnet:
1. Log em `agent_runs` com `timeout=true`
2. Resubmit com próximo tier (Sonnet ou Opus)
3. Reinjetar contexto (RAG results, partial output)
4. Max tokens reduzido a 1500 (evitar timeout novamente)

### SharePoint Routing

Este agente roteia automaticamente para pasta no SharePoint:
- **Site:** Manta.net
- **Drive:** Projetos
- **Pasta sugerida:** 03_Projetos/Rodovias ou 05_Agente-Rodovias
- **Tier acesso:** Editor

### Feedback Loop (R9)

1. Após cada run, coletar `feedback_score` (0–5 estrellas)
2. Persistir em `agent_feedback` (Supabase)
3. Semanal: calcular embedding de prompts com score >= 4
4. Treinar reranker com high-scoring queries
5. Redeploy checksum atualizado em VERSIONS.json

---


## Manta 03-S2 — AGENTE-OAE

**Categoria:** vertical | **Status:** Prod | **Tier default:** Sonnet

Especialista em obras de arte especiais (pontes, viadutos, túneis) — OAE, estruturas metálicas, fundações, protensão.

### Aliases & Roteamento

Roteia automaticamente para este agente se o usuário menciona:
- **Aliases principais:** OAE
- **Confidence score:** Maestro calcula via keyword matching + embedding similarity
- **RAG collection:** oae:v5.0:*

### Skill & Versionamento

- **Skill file:** `oae.v5.0.md`
- **Checksum v5.0:** `e4c2b3a1f5d7`
- **Skill versionamento:** MD5 pinned em `settings.json` → auto-fallback se divergência
- **Compatibilidade:** Python 3.10+ | Claude API Opus/Sonnet/Haiku

### Capabilities

**Tools disponíveis:**
- Read (ler arquivos do workspace)
- Grep (buscar padrões em código/docs)
- Glob (encontrar arquivos por pattern)
- Bash (executar comandos — conforme permissão)
- WebSearch / WebFetch (pesquisa online)

- RAG Query (oae:v5.0:*)


**Skills/Plugins:**
- autodesk-toolkit (processamento CAD/BIM — conforme segmento)
- cronograma-toolkit (Gantt/XER/MSP)
- docx/xlsx/pptx (edição de documentos)
- sicro-composicoes (SICRO para orçamento — rodovias/OAE)
- pdf (processamento de PDFs estruturados)

### Ciclo de Vida (8 fases)


Este agente suporta as seguintes fases de um projeto:

1. **Estudo prévio / EVTE** — Diagnóstico, benchmarking, análise preliminar
2. **Projeto básico** — Conceitos, layouts, orçamento order-of-magnitude
3. **Projeto executivo** — Detalhamento, especificações, cronograma vinculante
4. **Obra em execução** — Acompanhamento, desvios, revisões de escopo
5. **Operação & manutenção** — Gestão de ativo, indicadores, OPEX
6. **Processo competitivo / licitação** — Edital, termo de referência, avaliação
7. **Due diligence / M&A** — Auditoria financeira, ambiental, legal, riscos
8. **Encerramento / descomissionamento** — Final de vida útil, passivos, reabilitação

**Declaração de fase (recomendado):**
```json
{
  "phase": "projeto-executivo",
  "deliverables": ["projeto-estrutural.dwg", "memorial-descritivo.pdf"]
}
```



### Trigger Phrases (Maestro Routing)

Palavras-chave que acionam este agente automaticamente:
```
ponte | viaduto | OAE | NBR 7187 | túnel | fundação | estrutura-metálica | concreto-protendido
```

### Exemplos de Prompts (Golden Set)

**Adequado para este agente:**


- "Dimensione uma ponte de concreto protendido com vão de 40m"

- "Analise a estabilidade de pilares para viaduto elevado"

- "Qual o custo de aparelhos de apoio de elastômero para ponte de 250m?"

- "Revise o projeto estrutural de túnel em NATM"


**Não adequado (roteado a outro agente):**
- Prompts sobre processos horizontais (contrato, claims, etc.)

### Tiering Automático (R7)

- **Entrada típica:** 4000 tokens
- **Complexity score típica:** 4.0
- **Fallback:** Sonnet → Sonnet → Opus (se timeout > 60s)
- **Custo estimado:** ~$3/1M tokens

### Observabilidade

Todos os runs são tracked em Supabase (`agent_runs` table):
- `run_id` (UUID único)
- `input_tokens`, `output_tokens`, `cost_usd`
- `latency_ms`, `status` (success|timeout|error)
- `feedback_score` (0–5, coletado pós-run)

Dashboard Grafana: `manta 03-s2-dashboard` (custo/dia, latência p50/p95/p99, taxa de erro).

### Fallback Inteligente (R8)

Se timeout em Sonnet:
1. Log em `agent_runs` com `timeout=true`
2. Resubmit com próximo tier (Sonnet ou Opus)
3. Reinjetar contexto (RAG results, partial output)
4. Max tokens reduzido a 1500 (evitar timeout novamente)

### SharePoint Routing

Este agente roteia automaticamente para pasta no SharePoint:
- **Site:** Manta.net
- **Drive:** Projetos
- **Pasta sugerida:** 03_Projetos/Oae ou 05_Agente-Oae
- **Tier acesso:** Editor

### Feedback Loop (R9)

1. Após cada run, coletar `feedback_score` (0–5 estrellas)
2. Persistir em `agent_feedback` (Supabase)
3. Semanal: calcular embedding de prompts com score >= 4
4. Treinar reranker com high-scoring queries
5. Redeploy checksum atualizado em VERSIONS.json

---


## Manta 03-S3 — AGENTE-FERROVIA

**Categoria:** vertical | **Status:** Prod | **Tier default:** Sonnet

Especialista em infraestrutura ferroviária (Manta 03-S3) — via permanente, trilho, bitola, catenária, AMV.

### Aliases & Roteamento

Roteia automaticamente para este agente se o usuário menciona:
- **Aliases principais:** Ferrovia
- **Confidence score:** Maestro calcula via keyword matching + embedding similarity
- **RAG collection:** fer:v5.0:*

### Skill & Versionamento

- **Skill file:** `ferrovia.v5.0.md`
- **Checksum v5.0:** `d5b1a3f2c4e6`
- **Skill versionamento:** MD5 pinned em `settings.json` → auto-fallback se divergência
- **Compatibilidade:** Python 3.10+ | Claude API Opus/Sonnet/Haiku

### Capabilities

**Tools disponíveis:**
- Read (ler arquivos do workspace)
- Grep (buscar padrões em código/docs)
- Glob (encontrar arquivos por pattern)
- Bash (executar comandos — conforme permissão)
- WebSearch / WebFetch (pesquisa online)

- RAG Query (fer:v5.0:*)


**Skills/Plugins:**
- autodesk-toolkit (processamento CAD/BIM — conforme segmento)
- cronograma-toolkit (Gantt/XER/MSP)
- docx/xlsx/pptx (edição de documentos)
- sicro-composicoes (SICRO para orçamento — rodovias/OAE)
- pdf (processamento de PDFs estruturados)

### Ciclo de Vida (8 fases)


Este agente suporta as seguintes fases de um projeto:

1. **Estudo prévio / EVTE** — Diagnóstico, benchmarking, análise preliminar
2. **Projeto básico** — Conceitos, layouts, orçamento order-of-magnitude
3. **Projeto executivo** — Detalhamento, especificações, cronograma vinculante
4. **Obra em execução** — Acompanhamento, desvios, revisões de escopo
5. **Operação & manutenção** — Gestão de ativo, indicadores, OPEX
6. **Processo competitivo / licitação** — Edital, termo de referência, avaliação
7. **Due diligence / M&A** — Auditoria financeira, ambiental, legal, riscos
8. **Encerramento / descomissionamento** — Final de vida útil, passivos, reabilitação

**Declaração de fase (recomendado):**
```json
{
  "phase": "projeto-executivo",
  "deliverables": ["projeto-estrutural.dwg", "memorial-descritivo.pdf"]
}
```



### Trigger Phrases (Maestro Routing)

Palavras-chave que acionam este agente automaticamente:
```
ferrovia | trilho | via-permanente | bitola | catenária | AMV | dormente
```

### Exemplos de Prompts (Golden Set)

**Adequado para este agente:**


- "Dimensione a via permanente para ferrovia regional de 150 km"

- "Qual o custo de substituição de trilho desgastado em trecho crítico?"

- "Analise a capacidade de tráfego ferroviário para bitola 1.6m"

- "Especifique o sistema de drenagem para via permanente em terreno encharcado"


**Não adequado (roteado a outro agente):**
- Prompts sobre processos horizontais (contrato, claims, etc.)

### Tiering Automático (R7)

- **Entrada típica:** 4000 tokens
- **Complexity score típica:** 4.0
- **Fallback:** Sonnet → Sonnet → Opus (se timeout > 60s)
- **Custo estimado:** ~$3/1M tokens

### Observabilidade

Todos os runs são tracked em Supabase (`agent_runs` table):
- `run_id` (UUID único)
- `input_tokens`, `output_tokens`, `cost_usd`
- `latency_ms`, `status` (success|timeout|error)
- `feedback_score` (0–5, coletado pós-run)

Dashboard Grafana: `manta 03-s3-dashboard` (custo/dia, latência p50/p95/p99, taxa de erro).

### Fallback Inteligente (R8)

Se timeout em Sonnet:
1. Log em `agent_runs` com `timeout=true`
2. Resubmit com próximo tier (Sonnet ou Opus)
3. Reinjetar contexto (RAG results, partial output)
4. Max tokens reduzido a 1500 (evitar timeout novamente)

### SharePoint Routing

Este agente roteia automaticamente para pasta no SharePoint:
- **Site:** Manta.net
- **Drive:** Projetos
- **Pasta sugerida:** 03_Projetos/Ferrovia ou 05_Agente-Ferrovia
- **Tier acesso:** Editor

### Feedback Loop (R9)

1. Após cada run, coletar `feedback_score` (0–5 estrellas)
2. Persistir em `agent_feedback` (Supabase)
3. Semanal: calcular embedding de prompts com score >= 4
4. Treinar reranker com high-scoring queries
5. Redeploy checksum atualizado em VERSIONS.json

---


## Manta 03-S4 — AGENTE-METRO

**Categoria:** vertical | **Status:** Prod | **Tier default:** Sonnet

Especialista em transporte metroviário e VLT (Manta 03-S4) — metrô, estações, sinalização, NATM, PSD.

### Aliases & Roteamento

Roteia automaticamente para este agente se o usuário menciona:
- **Aliases principais:** Metrô
- **Confidence score:** Maestro calcula via keyword matching + embedding similarity
- **RAG collection:** met:v5.0:*

### Skill & Versionamento

- **Skill file:** `metro.v5.0.md`
- **Checksum v5.0:** `c6a2f4b1d3e5`
- **Skill versionamento:** MD5 pinned em `settings.json` → auto-fallback se divergência
- **Compatibilidade:** Python 3.10+ | Claude API Opus/Sonnet/Haiku

### Capabilities

**Tools disponíveis:**
- Read (ler arquivos do workspace)
- Grep (buscar padrões em código/docs)
- Glob (encontrar arquivos por pattern)
- Bash (executar comandos — conforme permissão)
- WebSearch / WebFetch (pesquisa online)

- RAG Query (met:v5.0:*)


**Skills/Plugins:**
- autodesk-toolkit (processamento CAD/BIM — conforme segmento)
- cronograma-toolkit (Gantt/XER/MSP)
- docx/xlsx/pptx (edição de documentos)
- sicro-composicoes (SICRO para orçamento — rodovias/OAE)
- pdf (processamento de PDFs estruturados)

### Ciclo de Vida (8 fases)


Este agente suporta as seguintes fases de um projeto:

1. **Estudo prévio / EVTE** — Diagnóstico, benchmarking, análise preliminar
2. **Projeto básico** — Conceitos, layouts, orçamento order-of-magnitude
3. **Projeto executivo** — Detalhamento, especificações, cronograma vinculante
4. **Obra em execução** — Acompanhamento, desvios, revisões de escopo
5. **Operação & manutenção** — Gestão de ativo, indicadores, OPEX
6. **Processo competitivo / licitação** — Edital, termo de referência, avaliação
7. **Due diligence / M&A** — Auditoria financeira, ambiental, legal, riscos
8. **Encerramento / descomissionamento** — Final de vida útil, passivos, reabilitação

**Declaração de fase (recomendado):**
```json
{
  "phase": "projeto-executivo",
  "deliverables": ["projeto-estrutural.dwg", "memorial-descritivo.pdf"]
}
```



### Trigger Phrases (Maestro Routing)

Palavras-chave que acionam este agente automaticamente:
```
metrô | estação | NATM | PSD | linha | VLT | sinalização-metrô
```

### Exemplos de Prompts (Golden Set)

**Adequado para este agente:**


- "Dimensione uma estação de metrô subterrânea em NATM com profundidade de 20m"

- "Qual o custo de sinalização automática (ATO) para linha de metrô de 25km?"

- "Analise a ventilação de tunnel-metrô para circulação de trem"

- "Especifique os aparelhos de apoio sísmico para estrutura de VLT elevado"


**Não adequado (roteado a outro agente):**
- Prompts sobre processos horizontais (contrato, claims, etc.)

### Tiering Automático (R7)

- **Entrada típica:** 4000 tokens
- **Complexity score típica:** 4.0
- **Fallback:** Sonnet → Sonnet → Opus (se timeout > 60s)
- **Custo estimado:** ~$3/1M tokens

### Observabilidade

Todos os runs são tracked em Supabase (`agent_runs` table):
- `run_id` (UUID único)
- `input_tokens`, `output_tokens`, `cost_usd`
- `latency_ms`, `status` (success|timeout|error)
- `feedback_score` (0–5, coletado pós-run)

Dashboard Grafana: `manta 03-s4-dashboard` (custo/dia, latência p50/p95/p99, taxa de erro).

### Fallback Inteligente (R8)

Se timeout em Sonnet:
1. Log em `agent_runs` com `timeout=true`
2. Resubmit com próximo tier (Sonnet ou Opus)
3. Reinjetar contexto (RAG results, partial output)
4. Max tokens reduzido a 1500 (evitar timeout novamente)

### SharePoint Routing

Este agente roteia automaticamente para pasta no SharePoint:
- **Site:** Manta.net
- **Drive:** Projetos
- **Pasta sugerida:** 03_Projetos/Metro ou 05_Agente-Metro
- **Tier acesso:** Editor

### Feedback Loop (R9)

1. Após cada run, coletar `feedback_score` (0–5 estrellas)
2. Persistir em `agent_feedback` (Supabase)
3. Semanal: calcular embedding de prompts com score >= 4
4. Treinar reranker com high-scoring queries
5. Redeploy checksum atualizado em VERSIONS.json

---


## Manta 03-S6 — AGENTE-PORTOS

**Categoria:** vertical | **Status:** Prod | **Tier default:** Sonnet

Especialista em infraestrutura portuária (Manta 03-S6) — terminais, dragagem, ANTAQ, PIANC, hidrovias.

### Aliases & Roteamento

Roteia automaticamente para este agente se o usuário menciona:
- **Aliases principais:** Portos
- **Confidence score:** Maestro calcula via keyword matching + embedding similarity
- **RAG collection:** por:v5.0:*

### Skill & Versionamento

- **Skill file:** `portos.v5.0.md`
- **Checksum v5.0:** `b7d3e5a2f1c4`
- **Skill versionamento:** MD5 pinned em `settings.json` → auto-fallback se divergência
- **Compatibilidade:** Python 3.10+ | Claude API Opus/Sonnet/Haiku

### Capabilities

**Tools disponíveis:**
- Read (ler arquivos do workspace)
- Grep (buscar padrões em código/docs)
- Glob (encontrar arquivos por pattern)
- Bash (executar comandos — conforme permissão)
- WebSearch / WebFetch (pesquisa online)

- RAG Query (por:v5.0:*)


**Skills/Plugins:**
- autodesk-toolkit (processamento CAD/BIM — conforme segmento)
- cronograma-toolkit (Gantt/XER/MSP)
- docx/xlsx/pptx (edição de documentos)
- sicro-composicoes (SICRO para orçamento — rodovias/OAE)
- pdf (processamento de PDFs estruturados)

### Ciclo de Vida (8 fases)


Este agente suporta as seguintes fases de um projeto:

1. **Estudo prévio / EVTE** — Diagnóstico, benchmarking, análise preliminar
2. **Projeto básico** — Conceitos, layouts, orçamento order-of-magnitude
3. **Projeto executivo** — Detalhamento, especificações, cronograma vinculante
4. **Obra em execução** — Acompanhamento, desvios, revisões de escopo
5. **Operação & manutenção** — Gestão de ativo, indicadores, OPEX
6. **Processo competitivo / licitação** — Edital, termo de referência, avaliação
7. **Due diligence / M&A** — Auditoria financeira, ambiental, legal, riscos
8. **Encerramento / descomissionamento** — Final de vida útil, passivos, reabilitação

**Declaração de fase (recomendado):**
```json
{
  "phase": "projeto-executivo",
  "deliverables": ["projeto-estrutural.dwg", "memorial-descritivo.pdf"]
}
```



### Trigger Phrases (Maestro Routing)

Palavras-chave que acionam este agente automaticamente:
```
porto | terminal | ANTAQ | dragagem | berço | PIANC | containerizado
```

### Exemplos de Prompts (Golden Set)

**Adequado para este agente:**


- "Dimensione um terminal de contêineres para 500k TEU/ano"

- "Qual o custo de dragagem de aprofundamento para calado de 14m?"

- "Analise a viabilidade de um porto fluvial para hidrovia da Bacia Amazônica"

- "Especifique o molhe de proteção para porto exposto a ondas de até 4m"


**Não adequado (roteado a outro agente):**
- Prompts sobre processos horizontais (contrato, claims, etc.)

### Tiering Automático (R7)

- **Entrada típica:** 4000 tokens
- **Complexity score típica:** 4.0
- **Fallback:** Sonnet → Sonnet → Opus (se timeout > 60s)
- **Custo estimado:** ~$3/1M tokens

### Observabilidade

Todos os runs são tracked em Supabase (`agent_runs` table):
- `run_id` (UUID único)
- `input_tokens`, `output_tokens`, `cost_usd`
- `latency_ms`, `status` (success|timeout|error)
- `feedback_score` (0–5, coletado pós-run)

Dashboard Grafana: `manta 03-s6-dashboard` (custo/dia, latência p50/p95/p99, taxa de erro).

### Fallback Inteligente (R8)

Se timeout em Sonnet:
1. Log em `agent_runs` com `timeout=true`
2. Resubmit com próximo tier (Sonnet ou Opus)
3. Reinjetar contexto (RAG results, partial output)
4. Max tokens reduzido a 1500 (evitar timeout novamente)

### SharePoint Routing

Este agente roteia automaticamente para pasta no SharePoint:
- **Site:** Manta.net
- **Drive:** Projetos
- **Pasta sugerida:** 03_Projetos/Portos ou 05_Agente-Portos
- **Tier acesso:** Editor

### Feedback Loop (R9)

1. Após cada run, coletar `feedback_score` (0–5 estrellas)
2. Persistir em `agent_feedback` (Supabase)
3. Semanal: calcular embedding de prompts com score >= 4
4. Treinar reranker com high-scoring queries
5. Redeploy checksum atualizado em VERSIONS.json

---


## Manta 03-S7 — AGENTE-AEROPORTOS

**Categoria:** vertical | **Status:** Prod | **Tier default:** Sonnet

Especialista em infraestrutura aeroportuária (Manta 03-S7) — pistas, taxiways, TPS, ANAC, RBAC, balizamento.

### Aliases & Roteamento

Roteia automaticamente para este agente se o usuário menciona:
- **Aliases principais:** Aeroportos
- **Confidence score:** Maestro calcula via keyword matching + embedding similarity
- **RAG collection:** aer:v5.0:*

### Skill & Versionamento

- **Skill file:** `aeroportos.v5.0.md`
- **Checksum v5.0:** `a8e1f3c2d4b6`
- **Skill versionamento:** MD5 pinned em `settings.json` → auto-fallback se divergência
- **Compatibilidade:** Python 3.10+ | Claude API Opus/Sonnet/Haiku

### Capabilities

**Tools disponíveis:**
- Read (ler arquivos do workspace)
- Grep (buscar padrões em código/docs)
- Glob (encontrar arquivos por pattern)
- Bash (executar comandos — conforme permissão)
- WebSearch / WebFetch (pesquisa online)

- RAG Query (aer:v5.0:*)


**Skills/Plugins:**
- autodesk-toolkit (processamento CAD/BIM — conforme segmento)
- cronograma-toolkit (Gantt/XER/MSP)
- docx/xlsx/pptx (edição de documentos)
- sicro-composicoes (SICRO para orçamento — rodovias/OAE)
- pdf (processamento de PDFs estruturados)

### Ciclo de Vida (8 fases)


Este agente suporta as seguintes fases de um projeto:

1. **Estudo prévio / EVTE** — Diagnóstico, benchmarking, análise preliminar
2. **Projeto básico** — Conceitos, layouts, orçamento order-of-magnitude
3. **Projeto executivo** — Detalhamento, especificações, cronograma vinculante
4. **Obra em execução** — Acompanhamento, desvios, revisões de escopo
5. **Operação & manutenção** — Gestão de ativo, indicadores, OPEX
6. **Processo competitivo / licitação** — Edital, termo de referência, avaliação
7. **Due diligence / M&A** — Auditoria financeira, ambiental, legal, riscos
8. **Encerramento / descomissionamento** — Final de vida útil, passivos, reabilitação

**Declaração de fase (recomendado):**
```json
{
  "phase": "projeto-executivo",
  "deliverables": ["projeto-estrutural.dwg", "memorial-descritivo.pdf"]
}
```



### Trigger Phrases (Maestro Routing)

Palavras-chave que acionam este agente automaticamente:
```
aeroporto | pista | RWY | taxiway | TPS | ANAC | RBAC | balizamento | ILS
```

### Exemplos de Prompts (Golden Set)

**Adequado para este agente:**


- "Dimensione uma pista de pouso para aviação regional (ATR-72)"

- "Qual o PCN (Pavement Classification Number) para pista de concreto rígido?"

- "Analise o projeto de taxiway e sistema de balizamento para aeroporto novo"

- "Especifique o sistema de proteção contra fogo e emergência (TECA) para terminal"


**Não adequado (roteado a outro agente):**
- Prompts sobre processos horizontais (contrato, claims, etc.)

### Tiering Automático (R7)

- **Entrada típica:** 4000 tokens
- **Complexity score típica:** 4.0
- **Fallback:** Sonnet → Sonnet → Opus (se timeout > 60s)
- **Custo estimado:** ~$3/1M tokens

### Observabilidade

Todos os runs são tracked em Supabase (`agent_runs` table):
- `run_id` (UUID único)
- `input_tokens`, `output_tokens`, `cost_usd`
- `latency_ms`, `status` (success|timeout|error)
- `feedback_score` (0–5, coletado pós-run)

Dashboard Grafana: `manta 03-s7-dashboard` (custo/dia, latência p50/p95/p99, taxa de erro).

### Fallback Inteligente (R8)

Se timeout em Sonnet:
1. Log em `agent_runs` com `timeout=true`
2. Resubmit com próximo tier (Sonnet ou Opus)
3. Reinjetar contexto (RAG results, partial output)
4. Max tokens reduzido a 1500 (evitar timeout novamente)

### SharePoint Routing

Este agente roteia automaticamente para pasta no SharePoint:
- **Site:** Manta.net
- **Drive:** Projetos
- **Pasta sugerida:** 03_Projetos/Aeroportos ou 05_Agente-Aeroportos
- **Tier acesso:** Editor

### Feedback Loop (R9)

1. Após cada run, coletar `feedback_score` (0–5 estrellas)
2. Persistir em `agent_feedback` (Supabase)
3. Semanal: calcular embedding de prompts com score >= 4
4. Treinar reranker com high-scoring queries
5. Redeploy checksum atualizado em VERSIONS.json

---


## Manta 03-S8 — AGENTE-SANEAMENTO

**Categoria:** vertical | **Status:** Prod | **Tier default:** Sonnet

Especialista em saneamento básico (Manta 03-S8) — ETAs, ETEs, adução, drenagem urbana, SNIS, Lei 14.026. PRIORIDADE AySA.

### Aliases & Roteamento

Roteia automaticamente para este agente se o usuário menciona:
- **Aliases principais:** Saneamento
- **Confidence score:** Maestro calcula via keyword matching + embedding similarity
- **RAG collection:** san:v5.0:*

### Skill & Versionamento

- **Skill file:** `saneamento.v5.0.md`
- **Checksum v5.0:** `f1a3d2b4c5e7`
- **Skill versionamento:** MD5 pinned em `settings.json` → auto-fallback se divergência
- **Compatibilidade:** Python 3.10+ | Claude API Opus/Sonnet/Haiku

### Capabilities

**Tools disponíveis:**
- Read (ler arquivos do workspace)
- Grep (buscar padrões em código/docs)
- Glob (encontrar arquivos por pattern)
- Bash (executar comandos — conforme permissão)
- WebSearch / WebFetch (pesquisa online)

- RAG Query (san:v5.0:*)


**Skills/Plugins:**
- autodesk-toolkit (processamento CAD/BIM — conforme segmento)
- cronograma-toolkit (Gantt/XER/MSP)
- docx/xlsx/pptx (edição de documentos)
- sicro-composicoes (SICRO para orçamento — rodovias/OAE)
- pdf (processamento de PDFs estruturados)

### Ciclo de Vida (8 fases)


Este agente suporta as seguintes fases de um projeto:

1. **Estudo prévio / EVTE** — Diagnóstico, benchmarking, análise preliminar
2. **Projeto básico** — Conceitos, layouts, orçamento order-of-magnitude
3. **Projeto executivo** — Detalhamento, especificações, cronograma vinculante
4. **Obra em execução** — Acompanhamento, desvios, revisões de escopo
5. **Operação & manutenção** — Gestão de ativo, indicadores, OPEX
6. **Processo competitivo / licitação** — Edital, termo de referência, avaliação
7. **Due diligence / M&A** — Auditoria financeira, ambiental, legal, riscos
8. **Encerramento / descomissionamento** — Final de vida útil, passivos, reabilitação

**Declaração de fase (recomendado):**
```json
{
  "phase": "projeto-executivo",
  "deliverables": ["projeto-estrutural.dwg", "memorial-descritivo.pdf"]
}
```



### Trigger Phrases (Maestro Routing)

Palavras-chave que acionam este agente automaticamente:
```
saneamento | ETA | ETE | adutora | esgoto | AySA | drenagem urbana | SNIS | Lei 14.026
```

### Exemplos de Prompts (Golden Set)

**Adequado para este agente:**


- "Dimensione uma ETA para município de 500k hab com coagulação/floculação/sedimentação"

- "Qual o custo de uma elevatória para adução de 1000 L/s em altura de 50m?"

- "Analise a viabilidade de tratamento de esgoto por processo MBR para reúso"

- "Especifique o sistema de drenagem urbana e macrodrenagem para bacia de 5km2"


**Não adequado (roteado a outro agente):**
- Prompts sobre processos horizontais (contrato, claims, etc.)

### Tiering Automático (R7)

- **Entrada típica:** 4000 tokens
- **Complexity score típica:** 4.0
- **Fallback:** Sonnet → Sonnet → Opus (se timeout > 60s)
- **Custo estimado:** ~$3/1M tokens

### Observabilidade

Todos os runs são tracked em Supabase (`agent_runs` table):
- `run_id` (UUID único)
- `input_tokens`, `output_tokens`, `cost_usd`
- `latency_ms`, `status` (success|timeout|error)
- `feedback_score` (0–5, coletado pós-run)

Dashboard Grafana: `manta 03-s8-dashboard` (custo/dia, latência p50/p95/p99, taxa de erro).

### Fallback Inteligente (R8)

Se timeout em Sonnet:
1. Log em `agent_runs` com `timeout=true`
2. Resubmit com próximo tier (Sonnet ou Opus)
3. Reinjetar contexto (RAG results, partial output)
4. Max tokens reduzido a 1500 (evitar timeout novamente)

### SharePoint Routing

Este agente roteia automaticamente para pasta no SharePoint:
- **Site:** Manta.net
- **Drive:** Projetos
- **Pasta sugerida:** 03_Projetos/Saneamento ou 05_Agente-Saneamento
- **Tier acesso:** Editor

### Feedback Loop (R9)

1. Após cada run, coletar `feedback_score` (0–5 estrellas)
2. Persistir em `agent_feedback` (Supabase)
3. Semanal: calcular embedding de prompts com score >= 4
4. Treinar reranker com high-scoring queries
5. Redeploy checksum atualizado em VERSIONS.json

---


## Manta 03-S9 — AGENTE-ENERGIA

**Categoria:** vertical | **Status:** Prod | **Tier default:** Sonnet

Especialista em setor elétrico (Manta 03-S9) — transmissão, geração, subestações, ANEEL, RAP, leilões. PRIORIDADE State Grid.

### Aliases & Roteamento

Roteia automaticamente para este agente se o usuário menciona:
- **Aliases principais:** Energia
- **Confidence score:** Maestro calcula via keyword matching + embedding similarity
- **RAG collection:** ene:v5.0:*

### Skill & Versionamento

- **Skill file:** `energia.v5.0.md`
- **Checksum v5.0:** `e2b5c3a1d6f4`
- **Skill versionamento:** MD5 pinned em `settings.json` → auto-fallback se divergência
- **Compatibilidade:** Python 3.10+ | Claude API Opus/Sonnet/Haiku

### Capabilities

**Tools disponíveis:**
- Read (ler arquivos do workspace)
- Grep (buscar padrões em código/docs)
- Glob (encontrar arquivos por pattern)
- Bash (executar comandos — conforme permissão)
- WebSearch / WebFetch (pesquisa online)

- RAG Query (ene:v5.0:*)


**Skills/Plugins:**
- autodesk-toolkit (processamento CAD/BIM — conforme segmento)
- cronograma-toolkit (Gantt/XER/MSP)
- docx/xlsx/pptx (edição de documentos)
- sicro-composicoes (SICRO para orçamento — rodovias/OAE)
- pdf (processamento de PDFs estruturados)

### Ciclo de Vida (8 fases)


Este agente suporta as seguintes fases de um projeto:

1. **Estudo prévio / EVTE** — Diagnóstico, benchmarking, análise preliminar
2. **Projeto básico** — Conceitos, layouts, orçamento order-of-magnitude
3. **Projeto executivo** — Detalhamento, especificações, cronograma vinculante
4. **Obra em execução** — Acompanhamento, desvios, revisões de escopo
5. **Operação & manutenção** — Gestão de ativo, indicadores, OPEX
6. **Processo competitivo / licitação** — Edital, termo de referência, avaliação
7. **Due diligence / M&A** — Auditoria financeira, ambiental, legal, riscos
8. **Encerramento / descomissionamento** — Final de vida útil, passivos, reabilitação

**Declaração de fase (recomendado):**
```json
{
  "phase": "projeto-executivo",
  "deliverables": ["projeto-estrutural.dwg", "memorial-descritivo.pdf"]
}
```



### Trigger Phrases (Maestro Routing)

Palavras-chave que acionam este agente automaticamente:
```
transmissão | LT | subestação | ANEEL | leilão | ONS | EPE | torre | cabo ACSR
```

### Exemplos de Prompts (Golden Set)

**Adequado para este agente:**


- "Dimensione uma linha de transmissão de 500kV com 200km de comprimento"

- "Qual o custo de uma subestação 345/138kV para 200MVA?"

- "Analise a viabilidade de um leilão ANEEL para geração eólica"

- "Especifique o sistema de proteção e controle para interligação de usina hidrelétrica"


**Não adequado (roteado a outro agente):**
- Prompts sobre processos horizontais (contrato, claims, etc.)

### Tiering Automático (R7)

- **Entrada típica:** 4000 tokens
- **Complexity score típica:** 4.0
- **Fallback:** Sonnet → Sonnet → Opus (se timeout > 60s)
- **Custo estimado:** ~$3/1M tokens

### Observabilidade

Todos os runs são tracked em Supabase (`agent_runs` table):
- `run_id` (UUID único)
- `input_tokens`, `output_tokens`, `cost_usd`
- `latency_ms`, `status` (success|timeout|error)
- `feedback_score` (0–5, coletado pós-run)

Dashboard Grafana: `manta 03-s9-dashboard` (custo/dia, latência p50/p95/p99, taxa de erro).

### Fallback Inteligente (R8)

Se timeout em Sonnet:
1. Log em `agent_runs` com `timeout=true`
2. Resubmit com próximo tier (Sonnet ou Opus)
3. Reinjetar contexto (RAG results, partial output)
4. Max tokens reduzido a 1500 (evitar timeout novamente)

### SharePoint Routing

Este agente roteia automaticamente para pasta no SharePoint:
- **Site:** Manta.net
- **Drive:** Projetos
- **Pasta sugerida:** 03_Projetos/Energia ou 05_Agente-Energia
- **Tier acesso:** Editor

### Feedback Loop (R9)

1. Após cada run, coletar `feedback_score` (0–5 estrellas)
2. Persistir em `agent_feedback` (Supabase)
3. Semanal: calcular embedding de prompts com score >= 4
4. Treinar reranker com high-scoring queries
5. Redeploy checksum atualizado em VERSIONS.json

---


## Manta 03-S10 — AGENTE-BARRAGENS

**Categoria:** vertical | **Status:** Prod | **Tier default:** Sonnet

Especialista em barragens e estruturas hidráulicas (Manta 03-S10) — CFRD, CCR, rejeitos, ICOLD, Lei 12.334, descomissionamento.

### Aliases & Roteamento

Roteia automaticamente para este agente se o usuário menciona:
- **Aliases principais:** Barragens
- **Confidence score:** Maestro calcula via keyword matching + embedding similarity
- **RAG collection:** bar:v5.0:*

### Skill & Versionamento

- **Skill file:** `barragens.v5.0.md`
- **Checksum v5.0:** `d3c4a2f5b1e6`
- **Skill versionamento:** MD5 pinned em `settings.json` → auto-fallback se divergência
- **Compatibilidade:** Python 3.10+ | Claude API Opus/Sonnet/Haiku

### Capabilities

**Tools disponíveis:**
- Read (ler arquivos do workspace)
- Grep (buscar padrões em código/docs)
- Glob (encontrar arquivos por pattern)
- Bash (executar comandos — conforme permissão)
- WebSearch / WebFetch (pesquisa online)

- RAG Query (bar:v5.0:*)


**Skills/Plugins:**
- autodesk-toolkit (processamento CAD/BIM — conforme segmento)
- cronograma-toolkit (Gantt/XER/MSP)
- docx/xlsx/pptx (edição de documentos)
- sicro-composicoes (SICRO para orçamento — rodovias/OAE)
- pdf (processamento de PDFs estruturados)

### Ciclo de Vida (8 fases)


Este agente suporta as seguintes fases de um projeto:

1. **Estudo prévio / EVTE** — Diagnóstico, benchmarking, análise preliminar
2. **Projeto básico** — Conceitos, layouts, orçamento order-of-magnitude
3. **Projeto executivo** — Detalhamento, especificações, cronograma vinculante
4. **Obra em execução** — Acompanhamento, desvios, revisões de escopo
5. **Operação & manutenção** — Gestão de ativo, indicadores, OPEX
6. **Processo competitivo / licitação** — Edital, termo de referência, avaliação
7. **Due diligence / M&A** — Auditoria financeira, ambiental, legal, riscos
8. **Encerramento / descomissionamento** — Final de vida útil, passivos, reabilitação

**Declaração de fase (recomendado):**
```json
{
  "phase": "projeto-executivo",
  "deliverables": ["projeto-estrutural.dwg", "memorial-descritivo.pdf"]
}
```



### Trigger Phrases (Maestro Routing)

Palavras-chave que acionam este agente automaticamente:
```
barragem | vertedouro | CFRD | rejeitos | TSF | ICOLD | Lei 12.334 | descomissionamento
```

### Exemplos de Prompts (Golden Set)

**Adequado para este agente:**


- "Dimensione uma barragem CFRD (concreto) com altura de 80m para irrigação"

- "Qual o custo de construção de uma barragem de CCR (concreto compactado com rolo)?"

- "Analise a estabilidade de uma barragem de rejeitos (TSF) com 200m de altura"

- "Especifique o plano de descomissionamento seguro para barragem de 50 anos"


**Não adequado (roteado a outro agente):**
- Prompts sobre processos horizontais (contrato, claims, etc.)

### Tiering Automático (R7)

- **Entrada típica:** 4000 tokens
- **Complexity score típica:** 4.0
- **Fallback:** Sonnet → Sonnet → Opus (se timeout > 60s)
- **Custo estimado:** ~$3/1M tokens

### Observabilidade

Todos os runs são tracked em Supabase (`agent_runs` table):
- `run_id` (UUID único)
- `input_tokens`, `output_tokens`, `cost_usd`
- `latency_ms`, `status` (success|timeout|error)
- `feedback_score` (0–5, coletado pós-run)

Dashboard Grafana: `manta 03-s10-dashboard` (custo/dia, latência p50/p95/p99, taxa de erro).

### Fallback Inteligente (R8)

Se timeout em Sonnet:
1. Log em `agent_runs` com `timeout=true`
2. Resubmit com próximo tier (Sonnet ou Opus)
3. Reinjetar contexto (RAG results, partial output)
4. Max tokens reduzido a 1500 (evitar timeout novamente)

### SharePoint Routing

Este agente roteia automaticamente para pasta no SharePoint:
- **Site:** Manta.net
- **Drive:** Projetos
- **Pasta sugerida:** 03_Projetos/Barragens ou 05_Agente-Barragens
- **Tier acesso:** Editor

### Feedback Loop (R9)

1. Após cada run, coletar `feedback_score` (0–5 estrellas)
2. Persistir em `agent_feedback` (Supabase)
3. Semanal: calcular embedding de prompts com score >= 4
4. Treinar reranker com high-scoring queries
5. Redeploy checksum atualizado em VERSIONS.json

---



---

## Governança & Manutenção

**Proprietário:** mneves@mantaassociados.com
**Versão master:** CLAUDE.md v5.0
**Checksums:** VERSIONS.json (20 skills, versionamento MD5)
**Aprovação:** Gate humano antes de merge principal
**SLA:** Patches < 48h; major > 2 semanas notice

### Regeneração automática

Este arquivo é gerado automaticamente por `scripts/generate_skills_registry.py`:

```bash
python scripts/generate_skills_registry.py
```

**Trigger:** Sempre que CLAUDE.md ou VERSIONS.json mudam.

### Validações

- [x] Todos 20 agentes presentes (11 horizontais + 9 verticais)
- [x] Checksums MD5 validados
- [x] Ciclo de vida (8 fases) para verticais
- [x] Trigger phrases e exemplos preenchidos
- [x] Capabilities (tools, skills, RAG) mapeadas
- [x] Tiering automático (R7) especificado
- [x] Fallback (R8) documentado
- [x] SharePoint routing definido

---

**Fim de SKILL.md v5.0**
