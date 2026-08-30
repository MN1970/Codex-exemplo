#!/usr/bin/env python3
"""
agent_state_manager.py — State persistence manager for background agents

Objetivo:
  Gerenciar persistência de state entre background jobs.
  Complementa agent_memory_cache.sql com lógica de atualização.

Componentes:
  1. AgentStateManager — CRUD ops para agent_state, agent_memory
  2. State persistence: embedding vectors, intent scores, ratings
  3. Deduplication: evitar chunks duplicados via checksum (MD5)
  4. TTL management: purgar cache > 480 min (R10)
  5. Feedback loop: agregar ratings para fine-tuning (R9)

Fluxo:
  job_id = background_spawn("manta-03-s5", "...")
  # Agent processa
  background_store_result(job_id, result="...", rating=5)
  # StateManager:
  #   1. Armazena result em agent_memory (expires_at = now + 480 min)
  #   2. Atualiza agent_state (avg_user_rating, feedback_count)
  #   3. Calcula embedding do resultado
  #   4. Persiste embedding_vector em agent_state
  #   5. Log para feedback loop (R9)

Classes:
  - AgentStateManager
  - StateEntry (dataclass)
  - EmbeddingCache

Exit codes:
  0: Sucesso
  1: Erro conexão Supabase
  2: Validação falhou
"""

import sys
import os
import logging
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import hashlib
import base64

# Try to import Supabase and embedding client
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    logging.warning("Supabase client not installed")

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    logging.warning("requests not installed")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


# =====================================================================
# DATA CLASSES
# =====================================================================

@dataclass
class StateEntry:
    """Single entry in agent state cache."""
    agent_id: str
    session_id: str
    memory_key: str
    memory_value: Dict
    source_prompt: str
    user_rating: Optional[int] = None
    expires_at: Optional[str] = None

    def compute_checksum(self) -> str:
        """Compute MD5 checksum of memory_value (for dedup)."""
        value_str = json.dumps(self.memory_value, sort_keys=True)
        return hashlib.md5(value_str.encode()).hexdigest()


# =====================================================================
# STATE MANAGER
# =====================================================================

