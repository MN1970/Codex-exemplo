"""
Federation Broker — Multi-org Agent Orchestration

Handles capability manifests, trust tiers, data isolation, and cross-org routing.
Phase 4.1 implementation.
"""

import hashlib
import json
import logging
import asyncio
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod

import httpx
from cryptography import x509
from cryptography.hazmat.primitives import hashes
from sqlalchemy import create_engine, Column, String, JSON, DateTime, Integer
from sqlalchemy.orm import sessionmaker, declarative_base


# ============================================================================
# TRUST TIER DEFINITIONS
# ============================================================================

class TrustTier(Enum):
    """Agent trust classification in federation."""
    L1_MANTA = "L1_MANTA"           # Internal Manta agents
    L2_PARTNER = "L2_PARTNER"       # Certified partners (90-day SLA)
    L3_PUBLIC = "L3_PUBLIC"         # Community / third-party (request-based)


# ============================================================================
# CAPABILITY MANIFEST
# ============================================================================

@dataclass
class Capability:
    """Single agent capability."""
    name: str                          # "route-claims", "analyze-bridges", etc.
    domain: str                        # "claims", "infrastructure", "energy"
    version: str                       # "1.0.0"
    requires_org_context: bool         # Data isolation policy
    approved_orgs: List[str] = None   # Whitelist (None = all orgs can invoke)
    rate_limit_rps: int = 100         # Requests per second
    cost_usd_per_1k: float = 0.01     # Pricing for federation partners

    def validate(self):
        """Check manifest validity."""
        if not self.name or not self.domain or not self.version:
            raise ValueError("Capability requires name, domain, version")
        if self.rate_limit_rps <= 0:
            raise ValueError("rate_limit_rps must be > 0")


@dataclass
class CapabilityManifest:
    """Agent capability advertisement."""
    agent_id: str                      # "manta-03-s8" or "partner-acme-claims-v1"
    org_id: str                        # "org-1" (Manta), "org-2" (Partner)
    trust_tier: TrustTier
    capabilities: List[Capability]
    version: str = "1.0"
    signed_at: str = None             # ISO8601 timestamp
    signature_sha256: str = None      # HMAC-SHA256(manifest_json, org_secret_key)

    def to_json(self) -> str:
        """Serialize for signing."""
        data = asdict(self)
        data.pop("signature_sha256", None)
        data["trust_tier"] = self.trust_tier.value
        data["capabilities"] = [asdict(c) for c in self.capabilities]
        return json.dumps(data, sort_keys=True, default=str)

    def validate_signature(self, org_secret_key: str) -> bool:
        """Verify manifest integrity."""
        expected_sig = hashlib.sha256(
            self.to_json().encode() + org_secret_key.encode()
        ).hexdigest()
        return self.signature_sha256 == expected_sig


Base = declarative_base()


class FederationAgentRecord(Base):
    """Federated agent registry (Supabase)."""
    __tablename__ = "federation_agents"

    agent_id = Column(String, primary_key=True)
    org_id = Column(String, index=True)
    trust_tier = Column(String)
    manifest = Column(JSON)  # Full CapabilityManifest
    certificate_pem = Column(String)  # mTLS cert for org
    registered_at = Column(DateTime, default=datetime.utcnow)
    last_heartbeat = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Integer, default=1)


class FederationRoutingRecord(Base):
    """Immutable audit trail for federation queries."""
    __tablename__ = "federation_audit_log"

    request_id = Column(String, primary_key=True)
    source_org = Column(String, index=True)
    source_agent = Column(String)
    target_agent = Column(String)
    capability = Column(String)
    data_classification = Column(String)  # "PUBLIC", "INTERNAL", "CONFIDENTIAL"
    status = Column(String)  # "ALLOWED", "DENIED", "RATE_LIMITED"
    reason = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    cost_usd = Column(String)
    request_checksum = Column(String)  # SHA256 of request body


# ============================================================================
# FEDERATION BROKER
# ============================================================================

class DataIsolationPolicy:
    """Cross-org data isolation enforcement."""

    def __init__(self):
        self.isolation_rules = {
            "INTERNAL": ["L1_MANTA"],                      # Manta-only
            "CONFIDENTIAL": ["L1_MANTA", "L2_PARTNER"],   # Partners + Manta
            "PUBLIC": ["L1_MANTA", "L2_PARTNER", "L3_PUBLIC"],
        }

    def can_access(self, data_class: str, caller_tier: str) -> bool:
        """Check if caller tier can access data classification."""
        allowed_tiers = self.isolation_rules.get(data_class, [])
        return caller_tier in allowed_tiers


