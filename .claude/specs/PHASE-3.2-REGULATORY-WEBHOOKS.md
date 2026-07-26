# Phase 3.2 — Regulatory Webhooks Specification
**Manta Maestro v5.0** — Regulatory Intelligence Automation & Real-Time Policy Sync

**Document Version:** 3.2-20260726  
**Status:** 🟢 Ready for implementation (Gate 3, Q1 2027)  
**Audience:** Maestro team, Data engineering, DevOps, Compliance  
**Timeline:** Q1 2027 (Months 13-15 of Phase 3)  
**Success Criteria:** 4 active listeners, <6h latency, 99.5% uptime, 100% audit trail

---

## Executive Summary

Phase 3.2 implements automated regulatory intelligence collection from four Brazilian federal agencies (ANEEL, ANTAQ, ANA, ANAC) via:

1. **Polled webhooks** (6-hourly fallback strategy) — agency RSS feeds, APIs, publication calendars
2. **Event normalization** — unified JSON schema for routing to 5 agent verticals
3. **RAG auto-update** — regulatory changes → Supabase vector embeddings (automatic)
4. **Agent broadcasting** — Cowork notifications + autonomous agent re-analysis of affected policies
5. **Audit logging** — immutable regulatory change trail (GDPR + compliance)
6. **Retry & DLQ** — exponential backoff, dead-letter queue for monitoring failures

**Regulatory scope:**
- **ANEEL** (Agência Nacional de Energia Elétrica): R1–R6 resolutions, licitação notices, RAP modifications
- **ANTAQ** (Agência Nacional de Transportes Aquaviários): port regulations, vessel standards, terminal operations
- **ANA** (Agência Nacional de Águas): water resource policies, dam safety (PNSB), environmental permits
- **ANAC** (Agência Nacional de Aviação Civil): airport standards, aircraft operations, safety regulations

**Target agents:**
- Manta 03-S6 (Portos) ← ANTAQ
- Manta 03-S7 (Aeroportos) ← ANAC
- Manta 03-S8 (Saneamento) ← ANA
- Manta 03-S9 (Energia) ← ANEEL
- Manta 03-S10 (Barragens) ← ANA

---

## 1. REGULATORY LISTENERS ARCHITECTURE

### 1.1 ANEEL Listener (Energy Sector)

**Agency:** Agência Nacional de Energia Elétrica  
**Scope:** Electricity generation, transmission, distribution, and auctions  
**RAG Collection:** `ene:` (Anthropic embeddings, 1536 dimensions)

#### Data Sources

| Source | Frequency | Format | Latency Target | Auth |
|--------|-----------|--------|-----------------|------|
| Official Gazette (DOU) RSS | Daily 8am | RSS/XML | <2h | Public |
| ANEEL Resolutions API | Weekly Mon | JSON REST | <24h | Public API key |
| ANEEL Edital Portal | As-published | HTML scrape + PDF | <4h | Public + scraping |
| Market Operator (ONS) | Real-time | SFTP, XML | <1h | VPN + certs |
| CCEE Auction notifications | 2x/month | Email webhook | <30m | Email parser |

#### Event Types & Keywords

```yaml
# Resolution changes (R1-R6)
events:
  - type: resolution_published
    keywords:
      - "Resolução ANEEL"
      - "R[1-6]"
      - "REANEEL"
    priority: critical
    rtg_field: aneel_resolution

  - type: edital_published
    keywords:
      - "Edital de Licitação"
      - "Leilão"
      - "UTE|UHE|Transmissão"
    priority: high
    rtg_field: aneel_auction

  - type: rap_modified
    keywords:
      - "RAP"
      - "Receita Anual Permitida"
      - "reajuste|revisão"
    priority: high
    rtg_field: aneel_economics

  - type: tariff_adjustment
    keywords:
      - "Reajuste Tarifário"
      - "Parcela A"
      - "Parcela B"
    priority: medium
    rtg_field: aneel_tariff
```

#### ANEEL Polling Strategy

```python
class ANEELListener:
    poll_interval = 360  # 6 hours in minutes
    initial_backoff = 60  # 1 minute
    max_backoff = 3600  # 1 hour
    retry_count = 3
    
    async def poll_sources(self):
        """
        Daily 8am (UTC-3): Check DOU RSS feed
        Weekly Mon 10am: Query ANEEL REST API (resolutions from last 7 days)
        Continuous (6h intervals): Edital portal scrape via Selenium
        Real-time: ONS SFTP subscription (background listener)
        2x/month: CCEE email webhook parser
        """
        tasks = [
            self.fetch_dou_rss(),  # Daily, high precision
            self.fetch_aneel_api(),  # Weekly
            self.scrape_edital_portal(),  # 6-hourly
            self.listen_ons_sftp(),  # Background daemon
            self.parse_ccee_emails()  # Async event-driven
        ]
        results = await asyncio.gather(*tasks)
        return self.normalize_events(results)
    
    async def fetch_dou_rss(self):
        """
        RSS feed: https://www.in.gov.br/web/dou/-/edicao?p_p_state=maximized
        Filter: ANEEL, Ministério de Minas e Energia
        Parse: Title, Link, Publish Date, Content excerpt
        """
        feed_url = "https://www.in.gov.br/web/dou/-/edicao?p_p_state=maximized"
        # Scrape RSS → convert to unified event schema
        pass
    
    async def fetch_aneel_api(self):
        """
        Endpoint: https://api.aneel.gov.br/resolucoes/v1/
        Params: published_after, type=[R1|R2|R3|R4|R5|R6]
        Auth: API key from environment (ANEEL_API_KEY)
        Rate limit: 100 req/hour
        """
        headers = {"Authorization": f"Bearer {os.getenv('ANEEL_API_KEY')"}
        params = {
            "published_after": (datetime.utcnow() - timedelta(days=7)).isoformat(),
            "page_size": 100
        }
        response = await self.http_client.get(
            "https://api.aneel.gov.br/resolucoes/v1/",
            headers=headers,
            params=params
        )
        return response.json()["resolutions"]
    
    async def scrape_edital_portal(self):
        """
        Portal: https://www2.aneel.gov.br/editais/
        Method: Selenium + BeautifulSoup (JavaScript rendering)
        Detect: New rows in edital table (compare hash vs last scrape)
        Extract: Edital ID, Tipo, Data publicação, PDF link
        Timeout: 30 seconds
        """
        async with AsyncChromium() as browser:
            page = await browser.new_page()
            await page.goto("https://www2.aneel.gov.br/editais/", timeout=30000)
            html = await page.content()
            soup = BeautifulSoup(html, 'html.parser')
            table = soup.find('table', {'class': 'editais-list'})
            # Parse rows → check hash against stored hash
            pass
```

