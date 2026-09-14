# CLAUDE.md — Manta Maestro (Agent Registry)

Registro mestre dos agentes IA da Manta Associados. Este arquivo é o
"CLAUDE.md master" referenciado pelos SKILL.md e pelos runbooks
operacionais no SharePoint.

Versão: **v4.3.0** (2026-09-14) — v4.2 expansão S6–S10 (Portos,
Aeroportos, Saneamento, Energia, Barragens) + análise de modelo mestre de
proposta técnico-comercial + v4.3 draft do **agente-leitor-documental**
(Manta 08, camada de ingestão multi-formato PDF/Excel/DWG/Word/PPTX/BIM/
cronograma).

---

## MAPA COMPLETO DE AGENTES — 21 agentes, 3 eixos

### Eixo 1 — Horizontais (transversais a todos os segmentos)

| Código | Agente | Aliases | Tier default | Status |
|--------|--------|---------|--------------|--------|
| Manta 00 | maestro (router) | maestro, manta-router | Haiku→Sonnet | ✅ Operacional |
| Manta 01 | claims | 02-C, manta-claims | Opus | ✅ Operacional |
| Manta 08 | leitor-documental | manta-08, leitor-documental, document-reader | Haiku | 🆕 Proposto (v4.3) — camada de ingestão PDF/Excel/DWG/Word/PPTX/BIM/cronograma |
| Manta 02 | contratual | manta-02, contratual | Sonnet | ✅ Operacional |
| Manta 04 | imobiliario | manta-04 | Sonnet | ✅ Operacional |
| Manta 05 | orcamento | manta-05 | Sonnet | ✅ Operacional |
| Manta 06 | modelagem | manta-06 | Sonnet/Opus | ✅ Operacional |
| Manta 07 | cronograma | manta-07 | Sonnet | ✅ Operacional |
| Manta 13 | bd | manta-13, business-dev | Sonnet | ✅ Operacional |
| Manta 14 | apresentacoes | manta-14-pptx | Sonnet | ✅ Operacional |
| Manta 15 | advisory | manta-15, advisory | Sonnet/Opus | ✅ Operacional |
| Manta 16 | arquiteto-ia | manta-15-arq | Opus | ✅ Operacional |

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
```

---

## LEITOR DOCUMENTAL — Camada de ingestão multi-formato (Manta 08)

**Status: 🆕 Proposto (v4.3)** — draft de arquitetura, pendente gate
humano (MN) e wiring Supabase/SharePoint. Ver
`.claude/agents/agente-leitor-documental.md`,
`sharepoint/01-agentes-fundamentais/agente-leitor-documental/SKILL.md`
e `docs/DEPLOY-v4.3.md`.

Problema que resolve: hoje cada agente vertical (S1-S10) pode invocar
skills de formato (`pdf`, `xlsx`, `docx`, `autodesk-toolkit`,
`cronograma-toolkit`) por conta própria, sem um ponto único de
detecção de tipo, normalização de saída ou controle de idempotência.
O Manta 08 é a camada fina que fica **entre** a origem do arquivo
(SharePoint, upload, lote) e o agente vertical que interpreta o
conteúdo tecnicamente.

Pipeline: Recepção → Detecção de formato (extensão + magic bytes) →
Classificação de subtipo → Despacho para a skill de leitura correta →
Normalização em JSON canônico → Roteamento para o agente vertical
dono → Persistência na coleção RAG do segmento.

Tabela de despacho por formato:

```
.pdf                    → pdf (genérico); ler-edital; ler-edital-aneel;
                           evtea-extractor; leitura-diagrama-engenharia
.xlsx, .xls              → xlsx
.docx, .dotx             → docx
.pptx                    → pptx
.dwg, .dxf               → autodesk-toolkit (+ cad-quantifier/cqp-cad-bridge
                           se o objetivo for quantificar)
