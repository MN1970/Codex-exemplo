# Conversation API — Phase 3.3 Implementation Guide

**Target**: `maestro-api/maestro_api/conversations.py`  
**Framework**: FastAPI (extends Phase 3.1 Public API)  
**Feature**: Multi-turn sessions with context preservation  
**Timeline**: Phase 3.3 (Nov 16 - Dec 31, 2026)

This guide implements stateful conversations for Maestro agents, enabling multi-turn interactions with context awareness.

---

## Overview

```
User Session
  ├── Session ID (unique per user + agent)
  ├── Turn 1: "How to design ETA?"
  │    ├── Agent response (stored)
  │    ├── Tokens: input=45, output=280
  │    └── Context window: full response
  ├── Turn 2: "What about chemical treatment?" (can reference previous)
  │    ├── Retrieved context: embedding similarity to previous turns
  │    ├── Agent response with context
  │    └── Context window: last 2 turns + relevant chunks
  └── Turn N: conversation continues...
  ↓
Stored in maestro_conversations table with:
  - session_id (UUID)
  - agent_slug
  - user_id
  - turns (array of turn objects)
  - token_usage (cumulative)
  - created_at, updated_at
```

---

## Part 1: Data Models

```python
# maestro_api/models.py (EXTENSIONS)

from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum

class ConversationRole(str, Enum):
    """Role in conversation."""
    USER = "user"
    AGENT = "agent"
    SYSTEM = "system"

class ConversationTurn(BaseModel):
    """Single turn in a conversation."""
    turn_number: int
    role: ConversationRole
    content: str
    tokens: Dict[str, int] = {"input": 0, "output": 0}
    timestamp: datetime
    embedding: Optional[List[float]] = None  # For semantic search

class CreateSessionRequest(BaseModel):
    """Create a new conversation session."""
    agent_slug: str
    user_id: str = Field(..., min_length=1, max_length=255)
    metadata: Optional[Dict[str, str]] = None

class SessionResponse(BaseModel):
    """Conversation session response."""
    session_id: str
    agent_slug: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    token_usage: Dict[str, int]  # {"total_input": 1000, "total_output": 2500}
    turn_count: int

class ConversationTurnRequest(BaseModel):
    """Send a message in conversation."""
    session_id: str
    message: str = Field(..., min_length=1, max_length=5000)
    context_window: int = Field(default=5, ge=1, le=20)  # Number of previous turns to include

class ConversationTurnResponse(BaseModel):
    """Response to conversation turn."""
    session_id: str
    turn_number: int
    user_message: str
    agent_response: str
    tokens: Dict[str, int]
    retrieved_context: Optional[List[str]] = None  # Relevant previous turns
    latency_ms: int
    timestamp: datetime

class ConversationHistoryResponse(BaseModel):
    """Full conversation history."""
    session_id: str
    agent_slug: str
    turns: List[ConversationTurn]
    token_usage: Dict[str, int]
    created_at: datetime
```

---

## Part 2: Session Management