---

### 1.2 ANTAQ Listener (Port Sector)

**Agency:** Agência Nacional de Transportes Aquaviários  
**Scope:** Port operations, vessel standards, cargo regulations  
**RAG Collection:** `por:` (Anthropic embeddings, 1536 dimensions)

#### Data Sources

| Source | Frequency | Format | Latency Target | Auth |
|--------|-----------|--------|-----------------|------|
| ANTAQ Resolution Portal | Weekly | HTML + PDF | <24h | Public |
| Port Authority Notices | 2x/week | Email/RSS | <2h | Subscription |
| PIANC/IHO Guidelines | Monthly | PDF | <48h | Public download |
| BNDES Project notices | Bi-weekly | JSON API | <24h | Public API |
| Terminal Operator updates | Real-time | Webhook (custom) | <30m | Registered partners |

#### Event Types & Keywords

```yaml
events:
  - type: resolution_published
    keywords:
      - "Resolução ANTAQ"
      - "Portaria ANTAQ"
      - "NORMAM|PIANC"
    priority: critical
    rtg_field: antaq_regulation

  - type: vessel_standard_update
    keywords:
      - "Padrão de Navio"
      - "Certificação IMO|SOLAS|MARPOL"
      - "Capacidade|Arqueação"
    priority: high
    rtg_field: antaq_vessel

  - type: port_expansion
    keywords:
      - "Ampliação|Modernização de Porto"
      - "Berço|Bacia de Evolução"
      - "Dragagem|Aprofundamento"
    priority: medium
    rtg_field: antaq_infrastructure

  - type: environmental_regulation
    keywords:
      - "Gestão Ambiental"
      - "Efluentes|Resíduos|Poluição"
      - "CONAMA|IBAMA"
    priority: high
    rtg_field: antaq_environmental
```

#### ANTAQ Polling Strategy

```python
class ANTAQListener:
    poll_interval = 360  # 6 hours
    
    async def poll_sources(self):
        tasks = [
            self.fetch_antaq_resolutions(),  # Weekly + trending
            self.fetch_port_notices(),  # 2x/week email
            self.fetch_pianc_guidelines(),  # Monthly
            self.fetch_bndes_notices(),  # Bi-weekly
            self.listen_terminal_webhooks()  # Real-time
        ]
        results = await asyncio.gather(*tasks)
        return self.normalize_events(results)
    
    async def fetch_antaq_resolutions(self):
        """
        Portal: https://www.antaq.gov.br/portal/index.php/legislacao/resolucoes
        Method: Weekly scrape + RSS subscription
        Extract: Resolution ID, Type, Publish date, PDF link, Summary
        """
        rss_url = "https://www.antaq.gov.br/rss/resolucoes"
        # Parse RSS, check for new entries
        pass
    
    async def listen_terminal_webhooks(self):
        """
        Registered webhook endpoints for major port operators:
        - Codesp (Santos): webhook.codesp.com.br
        - TCP (Paranaguá): api.tcp.com.br/webhooks
        - TECON (Rio): api.tecon.com.br/events
        
        Payload: JSON with vessel arrival, berth allocation, cargo manifest changes
        Signature: HMAC-SHA256 validation
        Timeout: 30 seconds, retry 3x with exponential backoff
        """
        pass
```

---

### 1.3 ANA Listener (Water Resources & Dam Safety)

**Agency:** Agência Nacional de Águas e Saneamento Básico  
**Scope:** Water resource policies, dam safety, PNSB, environmental permits  
**RAG Collection:** `san:` (saneamento) + `bar:` (barragens)

#### Data Sources

| Source | Frequency | Format | Latency Target | Auth |
|--------|-----------|--------|-----------------|------|
| ANA Resolution Portal | Weekly | HTML + PDF | <24h | Public |
| SIGBM (Dam Registry) | Daily | XML API | <6h | Public API key |
| CNRH Resolutions | Monthly | Email digest | <48h | Email subscription |
| Environmental agency (IBAMA) | As-published | RSS/Portal | <24h | Public |
| State water agencies | Variable | Email/Portal | <72h | Manual subscription |

#### Event Types & Keywords

```yaml
events:
  - type: resolution_published
    keywords:
      - "Resolução ANA"
      - "Portaria MMA"
      - "Lei 14.026|SNIS"
    priority: critical
    rtg_field: ana_resolution

  - type: dam_safety_update
    keywords:
      - "Segurança de Barragens"
      - "PNSB|CBDB|ICOLD"
      - "Inspeção|Classificação"
    priority: critical
    rtg_field: ana_dam_safety

  - type: water_allocation_change
    keywords:
      - "Outorga|Alocação de Água"
      - "Vazão de Regularização"
      - "Estiagem|Secas"
    priority: high
    rtg_field: ana_allocation

  - type: sanitation_standard
    keywords:
      - "Saneamento Básico"
      - "ETA|ETE|Adutora"
      - "NBR 12211|NBR 12212"
    priority: medium
    rtg_field: ana_sanitation
```

