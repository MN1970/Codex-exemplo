"""
Federation Test Suite — Phase 4.1 Comprehensive Tests

Tests for:
- Broker capability routing
- mTLS authentication
- Data isolation enforcement
- AFP/1.0 protocol
- Rate limiting
- Audit logging
"""

import pytest
import json
import hashlib
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock, patch

# Import modules under test
import sys
sys.path.insert(0, '/home/user/Codex-exemplo')

from maestro.federation_broker import (
    FederationBroker, CapabilityManifest, Capability, TrustTier,
    DataIsolationPolicy, FederationAgentRecord, FederationRoutingRecord
)
from maestro.afp_protocol import (
    AFPMessage, AFPHandshake, AFPCapabilityAd, AFPRequest, AFPResponse,
    MessageType, AFPVersion
)
from maestro.mtls_handler import MTLSHandler, CertificateStatus
from maestro.data_isolation_validator import DataIsolationValidator


# ============================================================================
# CAPABILITY MANIFEST TESTS
# ============================================================================

class TestCapabilityManifest:
    """Test capability manifest creation and validation."""

    def test_capability_validation_valid(self):
        """Test valid capability."""
        cap = Capability(
            name="route-claims",
            domain="claims",
            version="1.0.0",
            requires_org_context=True,
        )
        cap.validate()  # Should not raise

    def test_capability_validation_missing_name(self):
        """Test capability with missing name."""
        cap = Capability(
            name="",
            domain="claims",
            version="1.0.0",
            requires_org_context=True,
        )
        with pytest.raises(ValueError, match="name"):
            cap.validate()

    def test_capability_validation_invalid_rate_limit(self):
        """Test capability with invalid rate limit."""
        cap = Capability(
            name="route-claims",
            domain="claims",
            version="1.0.0",
            requires_org_context=True,
            rate_limit_rps=0,
        )
        with pytest.raises(ValueError, match="rate_limit_rps"):
            cap.validate()

    def test_manifest_signature_generation(self):
        """Test manifest signature creation."""
        cap = Capability(
            name="route-claims",
            domain="claims",
            version="1.0.0",
            requires_org_context=True,
        )
        manifest = CapabilityManifest(
            agent_id="manta-01-claims",
            org_id="org-1",
            trust_tier=TrustTier.L1_MANTA,
            capabilities=[cap],
        )

        org_secret = "super-secret-key"
        manifest.signature_sha256 = hashlib.sha256(
            manifest.to_json().encode() + org_secret.encode()
        ).hexdigest()

        assert manifest.validate_signature(org_secret)

    def test_manifest_signature_validation_fails_wrong_key(self):
        """Test signature validation with wrong key."""
        cap = Capability(
            name="route-claims",
            domain="claims",
            version="1.0.0",
            requires_org_context=True,
        )
        manifest = CapabilityManifest(
            agent_id="manta-01-claims",
            org_id="org-1",
            trust_tier=TrustTier.L1_MANTA,
            capabilities=[cap],
        )

        manifest.signature_sha256 = "invalid-signature"
        assert not manifest.validate_signature("any-key")


# ============================================================================
# DATA ISOLATION POLICY TESTS
# ============================================================================

class TestDataIsolationPolicy:
    """Test data isolation enforcement."""

    def test_tier_access_public_data(self):
        """Test all tiers can access public data."""
        policy = DataIsolationPolicy()
        assert policy.can_access("PUBLIC", "L1_MANTA")
        assert policy.can_access("PUBLIC", "L2_PARTNER")
        assert policy.can_access("PUBLIC", "L3_PUBLIC")

    def test_tier_access_internal_data(self):
        """Test only L1_MANTA can access internal data."""
        policy = DataIsolationPolicy()
        assert policy.can_access("INTERNAL", "L1_MANTA")
        assert not policy.can_access("INTERNAL", "L2_PARTNER")
        assert not policy.can_access("INTERNAL", "L3_PUBLIC")

    def test_tier_access_confidential_data(self):
        """Test L1_MANTA and L2_PARTNER can access confidential."""
        policy = DataIsolationPolicy()
        assert policy.can_access("CONFIDENTIAL", "L1_MANTA")
        assert policy.can_access("CONFIDENTIAL", "L2_PARTNER")
        assert not policy.can_access("CONFIDENTIAL", "L3_PUBLIC")


# ============================================================================
# AFP/1.0 PROTOCOL TESTS
# ============================================================================

