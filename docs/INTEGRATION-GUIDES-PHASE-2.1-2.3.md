# Integration Guides — Phase 2.1-2.3 (Team Implementation)

**Status**: 📝 SPECIFICATIONS COMPLETE, AWAITING TEAM INTEGRATION  
**Timeline**: Parallel to Phase 2.4 & 2.5 deployment (Aug-Sep 2026)  
**Target Owners**: Cowork team (2.1, 2.3), Maestro team (2.2)

---

## Phase 2.1 — Feedback Loop Integration (Cowork Team)

### Overview

The feedback loop requires integration into Cowork's UI and a weekly scheduled analysis job.

**Database tables already exist** (created by Phase 1 migration):
- `maestro_user_feedback` — user feedback entries
- `maestro_routing_keywords` — routing rules (source of truth)
- `maestro_feedback_analysis` — weekly aggregated analysis
- `maestro_routing_ab_tests` — A/B test tracking

**Your integration tasks:**

### Task 1: Add "Was This Correct?" Button to Cowork UI

**Where**: Agent response display in Cowork  
**When**: After agent returns response  
**UI Component**: Thumbs up/down + optional confidence slider (1-5)

```typescript
// Cowork component pseudo-code

interface FeedbackPanel {
  agent_slug: string;
  user_message: string;
  agent_response: string;
  session_id: string;
}

async function submitFeedback(
  feedback: FeedbackPanel,
  approved: boolean,
  confidence: number  // 1-5 slider
) {
  // Call Maestro feedback endpoint
  const response = await fetch('/api/maestro/feedback', {
    method: 'POST',
    body: JSON.stringify({
      prompt: feedback.user_message,
      routed_agent: feedback.agent_slug,
      correct_agent: approved ? feedback.agent_slug : null,  // user can correct
      confidence,
      approved,
      timestamp: new Date(),
      session_id: feedback.session_id,
    })
  });

  // Show confirmation
  showNotification('Feedback recorded. Thank you!');
}
```

**Database insertion** (you can do this via Supabase JavaScript client):

```javascript
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_ANON_KEY
)

async function recordUserFeedback({
  user_id,
  prompt,
  routed_agent,
  correct_agent,
  confidence,
  approved
}) {
  const { data, error } = await supabase
    .from('maestro_user_feedback')
    .insert({
      user_id,
      prompt,
      routed_agent,
      correct_agent,
      confidence,
      approved,
      timestamp: new Date(),
    })

  if (error) throw error
  return data
}
```

**UI Mockup:**

```
┌─────────────────────────────────────────┐
│ Agent Response                          │
│ "A profundidade ideal para a ETA..."   │
├─────────────────────────────────────────┤
│ Was this agent correct?                 │
│                                         │
│  👍 Helpful    👎 Incorrect            │
│                                         │
│  Confidence: [●●●●○] 4/5               │
│                                         │
│  [What agent should have answered?  ▼] │
│  └─ Selectable: same agent, other...   │
│                                         │
│  [Submit Feedback]                      │
└─────────────────────────────────────────┘
```

### Task 2: Set Up Weekly Analysis Job

**Owner**: DevOps (schedule) + Cowork team (implementation)  
**Frequency**: Every Monday at 9 AM UTC  
**Job Type**: Supabase scheduled function or cron job

```sql
-- Supabase scheduled function
-- Can be triggered via pg_cron extension

CREATE OR REPLACE FUNCTION analyze_feedback_and_recommend()
RETURNS TABLE (
  agent_slug VARCHAR,
  approval_rate FLOAT,
  low_confidence_keywords TEXT[],
  recommended_action TEXT
) AS $$
BEGIN
  -- Get approval rate per agent (last 7 days)
  WITH agent_stats AS (
    SELECT
      routed_agent,
      COUNT(*) as total_feedback,
      SUM(CASE WHEN approved THEN 1 ELSE 0 END) as approved_count,
      AVG(confidence) as avg_confidence
    FROM maestro_user_feedback
    WHERE created_at > now() - interval '7 days'
    GROUP BY routed_agent
  )
  
  SELECT
    routed_agent,
    ROUND(approved_count::FLOAT / total_feedback, 2) as approval_rate,
    -- Extract keywords from low-confidence rejections
    (
      SELECT ARRAY_AGG(DISTINCT keyword)
      FROM maestro_routing_keywords
      WHERE agent_slug = agent_stats.routed_agent
        AND approval_count < 5  -- Low approval threshold
    ),
    CASE
      WHEN approval_rate < 0.70 THEN
        'Urgent: Boost ' || routed_agent || ' keywords'
      WHEN approval_rate < 0.85 THEN
        'Improve routing for ' || routed_agent
      ELSE
        'Performance acceptable'
    END as recommended_action
  FROM agent_stats
  ORDER BY approval_rate ASC;
END;
$$ LANGUAGE SQL;

-- Schedule for Monday 9 AM UTC
SELECT cron.schedule(
  'maestro_weekly_feedback_analysis',
  '0 9 * * 1',  -- Monday at 9 AM UTC
  'SELECT analyze_feedback_and_recommend();'
);
```

