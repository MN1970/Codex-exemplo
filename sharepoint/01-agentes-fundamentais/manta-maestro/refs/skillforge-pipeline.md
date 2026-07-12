# refs/skillforge-pipeline.md — manta-maestro

Referência canônica do **SkillForge** — Upgrade F do roadmap v4.7
(MNT-IA-20260712-001, §7). Pipeline que observa padrões repetitivos nos
episódios (Upgrade C) e propõe novas skills reutilizáveis para o
catálogo, com gate humano obrigatório antes de publicar.

Fonte: Zhang et al. 2025 "Agentic Context Engineering: adaptive
context for evolving agents" (arXiv:2505.xxxxx) + Axelsen et al. 2026
"MemSkill: turning episodic traces into reusable procedural knowledge"
(ICLR).

**Princípio central**: skills nascem da observação, não da
prescrição. Se um mesmo padrão de solução aparece ≥N vezes em
agent_episodes, o Maestro extrai o esqueleto, gera um SKILL.md
draft, e o MN aprova/rejeita. Sem prescrever = sem overfitting.

---

## 1. Pipeline em ASCII art

```
┌──────────────────────────────────────────────────────────────┐
│  agent_episodes (v4.7, Upgrade C) — 1000s de execuções logadas│
└─────────────────────────────┬────────────────────────────────┘
                              │
                              │  cron diário 03:00 UTC
                              ▼
┌──────────────────────────────────────────────────────────────┐
│  1. CLUSTERING                                                │
│  Agrupa episódios por similaridade de (agent_id + task_type + │
│  tools_sequence). Embedding: multilingual-e5-small 384d.       │
│  DBSCAN eps=0.15 min_samples=4.                                │
└─────────────────────────────┬────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│  2. PATTERN MINING                                            │
│  Cluster ≥ 4 episódios com quality_score ≥ 7 ⇒ candidato.     │
│  Extrai: prompt template compartilhado, sequência de tools,    │
│  parâmetros que variam vs fixos.                               │
└─────────────────────────────┬────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│  3. SKELETON GENERATION                                       │
│  Sonnet 4.6 recebe o cluster + episódios exemplares e gera:   │
│  - nome slug proposto                                          │
│  - SKILL.md draft (formato canônico)                           │
│  - lista de input_vars extraídas                                │
│  - success criteria sugeridos                                  │
└─────────────────────────────┬────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│  4. QUALITY GATE (automático)                                  │
│  Rejeita se: nome colide com skill existente / SKILL.md < 200│
│  tokens / cluster tem quality_score médio < 7 / MN já rejeitou│
│  proposta similar (LSH match).                                 │
└─────────────────────────────┬────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│  5. HUMAN GATE (MN)                                            │
│  Cria issue GH com o draft + 3 episódios exemplares linked.   │
│  MN: approve → publish OR reject → log em skillforge_rejects │
│  (usado no passo 4 para não re-propor).                        │
└─────────────────────────────┬────────────────────────────────┘
                              │  (só se approved)
                              ▼
┌──────────────────────────────────────────────────────────────┐
│  6. PUBLISH                                                    │
│  SKILL.md commitado em sharepoint/03-skills-forjadas/         │
│  publish_agents.py (v4.6 V7) empacota nos 4 canais.            │
│  Skill fica disponível para skills_preloaded do P2.            │
└──────────────────────────────────────────────────────────────┘
```

---

## 2. Regras (5 invariantes)

**R1 — Origem observacional.** Nenhuma skill é forjada sem ≥4
episódios reais com `quality_score ≥ 7`. Skills a-priori (feitas na
mão pelo MN sem observação) continuam permitidas, mas NÃO são
consideradas "forjadas" — vão para `sharepoint/04-skills-manuais/`.

**R2 — Nome único e prefixado.** Skills forjadas têm prefixo
`sf-<agente>-<verbo>-<obj>` (ex: `sf-portos-quantitativo-dragagem`)
para distinguir de skills manuais. Colisão de nome = rejeição
automática no passo 4.

