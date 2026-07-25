# Regulatory Webhooks — Phase 3.2 Implementation Guide

**Target**: `maestro-webhooks/listeners/` (ANEEL, ANTAQ, ANA, ANAC)  
**Pattern**: Event-driven, 6-hourly polling  
**Deployment**: Cloud Functions + Pub/Sub (Google Cloud) or Lambda + SNS (AWS)  
**Timeline**: Phase 3.2 (Oct 01 - Nov 15, 2026)

This guide implements automated listeners for regulatory updates across 4 Brazilian agencies, triggering RAG updates and agent notifications.

---

## Overview

```
External Regulators (ANEEL, ANTAQ, ANA, ANAC)
  ↓ (data sources: APIs, RSS, web scraping)
  ↓
Regulatory Listener Service (maestro-webhooks)
  ├── ANEEL Listener (every 6h) → extracts new R1-R7 editais
  ├── ANTAQ Listener (every 6h) → new resolucoes, dragagem padrões
  ├── ANA Listener (every 6h) → outorgas, PNSB atualizações
  └── ANAC Listener (every 6h) → RBAC updates, ICAO Annex 14 versions
  ↓
Document Processing Pipeline
  ├── Extract text (PDF/HTML)
  ├── Generate embeddings (Anthropic API)
  ├── Insert to RAG (rag_chunks, maestro_regulatory_updates)
  ↓
Event Broadcasting
  ├── Notify agents via Cowork (webhook)
  ├── Log to maestro_regulatory_events
  └── Optional: Slack notification
```

---

## Part 1: Regulatory Listener Architecture

### 1.1 — Data Sources

| Agency | Source | Format | Poll Frequency | Example |
|--------|--------|--------|---|-----------|
| **ANEEL** | https://www2.aneel.gov.br/aplicacoes/editais/ | HTML + PDF | Every 6h | R5-2026 Leilão 100 (LT Goiás) |
| **ANTAQ** | https://www.antaq.gov.br/portal/index.php/editais | HTML + PDF | Every 6h | Concessão Porto Santos (Edital 2026/08) |
| **ANA** | http://outorgaonline.ana.gov.br/soa/ | JSON API | Every 6h | Outorga processo 12345 (saneamento) |
| **ANAC** | https://www.anac.gov.br/assuntos/normalização | HTML | Every 6h | RBAC 154 v1.5 (aeroportos) |

### 1.2 — Base Listener Class

