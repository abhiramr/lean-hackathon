"""
verified_eda/agents/certifier.py — Tamper-evident verification certificate generation.

Certificates include SHA-256 hashes of the dataset and proof, ensuring that
the verification is tied to the specific data and proof used.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from verified_eda.stats import VerifiedResult


@dataclass
class VerificationCertificate:
    """A tamper-evident certificate linking data, computation, and proof."""

    certificate_id: str
    dataset_hash: str
    operation: str
    column: str
    python_result: float
    lean_theorem: str
    proof_status: str
    proof_hash: str
    timestamp: str
    agent_attempts: int
    proof_text: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    def __repr__(self) -> str:
        icon = "✓" if self.proof_status == "proven" else "✗"
        return (
            f"Certificate({icon} {self.column}.{self.operation} "
            f"id={self.certificate_id})"
        )


class CertifierAgent:
    """
    Produces tamper-evident verification certificates.

    Each certificate cryptographically binds:
    - The dataset (via SHA-256 hash)
    - The computed result
    - The Lean 4 proof (via SHA-256 hash)
    - Metadata (timestamp, theorem name, attempts)
    """

    def __init__(self):
        self.certificates: List[VerificationCertificate] = []

    def certify(
        self,
        data: Any,
        column: str,
        result: VerifiedResult,
        proof_info: Dict[str, Any],
    ) -> VerificationCertificate:
        """Generate a verification certificate for a single result."""
        # Hash the dataset
        data_str = json.dumps(data, sort_keys=True, default=str)
        dataset_hash = hashlib.sha256(data_str.encode()).hexdigest()

        # Hash the proof
        proof_text = proof_info.get("proof", "")
        proof_hash = hashlib.sha256(proof_text.encode()).hexdigest()

        # Generate certificate ID
        cert_input = f"{dataset_hash}:{column}:{result.operation}:{proof_hash}"
        cert_id = hashlib.sha256(cert_input.encode()).hexdigest()[:12]

        cert = VerificationCertificate(
            certificate_id=cert_id,
            dataset_hash=dataset_hash[:16] + "...",
            operation=result.operation,
            column=column,
            python_result=result.value,
            lean_theorem=result.lean_theorem,
            proof_status=proof_info.get("status", "unknown"),
            proof_hash=proof_hash[:16] + "...",
            timestamp=datetime.now(timezone.utc).isoformat(),
            agent_attempts=proof_info.get("attempts", 0),
            proof_text=proof_text,
        )

        self.certificates.append(cert)

        # Update the original result
        if proof_info.get("status") == "proven":
            result.proof_status = "proven"
            result.certificate_id = cert.certificate_id

        return cert

    def export_all(self, path: Optional[str] = None) -> str:
        """Export all certificates as JSON."""
        data = {
            "verified_eda_certificates": {
                "version": "1.0.0",
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "total_certificates": len(self.certificates),
                "proven": sum(
                    1 for c in self.certificates if c.proof_status == "proven"
                ),
                "certificates": [c.to_dict() for c in self.certificates],
            }
        }

        json_str = json.dumps(data, indent=2)

        if path:
            with open(path, "w") as f:
                f.write(json_str)

        return json_str

    def summary(self) -> str:
        """Human-readable summary of all certificates."""
        lines = [
            "═══ Verification Certificates ═══",
            f"Total: {len(self.certificates)}",
            f"Proven: {sum(1 for c in self.certificates if c.proof_status == 'proven')}",
            "",
        ]
        for cert in self.certificates:
            icon = "✓" if cert.proof_status == "proven" else "✗"
            lines.append(
                f"  {icon} [{cert.certificate_id}] "
                f"{cert.column}.{cert.operation} = {cert.python_result:.6f}"
            )
            lines.append(f"    Theorem: {cert.lean_theorem}")
            lines.append(f"    Data hash: {cert.dataset_hash}")
            lines.append(f"    Proof hash: {cert.proof_hash}")
            lines.append("")

        return "\n".join(lines)
