# Knowledge Hub — Operations Guide

## Overview

Knowledge Hub is a multi-org document management system with semantic search,
automatic chunking, embeddings, and versioning. Features:

- **Multipart upload**: PDF, CSV, DWG, TXT, DOCX (up to 500MB)
- **Auto-chunking**: 500-token chunks with 50-token overlap
- **Embeddings**: Sentence Transformers (all-MiniLM-L6-v2, 384 dims)
- **pgvector storage**: Semantic search via similarity scoring
- **Versioning**: Snapshots for rollback and comparison
- **Multi-org**: Per-organization document isolation with admin cross-org access
- **Progress tracking**: Real-time ingestion status (pending → processing → complete)

---

## Architecture

### Database Schema

Three main tables:

```sql
-- Document metadata and ingestion status
knowledge_documents (
  id UUID PRIMARY KEY,
  org_id UUID FK organizations.id,
  title VARCHAR(512),
  filename VARCHAR(512),
  file_type ENUM (pdf, csv, dwg, txt, docx),
  tags TEXT[] DEFAULT '{}',
  description TEXT,
  created_by UUID FK users.id,
  processing_status ENUM (pending, processing, complete, failed),
  progress_pct INT DEFAULT 0,
  error_message TEXT,
  size_bytes BIGINT,
  chunk_count INT,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now(),
  deleted_at TIMESTAMPTZ (soft-delete)
);

-- Document chunks with embeddings
knowledge_chunks (
  id UUID PRIMARY KEY,
  document_id UUID FK knowledge_documents.id ON DELETE CASCADE,
  chunk_index INT,
  content TEXT,
  content_tokens INT,
  embedding vector(384),  -- pgvector
  metadata JSONB (page, section, start_pos, etc.),
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Version history (snapshots)
knowledge_versions (
  id UUID PRIMARY KEY,
  document_id UUID FK knowledge_documents.id ON DELETE CASCADE,
  version_num INT,
  created_by UUID FK users.id,
  snapshot_json JSONB,
  created_at TIMESTAMPTZ DEFAULT now()
);
```

### Backend Stack

```
FastAPI router (routers/knowledge.py)
    ↓
Models (models/knowledge.py) + SQLAlchemy ORM
    ↓
PostgreSQL + pgvector extension
    ↓
Background tasks (tasks/knowledge_ingest.py)
    ├── File extraction (pypdf, pandas, python-docx)
    ├── Chunking (overlapping 500-token strategy)
    ├── Embedding (Sentence Transformers batch)
    └── Storage (asyncpg to pgvector)
```

### Frontend Stack

```
React component (KnowledgeHub.tsx)
    ↓
Hook (useKnowledgeHub.ts)
    ↓
Axios API client
    ↓
FastAPI endpoints
```

---

## API Endpoints

### POST /knowledge/upload
**Upload document (multipart, async processing)**

Request:
```bash
curl -X POST http://localhost:8000/knowledge/upload \
  -H "Authorization: Bearer <token>" \
  -F "file=@document.pdf" \
  -F "title=My Document" \
  -F 'tags=["rodovia", "pavimentação"]' \
  -F "description=Optional description"
```

Response (202 Accepted):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "org_id": "org-123",
  "title": "My Document",
  "filename": "document.pdf",
  "file_type": "pdf",
  "tags": ["rodovia", "pavimentação"],
  "processing_status": "pending",
  "progress_pct": 0,
  "chunk_count": 0,
  "created_at": "2026-07-27T10:00:00Z"
}
```

**Flow:**
1. Validates file (type, size)
2. Stores document metadata + sets status="pending"
3. Returns 202 Accepted immediately
4. Background task processes (extract → chunk → embed)
5. Poll `/knowledge/documents/{id}` to track `progress_pct` and `processing_status`

---

### GET /knowledge/documents
**List documents (with filters)**

Query parameters:
- `page`: 1-indexed (default 1)
- `page_size`: 1-100 (default 20)
- `tags`: CSV (tag1,tag2) - matches ANY
- `status_filter`: pending|processing|complete|failed
- `created_after`: RFC3339 timestamp
- `created_before`: RFC3339 timestamp
- `org_id`: admin only, filter by organization

Response:
```json
{
  "documents": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "My Document",
      "file_type": "pdf",
      "size_bytes": 2048000,
      "tags": ["rodovia"],
      "processing_status": "complete",
      "progress_pct": 100,
      "chunk_count": 12,
      "created_at": "2026-07-27T10:00:00Z"
    }
  ],
  "total": 42,
  "page": 1,
  "page_size": 20
}
```

---

### GET /knowledge/documents/{id}
**Retrieve document + chunks**

Response:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "My Document",
  "chunks": [
    {
      "id": "chunk-001",
      "chunk_index": 0,
      "content": "Lorem ipsum dolor sit amet...",
      "content_tokens": 487,
      "metadata": {
        "page": 1,
        "section": "introduction"
      },
      "created_at": "2026-07-27T10:05:00Z"
    }
  ]
}
```