```python
# maestro_api/conversations.py

from datetime import datetime, timedelta
from typing import List, Optional, Dict
import uuid
import logging
from supabase import create_client
from anthropic import Anthropic
import numpy as np

logger = logging.getLogger(__name__)

class ConversationManager:
    """Manage multi-turn conversations with context."""

    def __init__(self, supabase_url: str, supabase_key: str):
        self.db = create_client(supabase_url, supabase_key)
        self.anthropic = Anthropic()
        self.max_context_tokens = 2000

    # ======================================================================
    # SESSION CRUD
    # ======================================================================

    def create_session(
        self,
        agent_slug: str,
        user_id: str,
        metadata: Optional[Dict] = None,
    ) -> Dict:
        """Create new conversation session."""
        session_id = str(uuid.uuid4())

        result = self.db.table("maestro_conversations").insert({
            "session_id": session_id,
            "agent_slug": agent_slug,
            "user_id": user_id,
            "metadata": metadata or {},
            "token_usage": {"total_input": 0, "total_output": 0},
            "turn_count": 0,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }).execute()

        return {
            "session_id": session_id,
            "agent_slug": agent_slug,
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
            "token_usage": {"total_input": 0, "total_output": 0},
            "turn_count": 0,
        }

    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session details."""
        result = self.db.table("maestro_conversations").select(
            "*"
        ).eq("session_id", session_id).execute()

        return result.data[0] if result.data else None

    def list_sessions(
        self,
        user_id: str,
        agent_slug: Optional[str] = None,
        limit: int = 10,
    ) -> List[Dict]:
        """List sessions for a user."""
        query = self.db.table("maestro_conversations").select(
            "session_id, agent_slug, created_at, turn_count, token_usage"
        ).eq("user_id", user_id)

        if agent_slug:
            query = query.eq("agent_slug", agent_slug)

        query = query.order("created_at", desc=True).limit(limit)
        result = query.execute()

        return result.data

    def delete_session(self, session_id: str) -> bool:
        """Delete session and all turns (right-to-erasure)."""
        # Delete turns first
        self.db.table("maestro_conversation_turns").delete().eq(
            "session_id", session_id
        ).execute()

        # Delete session
        self.db.table("maestro_conversations").delete().eq(
            "session_id", session_id
        ).execute()

        return True

    # ======================================================================
    # TURN MANAGEMENT
    # ======================================================================

    def add_turn(
        self,
        session_id: str,
        user_message: str,
        agent_response: str,
        tokens: Dict[str, int],
    ) -> Dict:
        """Add turn to conversation."""
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        turn_number = session["turn_count"] + 1

        # Generate embedding for user message
        user_embedding = self._generate_embedding(user_message)

        # Store turn
        self.db.table("maestro_conversation_turns").insert({
            "session_id": session_id,
            "turn_number": turn_number,
            "user_message": user_message,
            "user_embedding": user_embedding,
            "agent_response": agent_response,
            "tokens_input": tokens.get("input", 0),
            "tokens_output": tokens.get("output", 0),
            "created_at": datetime.utcnow().isoformat(),
        }).execute()

        # Update session
        new_token_usage = {
            "total_input": session["token_usage"]["total_input"] + tokens.get("input", 0),
            "total_output": session["token_usage"]["total_output"] + tokens.get("output", 0),
        }

        self.db.table("maestro_conversations").update({
            "turn_count": turn_number,
            "token_usage": new_token_usage,
            "updated_at": datetime.utcnow().isoformat(),
        }).eq("session_id", session_id).execute()

        return {
            "session_id": session_id,
            "turn_number": turn_number,
            "tokens": tokens,
        }

    def get_turns(self, session_id: str, limit: int = 50) -> List[Dict]:
        """Get conversation turns."""
        result = self.db.table("maestro_conversation_turns").select(
            "*"
        ).eq("session_id", session_id).order("turn_number", desc=False).limit(limit).execute()

        return result.data

    # ======================================================================
    # CONTEXT RETRIEVAL
    # ======================================================================

    def retrieve_context(
        self,
        session_id: str,
        current_message: str,
        context_window: int = 5,
        similarity_threshold: float = 0.7,
    ) -> List[str]:
        """
        Retrieve relevant context from previous turns via semantic similarity.

        Args:
            session_id: Session ID
            current_message: Current user message
            context_window: Max turns to retrieve
            similarity_threshold: Min cosine similarity to include (0-1)

        Returns:
            List of relevant previous turns (formatted as strings)
        """
        # Get all turns
        turns = self.get_turns(session_id)
        if len(turns) == 0:
            return []

        # Generate embedding for current message
        current_embedding = self._generate_embedding(current_message)
        if not current_embedding:
            return []

        # Calculate similarity to all previous turns
        similarities = []
        for turn in turns:
            if not turn.get("user_embedding"):
                continue

            similarity = self._cosine_similarity(
                current_embedding,
                turn["user_embedding"]
            )
            similarities.append({
                "turn_number": turn["turn_number"],
                "user_message": turn["user_message"],
                "agent_response": turn["agent_response"],
                "similarity": similarity,
            })

        # Filter by threshold and sort by similarity
        relevant = [
            s for s in similarities
            if s["similarity"] >= similarity_threshold
        ]
        relevant.sort(key=lambda x: x["similarity"], reverse=True)

        # Format as strings
        context_items = relevant[:context_window]
        formatted_context = []

        for item in context_items:
            formatted_context.append(
                f"Previous turn (relevance: {item['similarity']:.2f}):\n"
                f"Q: {item['user_message']}\n"
                f"A: {item['agent_response']}"
            )

        return formatted_context

    def _generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding for text."""
        try:
            response = self.anthropic.embeddings.create(
                model="text-embedding-3-small",
                input=text[:3000],
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Embedding generation error: {e}")
            return None

    def _cosine_similarity(
        self,
        vec1: List[float],
        vec2: List[float],
    ) -> float:
        """Calculate cosine similarity between two vectors."""
        arr1 = np.array(vec1)
        arr2 = np.array(vec2)

        dot_product = np.dot(arr1, arr2)
        norm1 = np.linalg.norm(arr1)
        norm2 = np.linalg.norm(arr2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return float(dot_product / (norm1 * norm2))

    # ======================================================================
    # BUILD CONTEXT WINDOW
    # ======================================================================

    def build_context_window(
        self,
        session_id: str,
        current_message: str,
        context_window: int = 5,
    ) -> str:
        """
        Build context string for agent prompt.

        Returns formatted string with:
        1. Last N turns (recency)
        2. Similar previous turns (semantic relevance)
        """
        turns = self.get_turns(session_id, limit=context_window)

        # Recent context: last N turns
        recent_context = []
        for turn in turns[-context_window:]:
            recent_context.append(
                f"Q: {turn['user_message']}\nA: {turn['agent_response']}"
            )

        # Semantic context: similar previous turns
        semantic_context = self.retrieve_context(
            session_id,
            current_message,
            context_window=3,
        )

        # Combine
        context_parts = []

        if recent_context:
            context_parts.append("## Recent Context\n" + "\n---\n".join(recent_context))

        if semantic_context:
            context_parts.append("## Related Previous Conversations\n" + "\n---\n".join(semantic_context))

        return "\n\n".join(context_parts)
```

