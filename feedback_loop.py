#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
feedback_loop.py — Manta Maestro closed feedback loop (Thompson Sampling)
==========================================================================

Implements the "Fase 2.1 — Feedback loop" item from
docs/MANTA-MAESTRO-ECOSYSTEM-v5-UPGRADE.md (§2.2 "Learning from feedback",
§4.1 SQL schema): the Maestro router picks an agent for a query, the user
(or a downstream reviewer) rates the outcome, and that rating is fed back
as evidence that reshapes the probability of picking that agent next time
— a *closed* loop, because the routing decision itself consumes the
posterior that its own past decisions produced.

--------------------------------------------------------------------------
WHY THOMPSON SAMLING (informal derivation)
--------------------------------------------------------------------------
Each agent `i` is modeled as a Bernoulli arm with an unknown true
"success probability" theta_i in [0, 1] — the long-run rate at which
routing a query to that agent turns out to be the right call.

We keep a Beta distribution as the Bayesian *belief* about theta_i:

    prior:      theta_i ~ Beta(alpha_i, beta_i)
    PDF:        f(theta; a, b) = theta^(a-1) * (1-theta)^(b-1) / B(a, b)
                where B(a, b) = Gamma(a)Gamma(b) / Gamma(a+b)

Beta is the *conjugate prior* for the Bernoulli/Binomial likelihood, so
observing an outcome x in {0, 1} (1 = success, 0 = failure) updates the
belief in closed form, with no numerical integration required:

    posterior:  P(theta | x) ∝ P(x | theta) * P(theta)
                            = theta^x (1-theta)^(1-x) * Beta(a, b)
                            = Beta(a + x, b + (1 - x))

    i.e.        alpha_i <- alpha_i + x
                beta_i  <- beta_i  + (1 - x)

This module also accepts *fractional* rewards r in [0, 1] (e.g. a
"slow"/"incomplete" outcome is worth partial credit, not a clean 0/1).
We generalize the same update rule to fractional evidence:

                alpha_i <- alpha_i + r
                beta_i  <- beta_i  + (1 - r)

This keeps E[theta_i] and the update's "pull" proportional to how good/bad
the outcome was, without breaking the Beta-conjugacy algebra (this is the
standard practical extension used e.g. in Agrawal & Goyal, 2012,
"Analysis of Thompson Sampling for the multi-armed bandit problem", for
bounded, non-binary rewards).

Useful closed-form posterior statistics:

    mean:       E[theta_i]   = alpha_i / (alpha_i + beta_i)
    variance:   Var[theta_i] = (alpha_i * beta_i) /
                                ((alpha_i + beta_i)^2 * (alpha_i + beta_i + 1))

Note Var shrinks like O(1/n) as alpha_i+beta_i grows — the more feedback
an agent accumulates, the more confident (peaked) its Beta gets.

--------------------------------------------------------------------------
THOMPSON SAMPLING DECISION RULE
--------------------------------------------------------------------------
At decision time, instead of always routing to argmax_i E[theta_i] (which
over-exploits and never re-checks agents that got unlucky early on), we:

    1. Draw one sample  theta_i_hat ~ Beta(alpha_i, beta_i)   for every
       candidate agent i (posterior sampling).
    2. Route to          i* = argmax_i theta_i_hat

Because agents with wide (uncertain) posteriors occasionally sample a
high theta_i_hat by chance, this automatically explores under-tried
agents while converging to mostly-exploit the best agent as evidence
accumulates — Thompson Sampling is a randomized realization of
"optimism under uncertainty" and has near-optimal (logarithmic) regret
bounds for Bernoulli bandits (Agrawal & Goyal 2012; Chapelle & Li 2011).

--------------------------------------------------------------------------
PERSISTENCE / INTEGRATION
--------------------------------------------------------------------------
Two storage backends are provided behind the `FeedbackStore` interface:

  * `SQLiteFeedbackStore` — zero-dependency, file-based, used by the
    example below and good enough for a single Maestro process.

  * `SupabaseFeedbackStore` — thin adapter stub mapping onto the actual
    production tables already specified in
    docs/MANTA-MAESTRO-ECOSYSTEM-v5-UPGRADE.md §4.1:
        agents(id, ...)
        routing_feedback(id, routing_id, agent_id, query_hash, feedback,
                          comment, created_at)
        routing_events(id, routing_id, query, top_candidates,
                        chosen_agent_id, chosen_confidence, ...)
    Swap `FeedbackBandit(store=SupabaseFeedbackStore(...))` in when the
    Supabase project + client credentials are available; no other code
    needs to change because both stores implement `FeedbackStore`.