class TestAFPMessage:
    """Test AFP message creation and manipulation."""

    def test_message_creation(self):
        """Test basic AFP message creation."""
        msg = AFPMessage(
            message_type=MessageType.REQUEST.value,
            source={"agent_id": "agent-1", "org_id": "org-1"},
            target={"agent_id": "agent-2", "org_id": "org-2"},
            capability="route-claims",
            payload={"claim_id": "123"},
        )
        assert msg.message_type == "REQUEST"
        assert msg.source["agent_id"] == "agent-1"
        assert len(msg.message_id) > 0

    def test_message_json_serialization(self):
        """Test message serialization to JSON."""
        msg = AFPMessage(
            message_type=MessageType.REQUEST.value,
            source={"agent_id": "agent-1", "org_id": "org-1"},
            payload={"test": "data"},
        )
        json_str = msg.to_json()
        parsed = json.loads(json_str)
        assert parsed["message_type"] == "REQUEST"
        assert parsed["payload"]["test"] == "data"

    def test_message_signing(self):
        """Test message signature creation and verification."""
        msg = AFPMessage(
            message_type=MessageType.REQUEST.value,
            source={"agent_id": "agent-1", "org_id": "org-1"},
            payload={"data": "value"},
        )
        signing_key = "secret-key-123"
        cert_fingerprint = "sha256:abcd1234"

        msg.sign(signing_key, cert_fingerprint)
        assert msg.signature is not None
        assert msg.signature["algorithm"] == "HMAC-SHA256"
        assert msg.signature["certificate_fingerprint"] == cert_fingerprint

    def test_message_signature_verification(self):
        """Test signature verification."""
        msg = AFPMessage(
            message_type=MessageType.REQUEST.value,
            source={"agent_id": "agent-1", "org_id": "org-1"},
            payload={"data": "value"},
        )
        signing_key = "secret-key-123"
        msg.sign(signing_key, "sha256:abcd1234")

        # Verify with correct key
        assert msg.verify_signature(signing_key)

        # Verify with wrong key
        assert not msg.verify_signature("wrong-key")


class TestAFPHandshake:
    """Test AFP handshake protocol."""

    def test_handshake_request_creation(self):
        """Test handshake request message."""
        req = AFPHandshake.create_handshake_request(
            agent_id="partner-agent",
            org_id="org-2",
            cert_fingerprint="sha256:abc123",
        )
        assert req.message_type == "HANDSHAKE_REQUEST"
        assert req.source["agent_id"] == "partner-agent"
        assert req.payload["certificate_fingerprint"] == "sha256:abc123"

    def test_handshake_response_creation(self):
        """Test handshake response message."""
        req = AFPHandshake.create_handshake_request(
            agent_id="partner-agent",
            org_id="org-2",
            cert_fingerprint="sha256:abc123",
        )
        resp = AFPHandshake.create_handshake_response(
            request=req,
            challenge="challenge-token",
            accepted=True,
        )
        assert resp.message_type == "HANDSHAKE_RESPONSE"
        assert resp.payload["accepted"] is True
        assert resp.payload["challenge"] == "challenge-token"


class TestAFPCapabilityAdvertisement:
    """Test capability advertisement messages."""

    def test_capability_ad_creation(self):
        """Test capability advertisement."""
        cap = Capability(
            name="route-claims",
            domain="claims",
            version="1.0.0",
            requires_org_context=True,
        )
        ad = AFPCapabilityAd.create_advertisement(
            agent_id="partner-agent",
            org_id="org-2",
            capabilities=[cap],
        )
        assert ad.message_type == "CAPABILITY_ADVERTISEMENT"
        assert len(ad.payload["capabilities"]) == 1
        assert ad.payload["capabilities"][0]["name"] == "route-claims"

    def test_capability_ack_creation(self):
        """Test capability acknowledgment."""
        cap = Capability(
            name="route-claims",
            domain="claims",
            version="1.0.0",
            requires_org_context=True,
        )
        ad = AFPCapabilityAd.create_advertisement(
            agent_id="partner-agent",
            org_id="org-2",
            capabilities=[cap],
        )
        ack = AFPCapabilityAd.create_ack(request=ad, success=True)
        assert ack.message_type == "CAPABILITY_ACK"
        assert ack.payload["success"] is True


# ============================================================================
# DATA ISOLATION VALIDATOR TESTS
# ============================================================================

