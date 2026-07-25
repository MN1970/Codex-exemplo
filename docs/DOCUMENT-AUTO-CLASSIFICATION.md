# Document Auto-Classification — Phase 2.3

**Phase**: 2.3 (Sep 01 - Sep 15)  
**Goal**: Automatically classify uploaded documents and route to correct agent  
**Owner**: Cowork integration + Claude Code  
**Status**: 🔨 Design phase

---

## Overview

When a user uploads a PDF/DWG to SharePoint `03_Projetos/`, automatically:
1. Extract metadata + summarize content
2. Route through Maestro classifier (Manta 00)
3. Suggest correct agent + destination folder
4. User approves in Cowork → file moves/copies automatically
5. Record user approval as feedback signal (→ learning loop)

---

## Flow Diagram

```
┌─────────────────────────────────────────┐
│  User uploads file to SharePoint        │
│  03_Projetos/Nova-Pasta/design.pdf      │
└────────────────┬────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│  SharePoint Webhook / MCP Listener      │
│  Trigger: file uploaded                 │
└────────────────┬────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│  Extract Metadata & Summarize           │
│  - OCR / text extraction                │
│  - Summary (first 500 tokens)           │
│  - File type, size, owner               │
└────────────────┬────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│  Maestro Routing                        │
│  Input: document summary                │
│  Output: suggested_agent, confidence    │
│  (uses existing routing keywords)       │
└────────────────┬────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│  Cowork Notification                    │
│  "Document classified as S8 (Saneamento)│
│   Move to 03_Projetos/Saneamento/?      │
│   [Agree] [Disagree] [Manual review]"   │
└────────────────┬────────────────────────┘
         ┌───────┴────────┬───────────┬──────────┐
         ↓                ↓           ↓          ↓
      [Agree]          [Disagree]  [Manual]  [Cancel]
         ↓                ↓           ↓          ↓
    Move file       Record feedback Escalate  No action
    to folder       to ML loop       to human   (leave in place)
         ↓                ↓           ↓          ↓
    Update metadata  Update routing  Archive   
    Record approval   keywords         in temp
    in feedback table               folder
         ↓                ↓           ↓
    Return to user  Notify admin  Notify admin
    "✅ Moved"      "Need review"  "Manual needed"
```

---

## Implementation Details

### 1. Document Metadata Extraction

```python
# scripts/classify_document.py

class DocumentClassifier:
    def extract_metadata(file_path: str) -> DocumentMetadata:
        """Extract text, metadata, and summary from file."""
        
        # A. Text extraction
        if file_path.endswith('.pdf'):
            text = extract_pdf_text(file_path)
        elif file_path.endswith('.dwg'):
            text = extract_dwg_metadata(file_path)  # title blocks, layers
        elif file_path.endswith(('.docx', '.xlsx')):
            text = extract_office_text(file_path)
        else:
            text = ""
        
        # B. Summarize for routing
        summary = summarize_for_routing(text[:2000])  # first 2000 chars
        
        # C. Extract keywords
        keywords = extract_keywords(text)
        
        return DocumentMetadata(
            filename=file_path.split('/')[-1],
            file_size_mb=os.path.getsize(file_path) / 1e6,
            extracted_text=text,
            summary=summary,
            keywords=keywords,
            uploaded_by=metadata.owner,
            uploaded_at=datetime.utcnow(),
        )

    def classify(metadata: DocumentMetadata) -> ClassificationResult:
        """Route document through Maestro."""
        
        # Call Maestro with summary + keywords
        prompt = f"""
        Documento: {metadata.filename}
        Resumo: {metadata.summary}
        Palavras-chave: {', '.join(metadata.keywords)}
        
        Qual agente da Manta está mais indicado?
        Responda APENAS: agente-<segmento>
        """
        
        response = maestro_route(prompt)
        agent = parse_agent_slug(response)
        
        # Look up folder mapping
        folder_mapping = {
            'agente-saneamento': '03_Projetos/Saneamento',
            'agente-energia': '03_Projetos/Energia',
            'agente-portos': '03_Projetos/Portos',
            'agente-aeroportos': '03_Projetos/Aeroportos',
            'agente-barragens': '03_Projetos/Barragens',
        }
        
        return ClassificationResult(
            suggested_agent=agent,
            suggested_folder=folder_mapping.get(agent),
            confidence=0.85,  # from maestro routing score
            reasoning=f"Matched keywords: {metadata.keywords[:3]}",
        )
```

### 2. Cowork Integration

```python
# Cowork sends this notification to user:

def notify_user_classification(file_path: str, classification: ClassificationResult):
    """Notify user in Cowork; ask for approval."""
    
    notification = {
        "type": "document_classification",
        "title": f"📄 {file_path.split('/')[-1]}",
        "message": f"""
Documento classificado como:
**{classification.suggested_agent}** ({classification.confidence:.0%} confiança)

Motivo: {classification.reasoning}

Mover para **{classification.suggested_folder}**?
        """,
        "actions": [
            {"label": "Concordar e mover", "action": "approve", "variant": "primary"},
            {"label": "Discordar", "action": "reject", "variant": "secondary"},
            {"label": "Revisar manualmente", "action": "escalate", "variant": "tertiary"},
        ],
    }
    
    # Send to Cowork UI
    cowork.notify(user_id, notification)
    
    # Wait for user response (webhook callback)
    response = await cowork.wait_for_response(notification.id, timeout=3600)
    
    return response
```

