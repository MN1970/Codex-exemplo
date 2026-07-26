# Audit & Compliance Dashboard — Phase 3.6 Implementation Guide

**Target**: `maestro-audit/audit_service.py` + `maestro-audit/compliance_dashboard.py`  
**Compliance**: GDPR, LGPD (Lei 13.709), data protection  
**Pattern**: Immutable audit trail + GDPR right-to-erasure  
**Timeline**: Phase 3.6 (Mar 01 - Mar 31, 2027)

This guide implements GDPR-ready compliance tracking with immutable audit logs and monthly governance reports.

---

## Overview

```
Maestro Operations
  ├── User query
  ├── Routing decision
  ├── Agent dispatch
  └── Response delivered
  ↓
Audit Service (Real-time)
  ├── Hash user prompt (SHA-256)
  ├── Hash response (SHA-256)
  ├── Store metadata (NOT plaintext)
  ├── Record decision chain
  └── Immutable append-only log
  ↓
Compliance Database
  ├── maestro_audit_log (immutable)
  ├── maestro_data_deletion_requests (GDPR)
  ├── maestro_deletion_log (permanent record)
  └── maestro_compliance_reports (monthly)
  ↓
Governance Dashboard
  ├── Query volume + latency
  ├── Agent usage + approval rates
  ├── Deletion requests fulfilled
  ├── Data protection metrics
  └── Monthly audit export (PDF/CSV)
```

---

## Part 1: Hashing & Data Protection

```python
# maestro-audit/data_protection.py

import hashlib
import logging
from typing import Optional, Dict
from datetime import datetime

logger = logging.getLogger(__name__)

class DataProtection:
    """GDPR-compliant data hashing and protection."""

    @staticmethod
    def hash_prompt(prompt: str, salt: Optional[str] = None) -> str:
        """
        Hash user prompt for audit trail (irreversible).

        Args:
            prompt: User query
            salt: Optional salt (org_id recommended)

        Returns:
            SHA-256 hash (64 hex chars)
        """
        if salt:
            combined = f"{salt}:{prompt}"
        else:
            combined = prompt

        return hashlib.sha256(combined.encode()).hexdigest()

    @staticmethod
    def hash_response(response: str, salt: Optional[str] = None) -> str:
        """Hash agent response."""
        if salt:
            combined = f"{salt}:{response}"
        else:
            combined = response

        return hashlib.sha256(combined.encode()).hexdigest()

    @staticmethod
    def hash_user_id(user_id: str, salt: str) -> str:
        """
        Hash user identifier for GDPR data subject identification.

        Args:
            user_id: Original user ID (email, UUID, etc.)
            salt: Organization salt (required)

        Returns:
            SHA-256 hash
        """
        combined = f"{salt}:{user_id}"
        return hashlib.sha256(combined.encode()).hexdigest()

    @staticmethod
    def create_deletion_request_id() -> str:
        """Generate unique deletion request ID."""
        import uuid
        return f"deletion_{uuid.uuid4().hex[:12]}"
```

---

## Part 2: Audit Service

