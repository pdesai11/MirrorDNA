"""
Tests for truth_state.py module.
"""

import pytest
from mirrordna import (
    TruthTag,
    TruthAssertion,
    TruthStateEnforcer,
    compute_source_checksum,
    tag_statement
)


class TestTruthAssertion:
    """Tests for TruthAssertion dataclass."""

    def test_fact_assertion_requires_source(self):
        """FACT assertions must include source."""
        with pytest.raises(ValueError, match="FACT assertions must include source"):
            TruthAssertion(statement="Test", tag=TruthTag.FACT)

    def test_estimate_assertion_requires_confidence(self):
        """ESTIMATE assertions must include confidence."""
        with pytest.raises(ValueError, match="ESTIMATE assertions must include confidence"):
            TruthAssertion(statement="Test", tag=TruthTag.ESTIMATE, source="test")

    def test_estimate_confidence_range(self):
        """Confidence must be between 0.0 and 1.0."""
        with pytest.raises(ValueError, match="Confidence must be between"):
            TruthAssertion(
                statement="Test",
                tag=TruthTag.ESTIMATE,
                confidence=1.5
            )

    def test_valid_fact_assertion(self):
        """Valid FACT assertion creation."""
        assertion = TruthAssertion(
            statement="User prefers Python",
            tag=TruthTag.FACT,
            source="vault://memory_001"
        )
        assert assertion.statement == "User prefers Python"
        assert assertion.tag == TruthTag.FACT
        assert assertion.source == "vault://memory_001"

    def test_to_dict(self):
        """Serialization to dictionary."""
        assertion = TruthAssertion(
            statement="Test",
            tag=TruthTag.FACT,
            source="test_source"
        )
        d = assertion.to_dict()
        assert d["statement"] == "Test"
        assert d["tag"] == "FACT"
        assert d["source"] == "test_source"


class TestTruthStateEnforcer:
    """Tests for TruthStateEnforcer class."""

    def test_assert_fact(self):
        """Assert a fact with source."""
        enforcer = TruthStateEnforcer()
        assertion = enforcer.assert_fact(
            statement="User is named Alice",
            source="vault://identity",
            checksum="abc123"
        )
        assert assertion.tag == TruthTag.FACT
        assert len(enforcer.assertions) == 1

    def test_assert_estimate(self):
        """Assert an estimate with confidence."""
        enforcer = TruthStateEnforcer()
        assertion = enforcer.assert_estimate(
            statement="User likely works in tech",
            confidence=0.75
        )
        assert assertion.tag == TruthTag.ESTIMATE
        assert assertion.confidence == 0.75

    def test_assert_unknown(self):
        """Assert a knowledge gap."""
        enforcer = TruthStateEnforcer()
        assertion = enforcer.assert_unknown(
            statement="User's favorite color",
            reason="Not yet discussed"
        )
        assert assertion.tag == TruthTag.UNKNOWN
        assert assertion.source == "Not yet discussed"

    def test_detect_drift_with_mismatch(self):
        """Drift detected when checksums mismatch."""
        enforcer = TruthStateEnforcer()
        drift = enforcer.detect_drift(
            expected_checksum="abc123",
            actual_checksum="def456",
            source="vault://state"
        )
        assert drift is True
        assert len(enforcer.drift_log) == 1
        assert len(enforcer.get_assertions_by_tag(TruthTag.DRIFT)) == 1

    def test_detect_drift_no_mismatch(self):
        """No drift when checksums match."""
        enforcer = TruthStateEnforcer()
        drift = enforcer.detect_drift(
            expected_checksum="abc123",
            actual_checksum="abc123",
            source="vault://state"
        )
        assert drift is False
        assert len(enforcer.drift_log) == 0

    def test_get_assertions_by_tag(self):
        """Filter assertions by tag."""
        enforcer = TruthStateEnforcer()
        enforcer.assert_fact("Fact 1", source="s1")
        enforcer.assert_fact("Fact 2", source="s2")
        enforcer.assert_estimate("Est 1", confidence=0.5)

        facts = enforcer.get_assertions_by_tag(TruthTag.FACT)
        assert len(facts) == 2

        estimates = enforcer.get_assertions_by_tag(TruthTag.ESTIMATE)
        assert len(estimates) == 1

    def test_get_summary(self):
        """Get summary statistics."""
        enforcer = TruthStateEnforcer()
        enforcer.assert_fact("F1", source="s1")
        enforcer.assert_estimate("E1", confidence=0.7)
        enforcer.assert_unknown("U1")

        summary = enforcer.get_summary()
        assert summary["total_assertions"] == 3
        assert summary["by_tag"]["FACT"] == 1
        assert summary["by_tag"]["ESTIMATE"] == 1
        assert summary["by_tag"]["UNKNOWN"] == 1


class TestHelperFunctions:
    """Tests for helper functions."""

    def test_compute_source_checksum(self):
        """Compute SHA-256 checksum."""
        checksum = compute_source_checksum("test content")
        assert len(checksum) == 64
        assert isinstance(checksum, str)

        # Deterministic
        checksum2 = compute_source_checksum("test content")
        assert checksum == checksum2

    def test_tag_statement(self):
        """Create tagged statement."""
        assertion = tag_statement(
            statement="Test",
            tag=TruthTag.FACT,
            source="test_source"
        )
        assert assertion.statement == "Test"
        assert assertion.tag == TruthTag.FACT