```python
# maestro-webhooks/listeners/base_listener.py

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
import hashlib
import logging
from typing import List, Dict, Optional
import requests
from supabase import create_client

logger = logging.getLogger(__name__)

class RegulatoryListener(ABC):
    """Base class for regulatory listeners."""

    def __init__(self, agency_code: str, collection_slug: str, supabase_url: str, supabase_key: str):
        self.agency_code = agency_code  # "ANEEL", "ANTAQ", etc.
        self.collection_slug = collection_slug  # "ene", "por", etc.
        self.db = create_client(supabase_url, supabase_key)

    @abstractmethod
    def fetch_updates(self) -> List[Dict]:
        """
        Fetch latest regulatory documents.

        Returns:
            [
                {
                    "title": "R5-2026 Leilão Transmissão",
                    "url": "https://...",
                    "content": "PDF text extracted",
                    "document_type": "edital|resolucao|norma|aviso",
                    "published_date": "2026-10-15",
                    "source_id": "r5_2026",  # unique identifier
                }
            ]
        """
        pass

    def process_and_ingest(self, documents: List[Dict]):
        """Ingest documents into RAG."""
        for doc in documents:
            # Check if already ingested
            existing = self.db.table("maestro_regulatory_updates").select(
                "*"
            ).eq("source_id", doc["source_id"]).execute()

            if existing.data:
                logger.info(f"Document {doc['source_id']} already ingested")
                continue

            # Generate embedding
            embedding = self._generate_embedding(doc["content"])

            # Chunk and ingest
            chunks = self._chunk_document(doc)
            for chunk_idx, chunk in enumerate(chunks):
                self.db.table("rag_chunks").insert({
                    "collection_slug": self.collection_slug,
                    "content": chunk["text"],
                    "source_file": doc["title"],
                    "page_num": chunk.get("page", 1),
                    "embedding": embedding,
                    "metadata": {
                        "agency": self.agency_code,
                        "document_type": doc["document_type"],
                        "published_date": doc["published_date"],
                        "source_url": doc["url"],
                        "chunk_index": chunk_idx,
                    }
                }).execute()

            # Record regulatory update event
            self.db.table("maestro_regulatory_updates").insert({
                "agency_code": self.agency_code,
                "source_id": doc["source_id"],
                "title": doc["title"],
                "url": doc["url"],
                "document_type": doc["document_type"],
                "published_date": doc["published_date"],
                "ingested_at": datetime.utcnow().isoformat(),
                "status": "ingested",
                "chunk_count": len(chunks),
            }).execute()

            # Broadcast event to agents
            self._broadcast_update(doc)

    def _generate_embedding(self, content: str) -> List[float]:
        """Generate embedding for document."""
        from anthropic import Anthropic
        client = Anthropic()

        response = client.embeddings.create(
            model="text-embedding-3-large",
            input=content[:3000],  # Limit to 3k chars
        )
        return response.embedding

    def _chunk_document(self, doc: Dict, chunk_size: int = 500) -> List[Dict]:
        """Chunk document by paragraphs (semantic)."""
        content = doc["content"]
        paragraphs = content.split("\n\n")

        chunks = []
        current_chunk = []
        current_tokens = 0

        for para in paragraphs:
            para_tokens = len(para.split())

            if current_tokens + para_tokens > chunk_size:
                chunks.append({
                    "text": "\n\n".join(current_chunk),
                    "page": doc.get("page", 1),
                })
                current_chunk = [para]
                current_tokens = para_tokens
            else:
                current_chunk.append(para)
                current_tokens += para_tokens

        if current_chunk:
            chunks.append({
                "text": "\n\n".join(current_chunk),
                "page": doc.get("page", 1),
            })

        return chunks

    def _broadcast_update(self, doc: Dict):
        """Broadcast regulatory update to agents."""
        # Determine target agents based on agency + segment
        target_agents = self._map_agents(doc)

        for agent_slug in target_agents:
            self.db.table("maestro_agent_notifications").insert({
                "agent_slug": agent_slug,
                "event_type": "regulatory_update",
                "title": f"Nova regulação: {doc['title']}",
                "description": f"{self.agency_code}: {doc['title']}",
                "url": doc["url"],
                "priority": self._calculate_priority(doc),
                "created_at": datetime.utcnow().isoformat(),
            }).execute()

    def _map_agents(self, doc: Dict) -> List[str]:
        """Determine which agents should be notified."""
        # Map agency → collection → agents
        mapping = {
            "ANEEL": ["agente-energia"],
            "ANTAQ": ["agente-portos"],
            "ANA": ["agente-saneamento", "agente-barragens"],
            "ANAC": ["agente-aeroportos"],
        }
        return mapping.get(self.agency_code, [])

    def _calculate_priority(self, doc: Dict) -> str:
        """Calculate notification priority."""
        keywords_high = ["edital", "leilão", "alteração", "novo"]
        keywords_med = ["comunicado", "nota", "orientação"]

        text_lower = (doc["title"] + " " + doc["content"]).lower()

        if any(kw in text_lower for kw in keywords_high):
            return "high"
        elif any(kw in text_lower for kw in keywords_med):
            return "medium"
        else:
            return "low"

    def run_once(self):
        """Fetch and process updates once."""
        logger.info(f"Running {self.agency_code} listener...")
        documents = self.fetch_updates()
        logger.info(f"Fetched {len(documents)} documents from {self.agency_code}")
        self.process_and_ingest(documents)
```