#### ANA Polling Strategy

```python
class ANAListener:
    poll_interval = 360  # 6 hours
    
    async def poll_sources(self):
        tasks = [
            self.fetch_ana_resolutions(),  # Weekly
            self.fetch_sigbm_dams(),  # Daily (critical)
            self.fetch_cnrh_resolutions(),  # Monthly
            self.fetch_ibama_updates(),  # As-published
            self.fetch_state_agencies()  # Variable
        ]
        results = await asyncio.gather(*tasks)
        return self.normalize_events(results)
    
    async def fetch_sigbm_dams(self):
        """
        SIGBM API: https://www.ana.gov.br/sigbm/
        Endpoint: /api/v1/dams/updated-since?since={ISO8601_datetime}
        Auth: API key (ANA_SIGBM_API_KEY)
        Rate limit: 200 req/hour
        
        Critical fields:
        - dam_id, name, location, height
        - classification (size + hazard potential)
        - last_inspection, next_inspection
        - anomalies reported (if any)
        """
        headers = {"Authorization": f"Bearer {os.getenv('ANA_SIGBM_API_KEY')"}
        since = (datetime.utcnow() - timedelta(hours=6)).isoformat()
        response = await self.http_client.get(
            "https://www.ana.gov.br/sigbm/api/v1/dams/updated-since",
            headers=headers,
            params={"since": since}
        )
        return response.json()["dams"]
```

---

### 1.4 ANAC Listener (Aviation Sector)

**Agency:** Agência Nacional de Aviação Civil  
**Scope:** Airport standards, aircraft operations, safety regulations  
**RAG Collection:** `aer:` (Anthropic embeddings, 1536 dimensions)

#### Data Sources

| Source | Frequency | Format | Latency Target | Auth |
|--------|-----------|--------|-----------------|------|
| RBAC (Brazilian Civil Aviation Regulations) | Quarterly | HTML + PDF | <72h | Public download |
| ICAO Annex updates | Quarterly | PDF | <1 week | Public ICAO portal |
| ANAC Safety Directives | Bi-weekly | HTML + PDF | <24h | Public + email |
| Airport Authority notices | Real-time | Email/Webhook | <2h | Registered subscribers |
| FAA/EASA equivalency notices | Monthly | RSS/PDF | <48h | Public feeds |

#### Event Types & Keywords

```yaml
events:
  - type: rbac_update
    keywords:
      - "RBAC"
      - "Regulação de Aviação Civil"
      - "Part 121|Part 135"
    priority: critical
    rtg_field: anac_rbac

  - type: safety_directive
    keywords:
      - "AD|Airworthiness Directive"
      - "Emergency Order"
      - "Segurança de Voo"
    priority: critical
    rtg_field: anac_safety

  - type: airport_standard
    keywords:
      - "Padrão de Aeroporto"
      - "Pista|Taxiway|Hangar"
      - "ICAO Annex 14"
    priority: high
    rtg_field: anac_airport

  - type: equipment_certification
    keywords:
      - "Certificação de Equipamento"
      - "ILS|VOR|DVOR"
      - "Procedimento de Aproximação"
    priority: medium
    rtg_field: anac_equipment
```

#### ANAC Polling Strategy

```python
class ANACListener:
    poll_interval = 360  # 6 hours
    
    async def poll_sources(self):
        tasks = [
            self.fetch_rbac_updates(),  # Quarterly + trending
            self.fetch_icao_updates(),  # Quarterly
            self.fetch_safety_directives(),  # Bi-weekly
            self.fetch_airport_notices(),  # Real-time
            self.fetch_faa_equivalency()  # Monthly
        ]
        results = await asyncio.gather(*tasks)
        return self.normalize_events(results)
    
    async def fetch_safety_directives(self):
        """
        Portal: https://www.anac.gov.br/a-anac/legislacao/diretivas-de-aeronavegabilidade
        Method: Weekly RSS subscription + daily scrape for urgent notices
        Extract: AD number, Aircraft type, Title, Effective date, PDF link
        Priority: CRITICAL — all SDs trigger immediate agent review
        """
        rss_url = "https://www.anac.gov.br/rss/diretivas"
        # Parse RSS, identify new SDs
        pass
```

---

## 2. UNIFIED EVENT SCHEMA

### 2.1 Event Structure

```json
{
  "event_id": "evt_20270115_aneel_001",
  "timestamp": "2027-01-15T08:32:45Z",
  "source_agency": "ANEEL",
  "event_type": "resolution_published",
  "priority": "critical",
  "regulatory_domain": "energia",
  "affected_agents": ["Manta 03-S9"],
  
  "content": {
    "title": "Resolução ANEEL nº 2027/27 - Metodologia de Cálculo da RAP",
    "abstract": "Define nova metodologia para cálculo da Receita Anual Permitida...",
    "full_text_url": "https://www.in.gov.br/web/dou/-/edicao/2027/01/15",
    "document_url": "https://www2.aneel.gov.br/cedoc/res2027r.pdf",
    "publish_date": "2027-01-15",
    "effective_date": "2027-02-15",
    "revision_number": 1,
    
    "keywords": ["RAP", "receita permitida", "reajuste"],
    "entities": {
      "regulation_id": "R1",
      "related_regulations": ["R2", "R3"],
      "affected_sectors": ["transmission", "distribution"],
      "compliance_deadline": "2027-04-15"
    }
  },
  
  "metadata": {
    "source_url": "https://www.in.gov.br/",
    "source_type": "official_gazette",
    "extraction_method": "rss_feed",
    "confidence_score": 0.98,
    "language": "pt-BR",
    "checksum_md5": "a3f8c2e1b9d4f7e2c5a8b1d3f6e9c2a5"
  },
  
  "rag_metadata": {
    "rag_collection": "ene:",
    "embedding_status": "pending",
    "chunk_count": 0,
    "vector_ids": []
  },
  
  "audit": {
    "received_at": "2027-01-15T08:32:45Z",
    "processed_at": null,
    "agent_notified_at": null,
    "broadcast_status": "pending",
    "retry_count": 0,
    "last_error": null
  }
}
```

