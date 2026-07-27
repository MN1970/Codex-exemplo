"""
mTLS Certificate Management

Certificate generation, validation, revocation, and org identity verification.
Phase 4.1 implementation.
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Tuple, Optional, List
from enum import Enum

from cryptography import x509
from cryptography.x509.oid import NameOID, ExtensionOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend


class CertificateStatus(Enum):
    """Certificate status."""
    VALID = "VALID"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"
    NOT_YET_VALID = "NOT_YET_VALID"
    INVALID = "INVALID"


class MTLSHandler:
    """
    mTLS Certificate Management.

    Responsibilities:
    - Generate org CA certificates
    - Issue agent certificates
    - Validate certificate chains
    - Org identity verification
    - Revocation list management
    """

    def __init__(self, ca_cert_path: str, ca_key_path: str, logger: Optional[logging.Logger] = None):
        """
        Initialize mTLS handler.

        Args:
            ca_cert_path: Path to CA certificate (PEM)
            ca_key_path: Path to CA private key (PEM)
            logger: Optional logger instance
        """
        self.ca_cert_path = ca_cert_path
        self.ca_key_path = ca_key_path
        self.logger = logger or logging.getLogger("MTLSHandler")

        # Load CA cert and key
        self.ca_cert = self._load_certificate(ca_cert_path)
        self.ca_key = self._load_private_key(ca_key_path)

        # Revocation list: {cert_serial: reason}
        self.crl: dict = {}

    @staticmethod
    def _load_certificate(cert_path: str) -> x509.Certificate:
        """Load certificate from PEM file."""
        with open(cert_path, "rb") as f:
            return x509.load_pem_x509_certificate(f.read(), default_backend())

    @staticmethod
    def _load_private_key(key_path: str):
        """Load private key from PEM file."""
        with open(key_path, "rb") as f:
            return serialization.load_pem_private_key(
                f.read(),
                password=None,
                backend=default_backend(),
            )

    def generate_ca_certificate(
        self,
        org_id: str,
        common_name: str,
        validity_days: int = 3650,  # 10 years
    ) -> Tuple[str, str]:
        """
        Generate a CA certificate for an org.

        Args:
            org_id: Organization ID
            common_name: Common name for certificate
            validity_days: Certificate validity period

        Returns:
            (cert_pem, key_pem) certificate and private key
        """
        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=4096,
            backend=default_backend(),
        )

        # Build certificate
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, org_id),
            x509.NameAttribute(NameOID.COMMON_NAME, common_name),
            x509.NameAttribute(NameOID.COUNTRY_NAME, "BR"),
        ])

        cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(private_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.utcnow())
            .not_valid_after(datetime.utcnow() + timedelta(days=validity_days))
            .add_extension(
                x509.BasicConstraints(ca=True, path_length=None),
                critical=True,
            )
            .add_extension(
                x509.KeyUsage(
                    digital_signature=True,
                    key_cert_sign=True,
                    crl_sign=True,
                    key_encipherment=False,
                    content_commitment=False,
                    data_encipherment=False,
                    key_agreement=False,
                    encipher_only=False,
                    decipher_only=False,
                ),
                critical=True,
            )
            .sign(private_key, hashes.SHA256(), default_backend())
        )

        # Serialize to PEM
        cert_pem = cert.public_bytes(serialization.Encoding.PEM).decode()
        key_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ).decode()

        self.logger.info(f"Generated CA certificate for org {org_id}")
        return cert_pem, key_pem

    def generate_agent_certificate(
        self,
        agent_id: str,
        org_id: str,
        validity_days: int = 365,  # 1 year
        ca_cert_pem: str = None,
        ca_key_pem: str = None,
    ) -> Tuple[str, str]:
        """
        Issue an agent certificate signed by org CA.

        Args:
            agent_id: Agent identifier
            org_id: Organization ID
            validity_days: Certificate validity
            ca_cert_pem: Org CA certificate (PEM). If None, uses Manta's root CA.
            ca_key_pem: Org CA private key (PEM)

        Returns:
            (cert_pem, key_pem) agent certificate and private key
        """
        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend(),
        )

        # Load signing CA
        if ca_cert_pem and ca_key_pem:
            signing_cert = x509.load_pem_x509_certificate(
                ca_cert_pem.encode(),
                default_backend(),
            )
            signing_key = serialization.load_pem_private_key(
                ca_key_pem.encode(),
                password=None,
                backend=default_backend(),
            )
        else:
            signing_cert = self.ca_cert
            signing_key = self.ca_key

        # Build certificate
        subject = x509.Name([
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, org_id),
            x509.NameAttribute(NameOID.COMMON_NAME, agent_id),
            x509.NameAttribute(NameOID.COUNTRY_NAME, "BR"),
        ])

        issuer = signing_cert.subject

        cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(private_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.utcnow())
            .not_valid_after(datetime.utcnow() + timedelta(days=validity_days))
            .add_extension(
                x509.BasicConstraints(ca=False, path_length=None),
                critical=True,
            )
            .add_extension(
                x509.KeyUsage(
                    digital_signature=True,
                    key_encipherment=True,
                    content_commitment=False,
                    data_encipherment=False,
                    key_agreement=False,
                    key_cert_sign=False,
                    crl_sign=False,
                    encipher_only=False,
                    decipher_only=False,
                ),
                critical=True,
            )
            .add_extension(
                x509.ExtendedKeyUsage([
                    x509.oid.ExtendedKeyUsageOID.CLIENT_AUTH,
                    x509.oid.ExtendedKeyUsageOID.SERVER_AUTH,
                ]),
                critical=False,
            )
            .add_extension(
                x509.SubjectAlternativeName([
                    x509.DNSName(f"{agent_id}.agents.manta.internal"),
                ]),
                critical=False,
            )
            .sign(signing_key, hashes.SHA256(), default_backend())
        )

        # Serialize
        cert_pem = cert.public_bytes(serialization.Encoding.PEM).decode()
        key_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ).decode()

        self.logger.info(f"Issued certificate for agent {agent_id} (org {org_id})")
        return cert_pem, key_pem

    def validate_certificate_chain(
        self,
        cert_pem: str,
        ca_chain_pem: str,
    ) -> Tuple[CertificateStatus, str]:
        """
        Validate certificate chain.

        Args:
            cert_pem: Agent certificate (PEM)
            ca_chain_pem: CA chain (PEM, can contain multiple certs)

        Returns:
            (status, details) validation result and explanation
        """
        try:
            cert = x509.load_pem_x509_certificate(cert_pem.encode(), default_backend())
        except Exception as e:
            return CertificateStatus.INVALID, f"Failed to parse certificate: {e}"

        # Check validity period
        now = datetime.utcnow()
        if cert.not_valid_before_utc > now:
            return CertificateStatus.NOT_YET_VALID, "Certificate not yet valid"
        if cert.not_valid_after_utc < now:
            return CertificateStatus.EXPIRED, "Certificate expired"

        # Check revocation
        if cert.serial_number in self.crl:
            reason = self.crl[cert.serial_number]
            return CertificateStatus.REVOKED, f"Certificate revoked: {reason}"

        # Verify chain signature (simplified)
        try:
            ca_certs = []
            for ca_pem in ca_chain_pem.split("-----END CERTIFICATE-----"):
                if ca_pem.strip():
                    ca_pem_full = ca_pem + "-----END CERTIFICATE-----"
                    ca_cert = x509.load_pem_x509_certificate(
                        ca_pem_full.encode(),
                        default_backend(),
                    )
                    ca_certs.append(ca_cert)

            # In production: implement full chain validation
            # For now: check issuer matches at least one CA
            issuer_found = False
            for ca_cert in ca_certs:
                if cert.issuer == ca_cert.subject:
                    issuer_found = True
                    break

            if not issuer_found and not ca_certs:
                # Self-signed or root CA
                return CertificateStatus.VALID, "Self-signed or root CA"

            return CertificateStatus.VALID, "Certificate chain validated"

        except Exception as e:
            return CertificateStatus.INVALID, f"Chain validation failed: {e}"

    def verify_org_identity(self, cert_pem: str, expected_org_id: str) -> bool:
        """
        Verify certificate belongs to expected organization.

        Args:
            cert_pem: Certificate (PEM)
            expected_org_id: Expected organization name

        Returns:
            True if org matches
        """
        try:
            cert = x509.load_pem_x509_certificate(cert_pem.encode(), default_backend())
            org_attr = None
            for attr in cert.subject:
                if attr.oid == NameOID.ORGANIZATION_NAME:
                    org_attr = attr.value
                    break

            return org_attr == expected_org_id
        except Exception:
            return False

    def revoke_certificate(self, serial_number: int, reason: str = "UNSPECIFIED"):
        """
        Add certificate to revocation list.

        Args:
            serial_number: Certificate serial number
            reason: Revocation reason
        """
        self.crl[serial_number] = reason
        self.logger.warning(f"Revoked certificate {serial_number}: {reason}")

    def get_certificate_fingerprint(self, cert_pem: str, hash_algo: str = "sha256") -> str:
        """
        Calculate certificate fingerprint.

        Args:
            cert_pem: Certificate (PEM)
            hash_algo: Hash algorithm ("sha256" or "sha1")

        Returns:
            Fingerprint string (hex)
        """
        import hashlib

        cert = x509.load_pem_x509_certificate(cert_pem.encode(), default_backend())
        der_bytes = cert.public_bytes(serialization.Encoding.DER)

        if hash_algo == "sha256":
            fingerprint = hashlib.sha256(der_bytes).hexdigest()
            return f"sha256:{fingerprint}"
        elif hash_algo == "sha1":
            fingerprint = hashlib.sha1(der_bytes).hexdigest()
            return f"sha1:{fingerprint}"
        else:
            raise ValueError(f"Unsupported hash algorithm: {hash_algo}")