---

### PUT /knowledge/documents/{id}
**Update document metadata**

Request:
```json
{
  "title": "Updated Title",
  "tags": ["rodovia", "licitação"],
  "description": "New description"
}
```

**Side effect:** Creates version snapshot before modifying.

---

### DELETE /knowledge/documents/{id}
**Soft-delete document**

Sets `deleted_at` timestamp. Documents are filtered out from list views.
Chunks are preserved (cascade delete not performed) for audit trail.

---

### GET /knowledge/documents/{id}/versions
**List document versions**

Response:
```json
[
  {
    "id": "v-001",
    "version_num": 2,
    "created_by": "user-123",
    "snapshot_json": {
      "title": "Updated Title",
      "tags": ["rodovia"],
      "chunk_count": 12
    },
    "created_at": "2026-07-27T10:10:00Z"
  }
]
```

Sorted by version number (descending, newest first).

---

### POST /knowledge/semantic-search
**Semantic search across documents**

Request:
```json
{
  "query": "pavimentação de rodovia",
  "top_k": 10,
  "tags": ["rodovia"],
  "org_ids": []
}
```

Response:
```json
{
  "query": "pavimentação de rodovia",
  "results": [
    {
      "chunk_id": "chunk-001",
      "document_id": "doc-001",
      "document_title": "Projeto Executivo BR-101",
      "content": "Especificações técnicas para CBUQ e BGS...",
      "similarity_score": 0.87,
      "page_num": 5,
      "tags": ["rodovia"],
      "metadata": {"page": 5, "section": "specifications"}
    }
  ],
  "search_time_ms": 142.5
}
```

**Algorithm:**
1. Embed query via Sentence Transformers
2. pgvector `<->` operator (cosine distance) on `knowledge_chunks.embedding`
3. Sort by distance (ascending), limit to `top_k`
4. Return with similarity_score = 1 - distance

---

## Chunking Strategy

### Why 500 tokens?

- **Trade-off:** Balance between context (more tokens = more context) and
  granularity (fewer chunks = faster search, less redundancy)
- **Estimate:** 1 token ≈ 1 word → 500 tokens ≈ 500 words ≈ 2–3 paragraphs
- **Tunable:** Adjust `target_tokens` in `tasks/knowledge_ingest._chunk_paragraphs()`

### Why 50-token overlap?

- **Prevents context loss:** Chunks that split mid-sentence are re-indexed
  with the last N words of the previous chunk
- **Improves recall:** Queries that straddle chunk boundaries match both
  overlapping chunks
- **Cost:** ~10% redundant embeddings, acceptable trade-off

### Example

```
Document text:
[W1 W2 W3 ... W500] [W451 W452 ... W950] [W901 W902 ... W1400]
                ↑overlap (W451-W500)    ↑overlap (W901-W950)
```

### Configuration

Edit `tasks/knowledge_ingest._chunk_paragraphs()`:

```python
def _chunk_paragraphs(
    paragraphs: list[...],
    target_tokens: int = 500,      # Adjust chunk size here
    overlap_tokens: int = 50,       # Adjust overlap here
) -> list[...]:
    ...
```

---

## File Type Support

| Type | Extractor | Output | Status |
|------|-----------|--------|--------|
| PDF | pypdf | Text per page | ✅ Stable |
| CSV | pandas | Rows as text | ✅ Stable |
| TXT | built-in | Paragraphs | ✅ Stable |
| DOCX | python-docx | Paragraphs | ✅ Stable |
| DWG | (metadata only) | Placeholder | ⚠️ Partial |

### PDF Extraction

