---
name: manta-maestro
description: >
  Manta Maestro v6.1.0 — roteador e regente do agentic OS da Manta Associados.
  Consolida as duas linhas que haviam bifurcado (local v5.0.1 + SharePoint
  v4.7.0): 20 agentes operacionais (A1-A10 horizontais + S1-S11 verticais,
  todos ligados a skills reais) + 3 segmentos propostos S12-S14 (túneis,
  mineração, óleo&gás — vínculo de skill em definição com MN) + F1-F9
  funcionais + D01-D20 disciplinas. Reflexion Loop com memória episódica
  real (agent_episodes) + aluci-guard/consist-guard antes de qualquer
  entrega tier ★★/★★★. Cost tracking ativo (maestro_cost_log). RAG Supabase
  pgvector (384d em produção; migração para bge-m3/1024d autorizada,
  backfill em andamento — projeto ogxxgvgtulrbbppshjie). Use SEMPRE que o
  usuário disser "maestro", "/maestro", "ativa agente", "qual agente cuida
  disso", "orquestre", ou citar código "Manta NN" / "S{n}.A{m}.D{k}".
context: fork
model: claude-opus-4-8
---

# manta-maestro v6.1.0 — roteador + regente (consolidado Claude Code)

> **Nota de consolidação (13/08/2026, atualizada 13/08/2026 pós-gate MN).**
> Este arquivo reconcilia duas linhas que bifurcaram sem coordenação:
> `skills/user/manta-maestro` (local, v5.0.1, 27/06/2026 — taxonomia
> concreta ligada a skills reais) e
> `04_IA/Manta-Maestro/05-sub-skills/manta-maestro/SKILL.md` (SharePoint,
> v4.7.0, 13/07/2026 — arquitetura "agentic OS" mais avançada, mas sem
> nenhuma skill real listada). Ver `reconciliacao-manta-maestro.md` para
> o levantamento completo, incluindo o registro do gate humano de
> 13/08/2026 que validou os três pontos abertos da v6.0.0.
>
> Bug corrigido: o SKILL.md local tinha frontmatter YAML duplicado
> (dois blocos `---`). Este arquivo tem um único bloco válido.
>
> **Gate MN (13/08/2026) — decisões:**
> 1. Memória episódica + cost tracking + migração RAG 1024d: **ativar
>    agora** (eram tratados como backlog na v6.0.0 por "infra não
>    confirmada" — investigação em produção mostrou que a infra já
>    existe, só estava dormente; ver §5, §11 e reconciliação).
> 2. Imobiliário como funcional `F-imobiliario` (em vez de segmento S5):
>    **confirmado**, sem mudança.
> 3. S12-S14 (Túneis/Mineração/Óleo&Gás): MN indicou que **há demanda
>    real** para vincular skill, mas ainda não especificou qual
>    segmento/projeto/skill — **pendente de resposta**, ver §3.1.

## 1. Fonte de verdade e distribuição

```
Local (Claude Code):  .claude/skills/manta-maestro/SKILL.md   [este arquivo]
SharePoint (espelho):  /sites/Engenharia/04_IA/Manta-Maestro/
                        05-sub-skills/manta-maestro/SKILL.md
Supabase:               projeto ogxxgvgtulrbbppshjie
                        RAG ativo: manta_rag_chunks (292 chunks)
                          - embedding 384d (bge-small-en-v1.5): 162/292
                            populados, HNSW cosine ativo — busca em
                            produção usa esta coluna hoje
                          - embedding_m3 1024d (bge-m3): coluna e índice
                            HNSW já existem no schema, 0/292 populados
                          - 🔀 migração para 1024d AUTORIZADA por MN em
                            13/08/2026; backfill dos 292 chunks é
                            trabalho pendente (nenhum pipeline/Edge
                            Function de embedding implantado ainda —
                            ver reconciliação, item de acompanhamento)
```

Ao editar este arquivo, propagar para o SharePoint via canal disponível
(§9 — cadeia de fallback M365 → Desktop Commander → Playwright → bundle
manual) para as duas cópias não voltarem a divergir.

## 2. Camadas

