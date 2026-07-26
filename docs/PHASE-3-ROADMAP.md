# PHASE 3: Extension & Ecosystem (12-month roadmap)

**Period**: Aug 26, 2026 - Aug 26, 2027 | **Status**: 📋 Planning Phase  
**Objective**: Transform Maestro into open ecosystem with public API, regulatory webhooks, conversation features, and compliance infrastructure

---

## 📋 Overview

PHASE 3 activates ecosystem integration, allowing external partners, regulatory bodies, and internal teams to interact with Maestro via standardized APIs.

| Workstream | Deliverables | Timeline | Owner |
|-----------|--------------|----------|-------|
| **3.1** Public API | REST endpoint, OpenAPI spec, SDK | Sep 01 - Sep 30 | Claude Code |
| **3.2** Regulatory Webhooks | ANEEL, ANTAQ, ANA, ANAC listeners | Oct 01 - Nov 15 | DevOps + Claude Code |
| **3.3** Conversation API | Multi-turn sessions, context management | Nov 16 - Dec 31 | Maestro agents |
| **3.4** Agent Persona Sync | AskCAD integration, auto-update | Jan 01 - Jan 31 | Cowork + Claude Code |
| **3.5** Advanced Routing | LLM-assisted disambiguation | Feb 01 - Feb 28 | Maestro team |
| **3.6** Audit & Compliance | Dashboard, GDPR-ready logs | Mar 01 - Mar 31 | Security + DevOps |

---

## 3.1 — Maestro Public API (Sep 01 - Sep 30)

### Goal
External partners (Manta subsidiaries, consultants, integrators) can call Maestro for routing decisions without replicating keywords locally.

### API Endpoints

#### Route Decision
```
POST /api/v1/maestro/route
Content-Type: application/json

{
  "prompt": "Preciso projetar uma ETA de 200 mil hab",
  "context": {
    "segment": "saneamento",  // optional hint
    "session_id": "sess_123",
    "metadata": {}
  }
}

Response:
{
  "primary_agent": "agente-saneamento",
  "primary_score": 0.92,
  "alternatives": [
    {
      "agent": "agente-energia",
      "score": 0.78,
      "reason": "mentions subestação"
    }
  ],
  "orchestrated": false,  // was ambiguous → 2+ agents?
  "explanation": "Strong saneamento match on ETA keywords",
  "confidence": 0.92,
  "processing_time_ms": 145,
  "version": "v4.2",
  "timestamp": "2026-09-01T14:23:45Z"
}
```

#### Ask Agent
```
POST /api/v1/maestro/ask
Content-Type: application/json

{
  "agent_slug": "agente-saneamento",
  "message": "How do I design an ETA for 200k people?",
  "context": {
    "segment": "saneamento",
    "session_id": "sess_123",
    "conversation_history": []  // for multi-turn
  }
}

Response:
{
  "response": "[streaming or chunked response from agent]",
  "agent": "agente-saneamento",
  "model": "claude-sonnet-4-20250514",
  "usage": {
    "input_tokens": 450,
    "output_tokens": 1200
  },
  "processing_time_ms": 2300,
  "confidence": 0.88,
  "timestamp": "2026-09-01T14:24:10Z"
}
```

#### Batch Route
```
POST /api/v1/maestro/batch/route
Content-Type: application/json

{
  "prompts": [
    "Preciso projetar ETA",
    "CFRD de 100m de altura",
    "LT 500kV até SE"
  ]
}

Response:
{
  "results": [
    {
      "prompt": "Preciso projetar ETA",
      "agent": "agente-saneamento",
      "confidence": 0.92
    },
    // ... more results
  ],
  "batch_id": "batch_xyz",
  "processed": 3,
  "failed": 0,
  "processing_time_ms": 450
}
```

### Authentication
```
Bearer token-based (OAuth2 Client Credentials)

Headers:
Authorization: Bearer sk-live_xxxxxx
X-API-Key: (alternative basic auth)

Rate Limit:
- Free tier: 100 req/month
- Professional: 10,000 req/month
- Enterprise: Custom
```

