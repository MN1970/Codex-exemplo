"""
AFP/1.0 — Agent Federation Protocol

JSON-based message format and handshake for agent communication.
Phase 4.1 implementation.
"""

import json
import hashlib
import time
import uuid
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime


class MessageType(Enum):
    """AFP/1.0 message types."""
    HANDSHAKE_REQUEST = "HANDSHAKE_REQUEST"
    HANDSHAKE_RESPONSE = "HANDSHAKE_RESPONSE"
    CAPABILITY_ADVERTISEMENT = "CAPABILITY_ADVERTISEMENT"
    CAPABILITY_ACK = "CAPABILITY_ACK"
    REQUEST = "REQUEST"
    RESPONSE = "RESPONSE"
    ERROR = "ERROR"
    HEARTBEAT = "HEARTBEAT"


class AFPVersion:
    """AFP/1.0 version constants."""
    MAJOR = 1
    MINOR = 0
    PATCH = 0
    STRING = "1.0.0"


@dataclass
class AFPMessage:
    """
    AFP/1.0 Message Structure (JSON Schema).

    Example:
    {
        "type": "REQUEST",
        "version": "1.0.0",
        "message_id": "msg-abc123...",
        "timestamp": "2027-01-15T14:30:00Z",
        "source": {
            "agent_id": "partner-acme-claims-v1",
            "org_id": "org-2"
        },
        "target": {
            "agent_id": "manta-01-claims",
            "org_id": "org-1"
        },
        "capability": "route-claims",
        "payload": {...},
        "data_classification": "CONFIDENTIAL",
        "signature": {
            "algorithm": "HMAC-SHA256",
            "value": "abcd1234...",
            "certificate_fingerprint": "sha256:..."
        }
    }
    """

    message_type: str  # MessageType.value
    version: str = AFPVersion.STRING
    message_id: str = ""
    timestamp: str = ""
    source: Dict[str, str] = None  # {agent_id, org_id}
    target: Dict[str, str] = None  # {agent_id, org_id}
    capability: Optional[str] = None
    payload: Dict[str, Any] = None
    data_classification: str = "PUBLIC"
    signature: Dict[str, str] = None  # {algorithm, value, cert_fingerprint}

    def __post_init__(self):
        """Initialize defaults."""
        if not self.timestamp:
            self.timestamp = self._iso8601_now()
        if not self.message_id:
            self.message_id = self._generate_id()
        if not self.source:
            self.source = {}
        if not self.target:
            self.target = {}
        if not self.payload:
            self.payload = {}

    def to_json(self, include_signature: bool = True) -> str:
        """Serialize message."""
        data = asdict(self)
        if not include_signature:
            data.pop("signature", None)
        return json.dumps(data, sort_keys=True, default=str)

    def to_dict(self) -> Dict[str, Any]:
        """Return as dictionary."""
        return json.loads(self.to_json())

    @staticmethod
    def _generate_id() -> str:
        """Generate unique message ID."""
        return f"msg-{uuid.uuid4().hex[:16]}"

    @staticmethod
    def _iso8601_now() -> str:
        """Current timestamp in ISO8601."""
        return datetime.utcnow().isoformat() + "Z"

    def sign(self, signing_key: str, cert_fingerprint: str) -> None:
        """
        Sign message with HMAC-SHA256.

        Args:
            signing_key: Org's private key material (secret)
            cert_fingerprint: mTLS certificate fingerprint (for audit)
        """
        message_bytes = self.to_json(include_signature=False).encode()
        sig = hashlib.sha256(message_bytes + signing_key.encode()).hexdigest()

        self.signature = {
            "algorithm": "HMAC-SHA256",
            "value": sig,
            "certificate_fingerprint": cert_fingerprint,
        }

    def verify_signature(self, signing_key: str) -> bool:
        """
        Verify message signature.

        Args:
            signing_key: Org's private key material

        Returns:
            True if signature is valid
        """
        if not self.signature:
            return False

        message_bytes = self.to_json(include_signature=False).encode()
        expected_sig = hashlib.sha256(
            message_bytes + signing_key.encode()
        ).hexdigest()

        return self.signature.get("value") == expected_sig


class AFPHandshake:
    """
    AFP/1.0 Authentication Handshake.

    Flow:
    1. Agent A sends HANDSHAKE_REQUEST (client hello)
    2. Broker responds HANDSHAKE_RESPONSE (server hello + challenge)
    3. Agent A sends signed HANDSHAKE_REQUEST (proof of key possession)
    4. Broker sends HANDSHAKE_RESPONSE (success)
    5. Agents exchange capabilities (CAPABILITY_ADVERTISEMENT)
    """

    @staticmethod
    def create_handshake_request(
        agent_id: str,
        org_id: str,
        cert_fingerprint: str,
    ) -> AFPMessage:
        """
        Create initial handshake request.

        Args:
            agent_id: Agent identifier
            org_id: Organization identifier
            cert_fingerprint: mTLS cert fingerprint (sha256:...)

        Returns:
            HANDSHAKE_REQUEST message
        """
        return AFPMessage(
            message_type=MessageType.HANDSHAKE_REQUEST.value,
            source={"agent_id": agent_id, "org_id": org_id},
            payload={
                "certificate_fingerprint": cert_fingerprint,
                "supported_features": ["rate_limiting", "data_classification"],
            },
        )

    @staticmethod
    def create_handshake_response(
        request: AFPMessage,
        challenge: str,
        accepted: bool = True,
    ) -> AFPMessage:
        """
        Create handshake response (broker or target agent).

        Args:
            request: Original HANDSHAKE_REQUEST
            challenge: Random bytes (hex) for proof-of-possession
            accepted: Whether to accept connection

        Returns:
            HANDSHAKE_RESPONSE message
        """
        return AFPMessage(
            message_type=MessageType.HANDSHAKE_RESPONSE.value,
            source={"agent_id": "broker", "org_id": "manta"},
            target=request.source,
            payload={
                "accepted": accepted,
                "challenge": challenge,
                "broker_version": AFPVersion.STRING,
                "timestamp": int(time.time()),
            },
        )


