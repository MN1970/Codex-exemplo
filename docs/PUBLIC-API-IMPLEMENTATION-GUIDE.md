# Maestro Public API — Phase 3.1 Implementation Guide

**Target**: `maestro-api/maestro_api/server.py` and `maestro-api/sdk/python/maestro_sdk.py`  
**Framework**: FastAPI (Python 3.9+)  
**Deployment**: Docker + Kubernetes (or Cloud Run)  
**Timeline**: Phase 3.1 (Sep 01 - Sep 30, 2026)

This guide shows how to implement the public REST API for Manta Maestro, enabling partners to route queries and dispatch agents programmatically.

---

## Overview

The Public API provides three core endpoints:

1. **POST /maestro/route** — Identify best agent(s) for a prompt
2. **POST /maestro/ask** — Dispatch prompt to agent and get response
3. **POST /maestro/batch/route** — Route multiple prompts in parallel

All endpoints support:
- Authentication via API key (Bearer token)
- Rate limiting (free/pro/enterprise tiers)
- Structured JSON responses with explanations
- Error handling and retry guidance

---

## Architecture

```
Client (partner app)
  ↓
Maestro Public API (FastAPI server)
  ├── /maestro/route → Router logic (keywords + optionally LLM tie-breaker)
  ├── /maestro/ask → Agent dispatch (calls manta-hub internally)
  ├── /maestro/batch/route → Parallel routing
  └── /maestro/health → Status check
  ↓
Manta Hub (internal agent service)
  ├── Maestro router (keyword matching)
  ├── Orchestrator (ambiguous cases)
  └── Agent dispatch (20 specialized agents)
  ↓
Supabase (metrics logging)
  └── maestro_api_calls, api_rate_limit_log
```

---

## Part 1: FastAPI Server Implementation

### 1.1 — Project Structure

```
maestro-api/
├── maestro_api/
│   ├── __init__.py
│   ├── server.py                  # FastAPI app + routes
│   ├── auth.py                    # API key validation
│   ├── models.py                  # Pydantic request/response schemas
│   ├── router.py                  # Wrapper around manta-hub router
│   ├── agent_dispatcher.py        # Calls agents + caches responses
│   └── metrics.py                 # Logging + rate limiting
├── sdk/
│   └── python/
│       ├── maestro_sdk.py         # Client SDK
│       └── __init__.py
├── tests/
│   ├── test_api_routes.py
│   ├── test_auth.py
│   └── test_rate_limiting.py
├── Dockerfile
├── requirements.txt
└── README.md
```

### 1.2 — Pydantic Models

```python
# maestro_api/models.py

from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from enum import Enum

class RoutingRequest(BaseModel):
    """Input to /maestro/route endpoint."""
    prompt: str = Field(..., min_length=10, max_length=2000)
    top_k: int = Field(default=1, ge=1, le=5)
    include_orchestration: bool = Field(default=False)
    metadata: Optional[Dict[str, str]] = None

class RoutingResponse(BaseModel):
    """Response from /maestro/route endpoint."""
    primary_agent: str
    primary_score: float
    alternatives: List[Dict[str, float]] = []  # [{"agent": "S8", "score": 0.88}, ...]
    is_ambiguous: bool
    explanation: str
    confidence: float
    orchestration_recommended: Optional[bool] = None
    request_id: str

class AskRequest(BaseModel):
    """Input to /maestro/ask endpoint."""
    agent_slug: str
    message: str = Field(..., min_length=10, max_length=5000)
    context: Optional[str] = None
    session_id: Optional[str] = None  # for multi-turn
    streaming: bool = Field(default=False)

class AskResponse(BaseModel):
    """Response from /maestro/ask endpoint."""
    agent_slug: str
    response: str
    tokens: Dict[str, int]  # {"input": 250, "output": 450}
    latency_ms: int
    model_tier: str  # "haiku", "sonnet", "opus"
    request_id: str
    session_id: Optional[str] = None

class BatchRoutingRequest(BaseModel):
    """Input to /maestro/batch/route endpoint."""
    prompts: List[str] = Field(..., min_items=1, max_items=100)
    top_k: int = Field(default=1, ge=1, le=5)

class BatchRoutingResponse(BaseModel):
    """Response from /maestro/batch/route endpoint."""
    results: List[RoutingResponse]
    batch_id: str
    processed_at: str

class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str
    error_code: str
    request_id: str
    retry_after_seconds: Optional[int] = None
```