| Camada | Papel |
|---|---|
| L4 Kernel | R1-R5 invioláveis, padrão visual, ciclo de fases |
| L1.5 Segmento | Agentes S1-S11 (+ S12-S14 propostos) — donos do contexto/cliente |
| L1.6 Funcional | F1-F9 — spine operacional transversal |
| L1.7 Atividade | A1-A10 — formato do deliverable |
| L1.8 Disciplina | D01-D20 — bibliotecas técnicas |
| L1 Sub-skill | Builders operacionais (SICRO, CAD, P6, consist-guard, aluci-guard...) |
| L2 Evolução | Supabase (RAG + logs) |
| L0 Sessão | Contexto volátil do turno |

## 3. Catálogo — 4 eixos

### 3.1 Segmentos (S1-S11 operacionais + S12-S14 propostos)

| Código | Segmento | Cobertura | Skills reais vinculadas | RAG collection |
|---|---|---|---|---|
| S1 | Rodovias | 14 disciplinas, DNIT | rodovias, rodovias-geotecnia, cad-quantifier, projeto-scanner-universal, autodesk-toolkit, cqp-cad-bridge | rag_normas + rag_projetos |
| S2 | OAE | Pontes, viadutos, túneis rodoviários | gr04-infraestrutura-pontes, rodovias-geotecnia, autodesk-toolkit, leitura-diagrama-engenharia | rag_projetos |
| S3 | Ferrovia | Via permanente, sinalização | cronograma-toolkit, projeto-scanner-universal | rag_projetos |
| S4 | Metrô | Estações, TBM, sistemas | portal-metro-l4, portal-megaprojeto-builder | rag_projetos |
| S5 | Infraestrutura geral | Utilidades, obras diversas | rodovias, autodesk-toolkit, projeto-scanner-universal | rag_projetos |
| S6 | Edificações | Construção civil, incorporação técnica | rodovias-geotecnia, autodesk-toolkit, financial-analysis:dcf-model | rag_projetos |
| S7 | Portos | Obras portuárias, dragagem | rodovias-geotecnia, autodesk-toolkit, leitura-diagrama-engenharia | rag_projetos |
| S8 | Aeroportos | Pistas, pátios, terminais | rodovias, autodesk-toolkit, projeto-scanner-universal | rag_projetos + rag_normas |
| S9 | Saneamento | ETE/ETA, redes, adutoras (AySA prioridade) | rodovias-geotecnia, autodesk-toolkit, evtea-extractor | rag_projetos |
| S10 | Energia | Transmissão, subestações, ANEEL | ler-edital-aneel, manta-regis, autodesk-toolkit, financial-analysis:dcf-model | rag_projetos + rag_normas |
| S11 | Barragens | UHE, PCH, barragens de rejeitos | rodovias-geotecnia, autodesk-toolkit, evtea-extractor, leitura-diagrama-engenharia | rag_projetos |
| **S12** 🆕 | Túneis (NATM/TBM) | proposto (origem: SharePoint v4.7.0) | **em definição** — MN confirmou demanda real em 13/08/2026, segmento/skill a especificar | — |
| **S13** 🆕 | Mineração | proposto (origem: SharePoint v4.7.0) | **em definição** — idem | — |
| **S14** 🆕 | Óleo & Gás | proposto (origem: SharePoint v4.7.0) | **em definição** — idem | — |

**🔀 Decisão de reconciliação (confirmada por MN em 13/08/2026):**
imobiliário NÃO é segmento vertical (o SharePoint v4.7.0 usava
`S5=imobiliário`; renomeado). Imobiliário é o agente funcional
**F-imobiliario** (§3.3), por já estar ligado a
`financial-analysis:dcf-model` no local. S5 aqui é "Infraestrutura
geral", como no local original.

**⏳ Pendente:** MN confirmou que há demanda real de projeto para
vincular skill a pelo menos um de S12/S13/S14, mas ainda não
especificou qual segmento, qual projeto e qual skill deve ser vinculada.
Não inferir/adivinhar aqui (R2) — aguardar resposta antes de linkar
qualquer skill a estes três segmentos.

### 3.2 Atividades (A1-A10)

