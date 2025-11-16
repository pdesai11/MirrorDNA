"""
Tests for reflective_reviewer.py module.
"""

import pytest
import tempfile
import os
from mirrordna import (
    AuditDimension,
    ComplianceLevel,
    AuditResult,
    PhilosophicalAudit,
    ReflectiveReviewer,
    create_audit
)


class TestAuditResult:
    """Tests for AuditResult dataclass."""

    def test_create_audit_result(self):
        """Create basic audit result."""
        result = AuditResult(
            dimension=AuditDimension.SOVEREIGNTY,
            compliance=ComplianceLevel.YES,
            rationale="Full user control maintained"
        )
        assert result.dimension == AuditDimension.SOVEREIGNTY
        assert result.compliance == ComplianceLevel.YES

    def test_to_dict(self):
        """Serialize to dictionary."""
        result = AuditResult(
            dimension=AuditDimension.PRIVACY,
            compliance=ComplianceLevel.PARTIAL,
            rationale="Some privacy concerns",
            evidence=["No encryption"],
            recommendations=["Add encryption"]
        )
        d = result.to_dict()
        assert d["dimension"] == "PRIVACY"
        assert d["compliance"] == "PARTIAL"
        assert len(d["evidence"]) == 1
        assert len(d["recommendations"]) == 1


class TestPhilosophicalAudit:
    """Tests for PhilosophicalAudit dataclass."""

    def test_overall_compliance_all_yes(self):
        """All YES results -> overall YES."""
        results = {
            AuditDimension.SOVEREIGNTY: AuditResult(
                AuditDimension.SOVEREIGNTY, ComplianceLevel.YES, "Good"
            ),
            AuditDimension.PRIVACY: AuditResult(
                AuditDimension.PRIVACY, ComplianceLevel.YES, "Good"
            )
        }
        audit = PhilosophicalAudit(
            audit_id="test_001",
            target="test_module",
            results=results
        )
        assert audit.overall_compliance == ComplianceLevel.YES

    def test_overall_compliance_any_no(self):
        """Any NO result -> overall NO."""
        results = {
            AuditDimension.SOVEREIGNTY: AuditResult(
                AuditDimension.SOVEREIGNTY, ComplianceLevel.YES, "Good"
            ),
            AuditDimension.PRIVACY: AuditResult(
                AuditDimension.PRIVACY, ComplianceLevel.NO, "Bad"
            )
        }
        audit = PhilosophicalAudit(
            audit_id="test_002",
            target="test_module",
            results=results
        )
        assert audit.overall_compliance == ComplianceLevel.NO

    def test_overall_compliance_partial(self):
        """Mix of YES and PARTIAL -> overall PARTIAL."""
        results = {
            AuditDimension.SOVEREIGNTY: AuditResult(
                AuditDimension.SOVEREIGNTY, ComplianceLevel.YES, "Good"
            ),
            AuditDimension.PRIVACY: AuditResult(
                AuditDimension.PRIVACY, ComplianceLevel.PARTIAL, "Some issues"
            )
        }
        audit = PhilosophicalAudit(
            audit_id="test_003",
            target="test_module",
            results=results
        )
        assert audit.overall_compliance == ComplianceLevel.PARTIAL

    def test_to_dict(self):
        """Serialize audit to dictionary."""
        results = {
            AuditDimension.SOVEREIGNTY: AuditResult(
                AuditDimension.SOVEREIGNTY, ComplianceLevel.YES, "Good"
            )
        }
        audit = PhilosophicalAudit(
            audit_id="test_004",
            target="test_module",
            results=results
        )
        d = audit.to_dict()
        assert d["audit_id"] == "test_004"
        assert d["target"] == "test_module"
        assert "SOVEREIGNTY" in d["results"]