### 2.2 Event Priority Levels

| Priority | Condition | Agent Action | RAG Update | Notification |
|----------|-----------|-------------|------------|--------------|
| **CRITICAL** | Regulation change (R1-R6, safety directive) | Immediate re-analysis | Immediate | Push + email |
| **HIGH** | Edital published, dam classification change | Same-day review | 1h window | Push notification |
| **MEDIUM** | Tariff adjustment, non-binding guideline | Weekly batch review | Daily batch | In-portal only |
| **LOW** | Informational, best-practice document | Monthly digest | Monthly batch | None |

---

## 3. RAG AUTO-UPDATE MECHANISM

### 3.1 Supabase Integration

```sql
-- Table: regulatory_events
CREATE TABLE regulatory_events (
  id BIGSERIAL PRIMARY KEY,
  event_id VARCHAR(255) UNIQUE NOT NULL,
  source_agency VARCHAR(50) NOT NULL,
  event_type VARCHAR(100) NOT NULL,
  priority VARCHAR(20) NOT NULL,
  regulatory_domain VARCHAR(100) NOT NULL,
  affected_agents TEXT[] NOT NULL,
  
  title TEXT NOT NULL,
  abstract TEXT,
  full_text_url TEXT,
  document_url TEXT,
  publish_date TIMESTAMP NOT NULL,
  effective_date TIMESTAMP,
  
  keywords TEXT[],
  entities JSONB,
  metadata JSONB,
  
  rag_collection VARCHAR(50),
  embedding_status VARCHAR(20) DEFAULT 'pending',
  vector_ids BIGINT[],
  
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: regulatory_embeddings (pgvector extension)
CREATE TABLE regulatory_embeddings (
  id BIGSERIAL PRIMARY KEY,
  event_id VARCHAR(255) NOT NULL REFERENCES regulatory_events(event_id),
  chunk_id INTEGER NOT NULL,
  content TEXT NOT NULL,
  embedding vector(1536),
  
  rag_collection VARCHAR(50) NOT NULL,
  source_type VARCHAR(50),
  
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  UNIQUE(event_id, chunk_id)
);

-- Table: regulatory_audit_log
CREATE TABLE regulatory_audit_log (
  id BIGSERIAL PRIMARY KEY,
  event_id VARCHAR(255) NOT NULL REFERENCES regulatory_events(event_id),
  action VARCHAR(100) NOT NULL,
  agent_id VARCHAR(50),
  status VARCHAR(20) NOT NULL,
  details JSONB,
  
  logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  immutable BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_regulatory_events_domain ON regulatory_events(regulatory_domain);
CREATE INDEX idx_regulatory_events_agency ON regulatory_events(source_agency);
CREATE INDEX idx_regulatory_events_priority ON regulatory_events(priority);
CREATE INDEX idx_regulatory_embeddings_collection ON regulatory_embeddings(rag_collection);
```

### 3.2 Auto-Embedding Pipeline

```python
class RAGAutoUpdateService:
    """
    Listens to regulatory_events table for pending embeddings.
    Converts events → chunks → embeddings → pgvector inserts.
    """
    
    def __init__(self, supabase_client, anthropic_client):
        self.supabase = supabase_client
        self.anthropic = anthropic_client
        self.embedding_model = "text-embedding-3-large"
        self.max_chunk_size = 500  # tokens
        self.chunk_overlap = 100
    
    async def watch_pending_events(self):
        """
        PostgreSQL LISTEN on regulatory_events table (via Supabase realtime).
        Triggers when embedding_status = 'pending'.
        """
        async def on_event_change(payload):
            event = payload["new"]
            if event["embedding_status"] == "pending":
                await self.embed_and_store(event)
        
        self.supabase.realtime.subscribe(
            table="regulatory_events",
            event="UPDATE"
        ).on_postgres_changes(
            event="*",
            schema="public",
            table="regulatory_events",
            callback=on_event_change
        ).subscribe()
    
    async def embed_and_store(self, event: dict):
        """
        1. Fetch full text from document_url (if available)
        2. Chunk content using token splitter (max 500 tokens, 100 overlap)
        3. Embed chunks via Anthropic API (batch)
        4. Store in regulatory_embeddings table
        5. Update event embedding_status = 'complete'
        """
        try:
            # Fetch document
            full_text = await self.fetch_document(event["document_url"])
            
            # Chunk
            chunks = self.chunk_text(
                text=full_text,
                max_tokens=500,
                overlap_tokens=100
            )
            
            # Embed (batch API for efficiency)
            embeddings = await self.anthropic.embeddings.create(
                model="text-embedding-3-large",
                input=[chunk["text"] for chunk in chunks],
                dimensions=1536
            )
            
            # Store in Supabase
            vector_ids = []
            for i, chunk in enumerate(chunks):
                result = self.supabase.table("regulatory_embeddings").insert({
                    "event_id": event["event_id"],
                    "chunk_id": i,
                    "content": chunk["text"],
                    "embedding": embeddings.data[i]["embedding"],
                    "rag_collection": event["rag_collection"],
                    "source_type": event["metadata"]["source_type"]
                }).execute()
                vector_ids.append(result.data[0]["id"])
            
            # Mark complete
            self.supabase.table("regulatory_events").update({
                "embedding_status": "complete",
                "vector_ids": vector_ids,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("event_id", event["event_id"]).execute()
            
            # Log
            self.audit_log(event["event_id"], "embedding_complete", "RAGAutoUpdateService")
            
        except Exception as e:
            await self.handle_embedding_error(event, e)
    
    async def fetch_document(self, url: str) -> str:
        """
        Download document (PDF/HTML).
        If PDF: Use pdfplumber to extract text.
        If HTML: Use BeautifulSoup to extract main content.
        """
        if url.endswith(".pdf"):
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=30) as resp:
                    pdf_bytes = await resp.read()
                    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                        return "\n".join(
                            page.extract_text() for page in pdf.pages
                        )
        else:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=30) as resp:
                    html = await resp.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    # Remove script, style tags
                    for tag in soup(['script', 'style']):
                        tag.decompose()
                    return soup.get_text(separator="\n", strip=True)
    
    def chunk_text(self, text: str, max_tokens: int, overlap_tokens: int) -> list:
        """
        Token-based chunking using tiktoken encoder (cl100k_base for GPT-4).
        Maintains semantic boundaries (sentences).
        """
        enc = tiktoken.get_encoding("cl100k_base")
        tokens = enc.encode(text)
        chunks = []
        i = 0
        while i < len(tokens):
            chunk_tokens = tokens[i:i + max_tokens]
            chunk_text = enc.decode(chunk_tokens)
            chunks.append({
                "text": chunk_text,
                "token_count": len(chunk_tokens)
            })
            i += max_tokens - overlap_tokens
        return chunks
    
    def audit_log(self, event_id: str, action: str, agent_id: str):
        """Immutable audit log entry."""
        self.supabase.table("regulatory_audit_log").insert({
            "event_id": event_id,
            "action": action,
            "agent_id": agent_id,
            "status": "success",
            "logged_at": datetime.utcnow().isoformat(),
            "immutable": True
        }).execute()
```