class AgentStateManager:
    """
    Manages agent state persistence in Supabase.

    Responsibilities:
      1. Store memory entries (agent_memory table)
      2. Update state metrics (agent_state table)
      3. Manage embeddings (embedding_vector)
      4. TTL cleanup (expires_at > now)
      5. Feedback aggregation (user_rating → avg)
      6. Deduplication (checksum)
    """

    def __init__(
        self,
        supabase_url: str = None,
        supabase_key: str = None,
        embedding_api_url: str = None
    ):
        """
        Initialize state manager.

        Args:
          supabase_url: Supabase project URL (env: SUPABASE_URL)
          supabase_key: Supabase API key (env: SUPABASE_KEY)
          embedding_api_url: Optional embedding API (env: EMBEDDING_API_URL)
        """
        self.supabase_url = supabase_url or os.getenv("SUPABASE_URL")
        self.supabase_key = supabase_key or os.getenv("SUPABASE_KEY")
        self.embedding_api_url = embedding_api_url or os.getenv("EMBEDDING_API_URL")
        self.client: Optional[Client] = None

        if SUPABASE_AVAILABLE and self.supabase_url and self.supabase_key:
            try:
                self.client = create_client(self.supabase_url, self.supabase_key)
                logger.info("Supabase client initialized for state management")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase: {e}")
        else:
            logger.warning("Supabase credentials not available")

    # =====================================================================
    # MEMORY OPERATIONS
    # =====================================================================

    def store_memory(
        self,
        agent_id: str,
        session_id: str,
        memory_key: str,
        memory_value: Dict,
        source_prompt: str,
        user_rating: Optional[int] = None,
        ttl_minutes: int = 480
    ) -> Optional[str]:
        """
        Store a memory entry (R10).

        Args:
          agent_id: Agent ID (e.g., "manta-03-s5")
          session_id: Session ID
          memory_key: Key (e.g., "query:embedding", "result:geotecnia")
          memory_value: Value (JSON dict)
          source_prompt: Original prompt
          user_rating: User rating (0-5)
          ttl_minutes: TTL in minutes (default: 480 = 8h)

        Returns:
          Memory entry ID or None if failed
        """
        if not self.client:
            logger.warning("Cannot store memory without Supabase")
            return None

        try:
            # Compute checksum for dedup
            entry = StateEntry(agent_id, session_id, memory_key, memory_value, source_prompt, user_rating)
            checksum = entry.compute_checksum()

            # Check for duplicate
            existing = self.client.table("agent_memory") \
                .select("id") \
                .eq("agent_id", agent_id) \
                .eq("checksum", checksum) \
                .limit(1) \
                .execute()

            if existing.data and len(existing.data) > 0:
                logger.info(f"Duplicate memory skipped: {checksum}")
                return existing.data[0]["id"]

            # Compute size
            value_str = json.dumps(memory_value)
            size_bytes = len(value_str.encode("utf-8"))

            # Insert
            expires_at = (datetime.now(timezone.utc) + timedelta(minutes=ttl_minutes)).isoformat()

            record = {
                "agent_id": agent_id,
                "session_id": session_id,
                "memory_key": memory_key,
                "memory_value": memory_value,
                "memory_size_bytes": size_bytes,
                "source_prompt": source_prompt,
                "user_rating": user_rating,
                "expires_at": expires_at,
                "checksum": checksum,
            }

            response = self.client.table("agent_memory").insert(record).execute()
            memory_id = response.data[0]["id"] if response.data else None
            logger.info(f"Memory stored: {memory_id} ({size_bytes} bytes)")
            return memory_id

        except Exception as e:
            logger.error(f"Failed to store memory: {e}")
            return None

    def get_memories(
        self,
        agent_id: str,
        session_id: Optional[str] = None,
        memory_key: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Retrieve memory entries.

        Args:
          agent_id: Agent ID
          session_id: Filter by session (optional)
          memory_key: Filter by key (optional)
          limit: Max results

        Returns:
          List of memory records
        """
        if not self.client:
            logger.warning("Cannot fetch memories without Supabase")
            return []

        try:
            query = self.client.table("agent_memory") \
                .select("*") \
                .eq("agent_id", agent_id) \
                .gt("expires_at", datetime.now(timezone.utc).isoformat())

            if session_id:
                query = query.eq("session_id", session_id)
            if memory_key:
                query = query.eq("memory_key", memory_key)

            response = query.order("created_at", desc=True).limit(limit).execute()
            return response.data if response.data else []

        except Exception as e:
            logger.error(f"Failed to fetch memories: {e}")
            return []

    def purge_expired_memories(self, agent_id: Optional[str] = None) -> int:
        """
        Delete expired memory entries (R10 policy).

        Args:
          agent_id: If provided, only purge this agent; else all agents

        Returns:
          Number of entries deleted
        """
        if not self.client:
            return 0

        try:
            query = self.client.table("agent_memory") \
                .delete() \
                .lt("expires_at", datetime.now(timezone.utc).isoformat())

            if agent_id:
                query = query.eq("agent_id", agent_id)

            response = query.execute()
            deleted = len(response.data) if response.data else 0
            logger.info(f"Purged {deleted} expired memories")
            return deleted

        except Exception as e:
            logger.error(f"Failed to purge memories: {e}")
            return 0

    # =====================================================================
    # STATE OPERATIONS (agent_state table)
    # =====================================================================

    def update_agent_state(
        self,
        agent_id: str,
        user_rating: Optional[int] = None,
        total_memory_size_bytes: Optional[int] = None,
        chunk_count: Optional[int] = None,
        last_query_text: Optional[str] = None,
        embedding_vector: Optional[List[float]] = None
    ) -> bool:
        """
        Update or create agent state entry (R9 feedback loop).

        Args:
          agent_id: Agent ID
          user_rating: New rating (0-5)
          total_memory_size_bytes: Total cache size
          chunk_count: Number of chunks in cache
          last_query_text: Last query processed
          embedding_vector: Embedding vector (1536 dims)

        Returns:
          True if successful
        """
        if not self.client:
            logger.warning("Cannot update state without Supabase")
            return False

        try:
            # Fetch existing state
            existing = self.client.table("agent_state") \
                .select("*") \
                .eq("agent_id", agent_id) \
                .limit(1) \
                .execute()

            update_data = {
                "last_updated": datetime.now(timezone.utc).isoformat(),
            }

            if user_rating is not None:
                # Update feedback aggregates
                if existing.data and len(existing.data) > 0:
                    old_count = existing.data[0].get("feedback_count", 0)
                    old_avg = existing.data[0].get("avg_user_rating", 0.0)

                    new_count = old_count + 1
                    new_avg = ((old_avg * old_count) + user_rating) / new_count
                    update_data["feedback_count"] = new_count
                    update_data["avg_user_rating"] = new_avg
                else:
                    update_data["feedback_count"] = 1
                    update_data["avg_user_rating"] = float(user_rating)

            if total_memory_size_bytes is not None:
                update_data["total_memory_size_bytes"] = total_memory_size_bytes

            if chunk_count is not None:
                update_data["chunk_count"] = chunk_count

            if last_query_text is not None:
                update_data["last_query_text"] = last_query_text

            if embedding_vector is not None:
                # Vector is stored as JSON array in Supabase pgvector type
                update_data["embedding_vector"] = embedding_vector

            # Upsert (create if not exists, update if does)
            if existing.data and len(existing.data) > 0:
                # Update
                self.client.table("agent_state") \
                    .update(update_data) \
                    .eq("agent_id", agent_id) \
                    .execute()
                logger.info(f"Agent state updated: {agent_id}")
            else:
                # Insert
                create_data = {
                    "agent_id": agent_id,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    **update_data
                }
                self.client.table("agent_state").insert(create_data).execute()
                logger.info(f"Agent state created: {agent_id}")

            return True

        except Exception as e:
            logger.error(f"Failed to update agent state: {e}")
            return False

    def get_agent_state(self, agent_id: str) -> Optional[Dict]:
        """
        Retrieve agent state entry.

        Args:
          agent_id: Agent ID

        Returns:
          Agent state dict or None
        """
        if not self.client:
            return None

        try:
            response = self.client.table("agent_state") \
                .select("*") \
                .eq("agent_id", agent_id) \
                .single() \
                .execute()
            return response.data if response.data else None

        except Exception as e:
            logger.error(f"Failed to fetch agent state: {e}")
            return None

    # =====================================================================
    # EMBEDDING OPERATIONS
    # =====================================================================

    def embed_text(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding for text via API.

        Args:
          text: Text to embed

        Returns:
          Embedding vector (1536 dims) or None if failed
        """
        if not self.embedding_api_url:
            logger.warning("Embedding API URL not configured")
            return None

        if not REQUESTS_AVAILABLE:
            logger.warning("requests library not available")
            return None

        try:
            response = requests.post(
                f"{self.embedding_api_url}/embed",
                json={"text": text},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            embedding = data.get("embedding")

            if embedding and len(embedding) == 1536:
                logger.info(f"Embedding generated: {len(embedding)} dims")
                return embedding
            else:
                logger.error(f"Invalid embedding shape: {len(embedding) if embedding else 'None'}")
                return None

        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            return None

    def cache_embedding(
        self,
        agent_id: str,
        query_text: str,
        embedding: List[float]
    ) -> bool:
        """
        Cache an embedding in agent_state.

        Args:
          agent_id: Agent ID
          query_text: The query text
          embedding: Embedding vector (1536 dims)

        Returns:
          True if successful
        """
        return self.update_agent_state(
            agent_id,
            last_query_text=query_text,
            embedding_vector=embedding
        )

    # =====================================================================
    # STATISTICS
    # =====================================================================

    def get_agent_stats(self, agent_id: str) -> Optional[Dict]:
        """
        Get usage statistics for an agent.

        Args:
          agent_id: Agent ID

        Returns:
          Stats dict with memory_size, chunk_count, avg_rating, etc.
        """
        if not self.client:
            return None

        try:
            state = self.get_agent_state(agent_id)
            if not state:
                return None

            return {
                "agent_id": agent_id,
                "total_memory_size_bytes": state.get("total_memory_size_bytes", 0),
                "chunk_count": state.get("chunk_count", 0),
                "avg_user_rating": state.get("avg_user_rating"),
                "feedback_count": state.get("feedback_count", 0),
                "last_query_text": state.get("last_query_text"),
                "last_updated": state.get("last_updated"),
            }

        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return None


# =====================================================================
# PUBLIC API
# =====================================================================

_manager: Optional[AgentStateManager] = None


def get_manager() -> AgentStateManager:
    """Get or create global state manager instance."""
    global _manager
    if _manager is None:
        _manager = AgentStateManager()
    return _manager


def store_result(
    agent_id: str,
    session_id: str,
    result_text: str,
    source_prompt: str,
    user_rating: Optional[int] = None,
    ttl_minutes: int = 480
) -> bool:
    """
    Store job result in agent memory (public API).

    Usage:
      store_result(
        agent_id="manta-03-s5",
        session_id="sess_abc",
        result_text="Análise geotécnica completa...",
        source_prompt="Analise viabilidade do túnel",
        user_rating=5
      )

    Args:
      agent_id: Agent ID
      session_id: Session ID
      result_text: Result text
      source_prompt: Original prompt
      user_rating: Optional rating (0-5)
      ttl_minutes: Cache TTL

    Returns:
      True if successful
    """
    manager = get_manager()

    # Store result in memory
    memory_id = manager.store_memory(
        agent_id,
        session_id,
        "result:output",
        {"text": result_text},
        source_prompt,
        user_rating,
        ttl_minutes
    )

    if not memory_id:
        return False

    # Update agent state
    manager.update_agent_state(agent_id, user_rating=user_rating)

    # Optionally embed the result
    embedding = manager.embed_text(result_text)
    if embedding:
        manager.cache_embedding(agent_id, source_prompt, embedding)

    return True


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Agent state manager CLI")
    subparsers = parser.add_subparsers(dest="command")

    # store command
    store_parser = subparsers.add_parser("store", help="Store memory")
    store_parser.add_argument("--agent-id", required=True)
    store_parser.add_argument("--session-id", required=True)
    store_parser.add_argument("--memory-key", required=True)
    store_parser.add_argument("--value", required=True)
    store_parser.add_argument("--prompt", required=True)
    store_parser.add_argument("--rating", type=int)

    # get command
    get_parser = subparsers.add_parser("get", help="Retrieve memories")
    get_parser.add_argument("--agent-id", required=True)
    get_parser.add_argument("--session-id")
    get_parser.add_argument("--limit", type=int, default=10)

    # state command
    state_parser = subparsers.add_parser("state", help="Get agent state")
    state_parser.add_argument("--agent-id", required=True)

    # stats command
    stats_parser = subparsers.add_parser("stats", help="Get agent stats")
    stats_parser.add_argument("--agent-id", required=True)

    # purge command
    purge_parser = subparsers.add_parser("purge", help="Purge expired memories")
    purge_parser.add_argument("--agent-id")

    args = parser.parse_args()
    manager = get_manager()

    if args.command == "store":
        value = json.loads(args.value)
        success = manager.store_memory(
            args.agent_id,
            args.session_id,
            args.memory_key,
            value,
            args.prompt,
            args.rating
        )
        print("OK" if success else "FAILED")

    elif args.command == "get":
        memories = manager.get_memories(args.agent_id, args.session_id, limit=args.limit)
        print(json.dumps(memories, indent=2, default=str))

    elif args.command == "state":
        state = manager.get_agent_state(args.agent_id)
        if state:
            print(json.dumps(state, indent=2, default=str))
        else:
            print("No state found")

    elif args.command == "stats":
        stats = manager.get_agent_stats(args.agent_id)
        if stats:
            print(json.dumps(stats, indent=2))
        else:
            print("No stats found")

    elif args.command == "purge":
        deleted = manager.purge_expired_memories(args.agent_id)
        print(f"Purged {deleted} entries")

    else:
        parser.print_help()
