# Runbook — Academic Knowledge Pipeline (WF-AKP-001) Stages 4-6

Passo-a-passo operacional para ativar as stages 4-6 depois que 1-3
concluírem.

## Pré-requisitos

- [ ] Payload das stages 1-3 exportado em
      `07_Conhecimento_Academico/03_exports/akp-ke-payload.json` (formato
      espelhado em `inventory/knowledge-elements.template.json`).
- [ ] Inventário sincronizado em
      `07_Conhecimento_Academico/03_exports/akp-theses-inventory.csv`
      (formato espelhado em `inventory/theses.template.csv`).
- [ ] Variáveis de ambiente locais preenchidas:
  ```
  export SUPABASE_URL=https://<project>.supabase.co
  export SUPABASE_SERVICE_ROLE_KEY=eyJ...
  export OPENAI_API_KEY=sk-...   # se embedding_model = text-embedding-3-*
  ```
- [ ] Aprovação MN via ticket WF-AKP-001.

## Stage 4 — pgvector ingestion

### 4.1 Aplicar migração
```bash
cd Codex-exemplo
supabase db push
# ou
psql "$SUPABASE_DB_URL" -f supabase/migrations/2026_07_12_akp_stages_4_6.sql
```

Confirmar:
```sql
SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';
SELECT COUNT(*) FROM rag_collections WHERE slug = 'academic-knowledge';  -- 1
SELECT COUNT(*) FROM information_schema.tables
 WHERE table_name IN ('academic_theses','academic_knowledge_elements');  -- 2
```

### 4.2 Rodar o ingestor
```bash
cd manta-hub
python scripts/akp_ingest.py \
  --input path/to/akp-ke-payload.json \
  --supabase-url $SUPABASE_URL \
  --supabase-key $SUPABASE_SERVICE_ROLE_KEY \
  --embedding-model text-embedding-3-small \
  --batch-size 20 \
  --dry-run   # remover quando validado
```

Ver `manta-hub/docs/AKP-INGESTION.md` para o detalhamento.

### 4.3 Validar
```sql
SELECT COUNT(*) FROM academic_theses;                     -- deve retornar 36
SELECT COUNT(*) FROM academic_knowledge_elements;         -- deve retornar 52
SELECT COUNT(*) FROM academic_knowledge_elements
 WHERE embedding IS NOT NULL;                             -- deve retornar 52
SELECT segmento, COUNT(*) FROM academic_knowledge_elements
 GROUP BY segmento ORDER BY segmento;                     -- distribuição por segmento
```

Query de sanidade (top-3 KEs para "dragagem em terminal graneleiro"):
```sql
-- Substituir o vector abaixo pelo embedding real gerado externamente
SELECT id, titulo, tese_id, similarity
  FROM match_academic_knowledge(
    query_embedding := '[0.01, 0.02, ...]'::vector(1536),
    match_count := 3,
    filter_segmento := 'portos'
  );
```

## Stage 5 — SharePoint indexing

### 5.1 Criar a pasta no SharePoint
```
07_Conhecimento_Academico/
├── 01_teses/
├── 02_knowledge-elements/
├── 03_exports/
└── 04_provenance/
```

Fazer upload dos 36 PDFs em `01_teses/` e dos 52 arquivos `KE-NNN.md`
em `02_knowledge-elements/`.

### 5.2 Registrar routing
Já vem incluído na migração (`sp_agent_routing` linha
`rag-academic-knowledge`). Verificar:
```sql
SELECT * FROM sp_agent_routing WHERE agent_slug = 'rag-academic-knowledge';
```

### 5.3 Configurar o crawler
No indexer de SharePoint (fora deste repo), adicionar a pasta
`07_Conhecimento_Academico/` como fonte e associar ao slug
`academic-knowledge`. Frequência sugerida: **diária**, notificar mudanças
ao webhook `POST /api/rag/reindex?collection=academic-knowledge`.

## Stage 6 — Agent activation

### 6.1 Verificar bindings
```sql
SELECT agent_slug, role, priority
  FROM agent_rag_bindings
 WHERE collection_slug = 'academic-knowledge'
 ORDER BY priority DESC;
```

Esperado: 12 linhas (4× S1-S4 + 5× S6-S10 + 2× horizontais + advisory).

### 6.2 Reload dos SKILL.md
Cada agente vertical S6-S10 tem `rag_consume: [<segmento>, academic-knowledge]`
adicionado no frontmatter (v4.3). Basta o Maestro recarregar o registry.

### 6.3 Smoke test — 5 prompts, um por segmento

| Segmento    | Prompt de teste                                                                                     |
|-------------|-----------------------------------------------------------------------------------------------------|
| portos      | "Qual o estado da arte para dragagem de manutenção em terminais amazônicos?"                        |
| aeroportos  | "Tem alguma tese recente criticando o dimensionamento de pista de aeródromos regionais?"            |
| saneamento  | "O que a literatura acadêmica diz sobre reúso de água para AySA em Buenos Aires?"                   |
| energia     | "Estado da arte em torres estaiadas ACSR para linhas de 500 kV — referências acadêmicas."           |
| barragens   | "Barragens de rejeitos por linha de centro pós-Brumadinho — teses de doutorado."                    |

Critério de aprovação: **≥3 KEs relevantes** no top-5 de cada resposta,
com citação bibtex renderizada.

### 6.4 Gate humano MN
- [ ] MN aprova as 5 respostas do smoke test.
- [ ] Merge do PR desta branch.
- [ ] Bump versão CLAUDE.md master v4.2 → v4.3.

## Rollback

Se qualquer stage falhar após produção:

```sql
BEGIN;
-- Ver bloco DOWN completo em supabase/migrations/2026_07_12_akp_stages_4_6.sql
COMMIT;
```

## Contatos

- **PO:** Manoel Neves (mneves@mantaassociados.com)
- **Tech lead:** Vinícius Magnos
- **Ticket:** WF-AKP-001
- **Slack:** #akp-pipeline