class TestReflectiveReviewer:
    """Tests for ReflectiveReviewer class."""

    def test_check_sovereignty(self):
        """Check sovereignty compliance."""
        reviewer = ReflectiveReviewer()
        result = reviewer.check_sovereignty(
            target="test_module",
            evidence=["User controls data", "No vendor lock-in"],
            rationale="Full sovereignty maintained",
            compliant=True
        )
        assert result.dimension == AuditDimension.SOVEREIGNTY
        assert result.compliance == ComplianceLevel.YES

    def test_check_privacy(self):
        """Check privacy compliance."""
        reviewer = ReflectiveReviewer()
        result = reviewer.check_privacy(
            target="test_module",
            evidence=["Encrypted at rest"],
            rationale="Privacy protected",
            compliant=True
        )
        assert result.dimension == AuditDimension.PRIVACY
        assert result.compliance == ComplianceLevel.YES

    def test_check_continuity(self):
        """Check continuity compliance."""
        reviewer = ReflectiveReviewer()
        result = reviewer.check_continuity(
            target="test_module",
            evidence=["Checksum verified", "Lineage tracked"],
            rationale="Continuity maintained",
            compliant=True
        )
        assert result.dimension == AuditDimension.CONTINUITY
        assert result.compliance == ComplianceLevel.YES

    def test_check_truth_state(self):
        """Check truth-state compliance."""
        reviewer = ReflectiveReviewer()
        result = reviewer.check_truth_state(
            target="test_module",
            evidence=["FEU tagged", "Source verified"],
            rationale="Truth-state enforced",
            compliant=True
        )
        assert result.dimension == AuditDimension.TRUTH_STATE
        assert result.compliance == ComplianceLevel.YES

    def test_audit_module_with_header(self):
        """Audit module with philosophical audit header."""
        # Create temporary file with audit header
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
            f.write('''"""
PHILOSOPHICAL AUDIT:
Sovereignty: YES
Privacy: PARTIAL
Continuity: YES
Truth-State: FACT
"""
''')
            temp_file = f.name

        try:
            reviewer = ReflectiveReviewer()
            audit = reviewer.audit_module(
                module_path=temp_file,
                target_id="temp_module"
            )

            assert audit.target == temp_file
            assert len(audit.results) == 4
            assert audit.results[AuditDimension.SOVEREIGNTY].compliance == ComplianceLevel.YES
            assert audit.results[AuditDimension.PRIVACY].compliance == ComplianceLevel.PARTIAL
        finally:
            os.unlink(temp_file)

    def test_audit_module_not_found(self):
        """Audit non-existent module."""
        reviewer = ReflectiveReviewer()
        audit = reviewer.audit_module(
            module_path="/nonexistent/module.py",
            target_id="missing_module"
        )

        # Should create audit with UNKNOWN compliance
        for result in audit.results.values():
            assert result.compliance == ComplianceLevel.UNKNOWN

    def test_get_audits_by_compliance(self):
        """Filter audits by compliance level."""
        reviewer = ReflectiveReviewer()

        # Create audits with different compliance levels
        audit1 = create_audit(
            target="module1",
            sovereignty=ComplianceLevel.YES,
            privacy=ComplianceLevel.YES,
            continuity=ComplianceLevel.YES,
            truth_state=ComplianceLevel.YES
        )
        reviewer.audits.append(audit1)

        audit2 = create_audit(
            target="module2",
            sovereignty=ComplianceLevel.NO,
            privacy=ComplianceLevel.NO,
            continuity=ComplianceLevel.NO,
            truth_state=ComplianceLevel.NO
        )
        reviewer.audits.append(audit2)

        yes_audits = reviewer.get_audits_by_compliance(ComplianceLevel.YES)
        assert len(yes_audits) == 1
        assert yes_audits[0].target == "module1"

        no_audits = reviewer.get_audits_by_compliance(ComplianceLevel.NO)
        assert len(no_audits) == 1
        assert no_audits[0].target == "module2"

    def test_get_audit_summary(self):
        """Get summary of all audits."""
        reviewer = ReflectiveReviewer()

        audit1 = create_audit(
            target="module1",
            sovereignty=ComplianceLevel.YES,
            privacy=ComplianceLevel.YES,
            continuity=ComplianceLevel.YES,
            truth_state=ComplianceLevel.YES
        )
        reviewer.audits.append(audit1)

        summary = reviewer.get_audit_summary()
        assert summary["total_audits"] == 1
        assert summary["by_compliance"]["YES"] == 1


class TestHelperFunctions:
    """Tests for helper functions."""

    def test_create_audit(self):
        """Create audit with specified compliance levels."""
        audit = create_audit(
            target="test_module",
            sovereignty=ComplianceLevel.YES,
            privacy=ComplianceLevel.PARTIAL,
            continuity=ComplianceLevel.YES,
            truth_state=ComplianceLevel.YES,
            rationale="Test audit"
        )

        assert audit.target == "test_module"
        assert audit.results[AuditDimension.SOVEREIGNTY].compliance == ComplianceLevel.YES
        assert audit.results[AuditDimension.PRIVACY].compliance == ComplianceLevel.PARTIAL
        assert audit.overall_compliance == ComplianceLevel.PARTIAL