### OpenAPI Spec
```yaml
openapi: 3.0.0
info:
  title: Maestro Routing API
  version: 1.0.0
  description: Manta Associados intelligent agent routing

servers:
  - url: https://api.maestro.manta.com/v1
    description: Production

paths:
  /maestro/route:
    post:
      summary: Route query to best agent
      operationId: routeQuery
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/RouteRequest'
      responses:
        '200':
          description: Routing decision
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/RouteResponse'
        '400':
          description: Invalid request
        '401':
          description: Unauthorized
        '429':
          description: Rate limited

  /maestro/ask:
    post:
      summary: Ask specific agent question
      operationId: askAgent
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/AskRequest'
      responses:
        '200':
          description: Agent response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/AskResponse'

components:
  schemas:
    RouteRequest:
      type: object
      required: [prompt]
      properties:
        prompt:
          type: string
          description: User query
        context:
          type: object
          properties:
            segment:
              type: string
              enum: [saneamento, energia, portos, aeroportos, barragens]
            session_id:
              type: string

    RouteResponse:
      type: object
      properties:
        primary_agent:
          type: string
        primary_score:
          type: number
          format: float
        alternatives:
          type: array
          items:
            type: object
        orchestrated:
          type: boolean
        confidence:
          type: number
          format: float
        processing_time_ms:
          type: integer
        timestamp:
          type: string
          format: date-time
```

### SDK (Python)
```python
# pip install maestro-sdk

from maestro import MaestroClient

client = MaestroClient(
    api_key="sk-live_xxxxxx",
    base_url="https://api.maestro.manta.com/v1"
)

# Route decision
result = client.route(
    prompt="Preciso projetar uma ETA",
    segment="saneamento"
)
print(f"Best agent: {result.primary_agent} ({result.confidence:.0%})")

# Ask agent
response = client.ask(
    agent="agente-saneamento",
    message="How do I design an ETA for 200k people?",
    session_id="sess_123"
)
print(response.text)

# Batch route
results = client.batch_route([
    "ETA design",
    "CFRD 100m",
    "LT 500kV"
])
```

### Deliverables (3.1)
- [ ] FastAPI server (`maestro/api/v1/server.py`)
- [ ] Route/Ask/Batch endpoints
- [ ] Authentication (Bearer token + rate limiting)
- [ ] OpenAPI/Swagger docs at `/docs`
- [ ] Python SDK (`maestro-sdk` package on PyPI)
- [ ] Usage metrics dashboard
- [ ] Pricing tiers + billing integration
- [ ] Partner onboarding guide

---

## 3.2 — Regulatory Webhooks (Oct 01 - Nov 15)

### Goal
Automatically ingest regulatory updates (ANEEL, ANTAQ, ANA, ANAC) and trigger RAG updates + agent notifications.

### Webhook Listeners

#### ANEEL (Agência Nacional de Energia Elétrica)
```
Monitored sources:
- ANEEL Editais: https://www.aneel.gov.br/editais
- Resoluções Normativas (R1-R5)
- ONS procedures
- EPE studies

On update:
1. Download new document
2. OCR + extract text
3. Generate embeddings
4. Insert to rag_chunks (collection: energia)
5. Notify agente-energia: "Nova norma ANEEL R6 publicada"
```

#### ANTAQ (Agência Nacional de Transportes Aquaviários)
```
Monitored sources:
- ANTAQ Resoluções: https://www.antaq.gov.br
- Port authority updates
- Leilão announcements

On update:
1. Extract resolution text
2. Ingest to RAG (collection: portos)
3. Notify agente-portos: "Resolução ANTAQ 2026/001 publicada"
```

#### ANA (Agência Nacional de Águas)
```
Monitored sources:
- ANA norms: https://www.ana.gov.br
- Water quality standards
- Dam safety bulletins (SIGBM)
- Hydrological forecasts

On update:
1. Process bulletin
2. Ingest to RAG (saneamento + barragens)
3. Notify both agents
```

#### ANAC (Agência Nacional de Aviação Civil)
```
Monitored sources:
- ANAC RBAC: https://www.anac.gov.br
- Safety bulletins
- NOTAM updates (high-frequency)

On update:
1. Process safety bulletin
2. Ingest to RAG (aeroportos)
3. Notify agente-aeroportos
```

### Implementation