class TestDataIsolationValidator:
    """Test data isolation validation."""

    def test_validator_initialization(self):
        """Test validator creation."""
        validator = DataIsolationValidator()
        assert validator is not None
        assert "org-1" in validator.org_data_patterns

    def test_request_isolation_no_leakage(self):
        """Test request validation with no data leakage."""
        validator = DataIsolationValidator()
        payload = {"project_id": "generic-123", "client_name": "Test Corp"}
        is_valid, violations = validator.validate_request_isolation(
            request_id="req-123",
            source_org="org-1",
            target_org="org-2",
            request_payload=payload,
        )
        # No Manta-specific data patterns matched
        assert is_valid

    def test_request_isolation_with_leakage(self):
        """Test request validation detects leakage."""
        validator = DataIsolationValidator()
        payload = {"project_id": "manta-12345"}  # Matches manta-\d{5}
        is_valid, violations = validator.validate_request_isolation(
            request_id="req-123",
            source_org="org-1",
            target_org="org-2",
            request_payload=payload,
        )
        assert not is_valid
        assert len(violations) > 0
        assert violations[0].severity == "HIGH"

    def test_isolation_report_generation(self):
        """Test isolation report generation."""
        validator = DataIsolationValidator()
        payload = {"project_id": "manta-12345"}
        validator.validate_request_isolation(
            request_id="req-123",
            source_org="org-1",
            target_org="org-2",
            request_payload=payload,
        )
        report = validator.get_isolation_report("org-1")
        assert report["org_id"] == "org-1"
        assert report["total_violations"] > 0


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestFederationIntegration:
    """Integration tests for federation system."""

    @pytest.mark.asyncio
    async def test_end_to_end_federation_flow(self):
        """Test complete federation flow: handshake -> capability ad -> request."""
        # 1. Handshake
        hs_req = AFPHandshake.create_handshake_request(
            agent_id="partner-claims",
            org_id="org-2",
            cert_fingerprint="sha256:partner123",
        )
        assert hs_req.message_type == "HANDSHAKE_REQUEST"

        # 2. Handshake response
        hs_resp = AFPHandshake.create_handshake_response(
            request=hs_req,
            challenge="broker-challenge",
            accepted=True,
        )
        assert hs_resp.payload["accepted"] is True

        # 3. Capability advertisement
        cap = Capability(
            name="classify-claim",
            domain="claims",
            version="1.0.0",
            requires_org_context=False,
        )
        ad = AFPCapabilityAd.create_advertisement(
            agent_id="partner-claims",
            org_id="org-2",
            capabilities=[cap],
        )
        assert ad.payload["total_capabilities"] == 1

        # 4. Capability ACK
        ack = AFPCapabilityAd.create_ack(request=ad, success=True)
        assert ack.payload["success"] is True

        # 5. Request
        req = AFPRequest.create_request(
            source_agent="manta-01-claims",
            source_org="org-1",
            target_agent="partner-claims",
            target_org="org-2",
            capability="classify-claim",
            payload={"claim_text": "..."},
            data_classification="CONFIDENTIAL",
        )
        assert req.capability == "classify-claim"
        assert req.data_classification == "CONFIDENTIAL"

        # 6. Response
        resp = AFPResponse.create_response(
            request=req,
            result={"classification": "auto", "confidence": 0.95},
            status="OK",
        )
        assert resp.message_type == "RESPONSE"
        assert resp.payload["result"]["classification"] == "auto"


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

class TestFederationPerformance:
    """Performance and scalability tests."""

    def test_message_creation_speed(self):
        """Test message creation throughput."""
        import time
        start = time.time()
        for i in range(1000):
            AFPMessage(
                message_type=MessageType.REQUEST.value,
                source={"agent_id": f"agent-{i}", "org_id": "org-1"},
                payload={"test": "data"},
            )
        elapsed = time.time() - start
        # Should create 1000 messages in < 100ms
        assert elapsed < 0.1

    def test_signature_verification_speed(self):
        """Test signature verification throughput."""
        import time
        msg = AFPMessage(
            message_type=MessageType.REQUEST.value,
            source={"agent_id": "agent-1", "org_id": "org-1"},
            payload={"data": "value"},
        )
        signing_key = "secret-key"
        msg.sign(signing_key, "sha256:abc")

        start = time.time()
        for _ in range(1000):
            msg.verify_signature(signing_key)
        elapsed = time.time() - start
        # Should verify 1000 sigs in < 200ms
        assert elapsed < 0.2


# ============================================================================
# SECURITY TESTS
# ============================================================================

class TestFederationSecurity:
    """Security-focused tests."""

    def test_isolation_policy_enforcement(self):
        """Test data isolation policy is enforced."""
        policy = DataIsolationPolicy()
        # L3_PUBLIC should not access INTERNAL data
        assert not policy.can_access("INTERNAL", "L3_PUBLIC")

    def test_manifest_tampering_detection(self):
        """Test tampered manifest is detected."""
        cap = Capability(
            name="route-claims",
            domain="claims",
            version="1.0.0",
            requires_org_context=True,
        )
        manifest = CapabilityManifest(
            agent_id="manta-01-claims",
            org_id="org-1",
            trust_tier=TrustTier.L1_MANTA,
            capabilities=[cap],
        )
        org_secret = "super-secret"
        manifest.signature_sha256 = hashlib.sha256(
            manifest.to_json().encode() + org_secret.encode()
        ).hexdigest()

        # Tamper with manifest
        manifest.agent_id = "hacked-agent"
        assert not manifest.validate_signature(org_secret)

    def test_data_exfiltration_detection(self):
        """Test data exfiltration is detected."""
        validator = DataIsolationValidator()
        validator.register_org_data_patterns("org-1", [r"secret-\d+"])

        # Try to exfiltrate secret data
        payload = {"hidden_data": "secret-12345"}
        is_valid, violations = validator.validate_request_isolation(
            request_id="req-exfil",
            source_org="org-1",
            target_org="org-3",
            request_payload=payload,
        )
        assert not is_valid
        assert len(violations) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