class AFPCapabilityAd:
    """
    AFP/1.0 Capability Advertisement.

    Sent after successful handshake to advertise agent's capabilities.
    """

    @staticmethod
    def create_advertisement(
        agent_id: str,
        org_id: str,
        capabilities: list,
    ) -> AFPMessage:
        """
        Create capability advertisement.

        Args:
            agent_id: Agent ID
            org_id: Org ID
            capabilities: List of Capability objects (from federation_broker.py)

        Returns:
            CAPABILITY_ADVERTISEMENT message
        """
        cap_list = []
        for cap in capabilities:
            cap_list.append({
                "name": cap.name,
                "domain": cap.domain,
                "version": cap.version,
                "requires_org_context": cap.requires_org_context,
                "rate_limit_rps": cap.rate_limit_rps,
                "cost_usd_per_1k": cap.cost_usd_per_1k,
            })

        return AFPMessage(
            message_type=MessageType.CAPABILITY_ADVERTISEMENT.value,
            source={"agent_id": agent_id, "org_id": org_id},
            target={"agent_id": "broker", "org_id": "manta"},
            payload={
                "capabilities": cap_list,
                "total_capabilities": len(cap_list),
                "manifest_version": "1.0",
            },
        )

    @staticmethod
    def create_ack(request: AFPMessage, success: bool = True) -> AFPMessage:
        """
        Acknowledge capability advertisement.

        Args:
            request: Original CAPABILITY_ADVERTISEMENT message
            success: Whether capabilities were registered

        Returns:
            CAPABILITY_ACK message
        """
        return AFPMessage(
            message_type=MessageType.CAPABILITY_ACK.value,
            source={"agent_id": "broker", "org_id": "manta"},
            target=request.source,
            payload={
                "success": success,
                "capabilities_registered": len(request.payload.get("capabilities", [])),
                "timestamp": int(time.time()),
            },
        )


class AFPRequest:
    """
    AFP/1.0 Request Message.

    Cross-org capability request.
    """

    @staticmethod
    def create_request(
        source_agent: str,
        source_org: str,
        target_agent: str,
        target_org: str,
        capability: str,
        payload: Dict[str, Any],
        data_classification: str = "PUBLIC",
    ) -> AFPMessage:
        """
        Create capability request.

        Args:
            source_agent: Calling agent ID
            source_org: Calling org ID
            target_agent: Target agent ID
            target_org: Target org ID
            capability: Capability name (e.g., "route-claims")
            payload: Request parameters
            data_classification: Data sensitivity level

        Returns:
            REQUEST message
        """
        return AFPMessage(
            message_type=MessageType.REQUEST.value,
            source={"agent_id": source_agent, "org_id": source_org},
            target={"agent_id": target_agent, "org_id": target_org},
            capability=capability,
            payload=payload,
            data_classification=data_classification,
        )


class AFPResponse:
    """
    AFP/1.0 Response Message.
    """

    @staticmethod
    def create_response(
        request: AFPMessage,
        result: Dict[str, Any],
        status: str = "OK",
    ) -> AFPMessage:
        """
        Create capability response.

        Args:
            request: Original REQUEST message
            result: Response data
            status: Status code ("OK", "ERROR", "TIMEOUT")

        Returns:
            RESPONSE message
        """
        return AFPMessage(
            message_type=MessageType.RESPONSE.value,
            source=request.target,  # Swap source/target
            target=request.source,
            capability=request.capability,
            payload={
                "status": status,
                "result": result,
                "request_id": request.message_id,
                "timestamp": int(time.time()),
            },
        )

    @staticmethod
    def create_error(
        request: AFPMessage,
        error_code: str,
        error_message: str,
    ) -> AFPMessage:
        """
        Create error response.

        Args:
            request: Original REQUEST message
            error_code: Error code ("TIMEOUT", "RATE_LIMITED", "DENIED", etc.)
            error_message: Human-readable error message

        Returns:
            ERROR message
        """
        return AFPMessage(
            message_type=MessageType.ERROR.value,
            source=request.target,
            target=request.source,
            capability=request.capability,
            payload={
                "error_code": error_code,
                "error_message": error_message,
                "request_id": request.message_id,
                "timestamp": int(time.time()),
            },
        )


class AFPHeartbeat:
    """
    AFP/1.0 Heartbeat (keep-alive).
    """

    @staticmethod
    def create_heartbeat(agent_id: str, org_id: str) -> AFPMessage:
        """
        Create heartbeat message.

        Args:
            agent_id: Agent ID
            org_id: Org ID

        Returns:
            HEARTBEAT message
        """
        return AFPMessage(
            message_type=MessageType.HEARTBEAT.value,
            source={"agent_id": agent_id, "org_id": org_id},
            target={"agent_id": "broker", "org_id": "manta"},
            payload={"timestamp": int(time.time())},
        )