.ifc, .rvt, .nwd, .nwc   → autodesk-toolkit
.xer, .mpp, .xml (MSPDI) → cronograma-toolkit
```

Este agente **não reimplementa parsing** — só decide qual skill
existente acionar e normaliza a saída dela. Não interpreta tecnicamente
o conteúdo (isso é do agente vertical) e não escreve de volta no
SharePoint sem confirmação humana.

Migração Supabase candidata (índice de idempotência
`doc_processing_index` + tabela de despacho `doc_format_dispatch`):
`supabase/migrations/2026_09_14_v4_3_leitor_documental.sql`.

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
`docs/PROPOSTA-COMERCIAL-SKILL-ADDENDUM.md`.

**Gate humano: ✅ aprovado por MN em 2026-09-10.** Falta só a aplicação
técnica: colar o bloco da Seção A do addendum em
`skill-proposta-comercial-SKILL.md` no SharePoint. Essa etapa está
bloqueada nesta sessão porque o conector `SharePoint_Manta` caiu
(MCP server disconnected) — precisa ser feita numa sessão com esse
conector ativo, ou manualmente por quem tem acesso ao SharePoint.

**Pendência a resolver antes de publicar:** a fonte de validação citada
(MNT-2026-COM-1183_**D**, 27 páginas) não foi localizada no SharePoint em
levantamento de 2026-09-10 — só existe a revisão **_C** (21 páginas,
24/08/2026), cujo controle de revisão interno não menciona uma `_D`.
Confirmar se a `_D` existe em outro local antes de publicar o addendum
citando-a como fonte, ou atualizar a referência para `_C`.

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

## DEPLOY CHECKLIST v4.3 (Leitor Documental)

Runbook completo em `docs/DEPLOY-v4.3.md`.

- [x] Definir agente `.claude/agents/agente-leitor-documental.md`
- [x] Escrever SKILL.md + mirror SharePoint (`sharepoint/01-agentes-fundamentais/agente-leitor-documental/`)
- [x] Escrever migração Supabase candidata (`doc_processing_index` + `doc_format_dispatch`)
- [ ] Aplicar migração Supabase v4.3
- [ ] Criar pasta SP `agente-leitor-documental/` e upload do SKILL.md
- [ ] Atualizar `ARQUITETURA-AGENTES-IA.md` no SP (v2.0.0 → v2.1.0)
- [ ] Testar dispatch por formato (PDF, edital, EVTEA, XLSX, DOCX, DWG, XER)
- [ ] Decisão MN: dispatch em banco vs. só Markdown; execução automática do Manta 08 vs. invocação explícita
- [ ] Gate humano: aprovação MN antes de promover a Operacional

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
        └── agente-leitor-documental.md  # 🆕 Manta 08 — ingestão multi-formato (v4.3, draft)
```

Os agentes existentes (Manta 00, 01, 02, 04-07, 13-16, 03-S1..S4) vivem
no repositório operacional do Maestro. Este repositório (`Codex-exemplo`)
serve como referência canônica versionada dos agentes verticais e do
mapa de routing.

---

## Histórico de versões

- **v4.3.0** (2026-09-14) — draft de arquitetura do
  **agente-leitor-documental** (Manta 08): camada horizontal de
  ingestão e normalização multi-formato (PDF, Excel/XLSX, DWG/DXF,
  Word/DOCX, PPTX, BIM IFC/RVT, cronograma XER/MPP) que fica entre a
  origem do arquivo (SharePoint, upload, lote) e os agentes verticais
  S1-S10. Reaproveita as skills de formato já existentes no catálogo
  (`pdf`, `xlsx`, `docx`, `pptx`, `autodesk-toolkit`,
  `cronograma-toolkit`) e os extratores especializados
  (`evtea-extractor`, `ler-edital`, `ler-edital-aneel`,
  `leitura-diagrama-engenharia`) — não reimplementa parsing próprio.
  Total de agentes: 20 → 21. Status: 🆕 Proposto, pendente gate humano
  MN e aplicação da migração Supabase (`docs/DEPLOY-v4.3.md`).
- **v4.2.2** (2026-09-10) — gate humano MN aprovado para a variante M6
  (addendum de proposta técnico-comercial). Aplicação no SharePoint
  pendente (conector `SharePoint_Manta` indisponível na sessão de
  aprovação). Levantamento completo do acervo de propostas/CVs/
  apresentações no SharePoint identificou que a fonte de validação
  citada (MNT-2026-COM-1183_D) não foi localizada — só a revisão _C
  existe; ver nota em "MODELO MESTRE DE PROPOSTA" acima.
- **v4.2.1** (2026-09-01) — análise e recomendação de modelo mestre de
  proposta técnico-comercial, validada contra a proposta MNT-2026-COM-1183_D
  e a skill `proposta-comercial` (A7-bd). Ver `docs/MODELO-MESTRE-PROPOSTA.md`.
- **v4.2** (2026-07-05) — expansão S6–S10 (Portos, Aeroportos,
  Saneamento, Energia, Barragens). 5 novos agentes verticais + 5
  coleções RAG + 5 pastas SP. Ticket MNT-2026-UPGRADE-AGENTS-S6S10.
- **v4.1** (anterior) — 15 agentes: horizontais + S1–S4.
