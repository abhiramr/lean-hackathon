"""Tests for verified_eda.stats — core statistical functions."""

import math
import pytest

from verified_eda.stats import (
    VerifiedResult,
    verified_mean,
    verified_variance,
    verified_std,
    verified_median,
    verified_min,
    verified_max,
)


class TestVerifiedResult:
    def test_repr(self):
        r = VerifiedResult(value=3.14, operation="mean", lean_theorem="mean_correct")
        assert "mean" in repr(r)

    def test_is_verified(self):
        r = VerifiedResult(value=1.0, operation="x", proof_status="proven")
        assert r.is_verified
        r2 = VerifiedResult(value=1.0, operation="x", proof_status="pending")
        assert not r2.is_verified


class TestMean:
    def test_basic(self):
        r = verified_mean([1.0, 2.0, 3.0, 4.0, 5.0])
        assert r.value == pytest.approx(3.0)
        assert r.operation == "mean"
        assert r.lean_theorem == "mean_correct"

    def test_single_element(self):
        r = verified_mean([42.0])
        assert r.value == pytest.approx(42.0)

    def test_negative_values(self):
        r = verified_mean([-10.0, 10.0])
        assert r.value == pytest.approx(0.0)

    def test_empty_raises(self):
        with pytest.raises(ValueError, match="empty"):
            verified_mean([])


class TestVariance:
    def test_basic(self):
        r = verified_variance([1.0, 2.0, 3.0, 4.0, 5.0])
        assert r.value == pytest.approx(2.0)
        assert r.operation == "variance"

    def test_constant_data(self):
        r = verified_variance([5.0, 5.0, 5.0, 5.0])
        assert r.value == pytest.approx(0.0)

    def test_nonnegative(self):
        """Variance must always be >= 0 (this is what the Lean proof guarantees)."""
        import random
        random.seed(42)
        for _ in range(100):
            data = [random.gauss(0, 10) for _ in range(50)]
            r = verified_variance(data)
            assert r.value >= 0, f"Variance was negative: {r.value}"

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            verified_variance([])


class TestStd:
    def test_basic(self):
        r = verified_std([1.0, 2.0, 3.0, 4.0, 5.0])
        assert r.value == pytest.approx(math.sqrt(2.0))

    def test_nonnegative(self):
        r = verified_std([1.0, 100.0, -50.0, 25.0])
        assert r.value >= 0


class TestMedian:
    def test_odd_count(self):
        r = verified_median([3.0, 1.0, 2.0])
        assert r.value == pytest.approx(2.0)

    def test_even_count(self):
        r = verified_median([1.0, 2.0, 3.0, 4.0])
        assert r.value == pytest.approx(2.5)

    def test_single(self):
        r = verified_median([99.0])
        assert r.value == pytest.approx(99.0)

    def test_in_range(self):
        """Median must be between min and max (Lean theorem: median_in_range)."""
        data = [10.0, 20.0, 30.0, 40.0, 50.0]
        r = verified_median(data)
        assert min(data) <= r.value <= max(data)

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            verified_median([])


class TestMinMax:
    def test_min(self):
        r = verified_min([5.0, 1.0, 3.0])
        assert r.value == pytest.approx(1.0)

    def test_max(self):
        r = verified_max([5.0, 1.0, 3.0])
        assert r.value == pytest.approx(5.0)
