"""
Data Isolation Validator

Cross-org data leakage detection and compliance validation.
Phase 4.1 implementation.
"""

import json
import hashlib
import logging
import re
from typing import Dict, List, Tuple, Any
from datetime import datetime
from dataclasses import dataclass


@dataclass
class IsolationViolation:
    """Record of potential data leakage."""
    violation_id: str
    source_org: str
    target_org: str
    request_id: str
    data_elements: List[str]  # e.g., ["client_name", "contract_id"]
    severity: str  # "CRITICAL", "HIGH", "MEDIUM", "LOW"
    timestamp: str
    details: str


class DataIsolationValidator:
    """
    Cross-Org Data Isolation Enforcement.

    Detects:
    - Unintended org context leakage
    - Shared internal data exposure
    - Query result exfiltration
    """

    def __init__(self, logger: logging.Logger = None):
        """
        Initialize validator.

        Args:
            logger: Optional logger instance
        """
        self.logger = logger or logging.getLogger("DataIsolationValidator")

        # Org-specific data patterns (PII, contracts, etc.)
        self.org_data_patterns: Dict[str, List[str]] = {
            # Format: {"org_id": ["regex pattern", ...]}
            "org-1": [  # Manta internal
                r"manta-\d{5}",  # Internal project IDs
                r"mneves@mantaassociados\.com",  # Internal emails
            ],
            "org-2": [  # Partner
                r"partner-acme-\d+",  # Partner project IDs
            ],
        }

        # Violation log: {org_id: [IsolationViolation, ...]}
        self.violations: Dict[str, List[IsolationViolation]] = {}

    def register_org_data_patterns(self, org_id: str, patterns: List[str]):
        """
        Register data patterns for an organization.

        Args:
            org_id: Organization ID
            patterns: List of regex patterns identifying org-specific data
        """
        self.org_data_patterns[org_id] = patterns
        self.logger.info(f"Registered {len(patterns)} patterns for org {org_id}")

    def validate_request_isolation(
        self,
        request_id: str,
        source_org: str,
        target_org: str,
        request_payload: Dict[str, Any],
    ) -> Tuple[bool, List[IsolationViolation]]:
        """
        Validate that request doesn't leak source org data to target org.

        Args:
            request_id: Request identifier
            source_org: Calling organization
            target_org: Target organization
            request_payload: Request body (will be scanned)

        Returns:
            (is_valid, violations) - True if request is safe to send
        """
        violations = []

        # Extract all strings from payload
        payload_strings = self._extract_strings(request_payload)

        # Check if any source org data patterns appear in request
        source_patterns = self.org_data_patterns.get(source_org, [])

        for pattern in source_patterns:
            try:
                regex = re.compile(pattern)
                matched_data = []
                for s in payload_strings:
                    if regex.search(str(s)):
                        matched_data.append(s)

                if matched_data:
                    violation = IsolationViolation(
                        violation_id=f"iso-{hashlib.md5(request_id.encode()).hexdigest()[:8]}",
                        source_org=source_org,
                        target_org=target_org,
                        request_id=request_id,
                        data_elements=matched_data[:5],  # Top 5 examples
                        severity="HIGH",
                        timestamp=datetime.utcnow().isoformat(),
                        details=f"Source org data matched pattern '{pattern}'",
                    )
                    violations.append(violation)
            except Exception as e:
                self.logger.warning(f"Pattern validation failed: {e}")

        # Store violations
        if violations:
            if source_org not in self.violations:
                self.violations[source_org] = []
            self.violations[source_org].extend(violations)

        return len(violations) == 0, violations

    def validate_response_isolation(
        self,
        request_id: str,
        source_org: str,
        target_org: str,
        response_payload: Dict[str, Any],
    ) -> Tuple[bool, List[IsolationViolation]]:
        """
        Validate that response doesn't leak target org data to source org.

        Args:
            request_id: Request identifier
            source_org: Calling organization
            target_org: Target organization
            response_payload: Response body

        Returns:
            (is_valid, violations) - True if response is safe to return
        """
        violations = []

        # Extract all strings from response
        response_strings = self._extract_strings(response_payload)

        # Check if any target org data patterns appear in response
        target_patterns = self.org_data_patterns.get(target_org, [])

        for pattern in target_patterns:
            try:
                regex = re.compile(pattern)
                matched_data = []
                for s in response_strings:
                    if regex.search(str(s)):
                        matched_data.append(s)

                if matched_data:
                    violation = IsolationViolation(
                        violation_id=f"iso-{hashlib.md5(request_id.encode()).hexdigest()[:8]}",
                        source_org=source_org,
                        target_org=target_org,
                        request_id=request_id,
                        data_elements=matched_data[:5],
                        severity="CRITICAL",  # More critical for response leakage
                        timestamp=datetime.utcnow().isoformat(),
                        details=f"Target org data leaked in response: pattern '{pattern}'",
                    )
                    violations.append(violation)
            except Exception as e:
                self.logger.warning(f"Pattern validation failed: {e}")

        if violations:
            if target_org not in self.violations:
                self.violations[target_org] = []
            self.violations[target_org].extend(violations)

        return len(violations) == 0, violations

    def get_isolation_report(self, org_id: str = None) -> Dict[str, Any]:
        """
        Generate isolation compliance report.

        Args:
            org_id: If specified, report for single org; else all orgs

        Returns:
            Report dictionary with violation summaries
        """
        if org_id:
            violations = self.violations.get(org_id, [])
            return {
                "org_id": org_id,
                "total_violations": len(violations),
                "critical": len([v for v in violations if v.severity == "CRITICAL"]),
                "high": len([v for v in violations if v.severity == "HIGH"]),
                "violations": [
                    {
                        "violation_id": v.violation_id,
                        "request_id": v.request_id,
                        "severity": v.severity,
                        "timestamp": v.timestamp,
                        "details": v.details,
                    }
                    for v in violations[-10:]  # Last 10
                ],
            }
        else:
            total = sum(len(v) for v in self.violations.values())
            critical = sum(
                len([v for v in violations if v.severity == "CRITICAL"])
                for violations in self.violations.values()
            )

            return {
                "timestamp": datetime.utcnow().isoformat(),
                "total_orgs": len(self.violations),
                "total_violations": total,
                "critical_violations": critical,
                "orgs": list(self.violations.keys()),
            }

    @staticmethod
    def _extract_strings(obj: Any, max_depth: int = 5) -> List[str]:
        """
        Recursively extract all strings from object.

        Args:
            obj: Object to scan
            max_depth: Maximum recursion depth

        Returns:
            List of strings found
        """
        strings = []

        if max_depth <= 0:
            return strings

        if isinstance(obj, str):
            return [obj]
        elif isinstance(obj, dict):
            for key, value in obj.items():
                strings.append(key)
                strings.extend(DataIsolationValidator._extract_strings(value, max_depth - 1))
        elif isinstance(obj, (list, tuple)):
            for item in obj:
                strings.extend(DataIsolationValidator._extract_strings(item, max_depth - 1))

        return strings