### Task 3: Create GitHub Issues from Recommendations

After the analysis job runs, create GitHub issues for agents needing improvement:

```bash
#!/bin/bash
# Run after feedback analysis

# Query results
RESULTS=$(psql "$DATABASE_URL" << 'SQL'
SELECT
  routed_agent,
  approval_rate,
  recommended_action,
  low_confidence_keywords
FROM maestro_feedback_analysis
WHERE week = date_trunc('week', now())
ORDER BY approval_rate ASC;
SQL
)

# Create issues for agents with approval_rate < 85%
while IFS= read -r agent approval action keywords; do
  if (( $(echo "$approval < 0.85" | bc -l) )); then
    gh issue create \
      --title "Routing improvement: $agent approval ${approval}%" \
      --body "Weekly feedback analysis recommends: $action

Low-confidence keywords: $keywords

Steps to improve:
1. Review rejected queries in maestro_user_feedback
2. Boost keywords in maestro_routing_keywords
3. Test with routing test suite
4. Re-enable once approval_rate > 85%"
  fi
done <<< "$RESULTS"
```

### Task 4: A/B Testing Setup (Optional)

For advanced feedback learning, implement A/B tests:

```sql
-- Table for tracking A/B tests
INSERT INTO maestro_routing_ab_tests (
  control_agent,
  experimental_agent,
  test_start,
  test_end,
  sample_size,
  control_approval_rate,
  experimental_approval_rate
)
VALUES (
  'agente-saneamento',
  'agente-saneamento-v2',
  now(),
  now() + interval '7 days',
  100,
  NULL,
  NULL
);

-- Randomly assign test users
UPDATE maestro_user_feedback
SET ab_test_id = (
  SELECT id FROM maestro_routing_ab_tests
  WHERE control_agent = 'agente-saneamento'
)
WHERE routed_agent = 'agente-saneamento'
  AND random() < 0.5
  AND created_at > now() - interval '7 days';
```

---

## Phase 2.2 — Orchestrator Integration (Maestro Team / manta-hub)

### Overview

The Orchestrator Agent (Manta 16) needs to be integrated into the maestro router to handle ambiguous queries.

**Specifications already provided**:
- `.claude/agents/maestro-orchestrator.md` — complete agent definition
- `docs/ORCHESTRATOR-IMPLEMENTATION-GUIDE.md` — reference code
- `tests/routing/test_multiagent_dispatch.md` — 10+ test cases

**Your integration tasks:**

### Task 1: Implement orchestrator.py in manta-hub

**Location**: `manta-hub/maestro/orchestrator.py`  
**Reference**: Copy from `docs/ORCHESTRATOR-IMPLEMENTATION-GUIDE.md` Part 2 (code is complete)

```python
# Already have in guide:
# - OrchestratorInput/Output dataclasses
# - MaestroOrchestrator class with orchestrate() method
# - System prompt building
# - Response parsing
# - Quality scoring

# Just copy and integrate into your codebase
```

### Task 2: Integrate with maestro router

**Location**: `manta-hub/maestro/router.py`  
**Changes needed**:

```python
from orchestrator import MaestroOrchestrator, OrchestratorInput

class MaestroRouter:
    def __init__(self):
        self.orchestrator = MaestroOrchestrator()
        # ... existing code

    def route_and_respond(self, user_prompt: str) -> str:
        # 1. Score all agents (existing logic)
        scores = self._score_agents(user_prompt)
        
        # 2. Check ambiguity: score_gap < 0.10 (10 percentage points)
        primary_agent = max(scores, key=scores.get)
        secondary_agent = max(
            (a for a in scores if a != primary_agent),
            key=scores.get,
            default=None
        )
        score_gap = scores[primary_agent] - scores[secondary_agent]

        is_ambiguous = score_gap < 0.10

        if is_ambiguous and secondary_agent:
            # 3. AMBIGUOUS: dispatch both agents
            primary_response = self._dispatch(primary_agent, user_prompt)
            secondary_response = self._dispatch(secondary_agent, user_prompt)

            # 4. Orchestrate
            orch_input = OrchestratorInput(
                user_prompt=user_prompt,
                primary_agent=primary_agent,
                primary_response=primary_response,
                secondary_agent=secondary_agent,
                secondary_response=secondary_response,
                routing_scores=scores,
                ambiguity_reason=f"Gap: {score_gap:.2f} < 0.10",
            )
            orch_output = self.orchestrator.orchestrate(orch_input)

            # 5. Log orchestration event
            self._log_orchestration(
                user_prompt,
                primary_agent,
                secondary_agent,
                orch_output.confidence,
            )

            return orch_output.merged_response

        else:
            # NOT AMBIGUOUS: normal routing
            return self._dispatch(primary_agent, user_prompt)
```

### Task 3: Create Test Cases

**Location**: `manta-hub/tests/test_orchestrator.py`  
**Reference**: Copy from `tests/routing/test_multiagent_dispatch.md`

Test cases are already documented with 10+ real-world scenarios:
- UHE + CFRD + LT (barragens + energia)
- ETE + subestação (saneamento + energia)
- Porto + aeroporto (portos + aeroportos)
- Etc.

```python
import pytest
from maestro.orchestrator import MaestroOrchestrator, OrchestratorInput

def test_uhe_cfrd_lte_orchestration():
    """Test UHE + CFRD + LT tie-breaking."""
    
    orch = MaestroOrchestrator()
    
    input_data = OrchestratorInput(
        user_prompt="Design UHE with CFRD 100m + LT 500kV",
        primary_agent="agente-barragens",
        primary_response="[CFRD design...]",
        secondary_agent="agente-energia",
        secondary_response="[LT routing...]",
        routing_scores={
            "agente-barragens": 0.95,
            "agente-energia": 0.88,
        },
        ambiguity_reason="Gap 0.07 < 0.10",
    )
    
    output = orch.orchestrate(input_data)
    
    # Assertions
    assert "Responsabilidade Primária" in output.merged_response
    assert "Cross-Concerns" in output.merged_response
    assert len(output.cross_concerns) >= 2
    assert output.confidence >= 0.75
```

### Task 4: Database Schema Integration

**Location**: Supabase  
**Tables needed**: Already defined in migrations

```sql
-- Already exists from Phase 1 migrations:
-- maestro_routing_trace — logs all routing decisions

-- Add columns for orchestration tracking:
ALTER TABLE maestro_routing_trace
ADD COLUMN IF NOT EXISTS is_ambiguous BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS orchestrator_confidence FLOAT,
ADD COLUMN IF NOT EXISTS orchestrator_recommendation TEXT;
```

### Task 5: Monitoring & Metrics

```python
# Monitor orchestration effectiveness
def get_orchestration_metrics(days: int = 7) -> Dict:
    """Get orchestration performance metrics."""
    
    # Orchestration rate (% of queries that trigger orchestration)
    orchestration_rate = (
        select count(*)
        from maestro_routing_trace
        where is_ambiguous = true
          and created_at > now() - interval '{days} days'
    ) / (
        select count(*)
        from maestro_routing_trace
        where created_at > now() - interval '{days} days'
    )
    
    # Average confidence
    avg_confidence = (
        select avg(orchestrator_confidence)
        from maestro_routing_trace
        where is_ambiguous = true
    )
    
    return {
        "orchestration_rate": orchestration_rate,  # Target: 5-10%
        "avg_confidence": avg_confidence,          # Target: >0.75
        "period_days": days,
    }
```

---

## Phase 2.3 — Document Auto-Classification (Cowork Team)

### Overview