```python
# scripts/regulatory_webhook_listener.py

import asyncio
from datetime import datetime
from supabase import create_client

class RegulatoryListener:
    def __init__(self):
        self.sources = {
            'aneel': 'https://www.aneel.gov.br/api/editais',
            'antaq': 'https://www.antaq.gov.br/api/resolucoes',
            'ana': 'https://www.ana.gov.br/api/normas',
            'anac': 'https://www.anac.gov.br/api/rbac',
        }
        self.supabase = create_client(...)

    async def poll_all_sources(self):
        """Poll all regulatory sources every 6 hours."""
        tasks = [
            self.poll_aneel(),
            self.poll_antaq(),
            self.poll_ana(),
            self.poll_anac(),
        ]
        results = await asyncio.gather(*tasks)
        return results

    async def poll_aneel(self):
        """Check ANEEL for new editais/resoluções."""
        # 1. Fetch from ANEEL API
        documents = await self.fetch_aneel_documents()
        
        # 2. Check if new (vs maestro_regulatory_updates table)
        new_docs = [d for d in documents 
                    if not self.is_in_database(d['id'], 'aneel')]
        
        # 3. For each new doc:
        for doc in new_docs:
            # Extract text
            text = await extract_pdf(doc['url'])
            
            # Generate embedding
            embedding = await self.embedder.embed(text[:2000])
            
            # Insert to RAG
            self.supabase.table('rag_chunks').insert({
                'collection_slug': 'energia',
                'content': text,
                'source_file': f"ANEEL_{doc['id']}",
                'source_url': doc['url'],
                'tier': 'T1',
                'metadata': {
                    'regulatory_source': 'aneel',
                    'document_id': doc['id'],
                    'published_date': doc['date'],
                    'document_type': 'Edital' if 'edital' in doc['title'].lower() else 'Resolução',
                }
            }).execute()
            
            # Notify agent
            await self.notify_agent(
                agent_slug='agente-energia',
                message=f"Novo ANEEL {doc['type']}: {doc['title']}",
                document_url=doc['url'],
                priority='high' if 'emergência' in doc.get('tags', []) else 'normal',
            )
            
            # Record in update log
            self.supabase.table('maestro_regulatory_updates').insert({
                'source': 'aneel',
                'document_id': doc['id'],
                'title': doc['title'],
                'published_date': doc['date'],
                'ingested_at': datetime.utcnow(),
                'agents_notified': ['agente-energia'],
                'rag_chunks_created': 1,
            }).execute()

    async def notify_agent(self, agent_slug, message, document_url, priority):
        """Send notification to agent in Cowork."""
        notification = {
            "agent_slug": agent_slug,
            "type": "regulatory_update",
            "priority": priority,
            "title": f"📋 Regulatory Update: {message}",
            "body": f"New regulatory document available: {document_url}",
            "action_url": document_url,
            "timestamp": datetime.utcnow(),
        }
        
        # Send via Cowork MCP
        await cowork.notify_agent(notification)
```

### Dashboard

```sql
-- maestro_regulatory_updates table

CREATE TABLE maestro_regulatory_updates (
  id BIGINT PRIMARY KEY,
  source TEXT NOT NULL,  -- aneel, antaq, ana, anac
  document_id TEXT UNIQUE NOT NULL,
  title TEXT NOT NULL,
  published_date DATE,
  ingested_at TIMESTAMPTZ DEFAULT now(),
  agents_notified TEXT[] DEFAULT ARRAY[]::TEXT[],
  rag_chunks_created INT DEFAULT 0,
  impact_score INT DEFAULT 0,  -- 1-10 how impactful?
  tags TEXT[] DEFAULT ARRAY[]::TEXT[],  -- urgent, safety, finance, etc
  UNIQUE(source, document_id)
);

-- View: Recent regulatory updates
SELECT
  source,
  COUNT(*) as updates_this_month,
  MAX(published_date) as latest_update,
  STRING_AGG(DISTINCT agents_notified::TEXT, ', ') as agents_affected
FROM maestro_regulatory_updates
WHERE published_date > now() - interval '30 days'
GROUP BY source
ORDER BY COUNT(*) DESC;
```

### Deliverables (3.2)
- [ ] `scripts/regulatory_webhook_listener.py` (ANEEL, ANTAQ, ANA, ANAC)
- [ ] `.github/workflows/poll-regulatory-updates.yml` (6-hourly cron)
- [ ] `maestro_regulatory_updates` table (tracking)
- [ ] Agent notification system (Cowork integration)
- [ ] Impact scoring (which updates affect which agents)
- [ ] Regulatory update dashboard
- [ ] Audit trail for compliance

---

## 3.3 — Conversation API (Nov 16 - Dec 31)