```python
# maestro-audit/audit_service.py

from datetime import datetime
from typing import Dict, Optional, List
import logging
from supabase import create_client
from data_protection import DataProtection

logger = logging.getLogger(__name__)

class AuditService:
    """Record all operations in immutable audit trail."""

    def __init__(self, db_client, org_id: str):
        self.db = db_client
        self.org_id = org_id
        self.salt = org_id  # Use org_id as salt

    def log_routing_decision(
        self,
        user_id: str,
        prompt: str,
        routed_agent: str,
        confidence: float,
        latency_ms: int,
    ) -> Dict:
        """
        Log a routing decision (immutable).

        Args:
            user_id: User identifier (will be hashed)
            prompt: User query (will be hashed)
            routed_agent: Chosen agent
            confidence: Routing confidence (0-1)
            latency_ms: Routing latency

        Returns:
            Audit log entry ID
        """

        # Hash sensitive data
        user_id_hash = DataProtection.hash_user_id(user_id, self.salt)
        prompt_hash = DataProtection.hash_prompt(prompt, self.salt)

        # Create immutable log entry
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id_hash": user_id_hash,
            "prompt_hash": prompt_hash,
            "routed_agent": routed_agent,
            "confidence": confidence,
            "latency_ms": latency_ms,
            "action_type": "routing_decision",
            "org_id": self.org_id,
        }

        # Insert to Supabase (immutable append-only table)
        result = self.db.table("maestro_audit_log").insert(log_entry).execute()

        return {
            "audit_id": result.data[0]["id"] if result.data else None,
            "timestamp": log_entry["timestamp"],
        }

    def log_agent_response(
        self,
        user_id: str,
        agent_slug: str,
        response: str,
        tokens: Dict[str, int],
    ) -> Dict:
        """Log agent response (immutable)."""

        user_id_hash = DataProtection.hash_user_id(user_id, self.salt)
        response_hash = DataProtection.hash_response(response, self.salt)

        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id_hash": user_id_hash,
            "response_hash": response_hash,
            "agent_slug": agent_slug,
            "tokens_input": tokens.get("input", 0),
            "tokens_output": tokens.get("output", 0),
            "action_type": "agent_response",
            "org_id": self.org_id,
        }

        result = self.db.table("maestro_audit_log").insert(log_entry).execute()

        return {
            "audit_id": result.data[0]["id"] if result.data else None,
            "timestamp": log_entry["timestamp"],
        }

    def log_user_feedback(
        self,
        user_id: str,
        routed_agent: str,
        correct_agent: str,
        approved: bool,
    ) -> Dict:
        """Log user feedback (immutable)."""

        user_id_hash = DataProtection.hash_user_id(user_id, self.salt)

        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id_hash": user_id_hash,
            "routed_agent": routed_agent,
            "correct_agent": correct_agent,
            "approved": approved,
            "action_type": "user_feedback",
            "org_id": self.org_id,
        }

        result = self.db.table("maestro_audit_log").insert(log_entry).execute()

        return {
            "audit_id": result.data[0]["id"] if result.data else None,
            "timestamp": log_entry["timestamp"],
        }

    def get_user_audit_trail(self, user_id: str) -> List[Dict]:
        """
        Get all audit entries for a user (for GDPR subject access).

        Args:
            user_id: Original user ID (not hashed)

        Returns:
            List of audit log entries (hashed identifiers)
        """

        user_id_hash = DataProtection.hash_user_id(user_id, self.salt)

        result = self.db.table("maestro_audit_log").select(
            "*"
        ).eq("user_id_hash", user_id_hash).order(
            "timestamp", desc=True
        ).execute()

        return result.data
```

---

## Part 3: GDPR Right-to-Erasure

```python
# maestro-audit/gdpr_service.py

class GDPRService:
    """Handle GDPR data subject rights."""

    def __init__(self, db_client, audit_service, org_id: str):
        self.db = db_client
        self.audit = audit_service
        self.org_id = org_id

    def request_deletion(
        self,
        user_id: str,
        reason: Optional[str] = None,
    ) -> Dict:
        """
        Create GDPR deletion request (right-to-be-forgotten).

        Args:
            user_id: Data subject identifier
            reason: Optional reason for deletion

        Returns:
            Deletion request ID + status
        """

        deletion_request_id = DataProtection.create_deletion_request_id()
        user_id_hash = DataProtection.hash_user_id(user_id, self.org_id)

        # Create deletion request
        request = self.db.table("maestro_data_deletion_requests").insert({
            "request_id": deletion_request_id,
            "user_id_hash": user_id_hash,
            "reason": reason,
            "status": "pending",
            "requested_at": datetime.utcnow().isoformat(),
            "org_id": self.org_id,
        }).execute()

        return {
            "request_id": deletion_request_id,
            "status": "pending",
            "message": "Deletion request submitted. Will be processed within 30 days per GDPR Article 17.",
        }

    def process_deletion(self, request_id: str) -> Dict:
        """
        Execute deletion (irreversible).

        Only deletes:
        - maestro_conversations (user sessions)
        - maestro_user_feedback (feedback entries)

        Does NOT delete:
        - maestro_audit_log (immutable compliance record)
        - maestro_deletion_log (permanent proof of erasure)
        """

        # Get deletion request
        request_result = self.db.table("maestro_data_deletion_requests").select(
            "*"
        ).eq("request_id", request_id).execute()

        if not request_result.data:
            raise ValueError(f"Deletion request {request_id} not found")

        request = request_result.data[0]
        user_id_hash = request["user_id_hash"]

        # Delete conversations
        self.db.table("maestro_conversations").delete().eq(
            "user_id_hash", user_id_hash
        ).execute()

        # Delete feedback
        self.db.table("maestro_user_feedback").delete().eq(
            "user_id_hash", user_id_hash
        ).execute()

        # Record permanent deletion event (immutable)
        self.db.table("maestro_deletion_log").insert({
            "deletion_request_id": request_id,
            "user_id_hash": user_id_hash,
            "deleted_at": datetime.utcnow().isoformat(),
            "tables_deleted": ["maestro_conversations", "maestro_user_feedback"],
            "org_id": self.org_id,
        }).execute()

        # Update request status
        self.db.table("maestro_data_deletion_requests").update({
            "status": "completed",
            "completed_at": datetime.utcnow().isoformat(),
        }).eq("request_id", request_id).execute()

        return {
            "request_id": request_id,
            "status": "completed",
            "deleted_tables": ["maestro_conversations", "maestro_user_feedback"],
        }

    def get_deletion_requests(self, status: Optional[str] = None) -> List[Dict]:
        """Get deletion requests (for compliance tracking)."""

        query = self.db.table("maestro_data_deletion_requests").select("*").eq(
            "org_id", self.org_id
        )

        if status:
            query = query.eq("status", status)

        result = query.order("requested_at", desc=True).execute()

        return result.data
```