---

## 4. AGENT BROADCASTING & COWORK NOTIFICATIONS

### 4.1 Broadcast Service

```python
class RegulatoryBroadcastService:
    """
    Routes regulatory events to target agents via:
    1. Cowork notifications (push + email)
    2. Autonomous agent re-analysis trigger
    3. RAG context injection (vector search)
    """
    
    def __init__(self, cowork_client, maestro_client):
        self.cowork = cowork_client
        self.maestro = maestro_client
    
    async def broadcast_event(self, event: dict):
        """
        Triggered when event.embedding_status = 'complete'.
        1. Identify affected agents
        2. Send Cowork push notification
        3. Trigger autonomous agent analysis
        4. Update audit log
        """
        agents = event["affected_agents"]
        
        for agent_code in agents:
            try:
                # 1. Cowork notification
                notification = await self.create_notification(event, agent_code)
                await self.cowork.send_notification(notification)
                
                # 2. Trigger agent autonomous analysis
                await self.trigger_agent_analysis(event, agent_code)
                
                # 3. Audit
                self.audit_log(
                    event["event_id"],
                    f"broadcast_to_{agent_code}",
                    "RegulatoryBroadcastService"
                )
                
            except Exception as e:
                await self.handle_broadcast_error(event, agent_code, e)
    
    async def create_notification(self, event: dict, agent_code: str) -> dict:
        """
        Cowork notification payload:
        - Title: Regulatory change summary
        - Body: Abstract + link to RAG context
        - CTA: "Review policy impact" button
        - Priority: Push + email if CRITICAL
        """
        
        priority_map = {
            "critical": "high",
            "high": "normal",
            "medium": "low",
            "low": "silent"
        }
        
        return {
            "recipient": agent_code,  # Cowork user/group ID
            "title": f"[{event['source_agency']}] {event['content']['title'][:80]}...",
            "body": event["content"]["abstract"][:200],
            "priority": priority_map[event["priority"]],
            "action_url": f"/agents/{agent_code}/analysis?event_id={event['event_id']}",
            "action_label": "Review policy impact",
            "tags": [
                event["source_agency"],
                event["regulatory_domain"],
                event["event_type"]
            ],
            "metadata": {
                "event_id": event["event_id"],
                "effective_date": event["content"]["effective_date"],
                "compliance_deadline": event["content"]["entities"].get("compliance_deadline")
            }
        }
    
    async def trigger_agent_analysis(self, event: dict, agent_code: str):
        """
        Invoke agent via Maestro API:
        POST /maestro/agents/{agent_code}/analyze-regulatory-event
        
        Payload includes:
        - event metadata
        - top-5 relevant RAG chunks (vector search)
        - compliance deadline
        - impact zones (projects, contracts)
        
        Agent responds with:
        - Risk assessment
        - Recommended actions
        - Affected artifacts (PDFs, contracts)
        """
        
        # Vector search for context
        rag_context = await self.semantic_search_rag(
            event["event_id"],
            event["rag_collection"],
            top_k=5
        )
        
        # Find affected projects in agent's knowledge base
        affected_projects = await self.find_affected_projects(
            agent_code,
            event
        )
        
        payload = {
            "event": event,
            "rag_context": rag_context,
            "affected_projects": affected_projects,
            "request_id": f"evt_{event['event_id']}_{agent_code}"
        }
        
        response = await self.maestro.post(
            f"/agents/{agent_code}/analyze-regulatory-event",
            json=payload,
            timeout=120
        )
        
        return response.json()
    
    async def semantic_search_rag(
        self,
        event_id: str,
        rag_collection: str,
        top_k: int = 5
    ) -> list:
        """
        Vector similarity search in Supabase pgvector.
        Finds chunks from the same event (or related events in same domain).
        """
        # Get event's embedding
        event_embedding = self.supabase.table(
            "regulatory_embeddings"
        ).select(
            "embedding"
        ).eq(
            "event_id", event_id
        ).order(
            "chunk_id", desc=False
        ).limit(1).execute()
        
        if not event_embedding.data:
            return []
        
        vector = event_embedding.data[0]["embedding"]
        
        # Similarity search
        results = self.supabase.rpc(
            "search_regulatory_embeddings",
            {
                "query_embedding": vector,
                "rag_collection": rag_collection,
                "match_count": top_k
            }
        ).execute()
        
        return results.data
```