### Goal
Support multi-turn conversations with context preservation. Users ask follow-up questions without repeating context.

### Session Management

```python
@app.post('/api/v1/maestro/sessions')
def create_session(user_id: str, segment: str = None):
    """Create new conversation session."""
    session = {
        'session_id': f"sess_{uuid.uuid4()}",
        'user_id': user_id,
        'segment': segment,
        'created_at': datetime.utcnow(),
        'turns': [],  # conversation history
        'context': {}  # accumulated context
    }
    supabase.table('maestro_conversations').insert(session).execute()
    return session

@app.post('/api/v1/maestro/sessions/{session_id}/messages')
def send_message(session_id: str, message: str, agent_slug: str = None):
    """Send message in session."""
    
    # 1. Fetch session + history
    session = supabase.table('maestro_conversations').select('*').eq('session_id', session_id).execute()
    
    # 2. Build context from previous turns
    context_text = "\n".join([
        f"User: {turn['user_message']}\nAgent: {turn['agent_response'][:500]}..."
        for turn in session.turns[-5:]  # Last 5 turns for context window
    ])
    
    # 3. If no agent specified, route the message
    if not agent_slug:
        routing = maestro.route(message, context=context_text)
        agent_slug = routing['primary_agent']
    
    # 4. Call agent with context
    full_prompt = f"""
Previous conversation:
{context_text}

User's new question: {message}
"""
    
    response = dispatch_agent(agent_slug, full_prompt)
    
    # 5. Store turn in conversation history
    turn = {
        'session_id': session_id,
        'turn_number': len(session.turns) + 1,
        'agent_slug': agent_slug,
        'user_message': message,
        'agent_response': response,
        'timestamp': datetime.utcnow(),
    }
    
    supabase.table('maestro_conversation_turns').insert(turn).execute()
    
    # 6. Update session context
    supabase.table('maestro_conversations').update({
        'context': {
            'last_agent': agent_slug,
            'message_count': len(session.turns) + 1,
            'last_updated': datetime.utcnow(),
        }
    }).eq('session_id', session_id).execute()
    
    return {
        'session_id': session_id,
        'agent': agent_slug,
        'response': response,
        'turn_number': len(session.turns) + 1,
    }

@app.get('/api/v1/maestro/sessions/{session_id}')
def get_session(session_id: str):
    """Retrieve conversation history."""
    
    session = supabase.table('maestro_conversations').select('*').eq('session_id', session_id).execute()
    turns = supabase.table('maestro_conversation_turns').select('*').eq('session_id', session_id).order('turn_number').execute()
    
    return {
        'session': session,
        'turns': turns,
        'conversation_count': len(turns),
    }
```

### Vector Context Retrieval

```python
# When context gets long, use vector similarity to find relevant previous turns

def get_context_for_message(session_id: str, new_message: str, max_tokens: int = 2000):
    """Retrieve most relevant previous turns via vector similarity."""
    
    # 1. Embed new message
    new_embedding = embedder.embed(new_message)
    
    # 2. Search previous turns by semantic similarity
    similar_turns = supabase.rpc('search_session_context', {
        'session_id': session_id,
        'query_embedding': new_embedding,
        'limit': 3,
    }).execute()
    
    # 3. Build context from top similar turns
    context = "\n".join([
        f"[Previous context]\nUser: {turn['user_message']}\nAgent: {turn['agent_response'][:300]}..."
        for turn in similar_turns['data']
    ])
    
    return context
```

### Deliverables (3.3)
- [ ] Session table: `maestro_conversations` + `maestro_conversation_turns`
- [ ] `/sessions` CRUD endpoints
- [ ] `/sessions/{id}/messages` send message endpoint
- [ ] Context window management (last N turns)
- [ ] Vector similarity for relevant context retrieval
- [ ] Session export (PDF/JSON conversation export)
- [ ] Multi-agent conversation handling (agent can change per turn)

---

## 3.4 — Agent Persona Sync (Jan 01 - Jan 31)

### Goal
Sync agent definitions from `.claude/agents/*.md` to AskCAD personas automatically. Personas always stay in sync with codebase.

### Flow

```
PR merged to main (changes to .claude/agents/*.md)
  ↓
GitHub Actions trigger
  ↓
Extract agent metadata from .md
  ↓
Call AskCAD API: Update persona
  ↓
Version tracking: Store sync record
  ↓
Notify on Cowork: "✅ Personas synced (5 agents)"
```