**R3 — Provenance obrigatória.** Todo `SKILL.md` forjado tem no
frontmatter YAML: `forged_by_skillforge: true`, `forged_at: <date>`,
`forged_from_episodes: [uuid1, uuid2, ...]`, `initial_quality_baseline: 7.4`.
Rastreabilidade completa.

**R4 — Gate humano MN obrigatório.** ZERO auto-publish. Toda skill
forjada passa por issue GH com o rótulo `skillforge-review` e requer
approval explícito do MN (comentário `/approve` ou label
`approved-mn`). Sem exceções. Isto garante:
- (a) o Maestro não pode "cozinhar" o próprio catálogo
- (b) MN mantém curadoria editorial da voz Manta
- (c) responsabilidade humana no output final

**R5 — Rev de retirada.** Skills forjadas têm coluna
`skillforge_health` em `v_skill_usage` (v4.7 nova). Se em 30d:
quality_score médio < 6, OU usage_count < 2, OU MN adicionou label
`deprecated`, a skill é auto-retirada (não deletada, movida para
`sharepoint/03-skills-forjadas/deprecated/`). Se não é útil, sai do
catálogo ativo.

---

## 3. Self-improving skills — o loop evolutivo

O SkillForge não emite skills imutáveis. Após publicação, cada uso é
avaliado pelo LLM-as-a-judge (v4.6 V5). O ciclo evolutivo:

```
publish → skill usada em N tarefas → judge scores logados
       → SkillForge diário observa scores da skill
       → se avg quality > 8 e trend > 0 ⇒ tag "stable"
       → se avg quality < 6 ou trend < 0 ⇒ propor v2
```

**Proposta de v2**: SkillForge não sobrescreve. Cria um SKILL.md draft
com sufixo `-v2` e abre issue "skill degradation" para o MN comparar
side-by-side. Se aprovado, `-v2` substitui `-v1` (que vai para
`deprecated/`).

**Auto-retirement**: se v1 tem score < 4 em janela 14d, o próprio
Maestro para de sugerir `skills_preloaded` desta skill mesmo sem MN
aprovar retirement. Não morre — só deixa de ser recomendada.

---

## 4. Exemplos de skills que o SkillForge geraria

### 4.1 Exemplo A — `sf-portos-extrator-pianc-dragagem`

**Origem observacional** (padrão em 4 tarefas de S7 portos):

| Episódio | Cliente | Volume dragagem estimado | Tools usadas |
|----------|---------|--------------------------|--------------|
| ep_a1f2 | Porto Central (ES) | 850k m³ | `RagSearch(por:PIANC 158) → ExecuteCode(volume calc) → Markdown` |
| ep_b3c4 | TUP Açu (RJ) | 1.2M m³ | mesma sequência |
| ep_c5d6 | Cabedelo (PB) | 320k m³ | mesma sequência |
| ep_d7e8 | Itapoá (SC) | 480k m³ | mesma sequência |

Quality scores: 7.8, 8.2, 7.5, 8.9. Média 8.1 ⇒ passa R1.

**SKILL.md draft gerado**:

```yaml
---
slug: sf-portos-extrator-pianc-dragagem
name: "Extrator de quantitativos de dragagem PIANC-158"
agent: agente-portos
tier: Sonnet
forged_by_skillforge: true
forged_at: 2026-07-13
forged_from_episodes: [ep_a1f2, ep_b3c4, ep_c5d6, ep_d7e8]
initial_quality_baseline: 8.1
input_vars: [porto_nome, canal_km, largura_m, prof_atual_m, prof_meta_m, sedimento_tipo]
---

## Objetivo
Estimar volume de dragagem inicial + folga PIANC 158 para
aprofundamento de canal de acesso portuário, entregando tabela
m³ por trecho em Markdown.

## Sequência canônica
1. `RagSearch("por:PIANC 158 §4 folga técnica dragagem")` — busca a
   folga aplicável (canal reto vs curva vs bacia evolução).
2. `ExecuteCode`: volume = área_seção × comprimento_trecho × fator,
   com sedimento_tipo definindo overdredge (silte=0.5m, areia=0.3m).
3. Tabela Markdown: colunas `trecho | área | prof_atual | prof_meta |
   overdredge | volume | volume_c_folga`.

## Success criteria default (herdado pelo P2)
- Tabela tem as 7 colunas prescritas
- Cita PIANC 158 §4 explicitamente na justificativa
- Volume ± 15% da baseline histórica (query `agent_episodes` para
  `manta_projects` similar)
```

