"""
verified_eda/pipeline.py — Full EDA pipeline with automatic verification.

Usage:
    eda = VerifiedEDA(data, columns=["col1", "col2"], dataset_name="My Data")
    eda.run()
    print(eda.report)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from verified_eda.stats import (
    VerifiedResult,
    verified_max,
    verified_mean,
    verified_median,
    verified_min,
    verified_std,
    verified_variance,
)
from verified_eda.correlation import (
    correlation_matrix,
    verified_histogram,
    verified_pearson,
)


@dataclass
class EDAReport:
    """A complete EDA report with verification status for every operation."""

    dataset_name: str
    n_rows: int
    n_cols: int
    results: Dict[str, List[VerifiedResult]] = field(default_factory=dict)
    correlation_results: List[VerifiedResult] = field(default_factory=list)
    histogram_results: Dict[str, VerifiedResult] = field(default_factory=dict)
    verification_status: str = "unverified"

    def add_result(self, col: str, result: VerifiedResult) -> None:
        self.results.setdefault(col, []).append(result)

    @property
    def all_results(self) -> List[VerifiedResult]:
        """Flatten all results into a single list."""
        flat = []
        for col_results in self.results.values():
            flat.extend(col_results)
        flat.extend(self.correlation_results)
        flat.extend(self.histogram_results.values())
        return flat

    @property
    def proven_count(self) -> int:
        return sum(1 for r in self.all_results if r.proof_status == "proven")

    @property
    def pending_count(self) -> int:
        return sum(1 for r in self.all_results if r.proof_status == "pending")

    @property
    def failed_count(self) -> int:
        return sum(1 for r in self.all_results if r.proof_status == "failed")

    @property
    def total_count(self) -> int:
        return len(self.all_results)

    def summary(self) -> str:
        """Human-readable summary of the EDA report."""
        lines = [
            f"═══ Verified EDA Report: {self.dataset_name} ═══",
            f"Dataset: {self.n_rows} rows × {self.n_cols} columns",
            f"Verification: {self.proven_count}/{self.total_count} operations proven",
            f"Status: {self.verification_status}",
            "",
        ]

        for col, results in self.results.items():
            lines.append(f"── {col} ──")
            for r in results:
                icon = "✓" if r.is_verified else ("…" if r.proof_status == "pending" else "✗")
                lines.append(f"  {icon} {r.operation:>10s} = {r.value:.6f}  [{r.lean_theorem}]")
            lines.append("")

        if self.histogram_results:
            lines.append("── Histograms ──")
            for col, r in self.histogram_results.items():
                icon = "✓" if r.is_verified else "…"
                lines.append(f"  {icon} {col}: {int(r.value)} items binned  [{r.lean_theorem}]")
            lines.append("")

        if self.correlation_results:
            lines.append("── Correlations ──")
            for r in self.correlation_results:
                icon = "✓" if r.is_verified else "…"
                lines.append(f"  {icon} r = {r.value:+.6f}  [{r.lean_theorem}]")

        return "\n".join(lines)


class VerifiedEDA:
    """
    Main EDA pipeline that computes statistics and prepares for verification.

    Usage:
        eda = VerifiedEDA(data, columns=["A", "B", "C"])
        eda.run()
        print(eda.report.summary())

        # Then verify with the orchestrator:
        from verified_eda.agents.orchestrator import Orchestrator
        orch = Orchestrator()
        orch.verify(eda)
    """

    STAT_FUNCTIONS = [
        verified_mean,
        verified_variance,
        verified_std,
        verified_median,
        verified_min,
        verified_max,
    ]

    def __init__(
        self,
        data: List[List[float]],
        columns: Optional[List[str]] = None,
        dataset_name: str = "unnamed",
    ):
        self.data = data
        self.n_rows = len(data)
        self.n_cols = len(data[0]) if data else 0

        if columns is None:
            self.columns = [f"col_{i}" for i in range(self.n_cols)]
        else:
            assert len(columns) == self.n_cols, (
                f"Column count mismatch: got {len(columns)}, expected {self.n_cols}"
            )
            self.columns = columns

        self.report = EDAReport(
            dataset_name=dataset_name,
            n_rows=self.n_rows,
            n_cols=self.n_cols,
        )
        self.lean_specs: List[str] = []

    def get_column(self, col_idx: int) -> List[float]:
        """Extract a single column from the data matrix."""
        return [row[col_idx] for row in self.data]

    def describe_column(self, col_idx: int, col_name: Optional[str] = None) -> None:
        """Run all descriptive statistics on a single column."""
        name = col_name or self.columns[col_idx]
        col_data = self.get_column(col_idx)

        for fn in self.STAT_FUNCTIONS:
            result = fn(col_data)
            self.report.add_result(name, result)

    def compute_histograms(self, bins: int = 10) -> None:
        """Compute histograms for all columns."""
        for i, col_name in enumerate(self.columns):
            col_data = self.get_column(i)
            _counts, _edges, verification = verified_histogram(col_data, bins=bins)
            self.report.histogram_results[col_name] = verification

    def compute_correlations(self) -> None:
        """Compute full correlation matrix."""
        all_columns = [self.get_column(i) for i in range(self.n_cols)]
        _matrix, results = correlation_matrix(all_columns, self.columns)
        self.report.correlation_results = results

    def run(self, bins: int = 10) -> EDAReport:
        """Run the full EDA pipeline."""
        # Descriptive stats for each column
        for i, col_name in enumerate(self.columns):
            self.describe_column(i, col_name)

        # Histograms
        self.compute_histograms(bins=bins)

        # Correlations (only if multiple columns)
        if self.n_cols >= 2:
            self.compute_correlations()

        return self.report
