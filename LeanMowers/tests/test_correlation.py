"""Tests for verified_eda.correlation — correlation and histogram functions."""

import pytest

from verified_eda.correlation import (
    verified_pearson,
    verified_histogram,
    verified_covariance,
    correlation_matrix,
)


class TestPearson:
    def test_perfect_positive(self):
        r = verified_pearson([1.0, 2.0, 3.0], [2.0, 4.0, 6.0])
        assert r.value == pytest.approx(1.0, abs=1e-10)

    def test_perfect_negative(self):
        r = verified_pearson([1.0, 2.0, 3.0], [6.0, 4.0, 2.0])
        assert r.value == pytest.approx(-1.0, abs=1e-10)

    def test_no_correlation(self):
        r = verified_pearson([1.0, 2.0, 3.0, 4.0], [1.0, -1.0, 1.0, -1.0])
        assert abs(r.value) < 0.5

    def test_bounded(self):
        """Pearson correlation must be in [-1, 1] (Lean theorem: pearson_bounded)."""
        import random
        random.seed(123)
        for _ in range(50):
            x = [random.gauss(0, 10) for _ in range(30)]
            y = [random.gauss(0, 10) for _ in range(30)]
            r = verified_pearson(x, y)
            assert -1.0 <= r.value <= 1.0, f"Correlation out of bounds: {r.value}"

    def test_zero_variance(self):
        r = verified_pearson([5.0, 5.0, 5.0], [1.0, 2.0, 3.0])
        assert r.value == 0.0
        assert r.proof_status == "proven"

    def test_unequal_length_raises(self):
        with pytest.raises(ValueError, match="equal length"):
            verified_pearson([1.0, 2.0], [1.0])

    def test_too_few_points_raises(self):
        with pytest.raises(ValueError, match="at least 2"):
            verified_pearson([1.0], [2.0])


class TestHistogram:
    def test_basic(self):
        data = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
        counts, edges, vr = verified_histogram(data, bins=5)
        assert len(counts) == 5
        assert len(edges) == 6
        assert sum(counts) == len(data)
        assert vr.lean_theorem == "histogram_conserves"

    def test_conservation(self):
        """Sum of counts must equal data length (Lean theorem: histogram_conserves)."""
        import random
        random.seed(99)
        data = [random.gauss(50, 15) for _ in range(200)]
        for bins in [5, 10, 20, 50]:
            counts, _, vr = verified_histogram(data, bins=bins)
            assert sum(counts) == len(data), f"Conservation violated with {bins} bins"

    def test_single_value(self):
        counts, edges, vr = verified_histogram([5.0, 5.0, 5.0], bins=3)
        assert sum(counts) == 3

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            verified_histogram([], bins=5)

    def test_zero_bins_raises(self):
        with pytest.raises(ValueError):
            verified_histogram([1.0], bins=0)


class TestCovariance:
    def test_self_covariance(self):
        data = [1.0, 2.0, 3.0, 4.0, 5.0]
        r = verified_covariance(data, data)
        # cov(x, x) = var(x)
        from verified_eda.stats import verified_variance
        v = verified_variance(data)
        assert r.value == pytest.approx(v.value)


class TestCorrelationMatrix:
    def test_shape(self):
        cols = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]]
        matrix, results = correlation_matrix(cols, ["A", "B", "C"])
        assert len(matrix) == 3
        assert all(len(row) == 3 for row in matrix)

    def test_diagonal_is_one(self):
        cols = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]
        matrix, _ = correlation_matrix(cols, ["A", "B"])
        assert matrix[0][0] == pytest.approx(1.0)
        assert matrix[1][1] == pytest.approx(1.0)

    def test_symmetric(self):
        cols = [[1.0, 2.0, 3.0], [3.0, 1.0, 2.0]]
        matrix, _ = correlation_matrix(cols, ["A", "B"])
        assert matrix[0][1] == pytest.approx(matrix[1][0])