---

## Part 3: API Endpoints

```python
# maestro_api/server.py (EXTENSIONS for conversations)

from fastapi import HTTPException, Path
from .conversations import ConversationManager

conv_manager = ConversationManager(
    supabase_url=os.getenv("SUPABASE_URL"),
    supabase_key=os.getenv("SUPABASE_ANON_KEY")
)

# ============================================================================
# ENDPOINT: POST /maestro/conversations (create session)
# ============================================================================

@app.post("/maestro/conversations", response_model=SessionResponse)
async def create_conversation(
    request: CreateSessionRequest,
    user: Dict = Depends(get_current_user),
):
    """
    Create a new conversation session with an agent.

    Example request:
    ```
    POST /maestro/conversations
    Authorization: Bearer sk-ant-xxxxx

    {
        "agent_slug": "agente-saneamento",
        "user_id": "user@company.com",
        "metadata": {"project": "AySA-2026"}
    }
    ```

    Example response:
    ```json
    {
        "session_id": "sess_abc123...",
        "agent_slug": "agente-saneamento",
        "user_id": "user@company.com",
        "created_at": "2026-11-16T10:30:00Z",
        "updated_at": "2026-11-16T10:30:00Z",
        "token_usage": {"total_input": 0, "total_output": 0},
        "turn_count": 0
    }
    ```
    """
    result = conv_manager.create_session(
        agent_slug=request.agent_slug,
        user_id=request.user_id,
        metadata=request.metadata,
    )

    return SessionResponse(**result)

# ============================================================================
# ENDPOINT: GET /maestro/conversations/{session_id}
# ============================================================================

@app.get("/maestro/conversations/{session_id}", response_model=SessionResponse)
async def get_conversation(
    session_id: str = Path(...),
    user: Dict = Depends(get_current_user),
):
    """Get conversation session details."""
    session = conv_manager.get_session(session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return SessionResponse(**session)

# ============================================================================
# ENDPOINT: GET /maestro/conversations (list sessions)
# ============================================================================

@app.get("/maestro/conversations", response_model=List[Dict])
async def list_conversations(
    agent_slug: Optional[str] = None,
    limit: int = 10,
    user: Dict = Depends(get_current_user),
):
    """List conversation sessions for current user."""
    sessions = conv_manager.list_sessions(
        user_id=user["api_key_id"],
        agent_slug=agent_slug,
        limit=limit,
    )
    return sessions

# ============================================================================
# ENDPOINT: POST /maestro/conversations/{session_id}/turns (send message)
# ============================================================================

@app.post("/maestro/conversations/{session_id}/turns", response_model=ConversationTurnResponse)
async def send_message(
    session_id: str = Path(...),
    request: ConversationTurnRequest = None,
    user: Dict = Depends(get_current_user),
    x_request_id: str = Header(default_factory=lambda: str(uuid.uuid4())),
):
    """
    Send a message in a conversation.

    Example request:
    ```
    POST /maestro/conversations/sess_abc123/turns
    Authorization: Bearer sk-ant-xxxxx

    {
        "message": "E qual a profundidade mínima para o reservatório?",
        "context_window": 5
    }
    ```

    Example response:
    ```json
    {
        "session_id": "sess_abc123",
        "turn_number": 2,
        "user_message": "E qual a profundidade...",
        "agent_response": "A profundidade mínima depende...",
        "tokens": {"input": 120, "output": 350},
        "retrieved_context": ["Previous turn (relevance: 0.92)..."],
        "latency_ms": 1240,
        "timestamp": "2026-11-16T10:35:00Z"
    }
    ```
    """

    request_id = x_request_id
    start_time = time.time()

    # Get session
    session = conv_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Retrieve context
    context_items = conv_manager.retrieve_context(
        session_id,
        request.message,
        context_window=request.context_window,
    )

    context_str = "\n\n".join(context_items) if context_items else ""

    # Build system prompt with context
    system_prompt = f"""You are {session['agent_slug']}, a specialized Manta Maestro agent.
Your previous conversation:

{context_str}

Continue this conversation naturally, referencing previous context when relevant."""

    # Dispatch agent
    try:
        response = router_client.dispatch_agent(
            agent_slug=session["agent_slug"],
            prompt=request.message,
            context=context_str,
            session_id=session_id,
        )

        latency_ms = int((time.time() - start_time) * 1000)

        # Store turn
        conv_manager.add_turn(
            session_id=session_id,
            user_message=request.message,
            agent_response=response["content"],
            tokens=response.get("tokens", {"input": 0, "output": 0}),
        )

        result = ConversationTurnResponse(
            session_id=session_id,
            turn_number=session["turn_count"] + 1,
            user_message=request.message,
            agent_response=response["content"],
            tokens=response.get("tokens", {"input": 0, "output": 0}),
            retrieved_context=context_items,
            latency_ms=latency_ms,
            timestamp=datetime.utcnow(),
        )

        # Log metrics
        await metrics_logger.log_api_call(
            request_id=request_id,
            api_key_id=user["api_key_id"],
            endpoint="/maestro/conversations/{session_id}/turns",
            prompt_tokens=len(request.message.split()) + len(context_str.split()),
            response_tokens=response.get("tokens", {}).get("output", 0),
            latency_ms=latency_ms,
            agent_slug=session["agent_slug"],
            status="success",
        )

        return result

    except Exception as e:
        logging.error(f"Conversation turn error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ============================================================================
# ENDPOINT: GET /maestro/conversations/{session_id}/history
# ============================================================================

@app.get("/maestro/conversations/{session_id}/history", response_model=ConversationHistoryResponse)
async def get_conversation_history(
    session_id: str = Path(...),
    user: Dict = Depends(get_current_user),
):
    """Get full conversation history."""
    session = conv_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    turns = conv_manager.get_turns(session_id)

    # Format turns
    formatted_turns = [
        ConversationTurn(
            turn_number=turn["turn_number"],
            role=ConversationRole.USER,
            content=turn["user_message"],
            tokens={"input": turn["tokens_input"], "output": 0},
            timestamp=datetime.fromisoformat(turn["created_at"]),
        ) for turn in turns
    ] + [
        ConversationTurn(
            turn_number=turn["turn_number"],
            role=ConversationRole.AGENT,
            content=turn["agent_response"],
            tokens={"input": 0, "output": turn["tokens_output"]},
            timestamp=datetime.fromisoformat(turn["created_at"]),
        ) for turn in turns
    ]

    formatted_turns.sort(key=lambda x: (x.turn_number, x.role.value))

    return ConversationHistoryResponse(
        session_id=session_id,
        agent_slug=session["agent_slug"],
        turns=formatted_turns,
        token_usage=session["token_usage"],
        created_at=datetime.fromisoformat(session["created_at"]),
    )

# ============================================================================
# ENDPOINT: DELETE /maestro/conversations/{session_id}
# ============================================================================

@app.delete("/maestro/conversations/{session_id}")
async def delete_conversation(
    session_id: str = Path(...),
    user: Dict = Depends(get_current_user),
):
    """Delete conversation (right-to-erasure)."""
    session = conv_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    conv_manager.delete_session(session_id)

    return {
        "message": "Conversation deleted",
        "session_id": session_id,
    }
```