### Implementation

```python
# scripts/sync_agents_to_askcad.py

class AskCADSync:
    def __init__(self, askcad_api_key: str):
        self.client = requests.Session()
        self.client.headers.update({
            "Authorization": f"Bearer {askcad_api_key}",
            "Content-Type": "application/json",
        })

    def sync_agent_persona(self, agent_file: Path) -> bool:
        """
        Sync .claude/agents/*.md to AskCAD persona
        
        Mapping:
        .claude/agents/agente-saneamento.md
          → AskCAD persona: "Manta 03-S8 Saneamento"
        """
        
        # 1. Parse agent .md
        agent_data = self.parse_agent_markdown(agent_file)
        
        # 2. Extract metadata
        persona_id = self.get_askcad_persona_id(agent_data['slug'])
        
        # 3. Build persona payload
        persona = {
            "name": agent_data['name'],
            "description": agent_data['description'],
            "role": agent_data['role'],
            "system_prompt": agent_data['system_prompt'],
            "capabilities": agent_data['capabilities'],
            "tags": agent_data['tags'],
            "metadata": {
                "manta_code": agent_data['code'],
                "segment": agent_data['segment'],
                "status": agent_data['status'],
                "version": agent_data['version'],
                "source": "claude-code-autosync",
                "last_synced": datetime.utcnow().isoformat(),
            },
        }
        
        # 4. Update persona in AskCAD
        response = self.client.put(
            f"https://api.askcad.com/v1/personas/{persona_id}",
            json=persona,
        )
        
        if response.status_code == 200:
            # 5. Record sync
            self.record_sync(agent_file, persona_id, success=True)
            return True
        else:
            self.record_sync(agent_file, persona_id, success=False, error=response.text)
            return False

    def parse_agent_markdown(self, file_path: Path) -> Dict[str, Any]:
        """Extract metadata from .claude/agents/*.md"""
        content = file_path.read_text()
        
        # Parse YAML frontmatter or structured comments
        # Extract: name, slug, role, system_prompt, capabilities, etc.
        
        return {
            'name': '...',
            'slug': file_path.stem,
            'code': '...',  # e.g., Manta 03-S8
            'segment': '...',  # e.g., saneamento
            'role': '...',
            'description': '...',
            'system_prompt': '...',
            'capabilities': [...],
            'tags': [...],
            'status': 'operational',
            'version': '1.0.0',
        }

    def record_sync(self, agent_file: Path, persona_id: str, success: bool, error: str = None):
        """Record sync event in Supabase."""
        supabase.table('maestro_askcad_sync').insert({
            'agent_slug': agent_file.stem,
            'persona_id': persona_id,
            'synced_at': datetime.utcnow(),
            'success': success,
            'error_message': error,
            'git_commit': os.environ.get('GITHUB_SHA'),
            'sync_source': 'github_actions',
        }).execute()
```

### CI/CD Integration

```yaml
# .github/workflows/sync-personas-to-askcad.yml

name: Sync Agent Personas to AskCAD

on:
  push:
    branches: [main]
    paths:
      - '.claude/agents/**'

jobs:
  sync-personas:
    runs-on: ubuntu-latest
    
    env:
      ASKCAD_API_KEY: ${{ secrets.ASKCAD_API_KEY }}
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Sync agent personas
        run: |
          python scripts/sync_agents_to_askcad.py --all
      
      - name: Record sync metrics
        if: always()
        run: |
          python - << 'EOF'
          import os
          from supabase import create_client
          
          # Query sync status
          result = supabase.table('maestro_askcad_sync').select(
            'count', count='exact'
          ).eq('synced_at', 'now()').execute()
          
          print(f"✅ Personas synced: {result.count}")
          EOF
```

### Deliverables (3.4)
- [ ] `scripts/sync_agents_to_askcad.py`
- [ ] `.github/workflows/sync-personas-to-askcad.yml`
- [ ] `maestro_askcad_sync` table (tracking)
- [ ] AskCAD API integration
- [ ] Version history in AskCAD
- [ ] Notification on sync completion

---

## 3.5 — Advanced Routing (Feb 01 - Feb 28)

### Goal
For edge cases where keywords don't clearly distinguish agents, use LLM-assisted disambiguation via Manta 16 (Orchestrator).

### Algorithm