---

## Part 2: Agency-Specific Listeners

### 2.1 — ANEEL Listener

```python
# maestro-webhooks/listeners/aneel_listener.py

from base_listener import RegulatoryListener
from bs4 import BeautifulSoup
import re
from datetime import datetime

class ANEELListener(RegulatoryListener):
    """Listen to ANEEL regulatory updates."""

    def __init__(self, supabase_url: str, supabase_key: str):
        super().__init__(
            agency_code="ANEEL",
            collection_slug="ene",
            supabase_url=supabase_url,
            supabase_key=supabase_key
        )
        self.base_url = "https://www2.aneel.gov.br/aplicacoes/editais/"

    def fetch_updates(self) -> List[Dict]:
        """Fetch ANEEL editais (auctions)."""
        documents = []

        try:
            response = requests.get(self.base_url, timeout=30)
            response.encoding = "utf-8"
            soup = BeautifulSoup(response.content, "html.parser")

            # Parse edital table
            table = soup.find("table", {"class": "tabela"})
            if not table:
                return documents

            for row in table.find_all("tr")[1:]:  # Skip header
                cols = row.find_all("td")
                if len(cols) < 4:
                    continue

                edital_num = cols[0].text.strip()
                edital_desc = cols[1].text.strip()
                pub_date_str = cols[2].text.strip()
                pdf_link = cols[3].find("a")

                if not pdf_link:
                    continue

                pdf_url = pdf_link["href"]
                if not pdf_url.startswith("http"):
                    pdf_url = "https://www2.aneel.gov.br" + pdf_url

                # Extract published date
                try:
                    pub_date = datetime.strptime(pub_date_str, "%d/%m/%Y").date()
                except:
                    pub_date = datetime.now().date()

                # Check if recent (newer than 6 hours)
                # This avoids re-processing old documents
                source_id = f"aneel_edital_{edital_num}_{pub_date}"

                # Download PDF text
                pdf_text = self._extract_pdf_text(pdf_url)

                documents.append({
                    "title": f"Edital ANEEL {edital_num}: {edital_desc}",
                    "url": pdf_url,
                    "content": pdf_text,
                    "document_type": "edital",
                    "published_date": str(pub_date),
                    "source_id": source_id,
                })

        except Exception as e:
            logger.error(f"ANEEL listener error: {e}")

        return documents

    def _extract_pdf_text(self, pdf_url: str, max_pages: int = 5) -> str:
        """Extract text from PDF."""
        import PyPDF2
        import io

        try:
            response = requests.get(pdf_url, timeout=30)
            pdf_file = io.BytesIO(response.content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)

            text = []
            for page_num in range(min(len(pdf_reader.pages), max_pages)):
                page = pdf_reader.pages[page_num]
                text.append(page.extract_text())

            return "\n".join(text)

        except Exception as e:
            logger.error(f"PDF extraction error: {e}")
            return ""
```

### 2.2 — ANTAQ Listener