### 1.3 — Authentication

```python
# maestro_api/auth.py

from typing import Optional
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthCredentials
import os
import hashlib
from datetime import datetime, timedelta

security = HTTPBearer()

class APIKeyValidator:
    """Validate API keys and enforce rate limits."""

    def __init__(self):
        self.valid_keys = {}  # Loaded from Supabase: {"key_hash": {"tier": "pro", "org": "..."}}
        self._load_keys()

    def _load_keys(self):
        """Load valid API keys from Supabase."""
        # In production: query maestro_api_keys table
        # For now: load from environment or secrets
        pass

    def validate_key(self, credentials: HTTPAuthCredentials) -> Dict[str, str]:
        """Validate Bearer token and return metadata."""
        key = credentials.credentials
        key_hash = hashlib.sha256(key.encode()).hexdigest()

        if key_hash not in self.valid_keys:
            raise HTTPException(
                status_code=401,
                detail="Invalid API key"
            )

        metadata = self.valid_keys[key_hash]
        return {
            "api_key_id": key_hash[:16],
            "org": metadata.get("org"),
            "tier": metadata.get("tier", "free"),
            "created_at": metadata.get("created_at"),
        }

async def get_current_user(credentials: HTTPAuthCredentials = Depends(security)) -> Dict[str, str]:
    """Dependency for FastAPI routes."""
    validator = APIKeyValidator()
    return validator.validate_key(credentials)
```

### 1.4 — Rate Limiting

```python
# maestro_api/metrics.py

import time
from datetime import datetime, timedelta
from typing import Dict
import redis  # or use Supabase for persistence

class RateLimiter:
    """Enforce rate limits by API key + tier."""

    # Tier limits: requests per minute
    TIER_LIMITS = {
        "free": 10,
        "pro": 100,
        "enterprise": 1000,
    }

    def __init__(self, redis_client=None):
        self.redis = redis_client or self._init_redis()

    def _init_redis(self):
        """Connect to Redis (or mock for testing)."""
        try:
            import redis
            return redis.Redis(host=os.getenv("REDIS_HOST", "localhost"), port=6379)
        except:
            return None  # Graceful fallback (no rate limiting)

    def check_rate_limit(self, api_key_id: str, tier: str) -> tuple[bool, Dict]:
        """Check if request is within tier limits."""
        limit = self.TIER_LIMITS.get(tier, 10)
        key = f"api:ratelimit:{api_key_id}"

        if self.redis:
            current = self.redis.incr(key)
            self.redis.expire(key, 60)  # Reset every minute

            if current > limit:
                return False, {
                    "remaining": 0,
                    "reset_in_seconds": self.redis.ttl(key),
                }
            return True, {
                "remaining": limit - current,
                "reset_in_seconds": self.redis.ttl(key),
            }
        else:
            # No Redis: allow all (log warning)
            return True, {"remaining": limit, "reset_in_seconds": 60}

class MetricsLogger:
    """Log API calls for monitoring."""

    def __init__(self, supabase_client):
        self.db = supabase_client

    async def log_api_call(
        self,
        request_id: str,
        api_key_id: str,
        endpoint: str,
        prompt_tokens: int,
        response_tokens: int,
        latency_ms: int,
        agent_slug: Optional[str] = None,
        status: str = "success",
    ):
        """Log to maestro_api_calls table."""
        self.db.table("maestro_api_calls").insert({
            "request_id": request_id,
            "api_key_id": api_key_id,
            "endpoint": endpoint,
            "prompt_tokens": prompt_tokens,
            "response_tokens": response_tokens,
            "latency_ms": latency_ms,
            "agent_slug": agent_slug,
            "status": status,
            "timestamp": datetime.utcnow().isoformat(),
        }).execute()
```