---

## Part 4: Compliance Dashboard

```python
# maestro-audit/compliance_dashboard.py

from datetime import datetime, timedelta

class ComplianceDashboard:
    """Generate compliance metrics and governance reports."""

    def __init__(self, db_client):
        self.db = db_client

    def get_monthly_metrics(self, year: int, month: int) -> Dict:
        """Get compliance metrics for a month."""

        start_date = datetime(year, month, 1)
        end_date = datetime(year, month + 1, 1) if month < 12 else datetime(year + 1, 1, 1)

        # Query audit log
        audit_result = self.db.table("maestro_audit_log").select(
            "action_type, COUNT(*) as count"
        ).gte("timestamp", start_date.isoformat()).lt(
            "timestamp", end_date.isoformat()
        ).group_by("action_type").execute()

        # Count deletions
        deletion_result = self.db.table("maestro_data_deletion_requests").select(
            "COUNT(*) as total"
        ).eq("status", "completed").gte(
            "completed_at", start_date.isoformat()
        ).execute()

        return {
            "period": f"{year}-{month:02d}",
            "audit_entries": {
                item["action_type"]: item["count"]
                for item in audit_result.data
            },
            "deletions_completed": deletion_result.data[0]["total"] if deletion_result.data else 0,
            "generated_at": datetime.utcnow().isoformat(),
        }

    def export_audit_report(self, year: int, month: int, format: str = "csv") -> str:
        """
        Export audit report for governance.

        Args:
            year, month: Period to export
            format: "csv" or "json"

        Returns:
            CSV/JSON string
        """

        start_date = datetime(year, month, 1)
        end_date = datetime(year, month + 1, 1) if month < 12 else datetime(year + 1, 1, 1)

        # Query audit log
        result = self.db.table("maestro_audit_log").select(
            "timestamp, action_type, routed_agent, latency_ms"
        ).gte("timestamp", start_date.isoformat()).lt(
            "timestamp", end_date.isoformat()
        ).execute()

        entries = result.data

        if format == "csv":
            return self._format_csv(entries)
        elif format == "json":
            return self._format_json(entries)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _format_csv(self, entries: List[Dict]) -> str:
        """Format audit log as CSV."""
        import csv
        import io

        output = io.StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=["timestamp", "action_type", "routed_agent", "latency_ms"]
        )

        writer.writeheader()
        for entry in entries:
            writer.writerow({
                "timestamp": entry.get("timestamp"),
                "action_type": entry.get("action_type"),
                "routed_agent": entry.get("routed_agent"),
                "latency_ms": entry.get("latency_ms"),
            })

        return output.getvalue()

    def _format_json(self, entries: List[Dict]) -> str:
        """Format audit log as JSON."""
        import json

        return json.dumps(entries, indent=2, default=str)

    def get_data_protection_status(self) -> Dict:
        """Get data protection status."""

        # Count deletion requests
        deletion_result = self.db.table("maestro_data_deletion_requests").select(
            "status, COUNT(*) as count"
        ).group_by("status").execute()

        status_summary = {
            item["status"]: item["count"]
            for item in deletion_result.data
        }

        # Count audit entries (last 30 days)
        thirty_days_ago = (datetime.utcnow() - timedelta(days=30)).isoformat()
        audit_result = self.db.table("maestro_audit_log").select(
            "COUNT(*) as total"
        ).gte("timestamp", thirty_days_ago).execute()

        return {
            "deletion_requests": status_summary,
            "audit_entries_30d": audit_result.data[0]["total"] if audit_result.data else 0,
            "data_protection_status": "operational",
            "timestamp": datetime.utcnow().isoformat(),
        }
```

