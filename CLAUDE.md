# CLAUDE.md — Manta Maestro (Agent Registry)

Registro mestre dos agentes IA da Manta Associados. Este arquivo é o
"CLAUDE.md master" referenciado pelos SKILL.md e pelos runbooks
operacionais no SharePoint.

Versão: **v4.3.0-draft** (2026-09-11) — proposta de novo agente horizontal
Manta 17 (geotecnia/geologia) para cobrir gap identificado no mapa de
agentes. **Aguardando gate humano (MN)** — ver seção "PROPOSTA — Manta 17
(geotecnia/geologia)". Mantém v4.2.1 (expansão S6–S10 + análise de modelo
mestre de proposta técnico-comercial) inalterada.

---

## MAPA COMPLETO DE AGENTES — 20 agentes operacionais + 1 proposto, 3 eixos

### Eixo 1 — Horizontais (transversais a todos os segmentos)

| Código | Agente | Aliases | Tier default | Status |
|--------|--------|---------|--------------|--------|
| Manta 00 | maestro (router) | maestro, manta-router | Haiku→Sonnet | ✅ Operacional |
| Manta 01 | claims | 02-C, manta-claims | Opus | ✅ Operacional |
| Manta 02 | contratual | manta-02, contratual | Sonnet | ✅ Operacional |
| Manta 04 | imobiliario | manta-04 | Sonnet | ✅ Operacional |
| Manta 05 | orcamento | manta-05 | Sonnet | ✅ Operacional |
| Manta 06 | modelagem | manta-06 | Sonnet/Opus | ✅ Operacional |
| Manta 07 | cronograma | manta-07 | Sonnet | ✅ Operacional |
| Manta 13 | bd | manta-13, business-dev | Sonnet | ✅ Operacional |
| Manta 14 | apresentacoes | manta-14-pptx | Sonnet | ✅ Operacional |
| Manta 15 | advisory | manta-15, advisory | Sonnet/Opus | ✅ Operacional |
| Manta 16 | arquiteto-ia | manta-15-arq | Opus | ✅ Operacional |
| Manta 17 | geotecnia | geotecnia, manta-17, geologia | Sonnet/Opus | 🆕 Proposto 2026-09-11 — aguarda gate MN |

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

## ROUTING — Maestro (Manta 00)

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

# PROPOSTO v4.3 (aguarda gate MN) — geotecnia/geologia (Manta 17, horizontal)
# Só dispara quando NENHUM segmento específico já foi identificado acima —
# é fallback, não substitui o roteamento por segmento.
IF menção a geotecnia|geologia|SPT|CPT|sondagem|mecânica dos solos|
   mecânica das rochas|talude|estabilidade de talude|contenção|
   cortina atirantada|ancoragem|rebaixamento de lençol freático|ISRM|
   ABGE|ABMS|NBR 6122|NBR 6484|laudo geológico-geotécnico
   E nenhuma regra de segmento acima já disparou
   → geotecnia (Manta 17)

# Quando o segmento já é claro, geotecnia entra por HANDOFF, não por
# routing direto (ver seção da proposta para o mapa completo):
#   S1 (subleito/terraplenagem), S2 (fundações OAE), S4/S5 (NATM/túneis),
#   S10 (geotecnia de barragens/rejeitos), 04-imobiliario (sondagens em DD)
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
| geotecnia | geo: | ABGE, ABMS, ISRM, NBR 6122/6484/9603, bancos de sondagem (SPT/CPT) | 🆕 proposto v4.3 — não criada (aguarda gate MN) |

---

## SHAREPOINT — Routing rules (sp_agent_routing)