### 1.5 — FastAPI Routes

```python
# maestro_api/server.py

from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.responses import StreamingResponse
import uuid
import time
import logging
from datetime import datetime

app = FastAPI(
    title="Maestro Public API",
    version="1.0.0",
    description="Route queries to Manta Maestro agents",
)

# Global instances
rate_limiter = RateLimiter()
metrics_logger = MetricsLogger(supabase_client)

# Import local modules
from .models import (
    RoutingRequest, RoutingResponse, AskRequest, AskResponse,
    BatchRoutingRequest, BatchRoutingResponse, ErrorResponse
)
from .auth import get_current_user
from .router import MaestroRouterClient

router_client = MaestroRouterClient()

# ============================================================================
# ENDPOINT 1: POST /maestro/route
# ============================================================================

@app.post("/maestro/route", response_model=RoutingResponse)
async def route_prompt(
    request: RoutingRequest,
    user: Dict = Depends(get_current_user),
    x_request_id: str = Header(default_factory=lambda: str(uuid.uuid4())),
):
    """
    Route a prompt to the best agent(s).

    Example request:
    ```
    POST /maestro/route
    Authorization: Bearer sk-ant-xxxxx
    Content-Type: application/json

    {
        "prompt": "Preciso projetar UHE com CFRD e LT 500kV",
        "top_k": 2,
        "include_orchestration": false
    }
    ```

    Example response:
    ```json
    {
        "primary_agent": "agente-barragens",
        "primary_score": 0.95,
        "alternatives": [
            {"agent": "agente-energia", "score": 0.88}
        ],
        "is_ambiguous": true,
        "explanation": "Primary: CFRD design expertise. Secondary: LT transmission expertise. Score gap 0.07 < 0.10 suggests multi-agent orchestration.",
        "confidence": 0.92,
        "orchestration_recommended": true,
        "request_id": "req_abc123..."
    }
    ```
    """

    request_id = x_request_id
    start_time = time.time()

    # Check rate limit
    allowed, rate_info = rate_limiter.check_rate_limit(user["api_key_id"], user["tier"])
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Retry after {rate_info['reset_in_seconds']}s",
            headers={
                "Retry-After": str(rate_info["reset_in_seconds"]),
                "X-RateLimit-Remaining": "0",
            }
        )

    try:
        # Call internal router
        result = router_client.route_and_score(request.prompt, top_k=request.top_k)

        primary_agent = result["primary"]
        primary_score = result["score"]
        alternatives = result.get("alternatives", [])

        # Check if ambiguous
        is_ambiguous = False
        orchestration_recommended = False

        if len(alternatives) > 0:
            secondary_score = alternatives[0]["score"]
            score_gap = primary_score - secondary_score
            is_ambiguous = score_gap < 0.10

        if is_ambiguous and request.include_orchestration:
            orchestration_recommended = True

        latency_ms = int((time.time() - start_time) * 1000)

        response = RoutingResponse(
            primary_agent=primary_agent,
            primary_score=primary_score,
            alternatives=alternatives,
            is_ambiguous=is_ambiguous,
            explanation=f"Primary: {primary_agent} (score {primary_score:.2f}). " +
                       (f"Secondary: {alternatives[0]['agent']} (score {alternatives[0]['score']:.2f}). " if alternatives else "") +
                       (f"Score gap {score_gap:.2f} < 0.10; orchestration recommended." if is_ambiguous else ""),
            confidence=0.95 if not is_ambiguous else 0.80,
            orchestration_recommended=orchestration_recommended,
            request_id=request_id,
        )

        # Log metrics (async, non-blocking)
        await metrics_logger.log_api_call(
            request_id=request_id,
            api_key_id=user["api_key_id"],
            endpoint="/maestro/route",
            prompt_tokens=len(request.prompt.split()),
            response_tokens=len(response.explanation.split()),
            latency_ms=latency_ms,
            status="success",
        )

        return response

    except Exception as e:
        logging.error(f"Route error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ============================================================================
# ENDPOINT 2: POST /maestro/ask
# ============================================================================

@app.post("/maestro/ask", response_model=AskResponse)
async def ask_agent(
    request: AskRequest,
    user: Dict = Depends(get_current_user),
    x_request_id: str = Header(default_factory=lambda: str(uuid.uuid4())),
):
    """
    Dispatch a message to a specific agent.

    Example request:
    ```
    POST /maestro/ask
    Authorization: Bearer sk-ant-xxxxx
    Content-Type: application/json

    {
        "agent_slug": "agente-barragens",
        "message": "Qual a altura máxima recomendada para CFRD?",
        "session_id": "sess_xyz789"
    }
    ```

    Example response:
    ```json
    {
        "agent_slug": "agente-barragens",
        "response": "A altura máxima de CFRD depende...",
        "tokens": {"input": 45, "output": 280},
        "latency_ms": 1240,
        "model_tier": "sonnet",
        "request_id": "req_def456...",
        "session_id": "sess_xyz789"
    }
    ```
    """

    request_id = x_request_id
    start_time = time.time()

    # Rate limiting
    allowed, rate_info = rate_limiter.check_rate_limit(user["api_key_id"], user["tier"])
    if not allowed:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    try:
        # Dispatch to agent
        agent_response = router_client.dispatch_agent(
            agent_slug=request.agent_slug,
            prompt=request.message,
            context=request.context,
            session_id=request.session_id,
        )

        latency_ms = int((time.time() - start_time) * 1000)

        response = AskResponse(
            agent_slug=request.agent_slug,
            response=agent_response["content"],
            tokens=agent_response.get("tokens", {"input": 0, "output": 0}),
            latency_ms=latency_ms,
            model_tier=agent_response.get("model_tier", "sonnet"),
            request_id=request_id,
            session_id=request.session_id,
        )

        # Log metrics
        await metrics_logger.log_api_call(
            request_id=request_id,
            api_key_id=user["api_key_id"],
            endpoint="/maestro/ask",
            prompt_tokens=len(request.message.split()),
            response_tokens=agent_response.get("tokens", {}).get("output", 0),
            latency_ms=latency_ms,
            agent_slug=request.agent_slug,
            status="success",
        )

        return response

    except Exception as e:
        logging.error(f"Ask error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ============================================================================
# ENDPOINT 3: POST /maestro/batch/route
# ============================================================================

@app.post("/maestro/batch/route", response_model=BatchRoutingResponse)
async def batch_route(
    request: BatchRoutingRequest,
    user: Dict = Depends(get_current_user),
    x_request_id: str = Header(default_factory=lambda: str(uuid.uuid4())),
):
    """
    Route multiple prompts in parallel.

    Example request:
    ```
    POST /maestro/batch/route
    Authorization: Bearer sk-ant-xxxxx
    Content-Type: application/json

    {
        "prompts": [
            "Preciso de uma ETA para saneamento",
            "Como dimensionar uma LT 500kV?",
            "Qual a profundidade ideal de dragagem?"
        ],
        "top_k": 1
    }
    ```
    """

    request_id = x_request_id
    batch_id = str(uuid.uuid4())
    start_time = time.time()

    # Rate limiting (batch counts as N requests)
    allowed, rate_info = rate_limiter.check_rate_limit(user["api_key_id"], user["tier"])
    if not allowed:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    try:
        # Route in parallel
        import asyncio
        tasks = [
            asyncio.create_task(
                asyncio.to_thread(
                    router_client.route_and_score,
                    prompt,
                    request.top_k
                )
            )
            for prompt in request.prompts
        ]

        results_data = await asyncio.gather(*tasks)

        # Build responses
        results = [
            RoutingResponse(
                primary_agent=r["primary"],
                primary_score=r["score"],
                alternatives=r.get("alternatives", []),
                is_ambiguous=False,  # Simplified
                explanation=f"Routed to {r['primary']}",
                confidence=r["score"],
                request_id=f"{request_id}:{i}",
            )
            for i, r in enumerate(results_data)
        ]

        latency_ms = int((time.time() - start_time) * 1000)

        response = BatchRoutingResponse(
            results=results,
            batch_id=batch_id,
            processed_at=datetime.utcnow().isoformat(),
        )

        # Log metrics
        await metrics_logger.log_api_call(
            request_id=batch_id,
            api_key_id=user["api_key_id"],
            endpoint="/maestro/batch/route",
            prompt_tokens=sum(len(p.split()) for p in request.prompts),
            response_tokens=len(response.results) * 50,  # Estimate
            latency_ms=latency_ms,
            status="success",
        )

        return response

    except Exception as e:
        logging.error(f"Batch route error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/maestro/health")
async def health_check():
    """Service health status."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
    }

# ============================================================================
# ERROR HANDLER
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return {
        "error": exc.detail,
        "error_code": str(exc.status_code),
        "request_id": request.headers.get("x-request-id", "unknown"),
        "retry_after_seconds": exc.headers.get("Retry-After"),
    }
```

