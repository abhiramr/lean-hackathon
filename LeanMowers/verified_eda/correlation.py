"""
verified_eda/correlation.py — Correlation analysis and histogram with verification.

Each function returns VerifiedResult (or annotated data) with Lean 4 proof references.
"""

from __future__ import annotations

from typing import List, Tuple

from verified_eda.stats import VerifiedResult, verified_mean, verified_std


def verified_pearson(x: List[float], y: List[float]) -> VerifiedResult:
    """
    Pearson correlation coefficient.

    Mathematical specification:
        r = cov(x, y) / (std(x) * std(y))
        where cov(x,y) = sum((xi - mx)(yi - my)) / n

    Lean 4 theorem: pearson_bounded
        Proves -1 ≤ r ≤ 1 via the Cauchy-Schwarz inequality.

    Preconditions:
        - x and y must have equal length
        - At least 2 data points
    """
    if len(x) != len(y):
        raise ValueError(f"Inputs must have equal length, got {len(x)} and {len(y)}")
    if len(x) < 2:
        raise ValueError("Need at least 2 data points for correlation")

    n = len(x)
    mx = sum(x) / n
    my = sum(y) / n

    cov = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y)) / n
    sx = verified_std(x).value
    sy = verified_std(y).value

    # Handle zero-variance case
    if sx == 0 or sy == 0:
        return VerifiedResult(
            value=0.0,
            operation="pearson",
            proof_status="proven",  # trivially true when variance is zero
            lean_theorem="pearson_zero_var",
            details={"reason": "zero variance in one or both inputs"},
        )

    r = cov / (sx * sy)
    # Clamp to [-1, 1] for floating-point safety
    r = max(-1.0, min(1.0, r))

    return VerifiedResult(
        value=r,
        operation="pearson",
        proof_status="pending",
        lean_theorem="pearson_bounded",
        details={"covariance": cov, "std_x": sx, "std_y": sy},
    )


def verified_histogram(
    data: List[float], bins: int = 10
) -> Tuple[List[int], List[float], VerifiedResult]:
    """
    Compute histogram with verified bin counts.

    Lean 4 theorem: histogram_conserves
        Proves sum(counts) == len(data) — no data points are lost during binning.

    Returns:
        (counts, edges, verification_result)
    """
    if len(data) == 0:
        raise ValueError("Cannot compute histogram of empty list")
    if bins < 1:
        raise ValueError("Number of bins must be positive")

    lo = min(data)
    hi = max(data)
    width = (hi - lo) / bins if hi > lo else 1.0
    edges = [lo + i * width for i in range(bins + 1)]

    counts = [0] * bins
    for val in data:
        if hi > lo:
            idx = min(int((val - lo) / width), bins - 1)
        else:
            idx = 0  # all values are equal
        counts[idx] += 1

    # Runtime assertion: conservation property
    total = sum(counts)
    assert total == len(data), (
        f"Histogram conservation violated: sum(counts)={total} != len(data)={len(data)}"
    )

    verification = VerifiedResult(
        value=float(total),
        operation="histogram",
        proof_status="pending",
        lean_theorem="histogram_conserves",
        details={"bins": bins, "total_count": total, "data_length": len(data)},
    )

    return counts, edges, verification


def verified_covariance(x: List[float], y: List[float]) -> VerifiedResult:
    """
    Population covariance.

    Spec: cov(x,y) = sum((xi - mx)(yi - my)) / n
    """
    if len(x) != len(y):
        raise ValueError("Inputs must have equal length")
    if len(x) == 0:
        raise ValueError("Cannot compute covariance of empty lists")

    n = len(x)
    mx = sum(x) / n
    my = sum(y) / n
    cov = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y)) / n

    return VerifiedResult(
        value=cov,
        operation="covariance",
        proof_status="pending",
        lean_theorem="covariance_symmetric",
        details={"mean_x": mx, "mean_y": my},
    )


def correlation_matrix(
    columns: List[List[float]], col_names: List[str]
) -> Tuple[List[List[float]], List[VerifiedResult]]:
    """
    Compute full correlation matrix with verification for each cell.

    Returns:
        (matrix, list_of_verified_results)
    """
    n = len(columns)
    matrix = [[0.0] * n for _ in range(n)]
    results = []

    for i in range(n):
        for j in range(n):
            if i == j:
                matrix[i][j] = 1.0
            elif j > i:
                vr = verified_pearson(columns[i], columns[j])
                matrix[i][j] = vr.value
                matrix[j][i] = vr.value
                results.append(vr)

    return matrix, results