When documents are uploaded to SharePoint, they should be automatically classified and suggested to the appropriate agent.

**Specification provided**: `docs/DOCUMENT-AUTO-CLASSIFICATION.md`

**Your integration tasks:**

### Task 1: Implement MCP Listener

**Type**: Webhook listener for SharePoint upload events  
**Trigger**: Document uploaded to `03_Projetos/` folder

```python
# maestro-listeners/sharepoint_document_listener.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging

app = FastAPI()
logger = logging.getLogger(__name__)

class SharePointUploadEvent(BaseModel):
    file_name: str
    file_url: str
    folder_path: str
    uploaded_by: str
    upload_time: str

@app.post("/webhook/sharepoint/document-uploaded")
async def handle_document_upload(event: SharePointUploadEvent):
    """Handle SharePoint document upload."""
    
    # 1. Extract metadata
    metadata = DocumentClassifier.extract_metadata(event.file_url)
    
    # 2. Classify via Maestro
    classification = DocumentClassifier.classify(metadata)
    
    # 3. Notify user in Cowork
    notification = await notify_user_in_cowork(
        title=f"📄 {event.file_name}",
        message=f"Classified as {classification.suggested_agent}",
        actions=[
            {"label": "Concordar e mover", "action": "approve"},
            {"label": "Discordar", "action": "reject"},
            {"label": "Revisar manualmente", "action": "escalate"},
        ],
        user_id=event.uploaded_by,
    )
    
    # 4. Wait for user response
    response = await notification.wait_for_response(timeout_seconds=3600)
    
    # 5. Execute action
    if response.action == "approve":
        # Move file in SharePoint
        move_file_in_sharepoint(
            event.file_url,
            f"03_Projetos/{classification.suggested_agent_segment}/"
        )
        # Record feedback
        record_feedback(
            approved=True,
            agent=classification.suggested_agent,
            document=event.file_name,
        )
    elif response.action == "reject":
        # Record feedback (rejection)
        record_feedback(
            approved=False,
            agent=classification.suggested_agent,
            document=event.file_name,
            correct_agent=response.selected_agent,
        )
    
    return {"status": "processed", "action": response.action}
```

### Task 2: Implement DocumentClassifier

```python
# maestro-listeners/document_classifier.py

from typing import Dict, Optional
import fitz  # PyMuPDF for PDF
from PIL import Image
import pytesseract
import logging

logger = logging.getLogger(__name__)

class DocumentClassifier:
    """Classify documents to appropriate agents."""
    
    @staticmethod
    def extract_metadata(file_url: str) -> Dict:
        """Extract text and metadata from document."""
        
        # Download file
        response = requests.get(file_url)
        
        # Detect file type
        if file_url.endswith('.pdf'):
            text = DocumentClassifier._extract_pdf(response.content)
        elif file_url.endswith('.docx'):
            text = DocumentClassifier._extract_docx(response.content)
        elif file_url.endswith('.xlsx'):
            text = DocumentClassifier._extract_xlsx(response.content)
        elif file_url.endswith(('.png', '.jpg', '.jpeg')):
            text = DocumentClassifier._extract_image(response.content)
        else:
            text = ""
        
        return {
            "filename": file_url.split('/')[-1],
            "content_sample": text[:1000],  # First 1000 chars
            "content_length": len(text),
            "file_type": file_url.split('.')[-1],
        }
    
    @staticmethod
    def classify(metadata: Dict) -> Dict:
        """Route metadata through Maestro router."""
        
        # Build routing prompt from metadata
        routing_prompt = f"""
Document: {metadata['filename']}
Content preview:
{metadata['content_sample']}

Which infrastructure agent should handle this document?
- agente-saneamento (ETA, ETE, adução)
- agente-energia (LT, subestações)
- agente-portos (dragagem, cais)
- agente-aeroportos (pistas, TPS)
- agente-barragens (CFRD, rejeitos)
"""
        
        # Call Maestro router
        result = maestro_router.route_and_respond(routing_prompt)
        
        return {
            "suggested_agent": result["agent"],
            "confidence": result["confidence"],
            "suggested_agent_segment": classify_segment(result["agent"]),
        }
    
    @staticmethod
    def _extract_pdf(content: bytes) -> str:
        """Extract text from PDF."""
        pdf = fitz.open(stream=content, filetype="pdf")
        text = ""
        for page in pdf:
            text += page.get_text()
        return text
    
    @staticmethod
    def _extract_docx(content: bytes) -> str:
        """Extract text from DOCX."""
        from docx import Document
        import io
        doc = Document(io.BytesIO(content))
        return "\n".join([p.text for p in doc.paragraphs])
    
    @staticmethod
    def _extract_xlsx(content: bytes) -> str:
        """Extract text from XLSX."""
        import openpyxl
        import io
        wb = openpyxl.load_workbook(io.BytesIO(content))
        text = ""
        for sheet in wb.sheetnames:
            ws = wb[sheet]
            for row in ws.iter_rows(values_only=True):
                text += " ".join(str(v) for v in row if v) + "\n"
        return text
    
    @staticmethod
    def _extract_image(content: bytes) -> str:
        """Extract text from image via OCR."""
        import io
        image = Image.open(io.BytesIO(content))
        return pytesseract.image_to_string(image)

def classify_segment(agent_slug: str) -> str:
    """Map agent to SharePoint segment."""
    mapping = {
        "agente-saneamento": "Saneamento",
        "agente-energia": "Energia",
        "agente-portos": "Portos",
        "agente-aeroportos": "Aeroportos",
        "agente-barragens": "Barragens",
    }
    return mapping.get(agent_slug, "Projetos")
```