---

## Part 2: Python SDK

### 2.1 — SDK Implementation

```python
# sdk/python/maestro_sdk.py

import requests
import json
from typing import List, Dict, Optional
import time

class MaestroClient:
    """Python SDK for Maestro Public API."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.maestro.manta-associados.com",
        timeout: int = 30,
    ):
        """
        Initialize client.

        Args:
            api_key: API key from Maestro dashboard
            base_url: API endpoint (default: production)
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        })

    def route(
        self,
        prompt: str,
        top_k: int = 1,
        include_orchestration: bool = False,
    ) -> Dict:
        """
        Route a prompt to the best agent(s).

        Args:
            prompt: User query (10-2000 chars)
            top_k: Number of alternatives to return (1-5)
            include_orchestration: If true, enable orchestration for ambiguous queries

        Returns:
            {
                "primary_agent": "agente-saneamento",
                "primary_score": 0.95,
                "alternatives": [...],
                "is_ambiguous": False,
                "explanation": "...",
                "request_id": "req_..."
            }
        """
        response = self.session.post(
            f"{self.base_url}/maestro/route",
            json={
                "prompt": prompt,
                "top_k": top_k,
                "include_orchestration": include_orchestration,
            },
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    def ask(
        self,
        agent_slug: str,
        message: str,
        context: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> Dict:
        """
        Ask a specific agent a question.

        Args:
            agent_slug: Agent ID (e.g., "agente-barragens")
            message: Question or prompt
            context: Optional context from previous turns
            session_id: Optional session ID for multi-turn conversation

        Returns:
            {
                "agent_slug": "agente-barragens",
                "response": "...",
                "tokens": {"input": 250, "output": 450},
                "latency_ms": 1240,
                "model_tier": "sonnet",
                "request_id": "req_..."
            }
        """
        response = self.session.post(
            f"{self.base_url}/maestro/ask",
            json={
                "agent_slug": agent_slug,
                "message": message,
                "context": context,
                "session_id": session_id,
            },
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    def batch_route(
        self,
        prompts: List[str],
        top_k: int = 1,
    ) -> Dict:
        """
        Route multiple prompts in parallel.

        Args:
            prompts: List of prompts (1-100 items)
            top_k: Number of alternatives per prompt

        Returns:
            {
                "results": [...],
                "batch_id": "batch_...",
                "processed_at": "2026-09-15T10:30:00Z"
            }
        """
        response = self.session.post(
            f"{self.base_url}/maestro/batch/route",
            json={
                "prompts": prompts,
                "top_k": top_k,
            },
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    def health(self) -> Dict:
        """Check API health."""
        response = self.session.get(
            f"{self.base_url}/maestro/health",
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()
```