```python
def route_with_fallback(prompt: str):
    """Route with LLM-assisted tie-breaker."""
    
    # 1. Try keyword routing first (fast)
    scores = score_agents_by_keywords(prompt)
    
    primary = max(scores, key=scores.get)
    primary_score = scores[primary]
    
    # Get runner-up
    remaining = {a: s for a, s in scores.items() if a != primary}
    secondary = max(remaining, key=remaining.get) if remaining else None
    secondary_score = remaining[secondary] if secondary else 0
    
    score_gap = primary_score - secondary_score
    
    # 2. If ambiguous (low confidence or close scores)
    if score_gap < 0.15 or primary_score < 0.70:
        # Use LLM tie-breaker
        
        disambiguation_prompt = f"""
        User query: "{prompt}"
        
        Top agents by keyword matching:
        1. {primary}: {primary_score:.0%}
        2. {secondary}: {secondary_score:.0%}
        
        The scores are very close. Which agent is MOST appropriate?
        Respond ONLY with agent slug, one sentence explanation.
        """
        
        llm_recommendation = call_orchestrator(
            prompt=disambiguation_prompt,
            tier='haiku',  # cheap/fast for this task
            max_tokens=50,
        )
        
        recommended_agent = parse_agent_from_response(llm_recommendation)
        
        # 3. Use LLM recommendation if confident
        if recommended_agent in [primary, secondary]:
            return recommended_agent
        else:
            return primary  # Fall back if LLM confused
    
    else:
        # High confidence from keywords
        return primary
```

### Monitoring

```sql
-- Track when LLM tie-breaker is used

CREATE TABLE maestro_tiebreaker_events (
  id BIGINT PRIMARY KEY,
  prompt TEXT NOT NULL,
  keyword_primary TEXT,
  keyword_score FLOAT,
  keyword_runner_up TEXT,
  llm_recommendation TEXT,
  final_agent TEXT,
  llm_correct BOOLEAN,  -- did user approve?
  latency_ms INT,
  timestamp TIMESTAMPTZ DEFAULT now()
);

-- Metric: How often does LLM tie-breaker improve routing?
SELECT
  COUNT(*) as total_tiebreakers,
  SUM(CASE WHEN llm_correct THEN 1 ELSE 0 END) as llm_correct,
  ROUND(100.0 * SUM(CASE WHEN llm_correct THEN 1 ELSE 0 END) / COUNT(*), 1) as effectiveness
FROM maestro_tiebreaker_events
WHERE timestamp > now() - interval '30 days';
```

### Deliverables (3.5)
- [ ] LLM tie-breaker logic in maestro router
- [ ] `maestro_tiebreaker_events` tracking table
- [ ] Effectiveness metrics + dashboard
- [ ] Fallback to keyword if LLM unsure
- [ ] Cost optimization (use Haiku for fast decision)

---

## 3.6 — Audit & Compliance Dashboard (Mar 01 - Mar 31)

### Goal
Full audit trail, GDPR compliance, and governance visibility.

### Compliance Features

#### Data Minimization
```python
# Store prompts/responses with hashing (not plaintext)

INSERT INTO maestro_audit_log (
  user_id,
  session_id,
  prompt_hash,       -- SHA256(prompt), not plaintext
  response_hash,     -- SHA256(response)
  agent_slug,
  tokens_used,
  timestamp,
  data_classification,  -- 'public', 'internal', 'confidential', 'restricted'
  retention_period_days  -- auto-delete after N days
) VALUES (...);
```

#### GDPR Right to Erasure
```python
def delete_user_data(user_id: str):
    """GDPR: Delete all data for user."""
    
    # 1. Anonymize audit logs
    supabase.table('maestro_audit_log').update({
        'user_id': None,
        'session_id': f"deleted_{uuid.uuid4()}",
        'prompt_hash': None,
        'response_hash': None,
    }).eq('user_id', user_id).execute()
    
    # 2. Delete conversation history
    supabase.table('maestro_conversations').delete().eq('user_id', user_id).execute()
    supabase.table('maestro_conversation_turns').delete().match({
        'session_id': f'%{user_id}%'
    }).execute()
    
    # 3. Record deletion event (immutable log)
    supabase.table('maestro_gdpr_deletions').insert({
        'user_id_hash': hashlib.sha256(user_id.encode()).hexdigest(),
        'deletion_timestamp': datetime.utcnow(),
        'tables_affected': ['audit_log', 'conversations', 'turns'],
    }).execute()
```

