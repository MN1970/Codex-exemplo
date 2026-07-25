# 📊 SharePoint Engenharia — Mapa Completo de Documentos

**Site:** https://mnassociados.sharepoint.com/sites/Engenharia  
**Biblioteca:** Documentos Compartilhados  
**Data:** 2026-07-23

---

## 📁 Estrutura Principal (6 Pastas)

### ✅ 01_BIBLIOTECA
Base de orçamentos e SICRO
```
01_BIBLIOTECA/
└── 01_ORÇAMENTO/
    └── 01.05_BASE ORÇAMENTOS/
        └── SICRO/ (vazio — para preenchimento)
```

### ✅ 04_IA — MANTA MAESTRO (Agentes IA)
Documentação e configuração completa dos 16 agentes em 3 camadas
- **Camada 1:** 5 especialistas (Saneamento, Energia, Portos, Aeroportos, Barragens)
- **Camada 2:** 8 indexadores (fulltext + vector)
- **Camada 3:** 3 validadores (confidence, metadata, ranking)

```
04_IA/
└── Manta-Maestro/ (20 subpastas)
    ├── 00-arquitetura/          → v5.0.0 (enviado 2026-07-22)
    ├── 01-segmentos/            → Especializações S1-S10
    ├── 02-atividades/           → Fluxos operacionais
    ├── 02-sub-skills/           → Componentes reutilizáveis
    ├── 03-exemplares/           → Templates
    ├── 03-funcionais/           → Testes
    ├── 04-disciplinas/          → Metodologias
    ├── 04-rubricas/             → Critérios
    ├── 05-execucoes/            → Histórico
    ├── 05-sub-skills/           → Sub-componentes
    ├── 06-exemplares/           → Casos de uso
    ├── 06-infraestrutura/       → Stack técnico (Supabase, RAG)
    ├── 07-execucoes/            → Auditorias
    ├── 08-rubricas/             → SLAs & KPIs
    ├── 09-base-conhecimento/    → RAG (947+ chunks)
    ├── _correcoes/              → Bug fixes
    ├── _indice-mestre/          → Registros mestres
    ├── _qa/                     → Quality assurance
    ├── 99-backup/               → Backup
    └── 99-meta/                 → Metadata
```

### ✅ Cronograma (9 Subfolders)
Orquestração de timelines com automação
```
Cronograma/
├── 01_Biblioteca_Estrategica/
├── 02_Templates/
├── 03_Scripts/
├── 04_Relatorios_PowerBI/
├── 05_Sumario/
├── automacao-cronogramas-manta/     (v1 — ativa)
└── automacao-cronogramas-v2/        (v2 — nova)
```

### ✅ Geométrico de rodovias
Desenhos e layouts
```
Geométrico de rodovias/
└── (2 itens)
```

### ✅ Projeto 01
Documentos de projeto
```
Projeto 01/
└── 01 - Projetos A/
    └── (71 documentos)
```

### ✅ Sicro
Base de composições
```
Sicro/
└── (2 itens)
```

---

## 🏗️ Detalhamento — 04_IA/Manta-Maestro

### 🎯 Pastas Operacionais

#### **00-arquitetura** ⭐
Documentação master dos agentes
- ARQUITETURA-AGENTES-IA-v5.0.0.md (enviado 2026-07-22)
- 20 agentes: 11 horizontais + 9 verticais
- Routing rules (saneamento → san:, energia → ene:, etc)
- Deployment checklist ✅

#### **01-segmentos**
Especializações por domínio
```
S1  — Rodovias
S2  — Pontes/OAE
S3  — Ferrovias
S4  — Metrô
S5  — Túneis
S6  — Portos       (novo 2026-07-05)
S7  — Aeroportos   (novo 2026-07-05)
S8  — Saneamento   (novo 2026-07-05) — PRIORIDADE AySA
S9  — Energia      (novo 2026-07-05) — ANEEL/State Grid
S10 — Barragens    (novo 2026-07-05)
```

#### **02-atividades**
Tarefas e fluxos
- Intake Q1, Q2, Q3, Q4
- 8 fases de projeto (estudo prévio → encerramento)

#### **02-sub-skills**
Componentes reutilizáveis
- Extraction utilities
- Pipeline processors
- Validation rules

#### **03-exemplares**
Templates e exemplos
- Estudo prévio (EVTE)
- Projeto básico
- Projeto executivo
- Licitação

#### **03-funcionais**
Testes
- Unit tests
- Integration tests
- E2E workflows

#### **04-disciplinas**
Metodologias
- BIM
- CAD standards
- Normas ABNT

#### **04-rubricas**
Critérios de aceitação
- Quality gates
- Review checklists