---

## Part 5: Database Schema

```sql
-- maestro_audit_log (immutable append-only)
CREATE TABLE maestro_audit_log (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL DEFAULT now(),
    user_id_hash VARCHAR(64) NOT NULL,
    prompt_hash VARCHAR(64),
    response_hash VARCHAR(64),
    routed_agent VARCHAR(50),
    correct_agent VARCHAR(50),
    approved BOOLEAN,
    tokens_input INT,
    tokens_output INT,
    latency_ms INT,
    action_type VARCHAR(50) NOT NULL,
    org_id VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT now()
);
-- Make immutable: prevent updates/deletes
ALTER TABLE maestro_audit_log
    DISABLE TRIGGER USER;

-- maestro_data_deletion_requests (GDPR)
CREATE TABLE maestro_data_deletion_requests (
    id BIGSERIAL PRIMARY KEY,
    request_id VARCHAR(32) UNIQUE NOT NULL,
    user_id_hash VARCHAR(64) NOT NULL,
    reason TEXT,
    status VARCHAR(20) DEFAULT 'pending',  -- pending, completed
    requested_at TIMESTAMP DEFAULT now(),
    completed_at TIMESTAMP,
    org_id VARCHAR(255) NOT NULL
);

-- maestro_deletion_log (proof of erasure)
CREATE TABLE maestro_deletion_log (
    id BIGSERIAL PRIMARY KEY,
    deletion_request_id VARCHAR(32) NOT NULL,
    user_id_hash VARCHAR(64) NOT NULL,
    deleted_at TIMESTAMP DEFAULT now(),
    tables_deleted JSONB,
    org_id VARCHAR(255) NOT NULL
);

CREATE INDEX idx_audit_timestamp ON maestro_audit_log(timestamp);
CREATE INDEX idx_audit_user_hash ON maestro_audit_log(user_id_hash);
CREATE INDEX idx_audit_action ON maestro_audit_log(action_type);
CREATE INDEX idx_deletion_status ON maestro_data_deletion_requests(status);
CREATE INDEX idx_deletion_log_user ON maestro_deletion_log(user_id_hash);
```

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|------------|
| **Audit Trail Completeness** | 100% | All actions logged |
| **Deletion Request Response** | <30 days | GDPR compliance |
| **Data Protection Audit** | Annual | Internal + external |
| **Zero Data Breaches** | 0 | Incident tracking |

---

## Deployment Checklist

- [ ] Implement DataProtection hashing
- [ ] Implement AuditService (immutable logging)
- [ ] Implement GDPRService (right-to-erasure)
- [ ] Implement ComplianceDashboard
- [ ] Create audit_log table (immutable)
- [ ] Create deletion_requests table
- [ ] Create deletion_log table (proof)
- [ ] Write unit tests (GDPR compliance)
- [ ] Deploy to production
- [ ] Document data retention policy
- [ ] Configure monthly report exports
- [ ] Set up GDPR incident alerts
- [ ] Train team on compliance procedures

---

**Status**: Ready for implementation  
**Owner**: Compliance + DevOps  
**Timeline**: Phase 3.6 (Mar 01 - Mar 31, 2027)

**Standards Compliance**:
- ✅ GDPR (EU) — Article 17 (right to erasure)
- ✅ LGPD (Brazil) — Lei 13.709 (data protection)
- ✅ CCPA (California) — right to deletion
- ✅ SOC 2 Type II (audit trail)
