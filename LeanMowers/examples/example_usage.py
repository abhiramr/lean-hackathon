#!/usr/bin/env python3
"""
example_usage.py — End-to-end demonstration of Verified EDA.

This script:
1. Creates a sample dataset
2. Runs the full EDA pipeline
3. Runs agentic verification (translator → prover → certifier)
4. Prints the verified report and certificates
"""

import random
import sys
import logging

# Uncomment for verbose agent logs:
# logging.basicConfig(level=logging.INFO)

from verified_eda.pipeline import VerifiedEDA
from verified_eda.agents.orchestrator import Orchestrator


def generate_sample_data(n: int = 100, seed: int = 42):
    """Generate a synthetic sales dataset."""
    random.seed(seed)
    data = []
    for _ in range(n):
        revenue = 30000 + random.gauss(25000, 12000)
        units = max(10, int(50 + random.gauss(100, 40)))
        margin = max(0.05, 0.15 + random.gauss(0.15, 0.08))
        growth = random.gauss(0.05, 0.15)
        data.append([revenue, float(units), margin, growth])
    return data


def main():
    print("╔══════════════════════════════════════════════════════════╗")
    print("║          VERIFIED EDA — Demonstration                   ║")
    print("║          Python × Lean 4 × Agentic AI                  ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()

    # ── Step 1: Generate data ──
    print("Step 1: Generating sample dataset...")
    data = generate_sample_data(n=100)
    columns = ["Revenue", "Units", "Margin", "Growth"]
    print(f"  → {len(data)} rows × {len(columns)} columns\n")

    # ── Step 2: Run EDA ──
    print("Step 2: Running EDA pipeline...")
    eda = VerifiedEDA(data, columns=columns, dataset_name="Q1 Sales 2026")
    report = eda.run(bins=10)
    print(f"  → {report.total_count} operations computed\n")

    # ── Step 3: Print unverified report ──
    print("Step 3: EDA Results (pre-verification):")
    print("─" * 55)
    print(report.summary())
    print()

    # ── Step 4: Run agentic verification ──
    print("Step 4: Running agentic verification pipeline...")
    print("  [Translator] Python AST → Lean 4 definitions")
    print("  [Prover]     Constructing tactic proofs")
    print("  [Certifier]  Generating SHA-256 certificates")
    print()

    orchestrator = Orchestrator()
    orchestrator.verify(eda)

    # ── Step 5: Print verification log ──
    print("Step 5: Verification Log:")
    print("─" * 55)
    orchestrator.print_log()
    print()

    # ── Step 6: Print verified report ──
    print("Step 6: Verified EDA Report:")
    print("─" * 55)
    print(report.summary())
    print()

    # ── Step 7: Print certificates ──
    print("Step 7: Verification Certificates:")
    print("─" * 55)
    print(orchestrator.certifier.summary())

    # ── Step 8: Export certificates ──
    cert_path = "verification_certificates.json"
    orchestrator.certifier.export_all(path=cert_path)
    print(f"\n  → Certificates exported to {cert_path}")

    # ── Summary ──
    print()
    print("═" * 55)
    proven = report.proven_count
    total = report.total_count
    print(f"  FINAL: {proven}/{total} operations formally verified")
    print(f"  STATUS: {report.verification_status}")
    print("═" * 55)

    return 0 if report.verification_status in ("fully_verified", "partially_verified") else 1


if __name__ == "__main__":
    sys.exit(main())