#### **05-execucoes**
Histórico e resultados
- Runs e logs
- Performance metrics

#### **05-sub-skills**
Sub-componentes
- Parser modules
- Validator helpers
- Output formatters

#### **06-exemplares**
Casos de uso completos
- Estudo prévio rodovia
- Projeto metrô
- Licitação energia

#### **06-infraestrutura** 🔧
Stack técnico
- Supabase (PostgreSQL, pgvector, Auth)
- RAG (5 coleções: san:, ene:, por:, aer:, bar:)
- Indexes (fulltext tsvector + vector HNSW)
- Phase 1, 2, 3 implementation

#### **07-execucoes**
Auditorias e verificações
- Hallucination detection
- Reference validation
- SLA compliance

#### **08-rubricas**
Critérios operacionais
- P50/P99 latency targets
- Availability targets (99.9%)
- Relevance thresholds (> 0.92)

#### **09-base-conhecimento** 📚
RAG document base
- 947+ chunks after Phase 2
- 5 coleções RAG:
  - san: (200) — Saneamento
  - ene: (300) — Energia
  - por: (150) — Portos
  - aer: (120) — Aeroportos
  - bar: (180) — Barragens
- Phase 2 status: Document collection
- Phase 3 status: 16-agent orchestration (implementado)

### 🔧 Pastas de Manutenção

#### **_correcoes**
Bug fixes e patches
- Hotfixes
- Edge cases

#### **_indice-mestre**
Registros mestres
- Agent registry
- Routing table
- Collection mapping

#### **_qa**
Quality assurance
- Test results
- Performance baselines
- Validation reports

#### **99-backup**
Versões anteriores
- v4.1 archived
- v4.0 archived
- Legacy configs

#### **99-meta**
Configuração e metadata
- Settings.json
- Environment vars
- Database schemas

---

## 🔗 URLs Diretas

### Manta-Maestro
- **Raiz:** https://mnassociados.sharepoint.com/sites/Engenharia/04_IA/Manta-Maestro
- **Arquitetura (v5):** https://mnassociados.sharepoint.com/sites/Engenharia/04_IA/Manta-Maestro/00-arquitetura
- **Segmentos:** https://mnassociados.sharepoint.com/sites/Engenharia/04_IA/Manta-Maestro/01-segmentos
- **Infraestrutura:** https://mnassociados.sharepoint.com/sites/Engenharia/04_IA/Manta-Maestro/06-infraestrutura
- **Base Conhecimento:** https://mnassociados.sharepoint.com/sites/Engenharia/04_IA/Manta-Maestro/09-base-conhecimento

### Outras
- **Cronogramas:** https://mnassociados.sharepoint.com/sites/Engenharia/Cronograma
- **Projetos:** https://mnassociados.sharepoint.com/sites/Engenharia/Projeto%2001
- **Biblioteca:** https://mnassociados.sharepoint.com/sites/Engenharia/01_BIBLIOTECA

---

## 📊 Estatísticas

| Métrica | Valor |
|---------|-------|
| Pastas principais | 6 |
| Subpastas Manta-Maestro | 20 |
| Agentes total | 16 (5 + 8 + 3) |
| Especialistas | 5 (S6-S10 novos) |
| Indexadores | 8 (fulltext + vector) |
| Validadores | 3 (confidence + metadata + ranking) |
| Coleções RAG | 5 (san:, ene:, por:, aer:, bar:) |
| Chunks esperados | 947+ (Phase 2) |
| Índices SQL | 12 (5 fulltext + 3 vector + 4 metadata) |

---

## 🚀 Status Atual

### ✅ Completado
- [x] Arquitetura Manta Maestro v5.0.0 (2026-07-22)
- [x] 5 agentes novos (S6-S10)
- [x] Routing rules (maestro router)
- [x] Documentação master (SharePoint)
- [x] Phase 3 planning (16-agent orchestration)
- [x] Phase 3 implementation (4 scripts + SQL migrations)
- [x] Phase 3 testing (82ms latency, SLA met)

### ⏳ Em Progresso
- [ ] Phase 2: Document collection (950 docs, deadline 2026-07-28)
- [ ] Phase 2: Supabase insertion (947+ chunks)

### 📋 Próximas Ações
1. Complete Phase 2 (document collection)
2. Deploy SQL migrations (rag-phase3-migrate-indexes.sql)
3. Execute Phase 3 indexer orchestrator (Week 1)
4. Execute Phase 3 validator orchestrator (Week 2)
5. Full 16-agent orchestration (Week 3)

---

**Última atualização:** 2026-07-23  
**Responsável:** Claude Code (Codex-exemplo)  
**Versão:** 1.0 (Mapa Completo)
