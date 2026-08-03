# CLAUDE.md — Manta Maestro (Agent Registry) v6.1.0

Registro mestre dos agentes IA da Manta Associados. Este arquivo é o
"CLAUDE.md master" referenciado pelos SKILL.md e pelos runbooks
operacionais no SharePoint.

Versão: **v6.1.0** (2026-08-01) — Taxonomia unificada S1–S14 + A1–A11 +
F1–F10 + D01–D23. Substitui v4.2. Fanout dinâmico via `list_folders`,
não hardcoded.

---

## MAPA COMPLETO — 27 agentes + 23 disciplinas, 4 eixos

### Eixo 1 — Segmentos Verticais (S1–S14)

| Código | Segmento | Agente | Norm | Status |
|--------|----------|--------|------|--------|
| S1 | Rodovias | agente-infraestrutura-S1 | DNIT IPR-726 | ✅ v6.1 |
| S2 | OAE (Pontes, Viadutos) | agente-infraestrutura-S2 | NBR 7187 | ✅ v6.1 |
| S3 | Ferrovia | agente-infraestrutura-S3 | ABNT NBR 13132 | ✅ v6.1 |
| S4 | Metrô/VLT | agente-infraestrutura-S4 | IEC 60898 | ✅ v6.1 |
| S5 | Imobiliário | manta-04 (SP-native) | NR-12/ABRE | ✅ v6.1 |
| S6 | Edificações | agente-edificacoes | NBR 6118 | ✅ v6.1 |
| S7 | Portos | agente-portos | ANTAQ/PIANC | ✅ v6.1 |
| S8 | Aeroportos | agente-aeroportos | ANAC/ICAO A14 | ✅ v6.1 |
| S9 | Saneamento (AySA) | agente-saneamento | Lei 14.026/SNIS | ✅ v6.1 |
| S10 | Energia | agente-energia | ANEEL/ONS | ✅ v6.1 |
| S11 | Barragens | agente-barragens | Lei 12.334/ICOLD | ✅ v6.1 |
| S12 | Túneis | agente-tuneis | DIN 18944 | ✅ v6.1 T2 |
| S13 | Mineração | agente-mineracao | DNPM/ANM | ✅ v6.1 T2 |
| S14 | Óleo & Gás | agente-oleo-gas | ANP/ABNT | ✅ v6.1 T2 |

### Eixo 2 — Atividades Horizontais (A1–A11)

| Código | Atividade | Agente | Entrada | Status |
|--------|-----------|--------|---------|--------|
| A1 | Proposta Técnica | manta-01-proposta | EVTEA/PB | ✅ v6.1 |
| A2 | Levantamento Quantidades | manta-02-quantidades | CAD/ODC | ✅ v6.1 |
| A3 | Orçamento | manta-05 | SICRO/SINAPI | ✅ v6.1 |
| A4 | Modelagem Financeira | manta-06 | VPL/TIR | ✅ v6.1 |
| A5 | Cronograma | manta-07 | CPM/Linha Balanço | ✅ v6.1 |
| A6 | Contratual | manta-02-contratual | EPC/PPP/TAC | ✅ v6.1 |
| A7 | Claims | manta-01-claims | TIA/Window | ✅ v6.1 |
| A8 | Advisory | manta-15 | Parecer/Laudo | ✅ v6.1 |
| A9 | Regulatório | manta-09-regulatorio | ART/RRT | ✅ v6.1 T1 |
| A10 | Risco | manta-10-risco | Monte Carlo/HAZOP | ✅ v6.1 T1 |
| A11 | Fiscalização | manta-11-fiscalizacao | RDO/NC/Medição | ✅ v6.1 T1 |

### Eixo 3 — Funcionais (F1–F10)

| Código | Funcional | Papel | Status |
|--------|-----------|-------|--------|
| F1 | IA | Model mgmt + tiering | ✅ v6.1 |
| F2 | SharePoint | Storage autoritativo | ✅ v6.1 |
| F3 | Portal | Cliente web | ✅ v6.1 |
| F4 | Extração | PDF/DWG→JSON | ✅ v6.1 |
| F5 | Notificação | Slack/Email | ✅ v6.1 |
| F6 | Trace | Audit trail (R1) | ✅ v6.1 |
| F7 | Guardrails | R1–R5 enforcement | ✅ v6.1 |
| F8 | Padronização | Templates DOCX/PPTX | ✅ v6.1 |
| F9 | Meta | Playbook IA + Agentes | ✅ v6.1 |
| F10 | Pesquisa Evolutiva | Scout (active learning) | ✅ v6.1 T1 |

### Eixo 4 — Disciplinas (D01–D23)

Categorias técnicas especializadas. Exemplo: D03 (Geotecnia) = ABNT NBR
6484, NBR 12069, ensaios SPT/triaxial. Integradas em S + A.

| Intervalo | Áreas | Exemplo |
|-----------|-------|---------|
| D01–D10 | Infra Linear | D02 Geométrico, D06 Drenagem |
| D11–D15 | Estrutural | D08 Contençõ, D14 Fundações |
| D16–D20 | Ambiental/Social | D16 Ambiental, D19 Desapropriação |
| D21–D23 | Especialidades | D21 BIM, D22 VPL, D23 Risco |

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