class FederationBroker:
    """
    Agent Federation Broker.

    Responsibilities:
    - Capability registry (manifest validation)
    - Multi-org routing with trust verification
    - Data isolation enforcement
    - Rate limiting & cost tracking
    - Audit logging (immutable)
    """

    def __init__(
        self,
        db_url: str,
        org_secrets: Dict[str, str],
        manta_org_id: str = "org-1",
    ):
        """
        Initialize broker.

        Args:
            db_url: Supabase connection string
            org_secrets: {org_id: secret_key} for signature validation
            manta_org_id: Manta's org identifier
        """
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

        self.org_secrets = org_secrets
        self.manta_org_id = manta_org_id
        self.isolation_policy = DataIsolationPolicy()
        self.logger = logging.getLogger("FederationBroker")

        # In-memory rate limiter: {agent_id: {cap_name: (count, reset_ts)}}
        self.rate_limiters: Dict[str, Dict[str, Tuple[int, float]]] = {}

    def register_agent(
        self,
        manifest: CapabilityManifest,
        certificate_pem: str,
    ) -> bool:
        """
        Register a federated agent.

        Args:
            manifest: Agent capability manifest
            certificate_pem: mTLS certificate (PEM format)

        Returns:
            True if registration succeeded

        Raises:
            ValueError: Invalid manifest or certificate
        """
        # Validate manifest
        for cap in manifest.capabilities:
            cap.validate()

        # Verify signature
        if not manifest.validate_signature(self.org_secrets.get(manifest.org_id, "")):
            self.logger.warning(
                f"Invalid signature for agent {manifest.agent_id} "
                f"(org {manifest.org_id})"
            )
            raise ValueError("Manifest signature validation failed")

        # Parse certificate (basic checks)
        try:
            cert = x509.load_pem_x509_certificate(certificate_pem.encode())
            if cert.not_valid_before_utc > datetime.utcnow():
                raise ValueError("Certificate not yet valid")
            if cert.not_valid_after_utc < datetime.utcnow():
                raise ValueError("Certificate expired")
        except Exception as e:
            raise ValueError(f"Certificate validation failed: {e}")

        # Store in registry
        session = self.Session()
        try:
            existing = session.query(FederationAgentRecord).filter_by(
                agent_id=manifest.agent_id
            ).first()

            if existing:
                # Update heartbeat + manifest
                existing.manifest = asdict(manifest)
                existing.last_heartbeat = datetime.utcnow()
                existing.is_active = 1
            else:
                # New registration
                record = FederationAgentRecord(
                    agent_id=manifest.agent_id,
                    org_id=manifest.org_id,
                    trust_tier=manifest.trust_tier.value,
                    manifest=asdict(manifest),
                    certificate_pem=certificate_pem,
                )
                session.add(record)

            session.commit()
            self.logger.info(
                f"Registered agent {manifest.agent_id} "
                f"({manifest.trust_tier.value}) with "
                f"{len(manifest.capabilities)} capabilities"
            )
            return True
        except Exception as e:
            session.rollback()
            self.logger.error(f"Registration failed: {e}")
            raise
        finally:
            session.close()

    async def route_cross_org_request(
        self,
        source_org: str,
        source_agent: str,
        target_capability: str,
        request_payload: Dict[str, Any],
        data_classification: str = "PUBLIC",
    ) -> Dict[str, Any]:
        """
        Route a cross-org capability request.

        Args:
            source_org: Calling org ID
            source_agent: Calling agent ID
            target_capability: Requested capability ("route-claims", etc.)
            request_payload: Request body
            data_classification: Data sensitivity ("PUBLIC", "INTERNAL", "CONFIDENTIAL")

        Returns:
            {
                "status": "ALLOWED" | "DENIED",
                "target_agent": str,
                "response": {...},
                "cost_usd": float,
                "request_id": str,
            }

        Raises:
            ValueError: Isolation policy violation
        """
        request_id = f"fed-{uuid.uuid4().hex[:12]}"

        # 1. Find target agent(s) offering capability
        session = self.Session()
        try:
            candidates = []
            for record in session.query(FederationAgentRecord).filter_by(
                is_active=1
            ).all():
                manifest = CapabilityManifest(**record.manifest)
                for cap in manifest.capabilities:
                    if cap.name == target_capability:
                        candidates.append((record, cap, manifest))

            if not candidates:
                self._audit_log(
                    request_id, source_org, source_agent, None,
                    target_capability, data_classification,
                    "DENIED", f"No agent offers capability: {target_capability}"
                )
                return {
                    "status": "DENIED",
                    "reason": "Capability not found in federation",
                    "request_id": request_id,
                }

            # 2. Get caller trust tier
            caller_record = session.query(FederationAgentRecord).filter_by(
                agent_id=source_agent
            ).first()
            caller_tier = (
                TrustTier[caller_record.trust_tier].value
                if caller_record
                else TrustTier.L3_PUBLIC.value
            )

            # 3. Check data isolation policy
            if not self.isolation_policy.can_access(data_classification, caller_tier):
                self._audit_log(
                    request_id, source_org, source_agent, None,
                    target_capability, data_classification,
                    "DENIED",
                    f"Isolation policy: {caller_tier} cannot access {data_classification}"
                )
                raise ValueError(
                    f"Data isolation policy violation: "
                    f"{caller_tier} → {data_classification}"
                )

            # 4. Select target agent (round-robin or capability-specific)
            target_record, target_cap, target_manifest = candidates[0]

            # 5. Check whitelist (if applicable)
            if target_cap.approved_orgs and source_org not in target_cap.approved_orgs:
                self._audit_log(
                    request_id, source_org, source_agent, target_record.agent_id,
                    target_capability, data_classification,
                    "DENIED", "Caller org not in approved whitelist"
                )
                return {
                    "status": "DENIED",
                    "reason": "Organization not approved for this capability",
                    "request_id": request_id,
                }

            # 6. Check rate limit
            allowed, cost = self._check_rate_limit(
                target_record.agent_id, target_cap
            )
            if not allowed:
                self._audit_log(
                    request_id, source_org, source_agent, target_record.agent_id,
                    target_capability, data_classification,
                    "RATE_LIMITED", "Rate limit exceeded"
                )
                return {
                    "status": "DENIED",
                    "reason": "Rate limit exceeded",
                    "request_id": request_id,
                }

            # 7. Forward request (mock implementation)
            response = await self._invoke_agent(
                target_record.agent_id,
                target_cap.name,
                request_payload,
            )

            # 8. Audit success
            self._audit_log(
                request_id, source_org, source_agent, target_record.agent_id,
                target_capability, data_classification,
                "ALLOWED", "Request processed", cost_usd=cost
            )

            return {
                "status": "ALLOWED",
                "target_agent": target_record.agent_id,
                "response": response,
                "cost_usd": cost,
                "request_id": request_id,
            }

        finally:
            session.close()

    def _check_rate_limit(self, agent_id: str, capability: Capability) -> Tuple[bool, float]:
        """Check rate limit for agent capability."""
        now = asyncio.get_event_loop().time()
        cap_key = f"{agent_id}:{capability.name}"

        if cap_key not in self.rate_limiters:
            self.rate_limiters[cap_key] = (0, now)

        count, reset_ts = self.rate_limiters[cap_key]

        # Reset every second
        if now >= reset_ts + 1.0:
            self.rate_limiters[cap_key] = (0, now)
            count = 0

        # Check limit
        if count >= capability.rate_limit_rps:
            return False, 0.0

        # Increment & calculate cost
        self.rate_limiters[cap_key] = (count + 1, reset_ts)
        cost = capability.cost_usd_per_1k / 1000.0

        return True, cost

    async def _invoke_agent(
        self,
        agent_id: str,
        capability: str,
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Invoke target agent (mock).

        In production:
        - Resolve agent endpoint from registry
        - Establish mTLS connection
        - Sign request with broker key
        - Forward to agent
        """
        # Mock response
        return {
            "agent": agent_id,
            "capability": capability,
            "result": "OK",
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _audit_log(
        self,
        request_id: str,
        source_org: str,
        source_agent: str,
        target_agent: Optional[str],
        capability: str,
        data_class: str,
        status: str,
        reason: str = "",
        cost_usd: float = 0.0,
    ):
        """Record immutable audit trail."""
        session = self.Session()
        try:
            checksum = hashlib.sha256(
                f"{request_id}{source_org}{target_agent}{capability}".encode()
            ).hexdigest()

            record = FederationRoutingRecord(
                request_id=request_id,
                source_org=source_org,
                source_agent=source_agent,
                target_agent=target_agent,
                capability=capability,
                data_classification=data_class,
                status=status,
                reason=reason,
                cost_usd=f"{cost_usd:.4f}",
                request_checksum=checksum,
            )
            session.add(record)
            session.commit()
        except Exception as e:
            self.logger.error(f"Audit log failed: {e}")
        finally:
            session.close()

    def get_federation_stats(self) -> Dict[str, Any]:
        """Return federation health metrics."""
        session = self.Session()
        try:
            total_agents = session.query(FederationAgentRecord).count()
            active_agents = session.query(FederationAgentRecord).filter_by(
                is_active=1
            ).count()

            # Last 24h stats
            cutoff = datetime.utcnow() - timedelta(hours=24)
            requests_24h = session.query(FederationRoutingRecord).filter(
                FederationRoutingRecord.timestamp >= cutoff
            ).count()

            allowed_24h = session.query(FederationRoutingRecord).filter(
                FederationRoutingRecord.timestamp >= cutoff,
                FederationRoutingRecord.status == "ALLOWED",
            ).count()

            return {
                "total_agents": total_agents,
                "active_agents": active_agents,
                "requests_24h": requests_24h,
                "allowed_24h": allowed_24h,
                "approval_rate": (
                    allowed_24h / requests_24h if requests_24h > 0 else 1.0
                ),
            }
        finally:
            session.close()