### 4.2 Exemplo B — `sf-advisory-comparador-benchmark-concessao`

**Origem observacional** (padrão em 4 tarefas de Manta 15 advisory):

Todos os 4 episódios foram "compare X com CCR/Motiva/EcoRodovias em
TIR real, prazo, riscos ambientais, alavancagem". Sempre a mesma
tabela 5×5, sempre citando os 3 comparáveis públicos.

**SKILL.md draft gerado**:

```yaml
---
slug: sf-advisory-comparador-benchmark-concessao
name: "Comparador de concessões rodoviárias vs benchmarks públicos"
agent: manta-15-advisory
tier: Sonnet
forged_by_skillforge: true
forged_at: 2026-07-13
forged_from_episodes: [ep_11a, ep_22b, ep_33c, ep_44d]
initial_quality_baseline: 7.6
input_vars: [ativo_nome, prazo_anos, tir_alvo, ipca_hoje]
---

## Objetivo
Comparar concessão rodoviária candidata com 3 benchmarks públicos
(CCR Nova Dutra, Motiva EcoRodovias, CCR AutoBAn), entregando
tabela 5×5 (linhas = 4 concessões, colunas = TIR real, prazo,
riscos ambientais, alavancagem, upside).

## Sequência canônica
1. `RagSearch("mcs: concessao rodoviaria benchmark TIR real")` —
   busca dados públicos dos 3 comparáveis.
2. `ExecuteCode`: normaliza TIR (real vs nominal), monta tabela.
3. Comentário editorial de 2 parágrafos sobre onde o ativo candidato
   se posiciona (mediana ou outlier).

## Success criteria default
- Tabela tem exatamente 4 linhas e 5 colunas
- TIR reportada em real (não nominal) para todos os 4
- Comentário editorial cita a mediana comparativa
```

---

## 5. Gate humano MN — como funciona operacionalmente

1. **Auto-detecção diária (03:00 UTC)**: SkillForge cria issue GH no
   repo `Codex-exemplo` com label `skillforge-review`, body contendo
   o draft SKILL.md e links para os episódios exemplares.
2. **MN revê** (dashboard `/admin/skillforge` no manta-hub):
   - **Approve**: comenta `/approve` — GH Action publica no SP.
   - **Approve com edit**: MN edita o draft direto no PR, aprova.
   - **Reject**: label `rejected-mn` + comentário curto (feedback é
     salvo em `skillforge_rejects` para SkillForge não re-propor).
3. **SLA**: 7 dias. Após 7d sem ação, issue vira `stale` e é
   arquivada (rejeição implícita).
4. **Métrica de saúde**: `v_skillforge_gate` mostra taxa aprovação,
   tempo médio de review, top-agents que geraram mais skills.

---

## 6. Custos e volumetria

- **Custo do pipeline diário**: ~US$0.50-1.20 (Sonnet 4.6 para
  skeleton generation + embeddings clustering).
- **Volumetria esperada** (baseline v4.7): 1-3 propostas de skill
  por semana no início; converge para 0-1 após 60d (padrões óbvios
  já capturados; skills raras dependem de mais episódios).
- **Tempo humano do MN**: ~10 min por review. 3/semana ⇒ 30 min/sem.

---

## Ver também

- `SKILL.md` §14.F — política operacional do SkillForge
- `episodic-memory-schema.md` — schema do `agent_episodes` que alimenta
- `p2-contract-template.md` — como skills forjadas entram em
  `skills_preloaded`
- `reflexion-loop-guide.md` — como `judge_score` (v4.6 V5) alimenta o
  loop evolutivo
- Roadmap MNT-IA-20260712-001 §7 — motivação e prior art