### 4.2 Cowork Notification Schema

```typescript
interface RegulatoryNotification {
  recipient: string;  // agent_code, e.g. "Manta 03-S9"
  title: string;
  body: string;
  priority: "high" | "normal" | "low" | "silent";
  action_url: string;
  action_label: string;
  tags: string[];  // ["ANEEL", "energia", "resolution_published"]
  metadata: {
    event_id: string;
    effective_date: string;
    compliance_deadline?: string;
    rag_chunks_count: number;
    document_url: string;
  };
  expires_at: string;  // ISO 8601, 30 days default
}
```

---

## 5. WEBHOOK RETRY LOGIC & DEAD-LETTER QUEUE

### 5.1 Retry Strategy

```python
class RegulatoryWebhookRetryService:
    """
    Exponential backoff retry for failed event processing:
    - Attempt 1: Immediate
    - Attempt 2: +60 seconds
    - Attempt 3: +300 seconds (5 min)
    - Attempt 4: +900 seconds (15 min)
    - Attempt 5: +3600 seconds (1 hour)
    - DLQ: After 5 failures, move to dead-letter queue
    """
    
    RETRY_CONFIG = {
        1: 0,       # immediate
        2: 60,      # 1 min
        3: 300,     # 5 min
        4: 900,     # 15 min
        5: 3600     # 1 hour
    }
    
    MAX_RETRIES = 5
    DLQ_TABLE = "regulatory_events_dlq"
    
    async def process_with_retry(self, event: dict):
        """
        Attempt processing with exponential backoff.
        """
        retry_count = 0
        last_error = None
        
        while retry_count < self.MAX_RETRIES:
            try:
                await self.process_event(event)
                self.audit_log(event["event_id"], "processed_success")
                return
                
            except Exception as e:
                retry_count += 1
                last_error = e
                
                if retry_count < self.MAX_RETRIES:
                    backoff = self.RETRY_CONFIG[retry_count + 1]
                    await asyncio.sleep(backoff)
                    self.audit_log(
                        event["event_id"],
                        f"retry_{retry_count}",
                        error=str(e)
                    )
        
        # All retries exhausted → DLQ
        await self.send_to_dlq(event, last_error, retry_count)
    
    async def send_to_dlq(self, event: dict, error: Exception, retry_count: int):
        """
        Move failed event to dead-letter queue.
        Triggers alert to DevOps team.
        """
        dlq_entry = {
            "event_id": event["event_id"],
            "original_event": event,
            "error_message": str(error),
            "error_type": type(error).__name__,
            "retry_count": retry_count,
            "failed_at": datetime.utcnow().isoformat(),
            "alert_status": "pending"
        }
        
        # Insert to DLQ table
        self.supabase.table(self.DLQ_TABLE).insert(dlq_entry).execute()
        
        # Send alert
        await self.send_dlq_alert(dlq_entry)
        
        # Audit
        self.audit_log(
            event["event_id"],
            "moved_to_dlq",
            error=str(error)
        )
    
    async def send_dlq_alert(self, dlq_entry: dict):
        """
        Slack/PagerDuty alert for DevOps team.
        Example: "Regulatory event processing failed after 5 retries: evt_20270115_aneel_001"
        """
        message = f"""
        ⚠️ Regulatory Webhook Failed (DLQ)
        Event: {dlq_entry['event_id']}
        Error: {dlq_entry['error_message']}
        Retries: {dlq_entry['retry_count']}/5
        
        Action: Review in DLQ dashboard and retry manually.
        """
        await self.alerting_service.send_slack_alert(message)
```

### 5.2 Dead-Letter Queue Table

```sql
-- Dead-letter queue for failed regulatory events
CREATE TABLE regulatory_events_dlq (
  id BIGSERIAL PRIMARY KEY,
  event_id VARCHAR(255) UNIQUE NOT NULL,
  original_event JSONB NOT NULL,
  error_message TEXT NOT NULL,
  error_type VARCHAR(100),
  retry_count INTEGER,
  
  failed_at TIMESTAMP NOT NULL,
  resolved_at TIMESTAMP,
  alert_status VARCHAR(20) DEFAULT 'pending',  -- pending, acknowledged, resolved
  
  manual_action JSONB,  -- DevOps intervention details
  
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_dlq_alert_status ON regulatory_events_dlq(alert_status);
CREATE INDEX idx_dlq_failed_at ON regulatory_events_dlq(failed_at);
```

---

## 6. AUDIT LOGGING & COMPLIANCE

### 6.1 Immutable Audit Log

