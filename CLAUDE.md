# CLAUDE.md — Manta Maestro (Agent Registry)

Registro mestre dos agentes IA da Manta Associados. Este arquivo é o
"CLAUDE.md master" referenciado pelos SKILL.md e pelos runbooks
operacionais no SharePoint.

Versão: **v4.3** (2026-07-13) — política de modelos + escalada explícita
por complexidade da tarefa.

---

## MAPA COMPLETO DE AGENTES — 20 agentes, 3 eixos

### Eixo 1 — Horizontais (transversais a todos os segmentos)

| Código | Agente | Aliases | Tier default | Status |
|--------|--------|---------|--------------|--------|
| Manta 00 | maestro (router) | maestro, manta-router | Haiku 4.5 → Sonnet 5 | ✅ Operacional |
| Manta 01 | claims | 02-C, manta-claims | Opus 4.8 | ✅ Operacional |
| Manta 02 | contratual | manta-02, contratual | Sonnet 5 | ✅ Operacional |
| Manta 04 | imobiliario | manta-04 | Sonnet 5 | ✅ Operacional |
| Manta 05 | orcamento | manta-05 | Sonnet 5 | ✅ Operacional |
| Manta 06 | modelagem | manta-06 | Sonnet 5 → Opus 4.8 | ✅ Operacional |
| Manta 07 | cronograma | manta-07 | Sonnet 5 | ✅ Operacional |
| Manta 13 | bd | manta-13, business-dev | Sonnet 5 | ✅ Operacional |
| Manta 14 | apresentacoes | manta-14-pptx | Sonnet 5 | ✅ Operacional |
| Manta 15 | advisory | manta-15, advisory | Sonnet 5 → Opus 4.8 | ✅ Operacional |
| Manta 16 | arquiteto-ia | manta-15-arq | Opus 4.8 | ✅ Operacional |

### Eixo 2 — Verticais por segmento (C3)

| Código | Segmento | Agente | Status |
|--------|----------|--------|--------|
| Manta 03-S1 | Rodovias | agente-infraestrutura (S1) | ✅ Operacional |
| Manta 03-S2 | OAE (pontes, viadutos) | agente-infraestrutura (S2) | ✅ Operacional |
| Manta 03-S3 | Ferrovia | agente-infraestrutura (S3) | ✅ Operacional |
| Manta 03-S4 | Metrô | agente-infraestrutura (S4) | ✅ Operacional |
| Manta 03-S5 | Túneis | agente-infraestrutura (S2+S4) | ⚡ Parcial (coberto por S2/S4) |
| Manta 03-S6 | Portos | agente-portos | 🆕 Criado 2026-07-05 |
| Manta 03-S7 | Aeroportos | agente-aeroportos | 🆕 Criado 2026-07-05 |
| Manta 03-S8 | Saneamento | agente-saneamento | 🆕 Criado 2026-07-05 — PRIORIDADE AySA |
| Manta 03-S9 | Energia | agente-energia | 🆕 Criado 2026-07-05 — ANEEL/State Grid |
| Manta 03-S10 | Barragens | agente-barragens | 🆕 Criado 2026-07-05 |

### Eixo 3 — Ciclo de vida (8 fases)

Todos os agentes verticais suportam as 8 fases via intake Q2:
1. Estudo prévio / EVTE
2. Projeto básico
3. Projeto executivo
4. Obra em execução
5. Operação & manutenção
6. Processo competitivo / licitação
7. Due diligence / M&A
8. Encerramento / descomissionamento

---

## POLÍTICA DE MODELOS — Escalação Manta

Política padrão para todos os 20 agentes. Escalação por **complexidade
da tarefa**, não por preferência do usuário. Determinístico primeiro;
LLM só quando o parser falhar.

Todos os `.claude/agents/*.md` deste repositório declaram `model:` no
frontmatter, seguindo os tiers abaixo.

### Tier 0 — Roteador / utilitários baratos (Haiku 4.5)

- Manta 00 maestro classificando intent Q1/Q2 do intake
- Título de conversa, memória reflexiva (Haiku extraction), dedupe de
  artefato, resumo curto
- Classificação de prancha (PRL/RioSP), `sheet_type` do OAE,
  `domain_detector` do AskCAD
- Alvo: > 60% dos turnos operacionais

### Tier 1 — Cavalo de batalha (Sonnet 5) — default de vertical + operacional

- Todos os verticais S1–S10 (rodovias, OAE, ferrovia, metrô, portos,
  aeroportos, saneamento, energia, barragens)
- Horizontais operacionais: 02 contratual, 04 imobiliário, 05 orçamento,
  07 cronograma, 13 BD, 14 apresentações
