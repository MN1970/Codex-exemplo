# Phase 2 Quick Start Guide

**Quick Reference for Phase 2 Features (2.1-2.5)**

---

## Installation

```bash
# Install Phase 2 dependencies
pip install -r requirements-phase2.txt

# Verify installation
python -c "import maestro; import api; print('✅ Phase 2 ready')"
```

---

## Phase 2.1: Feedback Loop

### For Data Team (Weekly Analysis)

```bash
# Run weekly feedback analysis
python scripts/weekly_feedback_report.py

# With date range
python scripts/weekly_feedback_report.py --since 2026-07-19 --until 2026-07-26

# Create GitHub issues for HIGH priority recommendations
python scripts/weekly_feedback_report.py --create-issues --repo mn1970/manta-hub

# Dry-run (preview without GitHub)
python scripts/weekly_feedback_report.py --dry-run
```

### Expected Output
```
Weekly Feedback Report — 2026-07-19 to 2026-07-26

Approval rates by agent:
agent                          total    approved     rate
agente-barragens                  24           21    87.5%
agente-energia                    18           16    88.9%
agente-saneamento                 12            9    75.0%

Recommendations (from analyze_feedback_and_recommend):
  [HIGH] agente-saneamento: Boost keywords for "drenagem" (n=3 failed)
  [MEDIUM] agente-energia: Review routing for "subestação" cases (n=2)
```

---

## Phase 2.2: Multi-Agent Orchestration

### For Maestro Team (Routing Integration)

```python
from maestro.orchestrator import MaestroOrchestrator, OrchestratorInput

# Initialize
orchestrator = MaestroOrchestrator()

# When ambiguous routing detected (gap < 10%)
if abs(scores["agent_1"] - scores["agent_2"]) < 0.10:
    input_data = OrchestratorInput(
        user_prompt=original_query,
        primary_agent=top_agent,
        primary_response=agent1_response,
        secondary_agent=second_agent,
        secondary_response=agent2_response,
        routing_scores=scores,
    )
    
    result = orchestrator.orchestrate(input_data)
    
    # Use merged response
    final_response = result.merged_response
    
    # Log orchestration metrics
    log_metric({
        "orchestrator_invoked": True,
        "primary_agent": result.primary_responsibility,
        "cross_concerns": len(result.cross_concerns),
        "confidence": result.confidence,
    })
```

### Testing Orchestration

```bash
# Run orchestration tests
pytest tests/orchestration/test_orchestrator.py -v

# Run E2E workflow
pytest tests/test_phase2_integration.py::TestPhase2EndToEndWorkflow -v
```

---

## Phase 2.3: Document Auto-Classification

### For SharePoint Team (Document Routing)

```python
from api.document_classifier import DocumentClassifier

# Initialize
classifier = DocumentClassifier()

# When document uploaded
result = classifier.classify("/path/to/document.pdf")

# Use classification for SharePoint automation
metadata = {
    "maestro_suggested_agent": result.primary_agent,
    "maestro_confidence": result.confidence,
    "maestro_suggested_folder": result.suggested_folder,
    "maestro_classification_reason": result.classification_reason,
}

# Update SharePoint file metadata
sharepoint.update_metadata(file_id, **metadata)

# Notify user
send_notification(
    f"Document '{result.file_name}' → {result.primary_agent} "
    f"({result.confidence:.0%}). Does this look right?"
)
```

### Supported Document Formats
- **PDF**: Full text extraction (first 3 pages)
- **Images**: OCR text extraction (PNG, JPG)
- **Text**: Plain text and Markdown
- **DOCX**: Word documents

### Testing Classification

```bash
# Run classifier tests
pytest tests/test_document_classifier.py -v

# Test with a document
python -c "
from api.document_classifier import DocumentClassifier
c = DocumentClassifier()
result = c.classify('sample.pdf')
print(f'Agent: {result.primary_agent} ({result.confidence:.0%})')
"
```

