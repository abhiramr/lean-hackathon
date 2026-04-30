"""Tests for the EDA pipeline and agentic verification."""

import pytest

from verified_eda.pipeline import VerifiedEDA, EDAReport
from verified_eda.agents.translator import TranslatorAgent
from verified_eda.agents.prover import ProverAgent, PROOF_TEMPLATES
from verified_eda.agents.certifier import CertifierAgent
from verified_eda.agents.orchestrator import Orchestrator
from verified_eda.stats import VerifiedResult, verified_mean


class TestPipeline:
    @pytest.fixture
    def sample_data(self):
        return [[1.0, 10.0], [2.0, 20.0], [3.0, 30.0], [4.0, 40.0], [5.0, 50.0]]

    def test_run(self, sample_data):
        eda = VerifiedEDA(sample_data, columns=["A", "B"], dataset_name="test")
        report = eda.run()
        assert report.n_rows == 5
        assert report.n_cols == 2
        assert "A" in report.results
        assert "B" in report.results
        assert report.total_count > 0

    def test_describe_column(self, sample_data):
        eda = VerifiedEDA(sample_data, columns=["A", "B"])
        eda.describe_column(0, "A")
        assert len(eda.report.results["A"]) == 6  # mean, var, std, median, min, max

    def test_correlations(self, sample_data):
        eda = VerifiedEDA(sample_data, columns=["A", "B"])
        eda.run()
        assert len(eda.report.correlation_results) > 0

    def test_histograms(self, sample_data):
        eda = VerifiedEDA(sample_data, columns=["A", "B"])
        eda.run(bins=3)
        assert len(eda.report.histogram_results) == 2

    def test_summary(self, sample_data):
        eda = VerifiedEDA(sample_data, columns=["A", "B"], dataset_name="Test")
        eda.run()
        s = eda.report.summary()
        assert "Test" in s
        assert "mean" in s


class TestTranslator:
    def test_template_translation(self):
        agent = TranslatorAgent()
        lean = agent.translate(verified_mean)
        assert "mean" in lean
        assert "listSum" in lean

    def test_translate_all(self):
        from verified_eda.stats import verified_mean, verified_variance
        agent = TranslatorAgent()
        code = agent.translate_all([verified_mean, verified_variance])
        assert "namespace VerifiedEDA" in code
        assert "end VerifiedEDA" in code


class TestProver:
    def test_known_theorem(self):
        agent = ProverAgent()
        result = agent.prove("variance_nonneg")
        assert result.status == "proven"
        assert result.proof != ""

    def test_all_templates(self):
        agent = ProverAgent()
        for name in PROOF_TEMPLATES:
            result = agent.prove(name)
            assert result.status == "proven", f"Failed to prove {name}"

    def test_unknown_theorem(self):
        agent = ProverAgent()
        result = agent.prove("nonexistent_theorem_xyz")
        assert result.status == "failed"

    def test_get_template(self):
        agent = ProverAgent()
        t = agent.get_template("sqDiff_nonneg")
        assert t is not None
        assert "mul_self_nonneg" in t


class TestCertifier:
    def test_certify(self):
        agent = CertifierAgent()
        result = VerifiedResult(value=3.0, operation="mean", lean_theorem="mean_correct")
        cert = agent.certify(
            data=[[1.0], [2.0], [3.0]],
            column="A",
            result=result,
            proof_info={"status": "proven", "proof": "rfl", "attempts": 1},
        )
        assert cert.proof_status == "proven"
        assert cert.certificate_id != ""
        assert len(agent.certificates) == 1

    def test_export(self):
        agent = CertifierAgent()
        result = VerifiedResult(value=3.0, operation="mean")
        agent.certify([[1.0]], "A", result, {"status": "proven", "proof": "rfl", "attempts": 1})
        json_str = agent.export_all()
        assert "verified_eda_certificates" in json_str


class TestOrchestrator:
    def test_full_verification(self):
        data = [[1.0, 10.0], [2.0, 20.0], [3.0, 30.0], [4.0, 40.0], [5.0, 50.0]]
        eda = VerifiedEDA(data, columns=["A", "B"], dataset_name="test")
        eda.run()

        orch = Orchestrator()
        orch.verify(eda)

        assert eda.report.proven_count > 0
        assert eda.report.verification_status in ("fully_verified", "partially_verified")
        assert len(orch.log) > 0
        assert len(orch.certifier.certificates) > 0
