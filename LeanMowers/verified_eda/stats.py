"""
verified_eda/stats.py — Core statistical functions with verification metadata.

Every function returns a VerifiedResult that carries:
  - The computed value
  - Which Lean 4 theorem certifies the operation
  - Current proof status (pending → proven/failed after verification)

Design principle: implementations are deliberately simple and map 1-to-1
to the Lean 4 definitions in lean/VerifiedEDA/Defs.lean so that the
correspondence is self-evident.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class VerifiedResult:
    """A computation result paired with its verification metadata."""

    value: float
    operation: str
    proof_status: str = "pending"  # 'pending' | 'proven' | 'failed'
    lean_theorem: str = ""
    certificate_id: Optional[str] = None
    details: dict = field(default_factory=dict)

    @property
    def is_verified(self) -> bool:
        return self.proof_status == "proven"

    def __repr__(self) -> str:
        icon = "✓" if self.is_verified else ("…" if self.proof_status == "pending" else "✗")
        return f"VerifiedResult({icon} {self.operation}={self.value:.6f}, theorem={self.lean_theorem})"


def verified_mean(data: List[float]) -> VerifiedResult:
    """
    Compute arithmetic mean with verification metadata.

    Mathematical specification:
        mean(xs) = sum(xs) / len(xs)

    Lean 4 theorem: mean_correct
        Proves that the implementation equals sum/count exactly.

    Precondition: data must be non-empty.
    """
    if len(data) == 0:
        raise ValueError("Cannot compute mean of empty list")

    total = sum(data)
    count = len(data)
    result = total / count

    return VerifiedResult(
        value=result,
        operation="mean",
        proof_status="pending",
        lean_theorem="mean_correct",
        details={"sum": total, "count": count},
    )


def verified_variance(data: List[float]) -> VerifiedResult:
    """
    Compute population variance with verification metadata.

    Mathematical specification:
        variance(xs) = sum((x - mean(xs))² for x in xs) / len(xs)

    Lean 4 theorems:
        - variance_nonneg: proves variance ≥ 0
        - variance_correct: proves implementation matches spec

    Precondition: data must be non-empty.
    """
    if len(data) == 0:
        raise ValueError("Cannot compute variance of empty list")

    m = verified_mean(data).value
    sq_diffs = [(x - m) ** 2 for x in data]
    result = sum(sq_diffs) / len(data)

    return VerifiedResult(
        value=result,
        operation="variance",
        proof_status="pending",
        lean_theorem="variance_nonneg",
        details={"mean": m, "sum_sq_diffs": sum(sq_diffs)},
    )


def verified_std(data: List[float]) -> VerifiedResult:
    """
    Compute population standard deviation.

    Mathematical specification:
        std(xs) = sqrt(variance(xs))

    Lean 4 theorem: std_nonneg
        Proves std ≥ 0 (follows from variance ≥ 0 and sqrt monotonicity).
    """
    var_result = verified_variance(data)
    result = math.sqrt(var_result.value)

    return VerifiedResult(
        value=result,
        operation="std",
        proof_status="pending",
        lean_theorem="std_nonneg",
        details={"variance": var_result.value},
    )


def verified_median(data: List[float]) -> VerifiedResult:
    """
    Compute median with verification metadata.

    Mathematical specification:
        For sorted list s of length n:
        - If n is odd:  median = s[n // 2]
        - If n is even: median = (s[n//2 - 1] + s[n//2]) / 2

    Lean 4 theorem: median_in_range
        Proves min(xs) ≤ median(xs) ≤ max(xs).
    """
    if len(data) == 0:
        raise ValueError("Cannot compute median of empty list")

    sorted_data = sorted(data)
    n = len(sorted_data)

    if n % 2 == 1:
        result = sorted_data[n // 2]
    else:
        result = (sorted_data[n // 2 - 1] + sorted_data[n // 2]) / 2

    return VerifiedResult(
        value=result,
        operation="median",
        proof_status="pending",
        lean_theorem="median_in_range",
        details={"sorted_min": sorted_data[0], "sorted_max": sorted_data[-1]},
    )


def verified_min(data: List[float]) -> VerifiedResult:
    """Minimum value. Lean theorem: min_in_list."""
    if not data:
        raise ValueError("Cannot compute min of empty list")
    return VerifiedResult(
        value=min(data),
        operation="min",
        proof_status="pending",
        lean_theorem="min_in_list",
    )


def verified_max(data: List[float]) -> VerifiedResult:
    """Maximum value. Lean theorem: max_in_list."""
    if not data:
        raise ValueError("Cannot compute max of empty list")
    return VerifiedResult(
        value=max(data),
        operation="max",
        proof_status="pending",
        lean_theorem="max_in_list",
    )