```sql
-- Immutable audit log for regulatory changes
CREATE TABLE regulatory_audit_log (
  id BIGSERIAL PRIMARY KEY,
  event_id VARCHAR(255) NOT NULL,
  
  action VARCHAR(100) NOT NULL,  -- "event_received", "embedding_complete", "broadcast_to_agent", etc.
  agent_id VARCHAR(50),
  status VARCHAR(20) NOT NULL,   -- "success", "failed", "pending"
  
  details JSONB,  -- Additional context: error messages, retry counts, user actions
  
  logged_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  immutable BOOLEAN NOT NULL DEFAULT TRUE,
  
  -- GDPR fields
  data_subject_id VARCHAR(255),  -- User/organization that triggered/accessed this
  retention_date TIMESTAMP,      -- Date to auto-delete (90 days default)
  
  UNIQUE(event_id, action, logged_at)
);

-- Enforce immutability via trigger
CREATE OR REPLACE FUNCTION prevent_audit_update()
RETURNS TRIGGER AS $$
BEGIN
  IF TG_OP = 'UPDATE' THEN
    RAISE EXCEPTION 'Audit log entries are immutable';
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER regulatory_audit_immutable
BEFORE UPDATE ON regulatory_audit_log
FOR EACH ROW
EXECUTE FUNCTION prevent_audit_update();

-- Indexing for compliance queries
CREATE INDEX idx_audit_event_id ON regulatory_audit_log(event_id);
CREATE INDEX idx_audit_action ON regulatory_audit_log(action);
CREATE INDEX idx_audit_logged_at ON regulatory_audit_log(logged_at);
CREATE INDEX idx_audit_retention ON regulatory_audit_log(retention_date);
```

### 6.2 Audit Actions & Fields

| Action | Trigger | Fields | Compliance Use |
|--------|---------|--------|-----------------|
| `event_received` | Listener polls agency | source, checksum, url | Data provenance |
| `event_normalized` | Schema validation | schema_version, validation_errors | Format compliance |
| `embedding_started` | RAG pipeline begins | chunk_count, model_version | AI transparency |
| `embedding_complete` | Vector store updated | vector_ids, collection, tokens_used | Cost tracking |
| `broadcast_initiated` | Agent notification sent | agent_code, notification_id | Notification audit |
| `agent_analysis_requested` | Autonomous review triggered | agent_code, request_id | Agent activity log |
| `agent_analysis_completed` | Agent returns assessment | agent_code, risk_level, recommendations | Decision record |
| `user_accessed_event` | Human views event details | user_id, access_type | GDPR access log |
| `event_deleted` | Retention window expires | deletion_reason, data_subject_id | GDPR erasure |

### 6.3 GDPR Compliance Module

```python
class RegulatoryGDPRService:
    """
    Right-to-erasure, access, and data minimization.
    """
    
    async def handle_erasure_request(self, data_subject_id: str):
        """
        Delete all regulatory events associated with a data subject.
        Maintain immutable audit trail of deletion.
        """
        # Find all events involving this data subject
        events = self.supabase.table("regulatory_events").select(
            "event_id"
        ).eq(
            "created_by", data_subject_id  # Assumes user tracking
        ).execute()
        
        for event in events.data:
            event_id = event["event_id"]
            
            # Delete embeddings
            self.supabase.table("regulatory_embeddings").delete().eq(
                "event_id", event_id
            ).execute()
            
            # Delete event
            self.supabase.table("regulatory_events").delete().eq(
                "event_id", event_id
            ).execute()
            
            # Log deletion (immutable)
            self.supabase.table("regulatory_audit_log").insert({
                "event_id": event_id,
                "action": "event_deleted",
                "status": "success",
                "details": {
                    "reason": "gdpr_erasure_request",
                    "data_subject_id": data_subject_id
                },
                "data_subject_id": data_subject_id,
                "logged_at": datetime.utcnow().isoformat()
            }).execute()
    
    async def handle_access_request(self, data_subject_id: str) -> dict:
        """
        Return all data involving a data subject (GDPR Article 15).
        """
        # Access logs
        access_logs = self.supabase.table("regulatory_audit_log").select(
            "*"
        ).eq(
            "data_subject_id", data_subject_id
        ).execute()
        
        # Events created by data subject
        events = self.supabase.table("regulatory_events").select(
            "*"
        ).eq(
            "created_by", data_subject_id
        ).execute()
        
        return {
            "access_request_date": datetime.utcnow().isoformat(),
            "data_subject_id": data_subject_id,
            "access_logs": access_logs.data,
            "events": events.data,
            "export_format": "json"
        }
```

---

## 7. DEPLOYMENT & OPERATIONS

### 7.1 Infrastructure (Kubernetes)

```yaml
# k8s/regulatory-webhooks-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: regulatory-webhooks
  namespace: maestro
spec:
  replicas: 3
  selector:
    matchLabels:
      app: regulatory-webhooks
  template:
    metadata:
      labels:
        app: regulatory-webhooks
    spec:
      containers:
      - name: aneel-listener
        image: gcr.io/manta-maestro/regulatory-aneel:v3.2
        env:
        - name: ANEEL_API_KEY
          valueFrom:
            secretKeyRef:
              name: regulatory-secrets
              key: aneel_api_key
        - name: POLL_INTERVAL_MINUTES
          value: "360"
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 60
      
      - name: antaq-listener
        image: gcr.io/manta-maestro/regulatory-antaq:v3.2
        # Similar config
      
      - name: ana-listener
        image: gcr.io/manta-maestro/regulatory-ana:v3.2
        # Similar config
      
      - name: anac-listener
        image: gcr.io/manta-maestro/regulatory-anac:v3.2
        # Similar config
      
      - name: broadcast-service
        image: gcr.io/manta-maestro/regulatory-broadcast:v3.2
        env:
        - name: MAESTRO_API_URL
          value: "http://maestro-api:8000"
        - name: COWORK_API_URL
          value: "https://cowork.anthropic.com/api"
```

### 7.2 Monitoring & Alerting