### 2.2 — SDK Usage Examples

```python
# examples/basic_routing.py

from maestro_sdk import MaestroClient

# Initialize client
client = MaestroClient(api_key="sk-ant-your-key-here")

# Example 1: Route a prompt
result = client.route(
    prompt="Preciso projetar uma UHE com CFRD e LT 500kV até SE"
)
print(f"Primary agent: {result['primary_agent']}")
print(f"Score: {result['primary_score']:.2f}")
print(f"Explanation: {result['explanation']}")

# Example 2: Ask a specific agent
response = client.ask(
    agent_slug="agente-barragens",
    message="Qual a altura máxima recomendada para CFRD em clima tropical?",
    session_id="sess_user123"
)
print(f"Agent response: {response['response']}")
print(f"Latency: {response['latency_ms']}ms")

# Example 3: Multi-turn conversation
session_id = "sess_user456"

q1 = client.ask(
    agent_slug="agente-energia",
    message="Como funciona leilão de transmissão?",
    session_id=session_id,
)
print(f"Q1 Response: {q1['response']}")

q2 = client.ask(
    agent_slug="agente-energia",
    message="E qual é a penalidade por atraso de obra?",
    session_id=session_id,
    context=q1['response'],  # Include previous response
)
print(f"Q2 Response (with context): {q2['response']}")

# Example 4: Batch routing
prompts = [
    "Preciso de saneamento básico para 100k habitantes",
    "Como dimensionar uma subestação 138/69kV?",
    "Qual a profundidade para ancoragem de plataforma?",
]

batch = client.batch_route(prompts)
for i, result in enumerate(batch['results']):
    print(f"Prompt {i+1}: {result['primary_agent']} (score: {result['primary_score']:.2f})")
```