--------------------------------------------------------------------------
API (as specified)
--------------------------------------------------------------------------
    bandit = FeedbackBandit(db_path="feedback.db")

    decision = bandit.getNextAgent(agents, query)
    # -> {"routing_id": ..., "chosen_agent_id": ..., "samples": {...}, ...}

    bandit.acceptFeedback(routing_id, feedback_type, agent_id)
    # feedback_type in {"correct", "wrong", "slow", "incomplete"}
"""

from __future__ import annotations

import hashlib
import json
import random
import sqlite3
import threading
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Union


# ==========================================================================
# Data structures
# ==========================================================================

@dataclass
class AgentPosterior:
    """
    Beta(alpha, beta) posterior belief over one agent's success rate.

    alpha, beta start at the prior (default: uniform Beta(1, 1), i.e.
    "no information, any success rate equally likely") and accumulate
    evidence via `alpha += reward`, `beta += (1 - reward)` on every
    piece of feedback (see module docstring for the derivation).
    """

    agent_id: str
    alpha: float = 1.0
    beta: float = 1.0
    n_updates: int = 0
    last_updated: Optional[float] = None

    @property
    def mean(self) -> float:
        # E[theta] = alpha / (alpha + beta)
        return self.alpha / (self.alpha + self.beta)

    @property
    def variance(self) -> float:
        # Var[theta] = (alpha*beta) / ((alpha+beta)^2 * (alpha+beta+1))
        a, b = self.alpha, self.beta
        return (a * b) / (((a + b) ** 2) * (a + b + 1))

    def sample(self, rng: Optional[random.Random] = None) -> float:
        """Draw one posterior sample theta_hat ~ Beta(alpha, beta)."""
        r = rng or random
        return r.betavariate(self.alpha, self.beta)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "alpha": self.alpha,
            "beta": self.beta,
            "n_updates": self.n_updates,
            "mean": self.mean,
            "variance": self.variance,
            "last_updated": self.last_updated,
        }


# ==========================================================================
# Persistence layer
# ==========================================================================

class FeedbackStore(ABC):
    """
    Storage interface the bandit depends on. Implement this against
    SQLite (default, see below), Postgres/Supabase, Redis, etc. — the
    bandit's math never touches SQL directly, so swapping backends is
    a one-line change.
    """

    @abstractmethod
    def load_posterior(self, agent_id: str, prior_alpha: float,
                        prior_beta: float) -> AgentPosterior:
        """Return the persisted posterior for agent_id, or a fresh
        prior Beta(prior_alpha, prior_beta) if none exists yet."""

    @abstractmethod
    def save_posterior(self, posterior: AgentPosterior) -> None:
        """Persist (upsert) the posterior's current (alpha, beta)."""

    @abstractmethod
    def log_feedback(self, routing_id: str, agent_id: str,
                      feedback_type: str, reward: float) -> None:
        """Append an audit row to routing_feedback for traceability."""

    @abstractmethod
    def log_routing_event(self, routing_id: str, query: str,
                           candidates: Sequence[str], chosen_agent_id: str,
                           samples: Dict[str, float]) -> None:
        """Append an audit row to routing_events for traceability."""


