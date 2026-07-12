# Runbook — Manta Cases Pipeline (WF-MCP-001) Stages 4-6

Passo-a-passo operacional para ativar as stages 4-6 depois que 1-3
concluírem para o primeiro batch de projetos.

## Pré-requisitos

- [ ] Payload das stages 1-3 exportado em
      `08_Casos_Manta/03_exports/manta-cases-payload.json` (formato
      espelhado em `inventory/cases.template.json`).
- [ ] Inventário sincronizado em
      `08_Casos_Manta/03_exports/manta-projects-inventory.csv` (formato
      espelhado em `inventory/projects.template.csv`).
- [ ] `nda_level` revisado caso a caso — memoriais confidenciais NÃO
      entram como `interno` por descuido.
- [ ] Variáveis de ambiente locais preenchidas:
  ```
  export SUPABASE_URL=https://<project>.supabase.co
  export SUPABASE_SERVICE_ROLE_KEY=eyJ...
  export OPENAI_API_KEY=sk-...   # embedding via text-embedding-3-small
  export ANTHROPIC_API_KEY=sk-ant-...   # só se rodar `manta_cases_extract.py`
  ```
- [ ] Aprovação MN via ticket WF-MCP-001.

## Stage 4 — pgvector ingestion

### 4.1 Aplicar migração
```bash
cd Codex-exemplo
supabase db push
# ou
psql "$SUPABASE_DB_URL" -f supabase/migrations/2026_07_12_manta_cases_v4_6.sql
```

Confirmar:
```sql
SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';
SELECT COUNT(*) FROM rag_collections WHERE slug = 'manta-cases';   -- 1
SELECT COUNT(*) FROM information_schema.tables
 WHERE table_name IN ('manta_projects','manta_cases_elements');    -- 2
SELECT proname FROM pg_proc WHERE proname = 'match_manta_cases_hybrid'; -- 1
```

### 4.2 Extrair KEs a partir dos memoriais (stage 2 automatizada)

```bash
cd manta-hub
python scripts/manta_cases_extract.py \
  --input '/path/to/08_Casos_Manta/01_memoriais/epr-br365/*.pdf' \
  --project-meta /path/to/08_Casos_Manta/03_exports/epr-br365.project.json \
  --output /path/to/08_Casos_Manta/03_exports/epr-br365.cases.json \
  --max-budget-usd 5.00
```

Repetir por projeto. Custo esperado: US$ 0.10–0.30 por memorial (~3-8
KEs), variando com o número de páginas.

Consolidar os JSONs em um `manta-cases-payload.json` mestre.

### 4.3 Rodar o ingestor (TODO — mesmo padrão do `akp_ingest.py`)

```bash
# Espelho de akp_ingest.py, ainda não escrito nesta fase.
# python scripts/manta_cases_ingest.py \
#   --input manta-cases-payload.json \
#   --projects-inventory manta-projects-inventory.csv \
#   --supabase-url $SUPABASE_URL \
#   --supabase-key $SUPABASE_SERVICE_ROLE_KEY \
#   --embedding-model text-embedding-3-small \
#   --batch-size 20 \
#   --dry-run   # remover quando validado
```

Enquanto o ingestor não sai, UPSERT manual via SQL script gerado a
partir do JSON é aceitável para o batch piloto.

### 4.4 Validar

```sql
SELECT COUNT(*) FROM manta_projects;
SELECT COUNT(*) FROM manta_cases_elements;
SELECT COUNT(*) FROM manta_cases_elements WHERE embedding IS NOT NULL;
SELECT segmento, COUNT(*) FROM manta_cases_elements
 GROUP BY segmento ORDER BY segmento;
SELECT nda_level, COUNT(*) FROM manta_cases_elements
 GROUP BY nda_level ORDER BY _nda_rank(nda_level);
```

Query de sanidade (top-3 KEs de projetos rodoviários para o consumidor
`interno`, "compensação de terra" — combina termo normativo + semântica):