---

## Part 3: Database Schema (Supabase)

```sql
-- maestro_api_keys table
CREATE TABLE maestro_api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key_hash VARCHAR(64) UNIQUE NOT NULL,
    org_name VARCHAR(255) NOT NULL,
    tier VARCHAR(20) DEFAULT 'free' CHECK (tier IN ('free', 'pro', 'enterprise')),
    created_at TIMESTAMP DEFAULT now(),
    last_used_at TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    created_by UUID REFERENCES auth.users(id),
    UNIQUE(key_hash)
);

-- maestro_api_calls table
CREATE TABLE maestro_api_calls (
    id BIGSERIAL PRIMARY KEY,
    request_id UUID UNIQUE NOT NULL,
    api_key_id VARCHAR(16) NOT NULL,
    endpoint VARCHAR(50) NOT NULL,
    prompt_tokens INT,
    response_tokens INT,
    latency_ms INT,
    agent_slug VARCHAR(50),
    status VARCHAR(20) DEFAULT 'success',
    timestamp TIMESTAMP DEFAULT now(),
    FOREIGN KEY (api_key_id) REFERENCES maestro_api_keys(id)
);

-- maestro_api_usage table (for billing)
CREATE TABLE maestro_api_usage (
    id BIGSERIAL PRIMARY KEY,
    api_key_id VARCHAR(16),
    billing_month DATE,
    endpoint_calls INT DEFAULT 0,
    total_input_tokens BIGINT DEFAULT 0,
    total_output_tokens BIGINT DEFAULT 0,
    total_latency_ms BIGINT DEFAULT 0,
    cost_usd DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT now(),
    FOREIGN KEY (api_key_id) REFERENCES maestro_api_keys(id)
);

CREATE INDEX idx_api_calls_timestamp ON maestro_api_calls(timestamp);
CREATE INDEX idx_api_calls_api_key_id ON maestro_api_calls(api_key_id);
```