| Agente | Pasta SP sugerida | Pattern |
|--------|-------------------|---------|
| agente-saneamento | 03_Projetos/Saneamento/* | *.pdf, *.dwg, *.xlsx |
| agente-energia | 03_Projetos/Energia/* | *.pdf, *.dwg, *.xlsx |
| agente-portos | 03_Projetos/Portos/* | *.pdf, *.dwg, *.xlsx |
| agente-aeroportos | 03_Projetos/Aeroportos/* | *.pdf, *.dwg, *.xlsx |
| agente-barragens | 03_Projetos/Barragens/* | *.pdf, *.dwg, *.xlsx |
| agente-geotecnia | 03_Projetos/Geotecnia/* | *.pdf, *.dwg, *.xlsx (sondagens, laudos, boletins SPT/CPT) |

---

## MODELO MESTRE DE PROPOSTA

Análise de referência sobre uso da proposta MNT-2026-COM-1183_D (Concessão
Rota 2 de Julho) como modelo mestre de propostas técnico-comerciais do
Manta Maestro, validada contra a skill `proposta-comercial` (agente
A7-bd/Manta 13-bd — 18 seções canônicas). Ver `docs/MODELO-MESTRE-PROPOSTA.md`.

Recomendação: adotar como variante especializada "PTC-Infraestrutura/
Concessão de grande porte" (modo **M6**), incorporando ao padrão os blocos
de dados oficiais rastreáveis, cenários com success fee opcional, método
do paramétrico em etapas, infraestrutura incluída e ficha técnica de
fechamento — sem substituir o modo genérico M1 da skill. O texto pronto
para colar na skill de produção está em
`docs/PROPOSTA-COMERCIAL-SKILL-ADDENDUM.md`. Alteração na skill em si
depende de gate humano (MN) e é feita na fonte no SharePoint, fora deste
repositório — publicação ainda pendente (sem acesso de escrita ao
SharePoint nesta sessão).

---

## PROPOSTA — Manta 17 (geotecnia/geologia)

**Gap identificado**: nenhum dos 20 agentes cobre geotecnia/geologia como
disciplina própria. Hoje o tema aparece disperso e implícito dentro de
verticais que só tratam a fatia geotécnica ligada ao seu segmento:
S1 (terraplenagem/subleito), S2 (fundações de OAE, NBR 7187), S4/S5
(NATM em túneis) e S10 (estabilidade de taludes/rejeitos em barragens).
Não há hoje um lugar para perguntas geotécnicas "puras" (laudo de
sondagem em due diligence imobiliária, projeto de contenção, ensaio de
solo/rocha fora do contexto de uma obra linear) nem uma base de
conhecimento compartilhada (normas ABGE/ABMS/ISRM) entre esses verticais.

**Desenho proposto**: agente **horizontal** (não um novo segmento
vertical S11), porque geotecnia é uma disciplina transversal — como
`orcamento` (05) ou `modelagem` (06) — e não um tipo de ativo como
portos ou aeroportos. Análise completa em
`docs/PROPOSTA-AGENTE-GEOTECNIA-GEOLOGIA.md`.

**Delimitação de routing** (evita conflito com os verticais existentes):
- Routing direto do Maestro (Q1) só dispara em geotecnia (Manta 17)
  quando **nenhuma** regra de segmento já disparou (fallback).
- Quando o segmento já está claro, geotecnia atua por **handoff**
  (chamada pelo vertical, não substituindo-o):
  - S1 → geotecnia para SPT/CPT do subleito e estabilidade de cortes.
  - S2 → geotecnia para investigação de fundações profundas/rasas.
  - S4/S5 → geotecnia para caracterização de maciço rochoso (NATM).
  - S10 → geotecnia para estabilidade de taludes e liquefação de
    rejeitos (S10 mantém a titularidade regulatória PNSB/ANM).
  - 04-imobiliario → geotecnia para laudos de sondagem em DD.

**Escopo do agente**: mecânica dos solos e das rochas, campanhas de
investigação (SPT — NBR 6484, CPT/CPTu, sondagem rotativa, ensaios de
laboratório), classificação e caracterização geológico-geotécnica,
estabilidade de taludes (Bishop, Morgenstern-Price, Spencer),
contenções (cortina atirantada, solo grampeado, muro de gravidade),
fundações (NBR 6122), rebaixamento de lençol freático, mapeamento
geológico e risco geológico (queda de blocos, erosão, colapsividade).
Ver `.claude/agents/agente-geotecnia.md` para o agente completo.

**Status desta proposta**: agente e routing já estão escritos neste PR
(pronto para revisão), mas **nada foi criado fora deste repositório**
(sem migração Supabase, sem pasta SharePoint, sem skill registrada) —
segue exatamente o mesmo padrão de gate humano usado no addendum de
proposta comercial (`docs/PROPOSTA-COMERCIAL-SKILL-ADDENDUM.md`): a
aprovação de MN acontece na revisão/merge deste PR; os passos externos
(Supabase, SharePoint) só devem ser executados depois do merge.

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

## DEPLOY CHECKLIST v4.3 (proposta Manta 17 — não iniciar antes do merge)

- [x] Escrever `.claude/agents/agente-geotecnia.md`
- [x] Escrever análise/proposta (`docs/PROPOSTA-AGENTE-GEOTECNIA-GEOLOGIA.md`)
- [x] Draft de patch no CLAUDE.md master (agente, routing fallback, RAG,
  SharePoint routing) — **este PR**
- [ ] Gate humano: aprovação MN (revisão + merge deste PR)
- [ ] Criar coleção RAG `geotecnia` em Supabase (`rag_chunks`)
- [ ] Inserir routing rule `agente-geotecnia` em `sp_agent_routing`
- [ ] Criar pasta SP `03_Projetos/Geotecnia/`
- [ ] Escrever e subir `SKILL.md` para `01-agentes-fundamentais/agente-geotecnia/`
- [ ] Testar routing de fallback (garantir que prompts de S1/S2/S4/S5/S10
  continuam caindo no vertical certo, não em geotecnia)
- [ ] Atualizar `ARQUITETURA-AGENTES-IA.md` no SP

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
        ├── agente-barragens.md       # 🆕 S10
        └── agente-geotecnia.md       # 🆕 proposto v4.3 — Manta 17 (aguarda gate MN)
```

Os agentes existentes (Manta 00, 01, 02, 04-07, 13-16, 03-S1..S4) vivem
no repositório operacional do Maestro. Este repositório (`Codex-exemplo`)
serve como referência canônica versionada dos agentes verticais e do
mapa de routing.

---

## Histórico de versões

- **v4.3.0-draft** (2026-09-11) — proposta de agente horizontal Manta 17
  (geotecnia/geologia) para cobrir gap de disciplina transversal não
  atendida pelos verticais S1/S2/S4/S5/S10. Routing em modo fallback
  (não compete com regras de segmento existentes). **Não mergeado /
  não deployado** — aguarda gate humano MN. Ver
  `docs/PROPOSTA-AGENTE-GEOTECNIA-GEOLOGIA.md`.
- **v4.2.1** (2026-09-01) — análise e recomendação de modelo mestre de
  proposta técnico-comercial, validada contra a proposta MNT-2026-COM-1183_D
  e a skill `proposta-comercial` (A7-bd). Ver `docs/MODELO-MESTRE-PROPOSTA.md`.
- **v4.2** (2026-07-05) — expansão S6–S10 (Portos, Aeroportos,
  Saneamento, Energia, Barragens). 5 novos agentes verticais + 5
  coleções RAG + 5 pastas SP. Ticket MNT-2026-UPGRADE-AGENTS-S6S10.
- **v4.1** (anterior) — 15 agentes: horizontais + S1–S4.