## ROUTING — Maestro (Manta 00) v6.1.0

**Novo:** Fanout via `list_folders` (nunca hardcode caminhos).

```python
# Intake Q1: detect segmento + atividade + fase + complexidade
# Fanout descoberta:
folders_seg  = list_folders(lib="04_IA", path="Manta-Maestro/01-segmentos")
folders_ativ = list_folders(lib="04_IA", path="Manta-Maestro/02-atividades")
folders_func = list_folders(lib="04_IA", path="Manta-Maestro/03-funcionais")

# Match: cruza keywords com SKILL.md de cada folder candidata
# Consensus: 3/5 super-maioria entre agentes selecionados
# Entrega: DOCX + JSON com audit trail R1–R5
```

**Keywords Maestro (pattern matching):**

| Segmento | Keywords |
|----------|----------|
| S1 | rodovia, pavimento, DNIT, CBUQ, SICRO |
| S2 | ponte, viaduto, OAE, NBR 7187, TBM |
| S3 | ferrovia, trilho, AMV, dormente, via permanente |
| S4 | metrô, estação, NATM, PSD, linha 4-5, VLT |
| S5 | imóvel, edificação, construção, prédio |
| S6 | edificação, structural, concreto, armadura |
| S7 | porto, terminal, ANTAQ, dragagem, molhe, contêiner |
| S8 | aeroporto, pista pouso, ANAC, ICAO, RWY, TPS |
| S9 | saneamento, ETA, ETE, adutora, SNIS, AySA |
| S10 | energia, transmissão, LT, ANEEL, subestação, ONS |
| S11 | barragem, vertedouro, CFRD, CCR, Lei 12.334 |
| S12 | túnel, escavação, TBM, NATM, DIN 18944 |
| S13 | mineração, mina, ANM, lavra, rejeito |
| S14 | óleo, gás, ANP, E&P, exploração |

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

## Arquivos deste repositório (v6.1.0)

```
Codex-exemplo/
├── CLAUDE.md                         # este arquivo (master registry v6.1)
├── COWORK-INTEGRACAO-v6.1.md         # 🆕 Integração Cowork ↔ Maestro
├── .claude/
│   ├── settings.json                 # ✅ Sonnet + env vars Maestro
│   └── agents/
│       ├── agente-portos.md          # S7 (era S6)
│       ├── agente-aeroportos.md      # S8 (era S7)
│       ├── agente-saneamento.md      # S9 (era S8) — AySA
│       ├── agente-energia.md         # S10 (era S9) — ANEEL
│       └── agente-barragens.md       # S11 (era S10)
└── supabase/
    └── migrations/
        └── 2026_08_01_v6_1_taxonomy_reconciliation.sql  # candidata
```

**Fonte de verdade:** SharePoint `04_IA/Manta-Maestro/` (v6.1.0 canônica)

---

## Histórico de versões

- **v6.1.0** (2026-08-01) — ⭐ Taxonomia unificada S1–S14 + A1–A11 +
  F1–F10 + D01–D23. Fanout dinâmico via `list_folders`. 7 camadas
  operacionais. Integração Cowork nativa. RLS Supabase. Exemplares L3.
  Migração SQL candidata pronta. SharePoint autoritativo.
- **v4.2** (2026-07-05) — S6–S10 (Portos, Aeroportos, Saneamento,
  Energia, Barragens). 5 agentes novos + 5 coleções RAG.
- **v4.1** (anterior) — 15 agentes: horizontais + S1–S4.

---

## Reconciliação com Maestro Operacional

Legenda de renumeração (v4.2 → v6.1):

| Código legado | v6.1 canônico |
|---------------|---------------|
| Manta 03-S5 | S12 (Túneis) |
| Manta 03-S6 | S7 (Portos) |
| Manta 03-S7 | S8 (Aeroportos) |
| Manta 03-S8 | S9 (Saneamento) |
| Manta 03-S9 | S10 (Energia) |
| Manta 03-S10 | S11 (Barragens) |
| Manta 03-S11 | S13 (Mineração) |
| Manta 03-S12 | S14 (Óleo & Gás) |
| Manta 03-S13 | S6 (Edificações) |

Conversão automática em migration SQL (rollback incluso).

---

## DEPLOY CHECKLIST v6.1.0

**Status do repositório:**

- [x] `.claude/settings.json` com Sonnet + env vars
- [x] 5 agentes S7–S11 (ex-S6–S10) definidos e testados
- [x] COWORK-INTEGRACAO-v6.1.md documentado
- [x] CLAUDE.md v6.1 (este arquivo) atualizado
- [x] Git commits com rastreabilidade
- [ ] Executar migration SQL (gate MN duro)
- [ ] Habilitar RLS Supabase (3 tabelas críticas)
- [ ] Verificar LLM judge (cron de 30 dias)
- [ ] Testes end-to-end: S1 + Cowork intake

---

**Contato:** mneves@mantaassociados.com  
**Última atualização:** 2026-08-03T14:30:00Z  
**Próxima revisão:** 2026-09-01
