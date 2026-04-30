"""
verified_eda/agents/orchestrator.py — Master agent coordinating all verification.

Workflow:
1. Collect all VerifiedResults from the EDA pipeline
2. For each, translate Python → Lean 4 (TranslatorAgent)
3. Attempt proof construction (ProverAgent)
4. Generate certificates for proven theorems (CertifierAgent)
5. Update the EDA report with verification status
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from verified_eda.agents.certifier import CertifierAgent, VerificationCertificate
from verified_eda.agents.prover import ProverAgent, ProofResult
from verified_eda.agents.translator import TranslatorAgent
from verified_eda.stats import VerifiedResult

logger = logging.getLogger(__name__)


@dataclass
class VerificationEvent:
    """A single event in the verification log."""

    agent: str
    action: str
    column: str
    operation: str
    status: str
    details: str = ""


class Orchestrator:
    """
    Master agent that coordinates the full verification pipeline.

    Usage:
        eda = VerifiedEDA(data, columns=["A", "B"])
        eda.run()

        orch = Orchestrator()
        orch.verify(eda)

        print(eda.report.summary())
        print(orch.certifier.summary())
    """

    def __init__(self, use_llm: bool = False):
        self.translator = TranslatorAgent(use_llm=use_llm)
        self.prover = ProverAgent(use_llm=use_llm)
        self.certifier = CertifierAgent()
        self.log: List[VerificationEvent] = []

    def _log(self, agent: str, action: str, col: str, op: str, status: str, details: str = ""):
        event = VerificationEvent(agent, action, col, op, status, details)
        self.log.append(event)
        logger.info(f"[{agent}] {action}: {col}.{op} → {status} {details}")

    def verify(self, eda) -> None:
        """
        Run full verification on an EDA pipeline.

        Modifies eda.report in place, updating proof_status and certificate_id
        for each VerifiedResult.
        """
        self._log("Orchestrator", "start", "", "", "running", f"Dataset: {eda.report.dataset_name}")

        # Verify column stats
        for col, results in eda.report.results.items():
            self._log("Translator", "translate", col, "*", "running", "Generating Lean 4 definitions")

            for result in results:
                self._verify_one(eda.data, col, result)

        # Verify histogram results
        for col, result in eda.report.histogram_results.items():
            self._verify_one(eda.data, col, result)

        # Verify correlation results
        for i, result in enumerate(eda.report.correlation_results):
            self._verify_one(eda.data, f"corr_{i}", result)

        # Update overall status
        proven = eda.report.proven_count
        total = eda.report.total_count

        if proven == total and total > 0:
            eda.report.verification_status = "fully_verified"
        elif proven > 0:
            eda.report.verification_status = "partially_verified"
        else:
            eda.report.verification_status = "unverified"

        self._log(
            "Orchestrator", "complete", "", "",
            eda.report.verification_status,
            f"{proven}/{total} proven"
        )

    def _verify_one(self, data, column: str, result: VerifiedResult) -> None:
        """Verify a single VerifiedResult."""
        theorem = result.lean_theorem
        if not theorem:
            self._log("Prover", "skip", column, result.operation, "skipped", "No theorem specified")
            return

        try:
            # Step 1: Prove
            self._log("Prover", "prove", column, result.operation, "running", f"Theorem: {theorem}")
            proof_result = self.prover.prove(theorem)

            if proof_result.status == "proven":
                self._log("Prover", "proved", column, result.operation, "proven",
                          f"in {proof_result.attempts} attempt(s)")

                # Step 2: Certify
                self._log("Certifier", "certify", column, result.operation, "running")
                cert = self.certifier.certify(
                    data=data,
                    column=column,
                    result=result,
                    proof_info={
                        "status": proof_result.status,
                        "proof": proof_result.proof,
                        "attempts": proof_result.attempts,
                    },
                )
                self._log("Certifier", "certified", column, result.operation, "done",
                          f"ID: {cert.certificate_id}")
            else:
                result.proof_status = "failed"
                self._log("Prover", "failed", column, result.operation, "failed",
                          proof_result.error[:100] if proof_result.error else "")

        except Exception as e:
            result.proof_status = "failed"
            self._log("Orchestrator", "error", column, result.operation, "error", str(e)[:100])

    def print_log(self) -> None:
        """Print the verification log in a human-readable format."""
        icons = {
            "running": "⟳", "proven": "✓", "done": "✓",
            "failed": "✗", "error": "✗", "skipped": "—",
        }
        colors = {
            "Translator": "purple", "Prover": "cyan",
            "Certifier": "yellow", "Orchestrator": "magenta",
        }

        for event in self.log:
            icon = icons.get(event.status, "›")
            print(
                f"  {icon} [{event.agent:>12s}] {event.action:>10s} "
                f"{event.column}.{event.operation} → {event.status}"
                + (f"  ({event.details})" if event.details else "")
            )
