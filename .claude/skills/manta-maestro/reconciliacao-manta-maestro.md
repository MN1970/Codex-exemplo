# Reconciliação manta-maestro — local v5.0.1 × SharePoint v4.7.0

Levantamento de apoio ao `SKILL.md` v6.0.0 (13/08/2026). Registra por que
as duas linhas bifurcaram, o que cada uma tinha de diferente, e a decisão
tomada em cada ponto de conflito. Decisões já aplicadas no `SKILL.md` estão
marcadas lá com 🔀 e repetidas aqui com o raciocínio completo.

## Como bifurcou

| Linha | Local | Versão | Data | Característica |
|---|---|---|---|---|
| A | `skills/user/manta-maestro` (Claude Code) | v5.0.1 | 27/06/2026 | Taxonomia concreta: S1-S11 todos ligados a skills reais instaladas. Sem descrição do "agentic OS" mais amplo. |
| B | SharePoint `04_IA/Manta-Maestro/05-sub-skills/manta-maestro/SKILL.md` | v4.7.0 | 13/07/2026 | Arquitetura mais avançada (memória episódica, cost tracking, SkillForge, loop engineering, LLM-as-judge) mas nenhuma skill real listada — roadmap, não implementação. |

As duas evoluíram em paralelo por ~2 semanas sem que uma referenciasse a
outra. Nenhuma delas está "errada" — A é a implementação corrente, B é o
roadmap de arquitetura. O v6.0.0 funde as duas: taxonomia e skills reais de
A, estrutura de camadas/fluxo de B, com os itens de infraestrutura não
confirmada de B rebaixados a backlog (§11 do SKILL.md).

## Bug corrigido

O `SKILL.md` local (linha A) tinha frontmatter YAML duplicado — dois blocos
`---` no topo do arquivo, o segundo redundante. Isso pode quebrar parsers de
frontmatter que assumem um único bloco. Corrigido no v6.0.0: um único bloco
YAML válido.

## Decisões de reconciliação (🔀)

### 1. Segmento "imobiliário" (S5 em B) → F-imobiliario

- B listava `S5 = imobiliário` como segmento vertical.
- A não tinha imobiliário como segmento — tinha como parte funcional,
  já ligada a `financial-analysis:dcf-model`.
- **Decisão:** manter A. Imobiliário passa a ser o funcional
  `F-imobiliario` (§3.3 do SKILL.md), não um segmento vertical. `S5` no
  v6.0.0 é "Infraestrutura geral", como em A.
- **Motivo:** imobiliário em A já está integrado a uma skill real
  (`financial-analysis:dcf-model`); reclassificar como segmento em B
  teria exigido reconstruir esse vínculo sem ganho claro.

### 2. Embedding RAG — 384d (A) × 1024d/hybrid (B)

- A usa `BAAI/bge-small-en-v1.5`, 384 dimensões, confirmado em produção
  no projeto Supabase `ogxxgvgtulrbbppshjie`.
- B citava migração para `bge-m3`/1024d + busca híbrida (textual +
  vetorial), sem confirmação de que o schema já suporta isso.
- **Decisão:** manter 384d como padrão ativo. A migração para 1024d/hybrid
  fica registrada como item de backlog (§11) — **não migrar sem validar o
  schema real em produção primeiro**.
- **Motivo:** risco de quebrar RAG em produção por adotar uma spec de
  roadmap não verificada.

### 3. Nomes de modelo inexistentes

- B citava "Opus 4.7" e "Sonnet 4.6" no model tiering — esses modelos não
  existem.
- **Decisão:** corrigido para os modelos reais atuais (Haiku 4.5, Sonnet 5,
  Opus 4.8), mantendo o mapeamento de capacidade→modelo que B propunha.
- **Motivo:** erro factual simples; a lógica de tiering de B (rotear por
  capacidade, não por segmento) era boa e foi preservada.

### 4. Reflexion Loop — memória episódica (B) × skills existentes (A)

- B descrevia um Reflexion Loop apoiado em memória episódica
  (`agent_episodes` + `get_relevant_episodes()`), tabela não confirmada em
  produção.
- A não tinha Reflexion Loop formalizado, mas já tinha `aluci-guard` e
  `consist-guard` v2 instalados e operacionais.