```python
# manta-backend/tasks/knowledge_ingest._extract_pdf()
from pypdf import PdfReader

pdf = PdfReader(io.BytesIO(content))
for page_num, page in enumerate(pdf.pages, start=1):
    text = page.extract_text()
    metadata = {"page": page_num}
```

**OCR:** Optional via pytesseract. Set env var `ENABLE_PDF_OCR=true`.

### CSV Parsing

```python
# Each row becomes a chunk
df = pd.read_csv(io.BytesIO(content))
for idx, row in df.iterrows():
    text = " | ".join(f"{k}: {v}" for k, v in row.items())
```

### DWG Metadata

Currently extracts only filename/timestamp. Full CAD parsing requires
ezdxf (Autodesk integration) — planned for v2.0.

---

## Searching

### Semantic Search (Recommended)

Uses **Sentence Transformers** embeddings + pgvector similarity.

**Pros:**
- Understands meaning ("pavimentação" ~ "asfalto")
- Multi-language
- Works without explicit keywords

**Cons:**
- Slower than keyword search (~100–200ms per query)
- Requires embeddings to be computed upfront

**Usage:**
```bash
POST /knowledge/semantic-search
{
  "query": "O que é CBUQ?",
  "top_k": 5,
  "tags": ["rodovia"]
}
```

### Keyword Search (Future)

Would use PostgreSQL full-text search (GIN index on `tsvector`).
Plan: add `POST /knowledge/keyword-search` in v2.0.

---

## Versioning & Rollback

### Creating Versions

Automatically created when:
1. User updates document metadata (PUT /knowledge/documents/{id})

Manually create via:
```bash
POST /knowledge/documents/{id}/versions
```

### Snapshots

Each version stores JSON snapshot of document state:

```json
{
  "title": "Project Title",
  "description": "...",
  "tags": ["tag1", "tag2"],
  "chunk_count": 12,
  "metadata": {}
}
```

**Note:** Snapshots do NOT store chunk data (too large). Chunks are
immutable — rollback recreates document metadata only.

### Comparing Versions

Frontend can diff two snapshots:

```typescript
const v1 = versions[0];
const v2 = versions[1];

const diff = {
  title: v1.snapshot_json.title !== v2.snapshot_json.title ? {
    from: v1.snapshot_json.title,
    to: v2.snapshot_json.title
  } : null,
  // ...
};
```

---

## Performance & Scalability

### Indexing

Create indexes for common queries:

```sql
CREATE INDEX idx_knowledge_documents_org_id_created_at
  ON knowledge_documents(org_id, created_at DESC)
  WHERE deleted_at IS NULL;

CREATE INDEX idx_knowledge_chunks_document_id
  ON knowledge_chunks(document_id);

-- pgvector similarity search index (optional, large datasets)
CREATE INDEX idx_knowledge_chunks_embedding
  ON knowledge_chunks USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 100);
```

### Query Performance

- **List documents:** ~10ms (with indexes)
- **Semantic search:** ~100–200ms (5–10 chunks returned)
- **Upload + processing:** O(file_size)
  - PDF 10MB: ~30s (extraction + chunking + embedding)
  - CSV 1MB: ~5s

### Batch Embedding

Embeddings are generated in batches (default 32 chunks per batch):

```python
embeddings = await embed_batch(chunk_texts, batch_size=32)
```

Adjust in `tasks/knowledge_ingest.process_document_upload()`.

---

## Multi-Org Access Control

### Default Behavior

- User sees only documents in their active `org_id`
- Query filters automatically add `WHERE org_id = current_org_id`

### Admin Cross-Org Access

Admin users can pass `?org_id=other-org-id`:

```bash
GET /knowledge/documents?org_id=other-org-123
```

**Authorization:** Check user role (via JWT claims) before allowing.

---

## Error Handling

### Ingestion Failures

If background task fails:

1. `processing_status` → "failed"
2. `error_message` populated (first 512 chars)
3. User polls `/knowledge/documents/{id}` and sees failure

**Retry:**
```bash
DELETE /knowledge/documents/{id}
POST /knowledge/upload (re-upload same file)
```

### Soft-Delete Cleanup

Soft-deleted documents are hidden from list views.
To permanently delete (and cascade chunks):

```bash
# Manual DB cleanup (admin only)
DELETE FROM knowledge_documents WHERE deleted_at < now() - interval '90 days';
```