#### Compliance Dashboard

```sql
-- Governance view: Who accessed what?

CREATE VIEW maestro_compliance_audit AS
SELECT
  timestamp,
  user_id_hash,  -- anonymized
  agent_slug,
  data_classification,
  action_type,   -- 'route', 'ask', 'feedback'
  success,
  tokens_used,
  retention_until
FROM maestro_audit_log
ORDER BY timestamp DESC;

-- Monthly compliance report
SELECT
  data_classification,
  COUNT(*) as access_count,
  SUM(tokens_used) as total_tokens,
  COUNT(DISTINCT user_id_hash) as unique_users,
  MIN(timestamp) as first_access,
  MAX(timestamp) as last_access
FROM maestro_compliance_audit
WHERE timestamp > date_trunc('month', now()) - interval '30 days'
GROUP BY data_classification;
```

#### Audit Trail Export

```python
def export_audit_report(start_date: str, end_date: str, format: str = 'pdf'):
    """Export audit trail for compliance review."""
    
    # 1. Query audit logs
    logs = supabase.table('maestro_audit_log').select('*').between(
        'timestamp', start_date, end_date
    ).execute()
    
    # 2. Summarize by agent, user, classification
    summary = {
        'period': f'{start_date} to {end_date}',
        'total_queries': len(logs),
        'by_agent': Counter([log['agent_slug'] for log in logs]),
        'by_classification': Counter([log['data_classification'] for log in logs]),
        'total_tokens': sum(log['tokens_used'] for log in logs),
    }
    
    # 3. Export as PDF with charts
    if format == 'pdf':
        pdf = generate_audit_report_pdf(summary, logs)
        return pdf.write()
    elif format == 'csv':
        return generate_csv(logs)
```

### Deliverables (3.6)
- [ ] `maestro_audit_log` table with hashing
- [ ] `maestro_gdpr_deletions` immutable log
- [ ] Delete user data function (GDPR compliance)
- [ ] Audit dashboard (Grafana/Looker)
- [ ] Monthly compliance export (PDF)
- [ ] Data retention policies (auto-delete after N days)
- [ ] Access control logs (who can see what)

---

## Phase 3 Success Metrics

| Metric | Target | Timeline |
|--------|--------|----------|
| **Public API** | 2+ partners consuming | Dec 31 |
| **Regulatory Webhooks** | 4 sources (ANEEL, ANTAQ, ANA, ANAC) live | Nov 30 |
| **Conversation Sessions** | ≥100 sessions/week | Jan 31 |
| **Agent Personas** | 100% in sync with AskCAD | Feb 28 |
| **Audit Compliance** | GDPR-ready, zero data breaches | Mar 31 |
| **API Rate Limit** | <5% requests throttled | Ongoing |

---

## Timeline Gantt

```
Aug  Sep  Oct  Nov  Dec  Jan  Feb  Mar
├──┤  ├──┤  ├──┤  ├──┤  ├──┤  ├──┤  ├──┤
     [3.1]       [3.2]  [3.3]      [3.5]
                       [3.4]  [3.6]
└─────────────────────────────────────┘
         PHASE 3 (8 months)
```

---

## Risks & Mitigations

| Risk | Mitigation | Owner |
|------|-----------|-------|
| API adoption low | Beta partners early; free tier | Product |
| Regulatory source parsing fails | Manual fallback + monitoring | DevOps |
| Session storage scales poorly | Archive old sessions to cold storage | DevOps |
| AskCAD API changes | Build adapter layer; version handling | Cowork |
| GDPR compliance gaps | Security audit pre-launch | Security |

---

## Deployment Checklist

- [ ] Phase 3.1 (Public API): FastAPI + SDK + docs
- [ ] Phase 3.2 (Regulatory): 4 webhook listeners + monitoring
- [ ] Phase 3.3 (Conversation): Sessions + vector context
- [ ] Phase 3.4 (AskCAD Sync): Auto-update personas
- [ ] Phase 3.5 (Advanced Routing): LLM tie-breaker
- [ ] Phase 3.6 (Audit): GDPR-ready compliance

---

**Last Updated**: 2026-07-26  
**Status**: 📋 Planning phase (detailed specs ready)  
**Next Checkpoint**: 2026-08-31 (Phase 2 complete, Phase 3 implementation begins)
