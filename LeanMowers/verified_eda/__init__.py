"""
Verified EDA — Formally Verified Exploratory Data Analysis
Python × Lean 4 × Agentic AI

Every statistical computation is mirrored in Lean 4 with machine-checked proofs
guaranteeing correctness, non-negativity, boundedness, and conservation properties.
"""

__version__ = "1.0.0"

from verified_eda.stats import (
    VerifiedResult,
    verified_mean,
    verified_variance,
    verified_std,
    verified_median,
)
from verified_eda.correlation import verified_pearson, verified_histogram
from verified_eda.pipeline import VerifiedEDA, EDAReport

__all__ = [
    "VerifiedResult",
    "verified_mean",
    "verified_variance",
    "verified_std",
    "verified_median",
    "verified_pearson",
    "verified_histogram",
    "VerifiedEDA",
    "EDAReport",
]
