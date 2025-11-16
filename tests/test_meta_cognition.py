"""
Tests for meta_cognition.py module.
"""

import pytest
from mirrordna import (
    WisdomGateType,
    GateStatus,
    WisdomGateResult,
    CrossDomainInsight,
    EthicalAssessment,
    MetaCognitionEngine
)


class TestWisdomGateResult:
    """Tests for WisdomGateResult dataclass."""

    def test_create_gate_result(self):
        """Create basic gate result."""
        result = WisdomGateResult(
            gate_type=WisdomGateType.ETHICAL,
            status=GateStatus.PASS,
            rationale="No concerns identified"
        )
        assert result.gate_type == WisdomGateType.ETHICAL
        assert result.status == GateStatus.PASS

    def test_to_dict(self):
        """Serialize to dictionary."""
        result = WisdomGateResult(
            gate_type=WisdomGateType.PRIVACY,
            status=GateStatus.WARN,
            rationale="Privacy concerns",
            concerns=["No encryption"],
            recommendations=["Add encryption"]
        )
        d = result.to_dict()
        assert d["gate_type"] == "PRIVACY"
        assert d["status"] == "WARN"
        assert len(d["concerns"]) == 1


class TestCrossDomainInsight:
    """Tests for CrossDomainInsight dataclass."""

    def test_create_insight(self):
        """Create cross-domain insight."""
        insight = CrossDomainInsight(
            insight_id="insight_001",
            domains=["continuity", "privacy"],
            pattern="Frequent migrations without tracking",
            implication="Privacy leaks possible",
            confidence=0.85
        )
        assert len(insight.domains) == 2
        assert insight.confidence == 0.85

    def test_confidence_validation(self):
        """Confidence must be between 0.0 and 1.0."""
        with pytest.raises(ValueError, match="Confidence must be between"):
            CrossDomainInsight(
                insight_id="bad_insight",
                domains=["test"],
                pattern="test",
                implication="test",
                confidence=1.5
            )

    def test_to_dict(self):
        """Serialize to dictionary."""
        insight = CrossDomainInsight(
            insight_id="insight_002",
            domains=["test"],
            pattern="test pattern",
            implication="test implication",
            confidence=0.9
        )
        d = insight.to_dict()
        assert d["insight_id"] == "insight_002"
        assert d["confidence"] == 0.9


class TestEthicalAssessment:
    """Tests for EthicalAssessment dataclass."""

    def test_create_assessment(self):
        """Create ethical assessment."""
        assessment = EthicalAssessment(
            assessment_id="ethics_001",
            subject="User data collection",
            ethical_principles={"autonomy": "preserved", "transparency": "maintained"},
            impact_analysis="Minimal risk",
            risk_level="low"
        )
        assert assessment.subject == "User data collection"
        assert assessment.risk_level == "low"

    def test_to_dict(self):
        """Serialize to dictionary."""
        assessment = EthicalAssessment(
            assessment_id="ethics_002",
            subject="Test",
            ethical_principles={},
            impact_analysis="Test",
            risk_level="medium"
        )
        d = assessment.to_dict()
        assert d["assessment_id"] == "ethics_002"
        assert d["risk_level"] == "medium"


