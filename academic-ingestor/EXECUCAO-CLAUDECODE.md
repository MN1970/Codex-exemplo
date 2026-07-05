# WF-AKP-001 — Execução no Claude Code (Stages 4-6)

Registro do que foi de fato executado nesta sessão do Claude Code em cima do
handoff da sessão Claude Chat (Maurício, 2026-07-05). Complementa o `HANDOFF.md`.

## Contexto do handoff recebido

- Stages 1-3 vieram concluídos: 36 teses / 52 KEs, grader médio 8.9/10, aluci-guard
  100 % pass, gate humano aprovado.
- Handoff apontava `kwuubcnedqtapvykmyye` (manta-portal-piloto) como target Supabase.
  Verificação inicial: **esse projeto está INACTIVE**. Redirecionei para
  `ogxxgvgtulrbbppshjie` (manta-maestro, `ACTIVE_HEALTHY`, sa-east-1) — coerente com o
  restante do CLAUDE.md do repo (Manta Maestro v4.2).

## Stage 4 — M13 migration (aplicada)

Duas migrations aplicadas via MCP `apply_migration`:

| Migration                                     | Cria/altera                                                       |
|-----------------------------------------------|-------------------------------------------------------------------|
| `wf_akp_001_academic_ingestor`                | tabelas `teses_academicas`, `knowledge_extractions`, `ke_embeddings`; índices GIN/BTREE/HNSW; triggers `updated_at`; RLS + políticas `service_role`/`authenticated` |
| `wf_akp_001_align_with_handoff_schema`        | ADD `grader_score`, `aluci_status`, `conhecimentos jsonb` em `teses_academicas` (formato do HANDOFF) |

Extensão `vector 0.8.0` já estava instalada no projeto — reaproveitada. Índice
HNSW `vector_cosine_ops`, mesma convenção do `manta_rag_chunks` existente
(embeddings 768d, modelo `paraphrase-multilingual-mpnet-base-v2`).

O arquivo consolidado e re-aplicável está em
`supabase/migration_teses_academicas.sql`.

## Stage 5 — Seed das 36 teses (aplicado)

Arquivo `supabase/inserts_teses.sql` (do handoff) executado em 6 lotes de 6
INSERTs via MCP `execute_sql` (uma tentativa em bloco único falhou por typo de
transcrição — a transação inteira rolou back sem inserir nada; o arquivo em
disco está íntegro). Todos os INSERTs usam `ON CONFLICT (codigo) DO UPDATE`,
então re-execução é idempotente.

Validação:

```sql
select count(*) as teses,
       sum(jsonb_array_length(conhecimentos)) as total_kes
from teses_academicas;
-- teses = 36 ✓
-- total_kes = 52 ✓
```

Depois normalizei os KEs para a tabela `knowledge_extractions` (uma linha por
KE, com FK para tese, agentes copiados, `approved_by='Maurício Neves'`,
`approved_at='2026-07-05'`):

```sql
insert into knowledge_extractions (ke_codigo, tese_codigo, tipo, descricao, agentes_destino, grader_score, aluci_status, approved_by, approved_at)
select ke->>'id', t.codigo, ke->>'tipo', ke->>'desc',
       t.agentes_destino, t.grader_score, t.aluci_status,
       'Maurício Neves', '2026-07-05T00:00:00Z'::timestamptz
from teses_academicas t cross join lateral jsonb_array_elements(t.conhecimentos) as ke
on conflict (ke_codigo) do update set ...;
-- 52 KEs inseridos ✓
```

E marquei todas as teses como `status='graded'` (o status pós-gate ainda é
`graded`; muda para `ingested` quando o M18 rodar em produção).

Rollup por bloco (do banco):

| Bloco | Teses | KEs | Grader avg |
|-------|-------|-----|-----------|
| B1    | 5     | 7   | 9.07      |
| B2    | 5     | 6   | 8.16      |
| B3    | 3     | 5   | 9.00      |
| B4    | 6     | 8   | 9.00      |
| B5    | 6     | 9   | 9.10      |
| B6    | 3     | 5   | 9.00      |
| B7    | 5     | 7   | 8.95      |
| B8    | 3     | 5   | 8.90      |

## Stage 6.1 — M18 embedding pipeline (código pronto)

`src/m18_embeddings.py` — script Python executável que:
1. Lista KEs sem embedding (LEFT-JOIN via 2 queries no PostgREST).
2. Constrói o `chunk_text` como `[<tipo>] [<agentes>] <descricao>` (enriquece o
   retrieval por lente).
3. Gera embeddings 768d normalizados com sentence-transformers.
4. Upsert em `ke_embeddings` (idempotente via `on_conflict`).

**Não foi executado** nesta sessão — precisa de `SUPABASE_SERVICE_KEY` (não
está no ambiente) e ~470MB de download do modelo mpnet do HuggingFace.
Instruções de execução no cabeçalho do arquivo.

## Stage 6.2 — M20 SharePoint uploader (código pronto)

`src/m20_sharepoint_upload.py` — scaffold documentado que:
1. Faz OAuth `client_credentials` via MSAL (App-only, `Sites.ReadWrite.All`).
2. Resolve `drive_id` do site.
3. Cria `04_IA/Manta-Maestro/Teses/{bloco}/` sob demanda.
4. Upload dos PDFs (`{codigo}.pdf`) — single-request para <4MB, upload session
   com chunks de 5MB e retentativa exponencial para arquivos maiores.
5. Upload do `INDICE-KEs.md` como referência.
6. Emite relatório JSON com status por código.

**Não foi executado** — depende dos secrets `SP_TENANT_ID/CLIENT_ID/CLIENT_SECRET/SITE_ID`
e dos PDFs em disco (nenhum PDF foi baixado nesta sessão; a pasta `pdfs/` está vazia).
Rode com `--dry-run` primeiro para validar o mapeamento local→remoto.

## O que ficou pendente

| Passo                    | Motivo                                     | Como destravar                                |
|--------------------------|--------------------------------------------|-----------------------------------------------|
| M18 embeddings em prod   | `SUPABASE_SERVICE_KEY` não disponível      | `export SUPABASE_SERVICE_KEY=... && python src/m18_embeddings.py` |
| Download dos 36 PDFs     | Fetch massivo de fontes externas não iniciado | Reusar `batch_processor.py` (referência no `HANDOFF.md`) com `httpx` respeitando robots.txt |
| M20 upload SP            | Secrets SharePoint + PDFs em disco         | Depois do fetch: `python src/m20_sharepoint_upload.py --catalog ../MASTER-CATALOG.json --pdfs ../pdfs/` |
| Atualização INDICE-MANTA | Fora do escopo desta sessão                 | Adicionar seção "Conhecimento Acadêmico" apontando para `academic-ingestor/INDICE-KEs.md` |