### Task 3: Cowork Notification Integration

```python
# Integrate with Cowork's notification system

async def notify_user_in_cowork(
    title: str,
    message: str,
    actions: List[Dict],
    user_id: str,
) -> Notification:
    """Send classification notification to user in Cowork."""
    
    # Create notification in Cowork via MCP
    cowork_client = CoworkClient()
    
    notification = await cowork_client.create_notification(
        user_id=user_id,
        title=title,
        message=message,
        type="document_classification",
        actions=actions,
        metadata={
            "source": "maestro_document_classifier",
            "timestamp": datetime.utcnow().isoformat(),
        }
    )
    
    return notification
```

### Task 4: Recording Feedback

```python
# Feed classification decisions back to feedback loop

def record_feedback(
    approved: bool,
    agent: str,
    document: str,
    correct_agent: Optional[str] = None,
):
    """Record document classification feedback."""
    
    supabase.table('maestro_user_feedback').insert({
        'prompt': document,  # Document filename as proxy
        'routed_agent': agent,
        'correct_agent': correct_agent or agent,
        'confidence': 4,  # Classification confidence
        'approved': approved,
        'timestamp': datetime.utcnow(),
        'feedback_type': 'document_classification',
    }).execute()
```

---

## Success Criteria

### Phase 2.1 (Cowork Team)
- [ ] "Was this correct?" button appears after agent response
- [ ] Feedback entries recorded in maestro_user_feedback table
- [ ] Weekly analysis job runs every Monday 9 AM
- [ ] GitHub issues created for agents with <85% approval
- [ ] Team trained on feedback loop

### Phase 2.2 (Maestro Team / manta-hub)
- [ ] orchestrator.py implemented and integrated
- [ ] Score gap detection (<0.10) triggers orchestration
- [ ] 10+ test cases pass (from test_multiagent_dispatch.md)
- [ ] Orchestration rate: 5-10% of queries
- [ ] Merge quality score: >0.75 average
- [ ] Logging enabled to maestro_routing_trace

### Phase 2.3 (Cowork Team)
- [ ] MCP listener running for SharePoint uploads
- [ ] DocumentClassifier extracts text from PDF/DOCX/XLSX/images
- [ ] Classification notifications appear in Cowork UI
- [ ] File movement works (approve action)
- [ ] Feedback recorded for classification decisions
- [ ] Classification accuracy: >80%

---

## Timeline

- **Aug 01-09**: Phase 2.4 & 2.5 deployment (production)
- **Aug 10-31**: Phase 2.1, 2.2, 2.3 integration (parallel)
- **Sep 01-15**: Integration testing + fixes
- **Sep 15+**: All Phase 2 workstreams operational

---

**Owner**: Team leads (Cowork, Maestro, DevOps)  
**Status**: Specifications ready, awaiting implementation  
**Support**: Reference implementation guides in `/docs/` directory