```sql
SELECT id, titulo, projeto_id, nda_level, rrf_score
  FROM match_manta_cases_hybrid(
    query_text := 'compensação de terra em duplicação de rodovia',
    query_embedding := '[...]'::vector(1536),
    match_count := 3,
    filter_segmento := 'rodovias',
    filter_nda_level := 'interno'
  );
```

Testar também com `filter_nda_level := 'publico'` para verificar que KEs
confidenciais NÃO aparecem.

## Stage 5 — SharePoint indexing

### 5.1 Criar a pasta no SharePoint

```
08_Casos_Manta/
├── 01_memoriais/
│   └── <projeto-slug>/          # 1 subpasta por projeto
├── 02_case_elements/
├── 03_exports/
└── 04_provenance/
```

Fazer upload dos PDFs/DOCX em `01_memoriais/<slug>/` e dos arquivos
`MCS-NNNNN.md` (opcionais, para revisão humana) em `02_case_elements/`.

### 5.2 Registrar routing

Já vem incluído na migração (`sp_agent_routing` linha `rag-manta-cases`).
Verificar:

```sql
SELECT * FROM sp_agent_routing WHERE agent_slug = 'rag-manta-cases';
```

### 5.3 Configurar o crawler

No indexer de SharePoint (fora deste repo), adicionar a pasta
`08_Casos_Manta/` como fonte e associar ao slug `manta-cases`.
Frequência sugerida: **diária**, notificar mudanças ao webhook
`POST /api/rag/reindex?collection=manta-cases`.

O crawler DEVE respeitar as permissões SharePoint da subpasta do
projeto: pastas com `nda_level=confidencial|restrito` só são indexadas
quando a service account tiver ACL apropriado.

## Stage 6 — Agent activation

### 6.1 Verificar bindings

```sql
SELECT agent_slug, role, priority
  FROM agent_rag_bindings
 WHERE collection_slug = 'manta-cases'
 ORDER BY priority DESC;
```

Esperado: 15 linhas (4× S1-S4 + 9× S5-S13 + 2× horizontais). Priority=120
em todos (110 no arquiteto-ia).

### 6.2 Reload dos SKILL.md

Cada agente vertical S6-S13 tem `rag_consume:` estendido para incluir
`manta-cases`. Bastar o Maestro recarregar o registry.

### 6.3 Smoke test — pelo menos 5 prompts

| Segmento    | Prompt de teste                                                                     | Teto NDA |
|-------------|-------------------------------------------------------------------------------------|----------|
| rodovias    | "Como a Manta resolveu compensação de terra em duplicação com faixa apertada?"      | interno  |
| oae         | "Já fizemos claim de reequilíbrio por variação de aço em OAE grande vão?"           | interno  |
| saneamento  | "Padrão de projeto executivo de ETA que a Manta consolidou em AySA."                | interno  |
| barragens   | "Contra-exemplos de alteamento a montante em nossos memoriais pós-Brumadinho."      | interno  |
| energia     | "Memória de cálculo para RAP em leilão ANEEL de transmissão 500 kV, caso Manta."    | interno  |

Critério de aprovação: **≥3 KEs relevantes** no top-5 de cada resposta,
com `citacao_interna` renderizada. Repetir 1 prompt com
`filter_nda_level='publico'` para confirmar que confidenciais somem.

### 6.4 Gate humano MN

- [ ] MN aprova as respostas do smoke test.
- [ ] MN valida a lista de projetos entrantes no primeiro batch (NDA
      revisado 1-a-1).
- [ ] Merge do PR desta branch.
- [ ] Bump versão CLAUDE.md master (proposta MN).

## Rollback

Se qualquer stage falhar após produção:

```sql
BEGIN;
-- Ver bloco DOWN completo em supabase/migrations/2026_07_12_manta_cases_v4_6.sql
COMMIT;
```

## Contatos

- **PO:** Manoel Neves (mneves@mantaassociados.com)
- **Tech lead:** Vinícius Magnos
- **Ticket:** WF-MCP-001
- **Slack:** #mcp-pipeline