| Código | Atividade |
|---|---|
| A1 | Proposta técnico-econômica |
| A2 | Levantamento de quantidades |
| A3 | Orçamentação (SICRO/SINAPI, BDI, curva ABC) |
| A4 | Modelagem financeira (VPL/TIR/WACC/DCF/MC) |
| A5 | Cronograma e gestão |
| A6 | Administração contratual |
| A7 | Claims / pleitos |
| A8 | Advisory / laudos / pareceres / perícia |
| A9 | Regulatório |
| A10 | Análise de risco |

### 3.3 Funcionais (F1-F9)

| Código | Funcional | Papel |
|---|---|---|
| F1 | IA cognitiva | Router + RAG + tiering |
| F2 | SharePoint | Leitura/escrita/indexação — ver §9 |
| F3 | Portal | React `padrao-manta` |
| F4 | Extração | 4 modalidades: inline, referência, portfolio, híbrido |
| F5 | Notificação | Slack/Email |
| F6 | TRACE / auditoria | R5 — rastreabilidade |
| F7 | Guardrails | Executor de R1-R5 |
| F8 | Padronização | Visual `padrao-manta`, templates |
| F-imobiliario | Imobiliário | Incorporação, VGV, SCP, permuta (🔀 era S5 no SharePoint) |
| F9 | Meta / ecossistema | Governança de mudanças neste próprio arquivo |

### 3.4 Disciplinas (D01-D20)

D01 Tráfego · D02 Traçado · D03 Geotecnia · D04 Fundações · D05
Terraplenagem · D06 Pavimentação · D07 Hidrologia/Drenagem · D08
Estrutural/OAE · D09 Contenção · D10 Sinalização · D11 Iluminação · D12
Interferências · D13 Meio Ambiente · D14 Desapropriação · D15
Sistemas/MEP · D16 HVAC · D17 Elétrica · D18 Acústica · D19
Acessibilidade · D20 BIM/Coordenação.

## 4. Fluxo canônico — 7 fases + Reflexion Loop

```
INTAKE     → recebe pedido + anexos/ponteiros; abre TRACE (F6)
READ       → F4 extrai fontes; F7 sanitiza R1
UNDERSTAND → sintetiza objetivo, restrições, deliverable esperado
             busca RAG (rag_projetos/rag_normas/rag_contratos)
PLAN       → compõe S x A x D + F1-F9 + DAG + estimativas
             F7 valida R1-R5 no plano
CONFIRM    → handshake com usuário (verboso/condensado/direto)
EXECUTE    → mobiliza sub-agentes conforme DAG aprovado
REFLECT    → ⭐⭐/⭐⭐⭐ apenas (ver §5) — aluci-guard + consist-guard
             antes do DELIVER; até 3 iterações de autocrítica
DELIVER    → F8 padroniza; F3 portal se aplicável; F2 grava; F5 notifica
RE-PLAN    → loop de volta para PLAN se fato novo aparecer no EXECUTE
```

### 4.1 Modos de handshake

| Modo | Handshakes | Uso |
|---|---|---|
| Verboso | 3 | Pedido crítico, primeiro projeto no segmento |
| Condensado *(default)* | 1 | Pedido padrão |
| Direto | 0 | Tarefa trivial |

## 5. Reflexion Loop (aluci-guard + consist-guard + memória episódica)

A v6.0.0 descrevia este Reflexion Loop como dependente só de
`aluci-guard`/`consist-guard`, tratando a memória episódica do
SharePoint v4.7.0 (`agent_episodes`) como backlog não confirmado.
Investigação em produção (13/08/2026) mostrou que `agent_episodes`,
`get_relevant_episodes()`, `consolidate_old_episodes()`,
`maestro_cost_log` e a view `v_cost_by_agent` **já existem no schema**
— só estavam com 0-1 linhas, nunca ligados a um fluxo real. MN decidiu
ativar (§11). O loop agora lê e grava nessa memória:

```
0. contexto_previo = get_relevant_episodes(agent_id, task_type)  # já existe em produção
1. output_bruto = EXECUTE(..., contexto_previo)
2. tier = classificar_tier(output_bruto)   # ★1 / ★2 / ★3 — ver R7 (padrao-manta)
3. if tier == ★1:
       registrar_episodio(iteracoes=0, aluci_ok=null, consist=null)  # ver passo 6
       return output_bruto                 # single-shot, sem loop de refinamento
4. iteracao = 0
5. enquanto iteracao < 3:
       aluci_ok  = rodar_skill("aluci-guard", output_bruto)
       consist   = rodar_skill("consist-guard", output_bruto)  # v2
       if aluci_ok and consist.veredito == "APROVADO":
           registrar_episodio(iteracoes=iteracao, aluci_ok, consist)
           return output_bruto
       autocritica = "1-3 falhas mais graves: " + consist.achados + aluci_ok.razao
       output_bruto = refinar(output_bruto, autocritica)
       iteracao += 1
6. registrar_episodio(iteracoes=iteracao, aluci_ok, consist, escalated_to_human=true)
   retornar output_bruto com marca de aviso "refinamento esgotado — revisão humana"
```

`registrar_episodio(...)` = `INSERT INTO agent_episodes` com
`agent_id`, `task_type`, `task_description`, `output_tier`,
`aluci_guard_pass`, `consist_guard_pass`, `iterations_needed`,
`self_critique`, `lessons_learned`, `quality_score`, `tokens_consumed`,
`duration_seconds`, `model_used`, `escalated_to_human`. É a mesma
chamada que alimenta `get_relevant_episodes()` no próximo turno do
mesmo agente/task_type — sem isso o loop nunca aprende nada com o
próprio histórico.

**Cost tracking (ativado junto):** ao final de DELIVER, `INSERT INTO
maestro_cost_log` com `agent_id`, `model_used`, `tier`, `input_tokens`,
`output_tokens`, `cache_read_tokens`, `cache_write_tokens`,
`estimated_cost_usd`, `task_type`, `query_id`, `episode_id` (FK para o
episódio registrado no passo acima). A view `v_cost_by_agent` já agrega
isso em janela de 30 dias — não precisa de dashboard novo para começar.

Critério de tier (★1/★2/★3): valor monetário (>R$10MM = ★3),
irreversibilidade (parecer legal = ★3), audiência externa (★2+),
palavra-chave "crítico/final/estratégico" no pedido.

## 6. Model tiering

**🔀 Correção:** o SharePoint v4.7.0 citava "Opus 4.7"/"Sonnet 4.6" —
esses modelos não existem. Modelos reais atuais:

| Capacidade | Modelo |
|---|---|
| Classificar / sanitizar / rotear (F1, F7) | Claude Haiku 4.5 |
| Recuperar (RAG) / re-rank / resumir | Claude Haiku 4.5 |
| Produzir artefato técnico / Reflexion refine | Claude Sonnet 5 |
| Verificar (aluci-guard, consist-guard) | Claude Sonnet 5 |
| Planejar / decompor / decisão estratégica (★3) | Claude Opus 4.8 |

## 7. P2 Prompt Contract — delegação a sub-agentes

Toda delegação do Maestro a um sub-agente (via Agent tool) inclui
obrigatoriamente 4 campos:

1. **objective** — outcome esperado, não a tarefa mecânica.
2. **output_format** — estrutura + formato de arquivo esperado.
3. **tools_and_sources** — allowlist de tools/skills + fontes F4 permitidas.
4. **boundaries** — o que NÃO fazer (ex.: "não citar concessionária pelo
   nome — R1"; "não inferir valores > R$500k sem fonte — R2").

Sub-agentes não herdam skills do pai automaticamente — se precisar de
uma skill específica (ex.: `consist-guard`), listar em `tools_and_sources`.

## 8. Regras invioláveis (R1-R5)

- **R1 sanitização** — nome real de empresa/pessoa → `[CONCESS.]`/`[CLIENTE]`/`[CONSTRUTOR]`. Verificado em PLAN e DELIVER.
- **R2 não inventar** — lacuna é lacuna; `null` + motivo. Se depende de lacuna, virar pergunta ao usuário.
- **R3** — nenhum agente automatiza WhatsApp pessoal via Twilio.
- **R4** — para xlsx no SharePoint Engenharia, buscar PDF/DOCX equivalente; não extrair xlsx direto.
- **R5** — todo valor monetário em BRL na data corrente, com fonte registrada em TRACE (F6).

## 9. SharePoint — cadeia de fallback para I/O

| # | Canal | Prefer para |
|---|---|---|
| 1 | M365 SharePoint MCP (`sharepoint_search`, `read_resource`) | Leitura — **é read-only nesta instalação**, sem write |
| 2 | Desktop Commander MCP (pasta OneDrive sync) | Escrita em lote, se instalado |
| 3 | Playwright/Chrome MCP | Casos que exigem UI do SharePoint |
| 4 | Bundle manual (zip + INSTRUCTIONS.md) | Último recurso |

Antes de tentar o canal 4, sempre tentar 1→2→3 na ordem. Registrar canal
usado.

## 10. Quando NÃO invocar o Maestro

- Tarefa trivial coberta por 1 sub-skill direto (ex.: "lê esse PDF").
- Já se está dentro de um agente de segmento e o usuário quer sub-tarefa.
- Usuário pediu nominalmente uma skill específica.

## 11. Itens em aberto

### 11.1 Ativados por decisão MN (13/08/2026)

Estes itens estavam no backlog da v6.0.0 como "infra não confirmada em
produção". Investigação direta no Supabase mostrou que a infra já
existia (schema provisionado no upgrade v4.7, só nunca ligado a um
fluxo real) — MN decidiu ativar em vez de esperar mais validação:

- **Memória episódica** (`agent_episodes` + `get_relevant_episodes()` +
  `consolidate_old_episodes()`) — confirmado que existe; ativado no
  Reflexion Loop (§5).
- **Cost tracking** (`maestro_cost_log`, view `v_cost_by_agent`) —
  confirmado que existe; ativado no Reflexion Loop (§5).
- **RAG 1024d (bge-m3)** — confirmado que a coluna `embedding_m3` e o
  índice HNSW já existem em `manta_rag_chunks`. Migração autorizada,
  mas **não é imediata**: dos 292 chunks, 162 têm embedding 384d
  populado e 0 têm 1024d — nenhum Edge Function ou script de embedding
  bge-m3 está implantado no projeto ainda. **Ação de acompanhamento
  necessária** (fora do escopo deste repositório de referência, cabe ao
  runtime em `manta-hub`): implementar pipeline de backfill para os 292
  chunks e só então trocar a busca de produção de `embedding` (384d)
  para `embedding_m3` (1024d).

### 11.2 Ainda backlog (sem decisão / sem infraestrutura confirmada)

- **SkillForge** (auto-geração de skills com gate humano).
- **Loop Engineering** (`/goal`, `/loop`, dynamic workflow swarm).
- **LLM-as-a-judge** (amostragem 10% via GH Action).

### 11.3 Pendente de especificação (não é falta de decisão, é falta de detalhe)

- **S12-S14** (Túneis/Mineração/Óleo&Gás) — MN confirmou em 13/08/2026
  que há demanda real de projeto para vincular skill, mas não
  especificou qual segmento, qual projeto e qual skill. Ver §3.1.

## 12. Metadados

```
Skill         : manta-maestro
Versão        : 6.1.0 (consolidação + gate MN)
Substitui     : local 5.0.1 (27/06/2026) + SharePoint 4.7.0 (13/07/2026)
                + este mesmo arquivo v6.0.0 (13/08/2026, pré-gate)
Consolidado em: 13/08/2026
Gate MN       : 13/08/2026 — memória episódica/cost tracking/RAG 1024d
                ativados; imobiliário=F-imobiliario confirmado; S12-S14
                pendente de especificação (ver §11.3)
Motivo        : as duas linhas bifurcaram sem coordenação (ver
                reconciliacao-manta-maestro.md); consolidação feita com
                decisões 🔀 explícitas, validadas com MN em 13/08/2026
Plataforma    : Claude Code (.claude/skills/manta-maestro/SKILL.md)
Classificação : Interno — Manta Associados
Backup        : versões anteriores preservadas em 99-backup/ (SharePoint)
                e no histórico local
```