---

## Part 4: Database Schema

```sql
-- maestro_conversations table
CREATE TABLE maestro_conversations (
    id BIGSERIAL PRIMARY KEY,
    session_id UUID UNIQUE NOT NULL,
    agent_slug VARCHAR(50) NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    metadata JSONB,
    token_usage JSONB DEFAULT '{"total_input": 0, "total_output": 0}',
    turn_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now()
);

-- maestro_conversation_turns table
CREATE TABLE maestro_conversation_turns (
    id BIGSERIAL PRIMARY KEY,
    session_id UUID NOT NULL,
    turn_number INT NOT NULL,
    user_message TEXT NOT NULL,
    user_embedding VECTOR(1536),  -- pgvector
    agent_response TEXT NOT NULL,
    tokens_input INT DEFAULT 0,
    tokens_output INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT now(),
    FOREIGN KEY (session_id) REFERENCES maestro_conversations(session_id),
    UNIQUE(session_id, turn_number)
);

CREATE INDEX idx_conversations_user_id ON maestro_conversations(user_id);
CREATE INDEX idx_conversations_agent_slug ON maestro_conversations(agent_slug);
CREATE INDEX idx_turns_session_id ON maestro_conversation_turns(session_id);
CREATE INDEX idx_turns_user_embedding ON maestro_conversation_turns USING ivfflat (user_embedding vector_cosine_ops);
```