- AskCAD Q&A sobre DXF/PDF (`ASKCAD_MODEL=claude-sonnet-5`)
- Fallback vision de extração: sondagem raster, prancha desconhecida,
  layer detection do balanço
- Persona builder / arquiteto de personas
- Alvo: ~25-30% dos turnos

### Tier 2 — Raciocínio pesado (Opus 4.8) — só quando justifica

- Manta 01 claims (litígio, valor em jogo)
- Manta 16 arquiteto-IA (design do próprio sistema de agentes)
- Manta 06 modelagem em casos complexos (otimização estrutural,
  verificação normativa cruzada)
- Manta 15 advisory em decisão estratégica de M&A / DD
- **Escalada automática** de qualquer Tier 1 quando qualquer um se
  aplicar:
  - Confidence do modelo < 0.5 no output
  - Retentativa após erro/ambiguidade
  - Fase 6 (licitação) ou Fase 7 (DD/M&A) do ciclo de vida
  - Usuário pedir explicitamente "análise a fundo", "revise
    cuidadosamente", "segundo parecer"
- Alvo: ≤ 10-15% dos turnos

### Regra transversal — Determinístico PRIMEIRO

**Zero LLM** em extração que já tem parser determinístico:

- OAE: regex universal NBR 7480 `(MULTx) N.M [Ax]B Ø D [C/S] C=L`
- Sondagem: templates ENGEFOTO e AS Geotecnia/PRVias (âncora estrita)
- LandXML: SAX streaming
- Ezdxf: HATCH → Shapely, LWPOLYLINE, TEXT/MTEXT
- Iluminação, Pavimentação, Terraplenagem: pipelines geométricos puros

LLM entra **só como fallback** quando o determinístico devolver
`confidence < 0.7` ou `template_unknown = true` (ex.: sondagens raster
escaneadas ativam `--llm` com Sonnet 5 vision; hoje ≈ US$ 0,09/laudo).

### Escalada — manual ANTES de automática

Ligar escalada automática (`Tier 1 → Tier 2` por confidence) **só
depois** de 1-2 semanas de operação com escalada manual/explícita.
Medir taxa de retrabalho, calibrar threshold nos dados reais. Sem
calibração empírica, Opus vira default silencioso e queima orçamento.

Fase 1 (agora): escalada manual, usuário/agente sinaliza "vá pra Opus".
Fase 2 (após medição): escalada automática por sinal de confidence.

### Como declarar tier em um agente novo

No frontmatter YAML de `.claude/agents/<nome>.md`:

```yaml
---
name: agente-exemplo
description: ...
tools: [Read, Grep, Glob, Bash, WebSearch, WebFetch]
model: sonnet   # haiku | sonnet | opus | fable
---
```

O harness resolve `sonnet` para a versão mais recente (hoje: Sonnet 5).
Para pinar versão específica, usar o id completo (ex.:
`claude-sonnet-5`).

---

## ROUTING — Maestro (Manta 00)

O maestro roda em **Haiku 4.5** para classificar intent (barato e
rápido). Cada regra abaixo despacha para o agente vertical em
**Sonnet 5**. Se o vertical retornar `confidence < 0.5` ou
`stage_failed`, o maestro re-despacha em **Opus 4.8**.

Regra de roteamento atualizada para Q1 do intake:

```
IF menção a saneamento|ETA|ETE|adutora|esgoto|AySA|drenagem urbana|SNIS
   → agente-saneamento (S8)

IF menção a transmissão|LT|subestação|ANEEL|RAP|leilão transmissão|ONS|EPE
   → agente-energia (S9)

IF menção a porto|terminal|ANTAQ|dragagem|molhe|berço|calado|contêiner|granel
   → agente-portos (S6)

IF menção a aeroporto|pista pouso|ANAC|ICAO|TPS|TECA|balizamento
   → agente-aeroportos (S7)

IF menção a barragem|vertedouro|CFRD|CCR|rejeitos|PNSB|ICOLD|CBDB|TSF
   → agente-barragens (S10)

# Regras existentes S1-S4 mantidas sem alteração
IF menção a rodovia|pavimento|CBUQ|BGS|terraplenagem|SICRO|DNIT
   → agente-infraestrutura S1

IF menção a ponte|viaduto|OAE|NBR 7187|túnel rodoviário
   → agente-infraestrutura S2

IF menção a ferrovia|trilho|AMV|dormente|via permanente
   → agente-infraestrutura S3

IF menção a metrô|estação|NATM|PSD|linha 4|linha 5|VLT
   → agente-infraestrutura S4
```

---

## RAG — Coleções em Supabase