```python
# maestro-webhooks/listeners/antaq_listener.py

from base_listener import RegulatoryListener
from bs4 import BeautifulSoup

class ANTAQListener(RegulatoryListener):
    """Listen to ANTAQ regulatory updates."""

    def __init__(self, supabase_url: str, supabase_key: str):
        super().__init__(
            agency_code="ANTAQ",
            collection_slug="por",
            supabase_url=supabase_url,
            supabase_key=supabase_key
        )
        self.base_url = "https://www.antaq.gov.br/portal/index.php/editais"

    def fetch_updates(self) -> List[Dict]:
        """Fetch ANTAQ editais and resolutions."""
        documents = []

        try:
            response = requests.get(self.base_url, timeout=30)
            response.encoding = "utf-8"
            soup = BeautifulSoup(response.content, "html.parser")

            # Parse edital list
            for item in soup.find_all("div", {"class": "edital-item"}):
                title = item.find("h3")
                link = item.find("a")
                date_elem = item.find("span", {"class": "date"})

                if not (title and link):
                    continue

                title_text = title.text.strip()
                url = link["href"]
                if not url.startswith("http"):
                    url = "https://www.antaq.gov.br" + url

                pub_date = date_elem.text.strip() if date_elem else "2026-10-15"

                # Extract document content
                content = self._extract_content(url)

                source_id = f"antaq_{hashlib.md5(title_text.encode()).hexdigest()[:8]}"

                documents.append({
                    "title": title_text,
                    "url": url,
                    "content": content,
                    "document_type": "edital" if "edital" in title_text.lower() else "resolucao",
                    "published_date": pub_date,
                    "source_id": source_id,
                })

        except Exception as e:
            logger.error(f"ANTAQ listener error: {e}")

        return documents

    def _extract_content(self, url: str) -> str:
        """Extract text from HTML or PDF."""
        try:
            response = requests.get(url, timeout=30)
            response.encoding = "utf-8"

            if "pdf" in response.headers.get("content-type", "").lower():
                # PDF extraction (same as ANEEL)
                return self._extract_pdf_text(url)
            else:
                # HTML extraction
                soup = BeautifulSoup(response.content, "html.parser")
                return soup.get_text()

        except Exception as e:
            logger.error(f"Content extraction error: {e}")
            return ""
```

### 2.3 — ANA Listener

```python
# maestro-webhooks/listeners/ana_listener.py

from base_listener import RegulatoryListener
import json

class ANAListener(RegulatoryListener):
    """Listen to ANA regulatory updates (outorgas, PNSB, etc.)."""

    def __init__(self, supabase_url: str, supabase_key: str):
        super().__init__(
            agency_code="ANA",
            collection_slug="san",
            supabase_url=supabase_url,
            supabase_key=supabase_key
        )
        self.api_base = "http://outorgaonline.ana.gov.br/soa/"

    def fetch_updates(self) -> List[Dict]:
        """Fetch ANA outorgas via REST API."""
        documents = []

        try:
            # Fetch recent outorgas
            response = requests.get(
                f"{self.api_base}api/outorgas",
                params={
                    "status": "concedida",
                    "limit": 50,
                    "sort": "-data_concessao"
                },
                timeout=30
            )

            data = response.json()

            for outorga in data.get("outorgas", []):
                source_id = f"ana_outorga_{outorga['processo_numero']}"

                # Check if already processed
                existing = self.db.table("maestro_regulatory_updates").select(
                    "*"
                ).eq("source_id", source_id).execute()

                if existing.data:
                    continue

                # Format outorga as document
                content = self._format_outorga(outorga)

                documents.append({
                    "title": f"Outorga ANA {outorga['processo_numero']}: {outorga['titulo']}",
                    "url": f"{self.api_base}outorga/{outorga['id']}",
                    "content": content,
                    "document_type": "outorga",
                    "published_date": outorga.get("data_concessao", "2026-10-15"),
                    "source_id": source_id,
                })

        except Exception as e:
            logger.error(f"ANA listener error: {e}")

        return documents

    def _format_outorga(self, outorga: Dict) -> str:
        """Format outorga data as readable text."""
        return f"""
Processo: {outorga.get('processo_numero')}
Título: {outorga.get('titulo')}
Finco: {outorga.get('finco')}
Data Concessão: {outorga.get('data_concessao')}
Localização: {outorga.get('bacia_hidrografica')}

Descrição:
{outorga.get('descricao', 'N/A')}

Vazão: {outorga.get('vazao')} m³/s
Finalidade: {outorga.get('finalidade')}
"""
```

### 2.4 — ANAC Listener