---

## Part 5: Python SDK Extension

```python
# sdk/python/maestro_sdk.py (EXTENSIONS)

class MaestroConversationClient:
    """SDK for Maestro Conversation API."""

    def __init__(self, api_key: str, base_url: str = "https://api.maestro.manta-associados.com"):
        self.base_client = MaestroClient(api_key, base_url)
        self.session = self.base_client.session

    def create_session(
        self,
        agent_slug: str,
        user_id: str,
        metadata: Optional[Dict] = None,
    ) -> Dict:
        """Create a conversation session."""
        response = self.session.post(
            f"{self.base_client.base_url}/maestro/conversations",
            json={
                "agent_slug": agent_slug,
                "user_id": user_id,
                "metadata": metadata or {},
            },
        )
        response.raise_for_status()
        return response.json()

    def send_message(
        self,
        session_id: str,
        message: str,
        context_window: int = 5,
    ) -> Dict:
        """Send a message in a conversation."""
        response = self.session.post(
            f"{self.base_client.base_url}/maestro/conversations/{session_id}/turns",
            json={
                "message": message,
                "context_window": context_window,
            },
        )
        response.raise_for_status()
        return response.json()

    def get_history(self, session_id: str) -> Dict:
        """Get conversation history."""
        response = self.session.get(
            f"{self.base_client.base_url}/maestro/conversations/{session_id}/history"
        )
        response.raise_for_status()
        return response.json()

# Example usage
client = MaestroConversationClient(api_key="sk-ant-...")

# Create session
session = client.create_session(
    agent_slug="agente-saneamento",
    user_id="user@company.com",
)
session_id = session["session_id"]

# Multi-turn conversation
q1 = client.send_message(session_id, "Como dimensionar uma ETA?")
print(f"Turn 1: {q1['agent_response'][:200]}...")

q2 = client.send_message(
    session_id,
    "E qual é o tempo de retenção ideal para floculação?"
)
print(f"Turn 2: {q2['agent_response'][:200]}...")
print(f"Retrieved context: {q2.get('retrieved_context', [])}")

# Get full history
history = client.get_history(session_id)
print(f"Total turns: {len(history['turns'])}")
print(f"Total tokens: {history['token_usage']}")
```

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|------------|
| **Session Creation Latency** | <500ms | API response time |
| **Turn Add Latency** | <1500ms | Dispatch + embedding + storage |
| **Context Retrieval Accuracy** | >80% | User satisfaction survey |
| **Embedding Quality** | >0.7 avg similarity | Semantic relevance |
| **Session Reuse Rate** | >40% | Sessions with 2+ turns |

---

## Deployment Checklist

- [ ] Add pgvector extension to Supabase
- [ ] Create maestro_conversations table
- [ ] Create maestro_conversation_turns table
- [ ] Implement ConversationManager class
- [ ] Add 5 conversation endpoints (CRUD + turns)
- [ ] Implement semantic context retrieval
- [ ] Write integration tests
- [ ] Deploy to staging
- [ ] Load test (100 concurrent sessions)
- [ ] Monitor context relevance
- [ ] Document in OpenAPI spec
- [ ] Update Python SDK
- [ ] Enable right-to-erasure (GDPR compliance)

---

**Status**: Ready for implementation  
**Owner**: Backend team (maestro-api repo)  
**Timeline**: Phase 3.3 (Nov 16 - Dec 31, 2026)
