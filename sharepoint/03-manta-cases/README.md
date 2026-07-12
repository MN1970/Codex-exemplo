# Casos Manta — WF-MCP-001

Coleção RAG **transversal** que reúne memoriais reais Manta (DDs, EVTEs,
projetos executivos, laudos, pleitos, auditorias) transformados em
Knowledge Elements curados para consumo por todos os agentes verticais
(S1-S13) e horizontais estratégicos (advisory, arquiteto-ia).

**Prioridade 120 > 100 (academic-knowledge):** memoriais reais Manta
valem MAIS que tese acadêmica em qualquer resolução de contexto.
Justificativa em `docs/WF-MCP-001.md`.

- **Ticket:** WF-MCP-001
- **Pipeline:** Manta Cases Pipeline
- **Slug Supabase:** `manta-cases` (`rag_collections`)
- **Prefixo storage:** `mcs:`
- **Pasta SharePoint:** `08_Casos_Manta/`
- **Status stages:**
  - Stage 1 (curadoria de memoriais)         ⏳ contínuo (MN + equipe)
  - Stage 2 (extração de KEs)                ⏳ script `manta_cases_extract.py`
  - Stage 3 (metadata + provenance)          ⏳ revisão MN
  - Stage 4 (pgvector ingestion)             🚧 esta migração
  - Stage 5 (SharePoint indexing)            🚧 esta pasta
  - Stage 6 (agent activation)               🚧 bindings priority=120

## Estrutura desta pasta

```
sharepoint/03-manta-cases/
├── README.md                       # este arquivo
├── runbook.md                      # passos operacionais stages 4-6
└── inventory/
    ├── projects.template.csv       # 1 linha/projeto (10 colunas)
    └── cases.template.json         # 1 objeto/KE (schema espelhado no ingestor)
```

O SharePoint espelho fica em `08_Casos_Manta/` com esta estrutura:

```
08_Casos_Manta/
├── 01_memoriais/                   # PDFs/DOCX originais dos memoriais
│   ├── epr-br365/
│   │   ├── memorial-DD-EPR-BR365-r03.pdf
│   │   ├── memorial-EVTE-EPR-BR365-r02.pdf
│   │   └── ...
│   ├── porto-santos-t41/
│   │   └── memorial-executivo-porto-santos-t41.pdf
│   └── ...
├── 02_case_elements/               # exports curados por KE
│   ├── MCS-00001.md
│   ├── MCS-00042.md
│   └── ...
├── 03_exports/
│   ├── manta-cases-payload.json    # payload consumido pelo ingestor
│   └── manta-projects-inventory.csv # inventário sincronizado
└── 04_provenance/
    └── stage-1-3-audit.json        # trilha de auditoria das stages iniciais
```

## Fluxo de atualização

1. **Novo projeto entra em curadoria** → subpasta em `01_memoriais/<slug>/`
   + linha em `03_exports/manta-projects-inventory.csv`.
2. **Extração de KEs (stage 2)** → `python scripts/manta_cases_extract.py`
   sobre os PDFs/DOCX do memorial (Claude Sonnet 4.6 gera 1-3 KEs por
   seção); arquivos `MCS-NNNNN.md` opcionalmente em `02_case_elements/`.
3. **Revisão MN (stage 3)** → merge em
   `03_exports/manta-cases-payload.json` com chunk + metadata +
   `nda_level` explícito + provenance.
4. **Ingestor** roda `scripts/manta_cases_ingest.py` (TODO — espelho do
   `akp_ingest.py`), calculando embeddings e fazendo UPSERT em
   `manta_projects` + `manta_cases_elements`.
5. **Rebind agentes**: novo segmento vertical → atualizar
   `agent_rag_bindings` (priority=120) via
   `INSERT ... ON CONFLICT DO NOTHING`.

## NDA compliance — regras de manejo

Cada projeto e cada KE carregam `nda_level` explícito. A função
`match_manta_cases_hybrid` filtra por teto autorizado do consumidor
(ordem: `publico` < `interno` < `confidencial` < `restrito`).

| Nível          | Uso permitido                                                       |
|----------------|---------------------------------------------------------------------|
| `publico`      | Citação livre (memoriais divulgados em conferências, papers).       |
| `interno`      | Uso dentro da Manta + parceiros com NDA vigente. **Default.**       |
| `confidencial` | Só equipe do projeto + owners do caso.                              |
| `restrito`     | Só MN + tech lead (cláusula contratual sensível, disputa ativa).    |

Regra de herança: `KE.nda_level` NUNCA pode ser MENOS restritivo que
`projeto.nda_level`. O ingestor rejeita a inserção nesse caso.

**Reclassificação automática (proposta — decisão MN):** memoriais de
projetos ENCERRADOS há mais de 5 anos podem migrar de `interno` para
`publico` mediante revisão manual. Não é feito por trigger — vira ticket
em `akp_curation_backlog` (reaproveitando a infraestrutura de v4.5).

## Auditoria mínima obrigatória (Stage 6 activation)

Antes de ativar consumo em produção:

- [ ] Cada `manta_projects.id` tem `sp_path` preenchido apontando para
      `08_Casos_Manta/01_memoriais/<slug>/`.
- [ ] Cada `manta_cases_elements` tem `embedding_created_at NOT NULL` e
      `embedding_model` registrado.
- [ ] Cada KE tem `nda_level` explícito (não vale herdar em silêncio;
      o revisor confirma o nível caso a caso).
- [ ] Ao menos 5 queries de teste (uma por segmento representativo)
      retornando top-3 KEs coerentes com o teto NDA correto.
- [ ] Gate humano MN antes de habilitar o consumo automático nos
      agentes de produção.

## Handoffs

| Contexto                                | Agente destino                     |
|-----------------------------------------|------------------------------------|
| Aplicabilidade contratual / claim       | agente-claims (Manta 01)           |
| Modelagem financeira derivada de caso   | agente-advisory (Manta 15)         |
| Argumentação de pleito                  | agente-contratual (Manta 02)       |
| Adaptação em orçamento (SICRO/TPU)      | agente-orcamento (Manta 05)        |
| Novo vertical (S14+) proposto           | agente-arquiteto-ia (Manta 16)     |

## Referências cruzadas

- `supabase/migrations/2026_07_12_manta_cases_v4_6.sql` — schema pgvector
  desta pasta.
- `manta-hub/scripts/manta_cases_extract.py` — extrator CLI (PDF/DOCX →
  JSON).
- `manta-hub/scripts/manta_cases_extract.README.md` — runbook do
  extrator.
- `docs/WF-MCP-001.md` — arquitetura do pipeline (por que casos > teses,
  regras NDA, integração com telemetria).
- `sharepoint/02-academic-knowledge/README.md` — pipeline paralelo AKP
  (prioridade 100).