```yaml
# k8s/regulatory-monitoring.yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: regulatory-webhooks-alerts
spec:
  groups:
  - name: regulatory_webhooks
    rules:
    - alert: RegulatoryListenerDown
      expr: up{job="regulatory-webhooks"} == 0
      for: 5m
      annotations:
        summary: "Regulatory listener {{ $labels.listener }} is down"
    
    - alert: RegulatoryEventLatency
      expr: histogram_quantile(0.95, regulatory_event_processing_duration_seconds) > 600
      for: 10m
      annotations:
        summary: "Regulatory event processing latency exceeds 10 minutes"
    
    - alert: RegulatoryDLQBacklog
      expr: count(regulatory_events_dlq{alert_status="pending"}) > 10
      for: 30m
      annotations:
        summary: "Dead-letter queue has {{ $value }} pending events"
    
    - alert: RegulatoryEmbeddingFailure
      expr: increase(regulatory_embedding_errors_total[1h]) > 5
      annotations:
        summary: "RAG embedding failures: {{ $value }} in last hour"
```

---

## 8. TESTING & VALIDATION

### 8.1 Test Scenarios

| Scenario | Test Data | Expected Result | Success Criteria |
|----------|-----------|-----------------|------------------|
| **T1: ANEEL Resolution** | Real ANEEL R1 resolution PDF | Event created, embedded, broadcast to S9 agent | <10s end-to-end |
| **T2: ANTAQ Edital** | Port expansion notice | Event routed to S6 agent | Notification delivered |
| **T3: ANA Dam Safety** | SIGBM dam classification update | Event triggers S10 analysis | Risk assessment generated |
| **T4: ANAC Safety Directive** | AD number, aircraft type | Broadcast to S7, <2h latency | Agent acknowledges |
| **T5: Retry Logic** | Simulated network timeout on event 1 | Event retried 5x, moved to DLQ | Alert sent to DevOps |
| **T6: RAG Auto-Update** | New event in ene: collection | Embeddings generated, searchable | Vector search returns event |
| **T7: GDPR Erasure** | Erasure request for data subject | Event and audit records deleted | Immutable deletion log created |
| **T8: Duplicate Detection** | Same event polled twice | Deduplicated via checksum | Single entry in DB |
| **T9: Priority Routing** | CRITICAL vs MEDIUM events | CRITICAL → immediate, MEDIUM → batch | Latency SLAs met |
| **T10: Multi-Agent Broadcast** | Event affecting 2 agents | Both agents notified + analyzed | Cowork logs confirm delivery |

### 8.2 Load Testing

```python
# tests/load_test_regulatory_webhooks.py
import asyncio
from locust import HttpUser, task, between

class RegulatoryWebhookLoadTest(HttpUser):
    wait_time = between(1, 5)
    
    @task
    async def broadcast_event(self):
        event = {
            "event_id": f"evt_{uuid.uuid4()}",
            "source_agency": random.choice(["ANEEL", "ANTAQ", "ANA", "ANAC"]),
            "priority": random.choice(["critical", "high", "medium"]),
            "affected_agents": ["Manta 03-S9"]
        }
        self.client.post("/webhooks/broadcast", json=event)
    
    # Simulate 100 concurrent events/min, measure latency p95/p99
```

---

## 9. SUCCESS METRICS (Gate 3)

| Metric | Target | Rationale |
|--------|--------|-----------|
| **Listener availability** | ≥99.5% uptime | 4 critical agency listeners |
| **Event latency** | <6 hours (agency → RAG) | Regulatory compliance window |
| **Embedding latency** | <30 min (event → searchable) | Agents need context for analysis |
| **Broadcast latency** | <5 min (embedding → agent) | Timely policy awareness |
| **Retry success rate** | ≥95% (after 5 attempts) | Minimize DLQ backlog |
| **RAG relevance** | ≥85% top-1 (semantic search) | Agents get useful context |
| **Audit trail completeness** | 100% (no blind spots) | GDPR/compliance requirement |

---

## 10. TIMELINE & DELIVERABLES (Q1 2027)

| Week | Milestone | Deliverable |
|------|-----------|-------------|
| Week 1-2 | Infrastructure setup | K8s manifests, Supabase schema, secrets management |
| Week 3-4 | Listener implementation | ANEEL, ANTAQ, ANA, ANAC listener code + unit tests |
| Week 5-6 | RAG auto-update pipeline | Embedding service, pgvector integration, test data |
| Week 7-8 | Broadcast & notifications | Cowork API integration, agent analysis trigger |
| Week 9-10 | Retry logic & DLQ | Error handling, monitoring dashboard |
| Week 11-12 | Load testing & hardening | 100 events/min stress test, latency tuning |
| Week 13 | Gate 3 validation | Success metrics verification, partner readiness |

---

## Quick Reference

**File paths (K8s):**
- Deployment: `/infra/k8s/regulatory-webhooks-deployment.yaml`
- Monitoring: `/infra/k8s/regulatory-monitoring.yaml`
- Secrets: `kubectl create secret generic regulatory-secrets --from-literal=aneel_api_key=...`

**Code modules:**
- Listeners: `src/listeners/{aneel,antaq,ana,anac}.py`
- RAG service: `src/services/rag_auto_update.py`
- Broadcast: `src/services/broadcast.py`
- Retry logic: `src/services/retry.py`
- GDPR: `src/services/gdpr.py`

**Databases:**
- Tables: `regulatory_events`, `regulatory_embeddings`, `regulatory_audit_log`, `regulatory_events_dlq`
- Extensions: `pgvector` (Supabase)

**Team contacts:**
- Maestro team (routing): maestro@mantaassociados.com
- Data team (RAG): data@mantaassociados.com
- DevOps (infrastructure): devops@mantaassociados.com

---

**Document prepared for Phase 3.2 implementation (Q1 2027).**  
**Gate approval required before proceeding to Phase 4.**