---

## Part 4: Deployment

### 4.1 — Docker

```dockerfile
# Dockerfile

FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY maestro_api/ ./maestro_api/
COPY sdk/ ./sdk/

CMD ["uvicorn", "maestro_api.server:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 4.2 — Kubernetes

```yaml
# k8s/deployment.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: maestro-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: maestro-api
  template:
    metadata:
      labels:
        app: maestro-api
    spec:
      containers:
      - name: maestro-api
        image: maestro-api:1.0.0
        ports:
        - containerPort: 8000
        env:
        - name: REDIS_HOST
          valueFrom:
            secretKeyRef:
              name: maestro-secrets
              key: redis-host
        - name: SUPABASE_URL
          valueFrom:
            secretKeyRef:
              name: maestro-secrets
              key: supabase-url
        - name: SUPABASE_ANON_KEY
          valueFrom:
            secretKeyRef:
              name: maestro-secrets
              key: supabase-anon-key
        livenessProbe:
          httpGet:
            path: /maestro/health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: maestro-api-service
spec:
  type: LoadBalancer
  selector:
    app: maestro-api
  ports:
  - port: 80
    targetPort: 8000
```

---

## Part 5: OpenAPI Specification

```yaml
# openapi.yaml

openapi: 3.0.0
info:
  title: Maestro Public API
  version: 1.0.0
  description: Route queries to Manta Maestro specialized agents
  contact:
    name: Manta Support
    email: support@manta-associados.com

servers:
  - url: https://api.maestro.manta-associados.com
    description: Production

paths:
  /maestro/route:
    post:
      summary: Route a prompt to the best agent(s)
      operationId: routePrompt
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/RoutingRequest'
      responses:
        '200':
          description: Routing result
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/RoutingResponse'
        '429':
          description: Rate limit exceeded
        '401':
          description: Unauthorized (invalid API key)

  /maestro/ask:
    post:
      summary: Dispatch a message to a specific agent
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
    RoutingRequest:
      type: object
      required:
        - prompt
      properties:
        prompt:
          type: string
          minLength: 10
          maxLength: 2000
        top_k:
          type: integer
          minimum: 1
          maximum: 5
          default: 1
        include_orchestration:
          type: boolean
          default: false

    RoutingResponse:
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
            properties:
              agent:
                type: string
              score:
                type: number
        is_ambiguous:
          type: boolean
        explanation:
          type: string
        confidence:
          type: number
        request_id:
          type: string
          format: uuid
```

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **API Latency (p95)** | <500ms | CloudWatch/Datadog |
| **Availability** | 99.9% | Uptime monitoring |
| **Rate Limit Compliance** | 100% | API call logs |
| **Error Rate** | <0.5% | HTTP 5xx rate |
| **Partner Adoption** | ≥2 partners | Known integrations |

---

## Deployment Checklist

- [ ] Implement FastAPI server with 3 endpoints
- [ ] Implement Python SDK (PyPI package)
- [ ] Set up Redis for rate limiting
- [ ] Create Supabase tables (api_keys, api_calls, usage)
- [ ] Configure authentication (API key validation)
- [ ] Write unit tests (>80% coverage)
- [ ] Deploy to staging environment
- [ ] Load test (100 concurrent users × 100 requests)
- [ ] Configure CloudFlare DNS + SSL
- [ ] Document in swagger.io
- [ ] Publish Python SDK to PyPI
- [ ] Create onboarding guide for partners
- [ ] Monitor for 30 days before GA

---

**Status**: Ready for implementation  
**Owner**: Backend team (maestro-api repo)  
**Timeline**: Phase 3.1 (Sep 01 - Sep 30, 2026)