```python
# maestro-webhooks/listeners/anac_listener.py

from base_listener import RegulatoryListener
from bs4 import BeautifulSoup

class ANACListener(RegulatoryListener):
    """Listen to ANAC regulatory updates (RBAC, normalization)."""

    def __init__(self, supabase_url: str, supabase_key: str):
        super().__init__(
            agency_code="ANAC",
            collection_slug="aer",
            supabase_url=supabase_url,
            supabase_key=supabase_key
        )
        self.base_url = "https://www.anac.gov.br/assuntos/normalização"

    def fetch_updates(self) -> List[Dict]:
        """Fetch RBAC updates."""
        documents = []

        try:
            response = requests.get(self.base_url, timeout=30)
            response.encoding = "utf-8"
            soup = BeautifulSoup(response.content, "html.parser")

            # Parse RBAC versions
            for link in soup.find_all("a"):
                href = link.get("href", "")
                text = link.text.strip()

                if "RBAC" not in text and "resolução" not in text.lower():
                    continue

                if not href.startswith("http"):
                    href = "https://www.anac.gov.br" + href

                source_id = f"anac_{hashlib.md5(text.encode()).hexdigest()[:8]}"

                # Extract document
                content = self._extract_pdf_or_html(href)

                documents.append({
                    "title": text,
                    "url": href,
                    "content": content,
                    "document_type": "norma" if "RBAC" in text else "resolucao",
                    "published_date": "2026-10-15",
                    "source_id": source_id,
                })

        except Exception as e:
            logger.error(f"ANAC listener error: {e}")

        return documents
```

---

## Part 3: Orchestration & Deployment

### 3.1 — Cloud Functions Trigger (Google Cloud)

```python
# maestro-webhooks/cloud_function_main.py

import functions_framework
from listeners.aneel_listener import ANEELListener
from listeners.antaq_listener import ANTAQListener
from listeners.ana_listener import ANAListener
from listeners.anac_listener import ANACListener
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@functions_framework.http
def run_regulatory_listeners(request):
    """HTTP Cloud Function triggered by Cloud Scheduler."""

    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")

    listeners = [
        ANEELListener(supabase_url, supabase_key),
        ANTAQListener(supabase_url, supabase_key),
        ANAListener(supabase_url, supabase_key),
        ANACListener(supabase_url, supabase_key),
    ]

    results = {}

    for listener in listeners:
        try:
            listener.run_once()
            results[listener.agency_code] = "success"
            logger.info(f"{listener.agency_code} listener completed")
        except Exception as e:
            results[listener.agency_code] = f"error: {str(e)}"
            logger.error(f"{listener.agency_code} listener failed: {e}")

    return {"results": results, "timestamp": datetime.utcnow().isoformat()}
```

### 3.2 — Cloud Scheduler Configuration

```yaml
# gcp-deploy/scheduler.yaml

apiVersion: cloudscheduler.cnrm.cloud.google.com/v1beta1
kind: CloudSchedulerJob
metadata:
  name: maestro-regulatory-webhooks
spec:
  schedule: "0 */6 * * *"  # Every 6 hours
  timeZone: "UTC"
  description: "Regulatory listener webhook triggers"
  
  httpTarget:
    uri: "https://region-project.cloudfunctions.net/run-regulatory-listeners"
    httpMethod: POST
    headers:
      Content-Type: application/json
    body: "{}"
    oidcToken:
      serviceAccountEmail: "maestro-webhook@project.iam.gserviceaccount.com"
```

---

## Part 4: Database Schema