---

## Phase 2.4: RAG Batch Ingestion

### For DevOps/Data Team (Monthly Job)

```bash
# List available collections
ls docs/rag-sources/

# Dry-run preview
python scripts/ingest_rag_batch.py \
  --segment saneamento \
  --tier T1 \
  --dry-run

# Full ingestion (one segment)
python scripts/ingest_rag_batch.py \
  --segment energia \
  --tier T2 \
  --batch-size 50

# Ingest all collections (production)
for segment in saneamento energia portos aeroportos barragens; do
  echo "Ingesting $segment..."
  python scripts/ingest_rag_batch.py --segment $segment
done
```

### Document Organization
```
docs/rag-sources/
├── saneamento/
│   ├── T1-normas/          (SNIS, NBR 12211-12218, Lei 14.026)
│   ├── T2-projetos/        (ETAs, ETEs, adutoras)
│   ├── T3-relatorios/      (Research, case studies)
│   └── T4-templates/       (Editais, manuais)
├── energia/
│   ├── T1-normas/          (ANEEL R1-R5, IEEE)
│   ├── T2-projetos/        (LT projects, substations)
│   └── ...
└── ... (other segments)
```

### TIER Strategies
- **T1**: Normas/leis (preserve section structure)
- **T2**: Projetos/estudos (extract tables + code)
- **T3**: Relatórios/pesquisa (semantic chunking)
- **T4**: Templates/editais (minimal processing)

### Output Metrics
```json
{
  "segment": "energia",
  "tier": "T1",
  "files_processed": 8,
  "total_chunks": 324,
  "embeddings_generated": 324,
  "db_inserts_succeeded": 324,
  "duration_seconds": 145.3
}
```

---

## Phase 2.5: SharePoint Sync

### For DevOps/GitHub Team (Automatic on PR Merge)

```bash
# Manual sync (for testing)
python scripts/sync_agents_to_sharepoint.py --dry-run

# Sync all agents
python scripts/sync_agents_to_sharepoint.py --all

# Sync one agent
python scripts/sync_agents_to_sharepoint.py --agent agente-barragens

# Sync only changed files
python scripts/sync_agents_to_sharepoint.py --changed
```

### Automatic Trigger (GitHub Actions)
- **Trigger**: PR merged to `main` with `.claude/agents/*.md` changes
- **Action**: Automatically syncs to SharePoint
- **Location**: `.github/workflows/sync-agents-to-sharepoint.yml`

### Agent Sync Mapping
```
.claude/agents/
├── agente-saneamento.md      → .../agente-saneamento/SKILL.md
├── agente-energia.md         → .../agente-energia/SKILL.md
├── agente-portos.md          → .../agente-portos/SKILL.md
├── agente-aeroportos.md      → .../agente-aeroportos/SKILL.md
└── agente-barragens.md       → .../agente-barragens/SKILL.md
```

---

## Testing All Phase 2 Features

### Full Test Suite

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
pytest tests/ -v --cov=maestro --cov=api

# Run by phase
pytest tests/orchestration/ -v          # Phase 2.2
pytest tests/test_document_classifier.py -v  # Phase 2.3
pytest tests/test_phase2_integration.py -v   # All phases

# Coverage report
pytest tests/ --cov=maestro --cov=api --cov-report=html
open htmlcov/index.html
```

### Quick Smoke Test

```bash
# Verify all modules import
python -c "
from maestro.orchestrator import MaestroOrchestrator
from api.document_classifier import DocumentClassifier
from scripts.ingest_rag_batch import RAGBatchIngester
print('✅ All Phase 2 modules loaded')
"
```

---

## Monitoring & Metrics

### Key Metrics to Track

| Feature | Metric | Target | How |
|---------|--------|--------|-----|
| Feedback | Approval rate | ≥85% | Weekly report |
| Orchestration | Invocation rate | 5-10% | maestro_runtime_metrics |
| Classification | Accuracy | ≥90% | maestro_user_feedback |
| RAG | Relevance | ≥85% | Top-1 accuracy |
| Sync | Success rate | 100% | GitHub Actions logs |

### Database Queries

```sql
-- Approval rates by agent
SELECT 
  primary_agent,
  COUNT(*) as total,
  SUM(CASE WHEN user_approved THEN 1 ELSE 0 END) as approved,
  ROUND(100.0 * SUM(CASE WHEN user_approved THEN 1 ELSE 0 END) / COUNT(*), 1) as approval_rate