### 3. Post-Approval Actions

```python
def process_classification_response(file_path: str, response: ApprovalResponse):
    """Handle user approval/rejection."""
    
    if response.action == "approve":
        # Move file to suggested folder
        destination = response.suggested_folder
        sharepoint_move(file_path, destination)
        
        # Update metadata
        update_sharepoint_metadata(destination, {
            "maestro_agent": response.agent,
            "maestro_confidence": response.confidence,
            "classification_approved": True,
            "classification_timestamp": datetime.utcnow(),
        })
        
        # Record positive feedback (learning loop)
        insert_maestro_user_feedback({
            "prompt": response.document_summary,
            "routed_agent": response.agent,
            "correct_agent": response.agent,  # user approved!
            "confidence": 5,  # max confidence
            "feedback_type": "document_classification_approval",
            "document_id": file_path,
        })
        
        return {"status": "moved", "folder": destination}
    
    elif response.action == "reject":
        # Record negative feedback
        insert_maestro_user_feedback({
            "prompt": response.document_summary,
            "routed_agent": response.suggested_agent,
            "correct_agent": response.correct_agent,  # user's choice
            "confidence": 1,  # low confidence (wrong choice)
            "feedback_type": "document_classification_rejection",
            "document_id": file_path,
            "notes": f"Corrected to {response.correct_agent}",
        })
        
        # Move to correct folder
        destination = folder_mapping[response.correct_agent]
        sharepoint_move(file_path, destination)
        
        return {"status": "moved_corrected", "folder": destination}
    
    elif response.action == "escalate":
        # Move to temp review folder
        sharepoint_move(file_path, "03_Projetos/_Review")
        
        # Notify admin for manual review
        notify_admin_manual_review(file_path, response.suggested_agent)
        
        return {"status": "escalated_for_review"}
```

### 4. MCP Listener / Webhook Handler

```python
# Part of Cowork listener; triggered on file upload

@app.webhook('/sharepoint/on_document_uploaded')
async def handle_document_upload(event: SharePointEvent):
    """
    Webhook from SharePoint OneDrive:
    - File uploaded to 03_Projetos/
    - Trigger classification pipeline
    """
    
    file_path = event.file_path
    
    # Skip if file already classified
    if has_classification_metadata(file_path):
        return {"status": "already_classified"}
    
    # Extract metadata
    metadata = DocumentClassifier.extract_metadata(file_path)
    
    # Classify
    classification = DocumentClassifier.classify(metadata)
    
    # Notify user
    user_response = await notify_user_classification(file_path, classification)
    
    # Process response
    result = process_classification_response(file_path, user_response)
    
    return result
```

---

## Integration with Feedback Loop

Classification approvals/rejections feed directly into maestro_user_feedback:

```sql
-- Weekly query: documents classified correctly
SELECT
  COUNT(*) as total_classifications,
  SUM(CASE WHEN correct_agent = routed_agent THEN 1 ELSE 0 END) as correct,
  ROUND(100.0 * SUM(CASE WHEN correct_agent = routed_agent THEN 1 ELSE 0 END) / COUNT(*), 1) as approval_rate
FROM maestro_user_feedback
WHERE feedback_type = 'document_classification_approval'
  AND classification_timestamp > now() - interval '7 days'
GROUP BY routed_agent
ORDER BY approval_rate DESC;
```

---

## Deployment Checklist

- [ ] Implement `DocumentClassifier` class
- [ ] Add MCP listener in Cowork (SharePoint upload webhook)
- [ ] Create folder mapping in `.claude/agents/*` metadata
- [ ] Integrate notification UI in Cowork (approve/reject buttons)
- [ ] Test with 5-10 sample documents
- [ ] Deploy to staging
- [ ] Configure SharePoint webhook URL
- [ ] Monitor approval rate (target: >80%)
- [ ] Iterate on keywords if approval rate < 75%

---

## Success Metrics

| Metric | Target | How Measured |
|--------|--------|--------------|
| **Classification Accuracy** | >80% | user_approval_rate in maestro_user_feedback |
| **Auto-Move Success** | >90% | documents successfully moved / total classified |
| **User Adoption** | >50% of uploads | percentage of 03_Projetos uploads with approval signal |
| **Latency** | <5s | time from upload to notification in Cowork |
| **Escalation Rate** | <10% | manual review / total classified |

---

## Roadmap Integration

- **Phase 2.3** (Sep 01-15): Implement core pipeline + Cowork integration
- **Phase 2.4** (Sep 16-30): Use classification signals to auto-ingest docs into RAG
- **Phase 2.5** (Oct 01-15): Auto-sync classified docs to SharePoint structure

---

**Last Updated**: 2026-07-26  
**Status**: Ready for implementation  
**Owner**: Cowork team (listener) + Claude Code (classifier)