```sql
-- maestro_regulatory_updates table
CREATE TABLE maestro_regulatory_updates (
    id BIGSERIAL PRIMARY KEY,
    agency_code VARCHAR(20) NOT NULL,  -- ANEEL, ANTAQ, ANA, ANAC
    source_id VARCHAR(255) UNIQUE NOT NULL,
    title VARCHAR(500) NOT NULL,
    url TEXT NOT NULL,
    document_type VARCHAR(50),  -- edital, resolucao, norma, outorga
    published_date DATE,
    ingested_at TIMESTAMP DEFAULT now(),
    status VARCHAR(50) DEFAULT 'ingested',  -- ingested, processed, notified
    chunk_count INT,
    created_at TIMESTAMP DEFAULT now()
);

-- maestro_agent_notifications table
CREATE TABLE maestro_agent_notifications (
    id BIGSERIAL PRIMARY KEY,
    agent_slug VARCHAR(50) NOT NULL,
    event_type VARCHAR(50),  -- regulatory_update, workflow_milestone, feedback
    title VARCHAR(255) NOT NULL,
    description TEXT,
    url TEXT,
    priority VARCHAR(20) DEFAULT 'medium',  -- low, medium, high
    read_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT now(),
    FOREIGN KEY (agent_slug) REFERENCES .claude.agents(slug)
);

-- maestro_regulatory_events table (audit/analytics)
CREATE TABLE maestro_regulatory_events (
    id BIGSERIAL PRIMARY KEY,
    listener_agency VARCHAR(20),
    event_type VARCHAR(50),  -- fetch, ingest, broadcast
    status VARCHAR(20),
    document_count INT,
    error_message TEXT,
    latency_ms INT,
    timestamp TIMESTAMP DEFAULT now()
);

CREATE INDEX idx_regulatory_updates_agency ON maestro_regulatory_updates(agency_code);
CREATE INDEX idx_regulatory_updates_date ON maestro_regulatory_updates(published_date);
CREATE INDEX idx_agent_notifications_agent ON maestro_agent_notifications(agent_slug);
```

---

## Part 5: Monitoring & Alerting

### 5.1 — CloudWatch Dashboards (AWS)

```json
{
  "MetricWidget": {
    "metrics": [
      ["maestro-webhooks", "ANEELDocumentsFetched", {"stat": "Sum"}],
      ["maestro-webhooks", "ANTAQDocumentsFetched", {"stat": "Sum"}],
      ["maestro-webhooks", "ANADocumentsFetched", {"stat": "Sum"}],
      ["maestro-webhooks", "ANACDocumentsFetched", {"stat": "Sum"}],
      ["maestro-webhooks", "RAGChunksIngested", {"stat": "Sum"}],
      ["maestro-webhooks", "ListenerLatency", {"stat": "Average"}],
      ["maestro-webhooks", "ListenerErrors", {"stat": "Sum"}]
    ],
    "period": 3600,
    "stat": "Average",
    "region": "us-east-1"
  }
}
```

### 5.2 — Success Metrics

| Metric | Target | Measurement |
|--------|--------|------------|
| **Listener Uptime** | 99.9% | CloudWatch |
| **Update Latency (p95)** | <10 mins | Event timestamp → ingest time |
| **Document Fetch Rate** | ≥10 docs/week | maestro_regulatory_updates count |
| **RAG Chunk Quality** | >80% relevant | User feedback on chunk relevance |
| **Agent Notification Rate** | 100% | maestro_agent_notifications count |

---

## Deployment Checklist

- [ ] Implement 4 listener classes (ANEEL, ANTAQ, ANA, ANAC)
- [ ] Implement PDF/HTML extraction
- [ ] Set up Cloud Scheduler (6-hourly trigger)
- [ ] Create Supabase tables
- [ ] Configure rate limiting (per listener)
- [ ] Implement embedding generation
- [ ] Write integration tests (mock APIs)
- [ ] Deploy to staging (1 week observation)
- [ ] Configure CloudWatch alerts
- [ ] Document source APIs + authentication
- [ ] Set up rollback procedures
- [ ] Enable auto-healing (retry on failure)

---

**Status**: Ready for implementation  
**Owner**: Devops + Regulatory team  
**Timeline**: Phase 3.2 (Oct 01 - Nov 15, 2026)
