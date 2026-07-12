# Conhecimento Acadêmico — WF-AKP-001

Coleção RAG **transversal** que reúne teses e Knowledge Elements curados
para consumo por todos os agentes verticais (S1-S10) e horizontais
estratégicos (advisory, arquiteto-ia).

- **Ticket:** WF-AKP-001
- **Pipeline:** Academic Knowledge Pipeline
- **Slug Supabase:** `academic-knowledge` (`rag_collections`)
- **Prefixo storage:** `ake:`
- **Pasta SharePoint:** `07_Conhecimento_Academico/`
- **Status stages:**
  - Stage 1 (curadoria de teses)         ✅ 36 teses
  - Stage 2 (extração de KEs)            ✅ 52 Knowledge Elements
  - Stage 3 (metadata + provenance)      ✅ pronto p/ embedding
  - Stage 4 (pgvector ingestion)         🚧 esta migração
  - Stage 5 (SharePoint indexing)        🚧 esta pasta
  - Stage 6 (agent activation)           🚧 hooks nos SKILL.md

## Estrutura desta pasta

```
sharepoint/02-academic-knowledge/
├── README.md                    # este arquivo
├── inventory/
│   ├── theses.template.csv      # 1 linha/tese (36 esperadas)
│   └── knowledge-elements.template.json  # 1 objeto/KE (52 esperados)
└── runbook.md                   # passos operacionais
```

O SharePoint espelho fica em `07_Conhecimento_Academico/` com esta
estrutura:

```
07_Conhecimento_Academico/
├── 01_teses/                    # PDFs originais (36 arquivos)
│   ├── silva-2019-dragagem.pdf
│   ├── pereira-2021-aerodromos-regionais.pdf
│   └── ...
├── 02_knowledge-elements/       # exports curados
│   ├── KE-001.md
│   ├── KE-052.md
│   └── ...
├── 03_exports/
│   ├── akp-ke-payload.json      # payload consumido pelo ingestor
│   └── akp-theses-inventory.csv # inventário sincronizado
└── 04_provenance/
    └── stage-1-3-audit.json     # trilha de auditoria das stages iniciais
```

## Fluxo de atualização

1. **Nova tese entra na curadoria** → PDF em `01_teses/` + linha em
   `03_exports/akp-theses-inventory.csv`.
2. **Extração de KEs** (stage 2) → arquivos `KE-NNN.md` em
   `02_knowledge-elements/`.
3. **Merge no payload** (stage 3) → atualiza
   `03_exports/akp-ke-payload.json` com chunk + metadata + provenance.
4. **Ingestor** roda `scripts/akp_ingest.py` (repo `manta-hub`),
   calculando embeddings e fazendo UPSERT em `academic_knowledge_elements`.
5. **Rebind agentes**: se um novo segmento vertical for adicionado, atualizar
   `agent_rag_bindings` via `INSERT ... ON CONFLICT DO NOTHING`.

## Auditoria mínima obrigatória (Stage 6 activation)

Antes de ativar consumo em produção:

- [ ] 36/36 teses com `sp_path` preenchido apontando para
      `07_Conhecimento_Academico/01_teses/<slug>.pdf`.
- [ ] 52/52 KEs com `embedding_created_at NOT NULL` e `embedding_model`
      registrado.
- [ ] Ao menos 5 queries de teste (uma por segmento S6-S10) retornando
      top-3 KEs coerentes.
- [ ] Gate humano MN antes de habilitar o consumo automático nos
      agentes de produção.

## Handoffs

| Contexto                                | Agente destino                     |
|-----------------------------------------|------------------------------------|
| Aplicabilidade regulatória / normativa  | agente-contratual                  |
| Modelagem financeira derivada de tese   | agente-advisory                    |
| Adaptação do KE em orçamento (SICRO)    | agente-orcamento (Manta 05)        |
| Novo vertical (S11+) proposto           | agente-arquiteto-ia (Manta 16)     |

## Referências cruzadas

- `supabase/migrations/2026_07_12_akp_stages_4_6.sql` — schema pgvector
  desta pasta.
- `manta-hub/scripts/akp_ingest.py` — ingestor CLI.
- `manta-hub/docs/AKP-INGESTION.md` — runbook do ingestor.
- `CLAUDE.md` v4.3 — registro no master.