---

## Best Practices

### Organization by Tags

Use consistent tag hierarchy:

```
Segment: rodovia | ferrovia | metrô | saneamento | energia
Phase:   estudo | projeto-basico | projeto-executivo | obra | operacao
Status:  em-progresso | concluido | ativo | arquivado
```

Example:
```bash
POST /knowledge/upload \
  -F 'tags=["rodovia", "projeto-executivo", "concluido"]'
```

### File Naming

Include metadata in filename:

```
DNIT_BR101_Projeto_Executivo_Pavimentacao_v2.pdf
AySA_Adutora_Calculos_Hidraulicos.xlsx
Terminal_Porto_Santos_DPA_Revisao3.dwg
```

### Regular Audits

Check for stale/duplicate documents:

```sql
-- Documents processing for >1 day
SELECT id, title, progress_pct FROM knowledge_documents
WHERE processing_status = 'processing'
  AND created_at < now() - interval '1 day';

-- Soft-deleted (inactive) documents
SELECT id, title, deleted_at FROM knowledge_documents
WHERE deleted_at IS NOT NULL
  AND deleted_at < now() - interval '180 days';
```

---

## Security

### Access Control

- All endpoints require `Authorization: Bearer <jwt>`
- Documents isolated by `org_id` + JWT claims
- Soft-delete prevents accidental data loss (recoverable via DB)

### File Scanning (Optional)

Enable virus scanning on upload:

```python
# manta-backend/routers/knowledge.py
from ml.virus_scanner import scan_file

if ENABLE_VIRUS_SCAN:
    is_clean = await scan_file(file.file)
    if not is_clean:
        raise HTTPException(status_code=403, detail="Virus detected")
```

### Data Privacy

- Embeddings stored in PostgreSQL (same as source docs)
- No third-party embedding service calls
- All processing on-premises

---

## Integration Examples

### Upload a PDF from Python

```python
import httpx

async with httpx.AsyncClient() as client:
    with open("document.pdf", "rb") as f:
        response = await client.post(
            "http://localhost:8000/knowledge/upload",
            headers={"Authorization": f"Bearer {token}"},
            files={"file": f},
            data={
                "title": "My Document",
                "tags": '["tag1", "tag2"]',
                "description": "Optional"
            }
        )
        doc = response.json()
        print(f"Uploaded: {doc['id']}")
```

### Search from JavaScript

```typescript
const results = await fetch('/api/knowledge/semantic-search', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({
    query: 'pavimentação de rodovia',
    top_k: 10,
    tags: ['rodovia']
  })
}).then(r => r.json());

console.log(results.results);
```

---

## Troubleshooting

### Upload stuck in "processing"

Check background task logs:
```bash
docker logs manta-backend | grep knowledge_ingest
```

If stuck >5 min, manually reset:
```sql
UPDATE knowledge_documents
SET processing_status = 'failed',
    error_message = 'Manual reset'
WHERE id = 'doc-id' AND processing_status = 'processing';
```

### Search returns 0 results

1. Verify embeddings were generated:
   ```sql
   SELECT COUNT(*) FROM knowledge_chunks
   WHERE document_id = 'doc-id' AND embedding IS NOT NULL;
   ```

2. Test with different query:
   ```bash
   POST /knowledge/semantic-search
   {"query": "test", "top_k": 10}
   ```

3. Check pgvector extension:
   ```bash
   docker exec -it postgres psql -c "CREATE EXTENSION IF NOT EXISTS vector;"
   ```

### Memory issues with large files

Increase Docker memory limit:
```yaml
# docker-compose.yml
services:
  manta-backend:
    mem_limit: 4g
```

Reduce batch size in `tasks/knowledge_ingest.py`:
```python
embeddings = await embed_batch(chunk_texts, batch_size=8)  # was 32
```

---

## Roadmap

- **v1.1:** Keyword search (full-text index)
- **v1.2:** OCR for images in PDFs
- **v1.3:** DWG full parsing (ezdxf)
- **v2.0:** Semantic caching (store embeddings metadata)
- **v2.1:** Bulk operations (tag many docs, export embeddings)
- **v2.2:** Integration with agent RAG (auto-ingest from SharePoint)

---

## Support

For bugs/feature requests, open an issue in the Codex-exemplo repo or
contact the Manta Associados IA team.