- **Decisão:** implementar o Reflexion Loop de B, mas trocando a dependência
  de memória episódica por chamadas diretas a `aluci-guard`/`consist-guard`
  (§5 do SKILL.md). Memória episódica fica em backlog (§11).
- **Motivo:** entrega o mesmo benefício (autocrítica antes de outputs
  ★★/★★★) sem depender de infraestrutura não confirmada.

### 5. Itens de roadmap de B sem contrapartida em produção

Rebaixados a backlog (§11 do SKILL.md), documentados mas não ativos:

- Memória episódica (`agent_episodes`)
- Cost tracking (`maestro_cost_log`, `v_cost_by_agent`)
- SkillForge (auto-geração de skills com gate humano)
- Loop Engineering (`/goal`, `/loop`, dynamic workflow swarm)
- LLM-as-a-judge (amostragem 10% via GH Action)
- S12-S14 (Túneis, Mineração, Óleo & Gás) — propostos em B sem skill
  vinculada; mantidos como segmentos propostos, não operacionais
- RAG 1024d/hybrid (ver item 2 acima)

**Motivo geral:** nenhum destes tem confirmação de que a infraestrutura
Supabase/CI necessária existe em produção. Documentar como backlog evita
que o Maestro assuma comportamento que na prática não roda, sem descartar
o trabalho de arquitetura já feito em B.

## Gate MN — resultado (13/08/2026)

### 1. `agent_episodes` e infraestrutura "não confirmada" — investigado, não apenas perguntado

Antes de levar ao MN, a tabela e o schema foram checados direto no
Supabase (`ogxxgvgtulrbbppshjie`) via MCP — isso é um fato verificável,
não uma decisão de negócio. Resultado, contrariando a suposição da
v6.0.0 de que essa infra "não estava confirmada em produção":

| Objeto | Existe? | Estado real |
|---|---|---|
| `agent_episodes` (tabela) | Sim | 1 linha. Comentário no schema: "v4.7 Upgrade A+C" |
| `get_relevant_episodes()` (função) | Sim | implementada |
| `consolidate_old_episodes()` (função) | Sim | implementada |
| `maestro_cost_log` (tabela) | Sim | 0 linhas |
| `v_cost_by_agent` (view) | Sim | existe, mas sem dados para agregar ainda |
| `manta_rag_chunks.embedding` (384d, bge-small) | Sim | 162/292 chunks populados; índice HNSW cosine ativo — **é o que a busca usa hoje** |
| `manta_rag_chunks.embedding_m3` (1024d, bge-m3) | Sim | coluna e índice HNSW já criados, **0/292 populados** |

Ou seja: o "backlog por infraestrutura não confirmada" da v6.0.0 estava
errado no diagnóstico — a infraestrutura existe e foi provisionada no
upgrade v4.7, só nunca foi ligada a nenhum fluxo real (dados vazios ou
quase vazios). Isso foi levado ao MN não como "existe ou não?" (já
respondido), e sim como "agora que sabemos que existe, ativamos?".

**Decisão do MN: ativar agora.** Memória episódica e cost tracking
foram religados ao Reflexion Loop (`SKILL.md` §5). A migração para
1024d/bge-m3 foi autorizada, mas o backfill dos 292 chunks (162 com
384d, 0 com 1024d) é trabalho pendente — não existe Edge Function nem
script de embedding bge-m3 implantado no projeto Supabase ainda, e essa
implementação cabe ao runtime (`manta-hub`), fora do escopo deste
repositório de referência. Registrado como ação de acompanhamento em
`SKILL.md` §11.1.

### 2. S12-S14 (Túneis/Mineração/Óleo&Gás) — demanda confirmada, especificação pendente

MN confirmou que **há demanda real** de projeto para vincular skill a
pelo menos um destes segmentos, mas a resposta não especificou qual
segmento (S12/S13/S14), qual projeto e qual skill deveria ser
vinculada. Por R2 (não inventar), isso não foi assumido — o `SKILL.md`
(§3.1, §11.3) registra o status como "em definição" e nenhuma skill foi
vinculada a S12/S13/S14 nesta rodada. **Precisa de uma resposta mais
específica do MN** antes de qualquer edição nesses segmentos.

### 3. Imobiliário — segmento (SharePoint) × funcional (local)

**Confirmado pelo MN**: mantém `F-imobiliario` como agente funcional
(decisão original da v6.0.0), sem reverter para segmento S5. Nenhuma
mudança necessária.