FROM maestro_routing_trace
WHERE timestamp > now() - interval '7 days'
GROUP BY primary_agent
ORDER BY approval_rate DESC;

-- Orchestration invocation
SELECT 
  COUNT(*) as orchestrations_triggered,
  ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM maestro_routing_trace WHERE timestamp > now() - interval '7 days'), 1) as percent_of_queries
FROM maestro_routing_trace
WHERE is_ambiguous = true
AND timestamp > now() - interval '7 days';

-- Classification accuracy
SELECT 
  routed_agent,
  COUNT(*) as total,
  SUM(CASE WHEN routed_agent = user_correct_agent THEN 1 ELSE 0 END) as correct,
  ROUND(100.0 * SUM(CASE WHEN routed_agent = user_correct_agent THEN 1 ELSE 0 END) / COUNT(*), 1) as accuracy
FROM maestro_document_classifications
WHERE timestamp > now() - interval '7 days'
GROUP BY routed_agent;
```

---

## Troubleshooting

### Orchestrator Not Triggering
```bash
# Check routing scores in logs
# Verify score gap calculation
gap = abs(score1 - score2)
if gap >= 0.10:  # NOT ambiguous
    # Orchestrator won't trigger
    
# Solution: Lower threshold in router config
# AMBIGUITY_THRESHOLD = 0.10  # Change to 0.15 for more orchestration
```

### Document Classification Low Confidence
```bash
# Check extracted text length
# Short documents may have low confidence
# Solution: Ensure documents have >500 chars of meaningful text

# Check supported format
# OCR for images may fail if text density is low
# Solution: Upload higher quality images or PDFs
```

### RAG Ingestion Slow
```bash
# Monitor batch size
# Default batch size = 50 items per API call
# Solution: Adjust batch-size parameter
python scripts/ingest_rag_batch.py --batch-size 100

# Monitor network latency
# Check Supabase connection
# Solution: Run during off-peak hours
```

### SharePoint Sync Fails
```bash
# Verify Graph API token
# Check SHAREPOINT_SITE_ID and SHAREPOINT_DRIVE_ID

# Check file permissions
# Ensure agent .md files are readable

# Verify network connectivity
# Test Microsoft Graph API access
curl -H "Authorization: Bearer $GRAPH_TOKEN" \
  https://graph.microsoft.com/v1.0/me
```

---

## Support & Documentation

- **Full Specs**: `docs/PHASE-2-IMPLEMENTATION-SUMMARY.md`
- **Runbooks**: `docs/RUNBOOK-PHASE-2.*.md`
- **Test Examples**: `tests/test_phase2_integration.py`
- **Code Comments**: In-code docstrings in each module

---

## Environment Variables

```bash
# Required
export ANTHROPIC_API_KEY="sk-..."
export SUPABASE_URL="https://xxx.supabase.co"
export SUPABASE_ANON_KEY="eyJxxx..."

# Optional (for SharePoint sync)
export SHAREPOINT_SITE_ID="xxx"
export SHAREPOINT_DRIVE_ID="xxx"
export MICROSOFT_GRAPH_TOKEN="Bearer xxx"

# Optional (for GitHub integration)
export GH_TOKEN="ghp_xxx"
```

---

**Phase 2 is now live. Deploy with confidence! 🚀**