class SQLiteFeedbackStore(FeedbackStore):
    """
    Zero-dependency persistence backend (stdlib sqlite3).

    Table layout intentionally mirrors the production Supabase schema
    from docs/MANTA-MAESTRO-ECOSYSTEM-v5-UPGRADE.md §4.1 so migrating
    to Postgres later is a straight `pg_dump`-style port, not a redesign:

        agent_posteriors  -- Beta(alpha, beta) state per agent (this
                             module's addition; production maps this
                             onto columns on `agents` or a side table)
        routing_feedback  -- 1 row per acceptFeedback() call
        routing_events    -- 1 row per getNextAgent() call
    """

    def __init__(self, db_path: str = "feedback.db"):
        self.db_path = db_path
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        with self._lock, self._conn:
            self._conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS agent_posteriors (
                    agent_id     TEXT PRIMARY KEY,
                    alpha        REAL NOT NULL,
                    beta         REAL NOT NULL,
                    n_updates    INTEGER NOT NULL DEFAULT 0,
                    updated_at   REAL
                );

                CREATE TABLE IF NOT EXISTS routing_feedback (
                    id           INTEGER PRIMARY KEY AUTOINCREMENT,
                    routing_id   TEXT NOT NULL,
                    agent_id     TEXT NOT NULL,
                    feedback     TEXT NOT NULL
                                 CHECK (feedback IN
                                     ('correct', 'wrong', 'slow', 'incomplete')),
                    reward       REAL NOT NULL,
                    created_at   REAL NOT NULL
                );

                CREATE TABLE IF NOT EXISTS routing_events (
                    id                INTEGER PRIMARY KEY AUTOINCREMENT,
                    routing_id        TEXT UNIQUE NOT NULL,
                    query_hash        TEXT,
                    query_preview     TEXT,
                    top_candidates    TEXT NOT NULL,   -- JSON array
                    chosen_agent_id   TEXT NOT NULL,
                    chosen_confidence REAL NOT NULL,   -- sampled theta_hat
                    samples           TEXT NOT NULL,   -- JSON {agent: theta_hat}
                    created_at        REAL NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_feedback_agent
                    ON routing_feedback(agent_id, created_at DESC);
                CREATE INDEX IF NOT EXISTS idx_routing_events_created
                    ON routing_events(created_at DESC);
                """
            )

    def load_posterior(self, agent_id: str, prior_alpha: float,
                        prior_beta: float) -> AgentPosterior:
        with self._lock:
            row = self._conn.execute(
                "SELECT * FROM agent_posteriors WHERE agent_id = ?",
                (agent_id,),
            ).fetchone()
        if row is None:
            return AgentPosterior(agent_id=agent_id, alpha=prior_alpha,
                                   beta=prior_beta)
        return AgentPosterior(
            agent_id=row["agent_id"],
            alpha=row["alpha"],
            beta=row["beta"],
            n_updates=row["n_updates"],
            last_updated=row["updated_at"],
        )

    def save_posterior(self, posterior: AgentPosterior) -> None:
        with self._lock, self._conn:
            self._conn.execute(
                """
                INSERT INTO agent_posteriors
                    (agent_id, alpha, beta, n_updates, updated_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(agent_id) DO UPDATE SET
                    alpha = excluded.alpha,
                    beta = excluded.beta,
                    n_updates = excluded.n_updates,
                    updated_at = excluded.updated_at
                """,
                (posterior.agent_id, posterior.alpha, posterior.beta,
                 posterior.n_updates, posterior.last_updated),
            )

    def log_feedback(self, routing_id: str, agent_id: str,
                      feedback_type: str, reward: float) -> None:
        with self._lock, self._conn:
            self._conn.execute(
                """
                INSERT INTO routing_feedback
                    (routing_id, agent_id, feedback, reward, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (routing_id, agent_id, feedback_type, reward, time.time()),
            )

    def log_routing_event(self, routing_id: str, query: str,
                           candidates: Sequence[str], chosen_agent_id: str,
                           samples: Dict[str, float]) -> None:
        query_hash = hashlib.sha256(query.encode("utf-8")).hexdigest() if query else None
        with self._lock, self._conn:
            self._conn.execute(
                """
                INSERT INTO routing_events
                    (routing_id, query_hash, query_preview, top_candidates,
                     chosen_agent_id, chosen_confidence, samples, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    routing_id,
                    query_hash,
                    (query[:200] if query else None),
                    json.dumps(list(candidates)),
                    chosen_agent_id,
                    samples.get(chosen_agent_id, 0.0),
                    json.dumps(samples),
                    time.time(),
                ),
            )

    def close(self) -> None:
        self._conn.close()


class SupabaseFeedbackStore(FeedbackStore):
    """
    Adapter stub for the production Supabase tables described in
    docs/MANTA-MAESTRO-ECOSYSTEM-v5-UPGRADE.md §4.1 (`agents`,
    `routing_feedback`, `routing_events`).

    Wire this up with the `supabase-py` client (or `psycopg2` directly
    against the Postgres connection string) and it becomes a drop-in
    replacement for SQLiteFeedbackStore — `FeedbackBandit` only ever
    talks to the `FeedbackStore` interface, never to SQL directly.

    NOTE: left unimplemented here (no network calls from this sandboxed
    module) — implement each method with the Supabase client, e.g.:

        def save_posterior(self, posterior):
            self.client.table("agent_posteriors").upsert({
                "agent_id": posterior.agent_id,
                "alpha": posterior.alpha,
                "beta": posterior.beta,
                "n_updates": posterior.n_updates,
                "updated_at": "now()",
            }).execute()
    """

    def __init__(self, client: Any = None, **_ignored: Any):
        self.client = client

    def load_posterior(self, agent_id, prior_alpha, prior_beta):
        raise NotImplementedError(
            "Implement with supabase-py: "
            "select alpha, beta from agent_posteriors where agent_id=..."
        )

    def save_posterior(self, posterior):
        raise NotImplementedError(
            "Implement with supabase-py: upsert into agent_posteriors"
        )

    def log_feedback(self, routing_id, agent_id, feedback_type, reward):
        raise NotImplementedError(
            "Implement with supabase-py: insert into routing_feedback"
        )

    def log_routing_event(self, routing_id, query, candidates,
                           chosen_agent_id, samples):
        raise NotImplementedError(
            "Implement with supabase-py: insert into routing_events"
        )


# ==========================================================================
# The bandit
# ==========================================================================

# feedback_type -> fractional reward r in [0, 1] used in the Beta update
# (alpha += r, beta += 1 - r). "correct"/"wrong" are the clean Bernoulli
# endpoints; "incomplete"/"slow" are partial-credit outcomes (§2.2 of the
# ecosystem doc lists exactly these four feedback values).
DEFAULT_REWARD_MAP: Dict[str, float] = {
    "correct": 1.0,
    "incomplete": 0.5,
    "slow": 0.3,
    "wrong": 0.0,
}


class FeedbackBandit:
    """
    Closed feedback loop for Maestro routing decisions, backed by
    per-agent Beta(alpha, beta) posteriors and Thompson Sampling.

    Typical lifecycle for one query:

        decision = bandit.getNextAgent(candidate_agent_ids, query)
        # ... route the query to decision["chosen_agent_id"], run it ...
        # ... later, once outcome quality is known (user rates it,
        #     or an automated grader scores it) ...
        bandit.acceptFeedback(decision["routing_id"], "correct",
                               decision["chosen_agent_id"])
    """

    def __init__(
        self,
        db_path: str = "feedback.db",
        store: Optional[FeedbackStore] = None,
        prior_alpha: float = 1.0,
        prior_beta: float = 1.0,
        reward_map: Optional[Dict[str, float]] = None,
        decay: float = 1.0,
        rng_seed: Optional[int] = None,
    ):
        """
        Args:
            db_path: path to the SQLite file (ignored if `store` given).
            store: a FeedbackStore instance (e.g. SupabaseFeedbackStore).
                   Defaults to SQLiteFeedbackStore(db_path).
            prior_alpha, prior_beta: Beta(alpha, beta) prior for agents
                   with no feedback yet. Default Beta(1, 1) = uniform.
            reward_map: override feedback_type -> reward in [0, 1].
            decay: optional evidence forgetting factor in (0, 1]. Before
                   each update, (alpha, beta) are pulled back towards the
                   prior by this factor:
                       alpha <- prior_a + decay * (alpha - prior_a)
                       beta  <- prior_b + decay * (beta  - prior_b)
                   decay=1.0 (default) disables forgetting (a fully
                   stationary bandit). decay<1.0 lets the loop adapt to
                   agents whose real-world quality drifts over time
                   (a standard non-stationary-bandit technique).
            rng_seed: seed for reproducible sampling (tests/demos).
        """
        self.store = store or SQLiteFeedbackStore(db_path)
        self.prior_alpha = prior_alpha
        self.prior_beta = prior_beta
        self.reward_map = dict(reward_map or DEFAULT_REWARD_MAP)
        self.decay = decay
        self._rng = random.Random(rng_seed) if rng_seed is not None else random
        self._cache: Dict[str, AgentPosterior] = {}
        self._cache_lock = threading.Lock()
        # routing_id -> chosen_agent_id, kept in-memory as a convenience
        # so callers don't have to thread agent_id through by hand
        # (they still can, and acceptFeedback's agent_id arg always wins).
        self._routing_log: Dict[str, str] = {}

    # ---------------------------------------------------------------
    # internal helpers
    # ---------------------------------------------------------------

    def _get_posterior(self, agent_id: str) -> AgentPosterior:
        with self._cache_lock:
            posterior = self._cache.get(agent_id)
            if posterior is None:
                posterior = self.store.load_posterior(
                    agent_id, self.prior_alpha, self.prior_beta
                )
                self._cache[agent_id] = posterior
            return posterior

    @staticmethod
    def _agent_id_of(agent: Union[str, Dict[str, Any]]) -> str:
        if isinstance(agent, str):
            return agent
        for key in ("agent_id", "id", "slug"):
            if key in agent:
                return agent[key]
        raise ValueError(f"Cannot extract agent_id from {agent!r}")

    # ---------------------------------------------------------------
    # public API
    # ---------------------------------------------------------------

    def acceptFeedback(
        self, routing_id: str, feedback_type: str, agent_id: str
    ) -> AgentPosterior:
        """
        Update the agent's Beta posterior with one piece of feedback.

        Bayesian update (Beta-Bernoulli conjugacy, fractional reward r):

            r = reward_map[feedback_type]          # in [0, 1]
            alpha_i <- alpha_i + r
            beta_i  <- beta_i  + (1 - r)

        Args:
            routing_id: the trace ID returned by a prior getNextAgent()
                        call (used only for audit logging here; the
                        update itself is keyed on agent_id, per spec).
            feedback_type: one of "correct", "wrong", "slow", "incomplete".
            agent_id: which agent this feedback is about.

        Returns:
            The agent's updated AgentPosterior (also persisted).

        Raises:
            ValueError: if feedback_type is not in `self.reward_map`.
        """
        if feedback_type not in self.reward_map:
            raise ValueError(
                f"Unknown feedback_type {feedback_type!r}; "
                f"expected one of {sorted(self.reward_map)}"
            )
        reward = self.reward_map[feedback_type]

        posterior = self._get_posterior(agent_id)

        if self.decay < 1.0:
            # Non-stationary forgetting: pull existing evidence back
            # towards the prior before adding the new observation, so
            # very old feedback matters less than recent feedback.
            posterior.alpha = self.prior_alpha + self.decay * (
                posterior.alpha - self.prior_alpha
            )
            posterior.beta = self.prior_beta + self.decay * (
                posterior.beta - self.prior_beta
            )

        # --- the actual Bayesian update ---
        posterior.alpha += reward
        posterior.beta += 1.0 - reward
        posterior.n_updates += 1
        posterior.last_updated = time.time()

        self.store.save_posterior(posterior)
        self.store.log_feedback(routing_id, agent_id, feedback_type, reward)
        return posterior

    def getNextAgent(
        self,
        agents: Sequence[Union[str, Dict[str, Any]]],
        query: str = "",
    ) -> Dict[str, Any]:
        """
        Thompson-sample one agent among candidates for this query.

        For every candidate agent i, draw
            theta_i_hat ~ Beta(alpha_i, beta_i)
        (one independent posterior sample per agent) and route to
            i* = argmax_i theta_i_hat

        Args:
            agents: candidate agent ids (strings) or dicts with an
                    "agent_id"/"id"/"slug" key — typically the shortlist
                    already produced by Maestro's keyword/BM25/semantic
                    routing (§2.3 of the ecosystem doc); this bandit
                    re-ranks *among* that shortlist rather than searching
                    the full registry itself.
            query: the raw query text, stored (hashed) for audit/replay;
                   purely informational for the base (non-contextual)
                   bandit implemented here.

        Returns:
            {
              "routing_id": str,          # trace id for acceptFeedback()
              "chosen_agent_id": str,
              "samples": {agent_id: theta_hat, ...},
              "posteriors": {agent_id: {"alpha":..,"beta":..,"mean":..}, ..},
            }

        Raises:
            ValueError: if `agents` is empty.
        """
        agent_ids = [self._agent_id_of(a) for a in agents]
        if not agent_ids:
            raise ValueError("getNextAgent() requires at least one candidate agent")

        samples: Dict[str, float] = {}
        posteriors: Dict[str, AgentPosterior] = {}
        for agent_id in agent_ids:
            posterior = self._get_posterior(agent_id)
            posteriors[agent_id] = posterior
            samples[agent_id] = posterior.sample(self._rng)

        chosen_agent_id = max(samples, key=samples.get)
        routing_id = str(uuid.uuid4())
        self._routing_log[routing_id] = chosen_agent_id

        self.store.log_routing_event(
            routing_id, query, agent_ids, chosen_agent_id, samples
        )

        return {
            "routing_id": routing_id,
            "chosen_agent_id": chosen_agent_id,
            "samples": samples,
            "posteriors": {aid: p.to_dict() for aid, p in posteriors.items()},
        }

    # ---------------------------------------------------------------
    # introspection helpers (not in the original spec, but useful for
    # dashboards / debugging without touching the DB directly)
    # ---------------------------------------------------------------

    def get_stats(self, agent_id: str) -> Dict[str, Any]:
        """Return the current posterior summary for one agent."""
        return self._get_posterior(agent_id).to_dict()

    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Return posterior summaries for every agent seen so far."""
        return {aid: p.to_dict() for aid, p in self._cache.items()}


# ==========================================================================
# Example usage
# ==========================================================================

def _demo() -> None:
    """
    Simulates several rounds of Maestro routing + feedback across the
    4 Eixo-2 vertical agents added in v4.2 (agente-saneamento,
    agente-energia, agente-portos, agente-barragens), with
    agente-saneamento seeded as the "actually best" agent for these
    queries so we can watch Thompson Sampling converge onto it.
    """
    import os

    demo_db = "/tmp/manta_feedback_demo.db"
    if os.path.exists(demo_db):
        os.remove(demo_db)

    bandit = FeedbackBandit(db_path=demo_db, rng_seed=42)

    candidates = [
        "agente-saneamento",
        "agente-energia",
        "agente-portos",
        "agente-barragens",
    ]

    # Ground-truth quality used only to simulate feedback in this demo —
    # a real Maestro would get "feedback_type" from an actual user or
    # an automated grader, not from a fixed table like this.
    true_quality = {
        "agente-saneamento": 0.85,   # this is the right agent most of the time
        "agente-energia": 0.30,
        "agente-portos": 0.20,
        "agente-barragens": 0.25,
    }

    sim_rng = random.Random(7)
    n_rounds = 200
    chosen_counts: Dict[str, int] = {a: 0 for a in candidates}

    for round_i in range(1, n_rounds + 1):
        query = f"Consulta simulada de saneamento urbano #{round_i}"
        decision = bandit.getNextAgent(candidates, query)
        chosen = decision["chosen_agent_id"]
        chosen_counts[chosen] += 1

        # Simulate an outcome for the chosen agent based on its true
        # quality, then translate it into one of the 4 feedback types.
        p_good = true_quality[chosen]
        roll = sim_rng.random()
        if roll < p_good:
            feedback_type = "correct"
        elif roll < p_good + 0.15:
            feedback_type = "incomplete"
        elif roll < p_good + 0.25:
            feedback_type = "slow"
        else:
            feedback_type = "wrong"

        bandit.acceptFeedback(decision["routing_id"], feedback_type, chosen)

    print(f"Routing counts over {n_rounds} rounds:")
    for agent_id, count in sorted(chosen_counts.items(), key=lambda kv: -kv[1]):
        print(f"  {agent_id:22s}: {count:4d} routes ({count / n_rounds:.0%})")

    print("\nFinal posterior stats:")
    for agent_id, stats in bandit.get_all_stats().items():
        print(
            f"  {agent_id:22s}: alpha={stats['alpha']:.1f} "
            f"beta={stats['beta']:.1f} mean={stats['mean']:.3f} "
            f"n_updates={stats['n_updates']}"
        )

    # A single one-off routing + feedback call, matching the API exactly
    # as specified in the task ("acceptFeedback(routing_id, feedback_type,
    # agent_id)" / "getNextAgent(agents, query)"):
    decision = bandit.getNextAgent(candidates, "ETE nova para AySA")
    print(f"\nNext single decision -> {decision['chosen_agent_id']} "
          f"(routing_id={decision['routing_id']})")
    bandit.acceptFeedback(decision["routing_id"], "correct",
                          decision["chosen_agent_id"])
    print("Feedback accepted; posterior updated.")


if __name__ == "__main__":
    _demo()