| Coleção | Prefixo storage | Fontes iniciais | Status |
|---------|-----------------|-----------------|--------|
| saneamento | san: | SNIS, IWA, NBR 12211-12218, Lei 14.026, editais BNDES | 🆕 v4.2 |
| energia | ene: | ANEEL editais, R1-R5 EPE, ONS, IEEE | 🆕 v4.2 |
| portos | por: | ANTAQ, PIANC, editais BNDES/ANTAQ | 🆕 v4.2 |
| aeroportos | aer: | ANAC/RBAC, ICAO Annex 14, FAA ACs | 🆕 v4.2 |
| barragens | bar: | ICOLD, CBDB, SIGBM, Lei 12.334 | 🆕 v4.2 |

---

## SHAREPOINT — Routing rules (sp_agent_routing)

| Agente | Pasta SP sugerida | Pattern |
|--------|-------------------|---------|
| agente-saneamento | 03_Projetos/Saneamento/* | *.pdf, *.dwg, *.xlsx |
| agente-energia | 03_Projetos/Energia/* | *.pdf, *.dwg, *.xlsx |
| agente-portos | 03_Projetos/Portos/* | *.pdf, *.dwg, *.xlsx |
| agente-aeroportos | 03_Projetos/Aeroportos/* | *.pdf, *.dwg, *.xlsx |
| agente-barragens | 03_Projetos/Barragens/* | *.pdf, *.dwg, *.xlsx |

---

## DEPLOY CHECKLIST v4.2

- [x] Copiar 5 agent .md para `.claude/agents/`
- [x] Aplicar patch no CLAUDE.md master (seção Agentes)
- [ ] Criar 5 coleções RAG em Supabase (`rag_chunks`)
- [ ] Inserir 5 routing rules em `sp_agent_routing`
- [ ] Criar pastas SP para novos segmentos
- [ ] Registrar skills no catálogo (skill registry)
- [ ] Testar routing do Maestro com prompts de cada segmento
- [ ] Upload dos SKILL.md para SP em `01-agentes-fundamentais/`
- [ ] Atualizar `ARQUITETURA-AGENTES-IA.md` no SP (v1.0.0 → v2.0.0)
- [ ] Gate humano: aprovação MN antes de merge

---

## DEPLOY CHECKLIST v4.3 (política de modelos)

- [x] Formalizar política de tiers no CLAUDE.md master
- [x] Anotar maestro com tier de rodagem (Haiku 4.5) no bloco ROUTING
- [x] Verificar frontmatter `model:` dos 5 verticais S6–S10 (todos
      `sonnet` — consistente com Tier 1)
- [ ] Auditar frontmatter dos agentes horizontais e S1–S4 no repositório
      operacional do Maestro (garantir `model:` explícito)
- [ ] Instrumentar telemetria de `confidence` por turno para calibrar
      threshold da escalada automática
- [ ] Definir sinal explícito de escalada manual ("análise a fundo" →
      Opus 4.8) no prompt de intake do Maestro
- [ ] Definir métricas de baseline (custo/turno, taxa de retrabalho por
      tier) antes de ligar escalada automática
- [ ] Gate humano: aprovação MN antes de merge

---

## Arquivos deste repositório

```
Codex-exemplo/
├── CLAUDE.md                         # este arquivo (master registry)
└── .claude/
    └── agents/
        ├── agente-portos.md          # 🆕 S6
        ├── agente-aeroportos.md      # 🆕 S7
        ├── agente-saneamento.md      # 🆕 S8 — prioridade AySA
        ├── agente-energia.md         # 🆕 S9 — ANEEL/State Grid
        └── agente-barragens.md       # 🆕 S10
```

Os agentes existentes (Manta 00, 01, 02, 04-07, 13-16, 03-S1..S4) vivem
no repositório operacional do Maestro. Este repositório (`Codex-exemplo`)
serve como referência canônica versionada dos agentes verticais e do
mapa de routing.

---

## Histórico de versões

- **v4.3** (2026-07-13) — política de modelos formalizada. Tier 0
  Haiku 4.5 (roteador/utilitários), Tier 1 Sonnet 5 (todos os
  verticais + operacionais), Tier 2 Opus 4.8 (claims, arquiteto-IA,
  modelagem/advisory complexos). Regra transversal "determinístico
  primeiro". Escalada manual antes de automática. Maestro anotado
  com tier no bloco de routing. Ticket MNT-2026-MODEL-POLICY.
- **v4.2** (2026-07-05) — expansão S6–S10 (Portos, Aeroportos,
  Saneamento, Energia, Barragens). 5 novos agentes verticais + 5
  coleções RAG + 5 pastas SP. Ticket MNT-2026-UPGRADE-AGENTS-S6S10.
- **v4.1** (anterior) — 15 agentes: horizontais + S1–S4.