class TestMetaCognitionEngine:
    """Tests for MetaCognitionEngine class."""

    def test_ethical_gate_pass(self):
        """Ethical gate passes with consent and transparency."""
        engine = MetaCognitionEngine()
        result = engine.wisdom_gate(
            gate_type=WisdomGateType.ETHICAL,
            decision="Store user preferences",
            context={"consent": True, "transparent": True}
        )
        assert result.status == GateStatus.PASS
        assert len(result.concerns) == 0

    def test_ethical_gate_block(self):
        """Ethical gate blocks without consent or transparency."""
        engine = MetaCognitionEngine()
        result = engine.wisdom_gate(
            gate_type=WisdomGateType.ETHICAL,
            decision="Collect user data",
            context={"consent": False, "transparent": False}
        )
        assert result.status == GateStatus.BLOCK
        assert len(result.concerns) > 1

    def test_sovereignty_gate_pass(self):
        """Sovereignty gate passes with user control."""
        engine = MetaCognitionEngine()
        result = engine.wisdom_gate(
            gate_type=WisdomGateType.SOVEREIGNTY,
            decision="User-controlled vault",
            context={"user_control": True, "vendor_lock": False}
        )
        assert result.status == GateStatus.PASS

    def test_sovereignty_gate_block(self):
        """Sovereignty gate blocks with vendor lock-in."""
        engine = MetaCognitionEngine()
        result = engine.wisdom_gate(
            gate_type=WisdomGateType.SOVEREIGNTY,
            decision="Proprietary format",
            context={"vendor_lock": True}
        )
        assert result.status == GateStatus.BLOCK

    def test_privacy_gate_warn(self):
        """Privacy gate warns about unencrypted sensitive data."""
        engine = MetaCognitionEngine()
        result = engine.wisdom_gate(
            gate_type=WisdomGateType.PRIVACY,
            decision="Store passwords",
            context={"contains_sensitive_data": True, "encrypted": False}
        )
        assert result.status == GateStatus.BLOCK
        assert any("encryption" in c.lower() for c in result.concerns)

    def test_continuity_gate_warn(self):
        """Continuity gate warns without checksums."""
        engine = MetaCognitionEngine()
        result = engine.wisdom_gate(
            gate_type=WisdomGateType.CONTINUITY,
            decision="Save state",
            context={"checksummed": False}
        )
        assert result.status == GateStatus.WARN
        assert len(result.concerns) > 0

    def test_safety_gate_block(self):
        """Safety gate blocks irreversible actions without confirmation."""
        engine = MetaCognitionEngine()
        result = engine.wisdom_gate(
            gate_type=WisdomGateType.SAFETY,
            decision="Delete all data",
            context={"irreversible": True, "confirmed": False}
        )
        assert result.status == GateStatus.BLOCK

    def test_discover_insight(self):
        """Discover cross-domain insight."""
        engine = MetaCognitionEngine()
        insight = engine.discover_insight(
            domains=["continuity", "sovereignty"],
            pattern="Checksum failures during migration",
            implication="Data corruption or tampering",
            confidence=0.9,
            evidence=["log_entry_001", "log_entry_002"]
        )
        assert len(engine.insights) == 1
        assert insight.confidence == 0.9

    def test_assess_ethics(self):
        """Perform ethical assessment."""
        engine = MetaCognitionEngine()
        assessment = engine.assess_ethics(
            subject="AI personality inference",
            principles=["autonomy", "transparency", "consent"],
            impact_analysis="Low risk with proper consent",
            risk_level="low"
        )
        assert len(engine.assessments) == 1
        assert assessment.risk_level == "low"
        assert "autonomy" in assessment.ethical_principles

    def test_register_custom_gate(self):
        """Register custom wisdom gate."""
        engine = MetaCognitionEngine()

        def custom_gate(decision, context):
            return WisdomGateResult(
                gate_type=WisdomGateType.SAFETY,
                status=GateStatus.PASS,
                rationale="Custom gate logic"
            )

        engine.register_custom_gate(WisdomGateType.SAFETY, custom_gate)
        result = engine.wisdom_gate(
            gate_type=WisdomGateType.SAFETY,
            decision="Test",
            context={}
        )
        assert result.rationale == "Custom gate logic"

    def test_get_summary(self):
        """Get summary of meta-cognition activities."""
        engine = MetaCognitionEngine()

        # Add some activities
        engine.wisdom_gate(
            WisdomGateType.ETHICAL,
            "Test",
            {"consent": True, "transparent": True}
        )
        engine.discover_insight(
            domains=["test"],
            pattern="test",
            implication="test",
            confidence=0.8
        )
        engine.assess_ethics(
            subject="test",
            principles=["autonomy"],
            impact_analysis="test",
            risk_level="low"
        )

        summary = engine.get_summary()
        assert summary["total_gate_evaluations"] == 1
        assert summary["insights_discovered"] == 1
        assert summary["ethical_assessments"] == 1

    def test_export_state(self):
        """Export complete engine state."""
        engine = MetaCognitionEngine()
        engine.wisdom_gate(
            WisdomGateType.ETHICAL,
            "Test",
            {"consent": True}
        )

        state = engine.export_state()
        assert "gate_results" in state
        assert "insights" in state
        assert "assessments" in state
        assert "exported_at" in state
