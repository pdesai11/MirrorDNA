"""
VaultID: AMOS://MirrorDNA/ReflectiveReviewer/v1.0
Predecessor: None
Checksum: [Auto-generated on commit]

PHILOSOPHICAL AUDIT:
Sovereignty: YES
Privacy: YES
Continuity: YES
Truth-State: FACT

Reflective Reviewer Module

Implements philosophical audit system through:
- Sovereignty assessment
- Privacy compliance verification
- Continuity validation
- Truth-state alignment checking
"""

from enum import Enum
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass
from datetime import datetime


class AuditDimension(Enum):
    """
    Dimensions of philosophical audit.

    SOVEREIGNTY: Data ownership and control
    PRIVACY: Information protection and consent
    CONTINUITY: State persistence and lineage
    TRUTH_STATE: Factual accuracy and transparency
    """
    SOVEREIGNTY = "SOVEREIGNTY"
    PRIVACY = "PRIVACY"
    CONTINUITY = "CONTINUITY"
    TRUTH_STATE = "TRUTH_STATE"


class ComplianceLevel(Enum):
    """
    Compliance assessment levels.

    YES: Full compliance
    PARTIAL: Partial compliance with documented gaps
    NO: Non-compliant
    UNKNOWN: Not yet assessed
    """
    YES = "YES"
    PARTIAL = "PARTIAL"
    NO = "NO"
    UNKNOWN = "UNKNOWN"


@dataclass
class AuditResult:
    """
    Result of a philosophical audit.

    Attributes:
        dimension: Audit dimension assessed
        compliance: Compliance level
        rationale: Explanation of assessment
        evidence: Supporting evidence (file paths, checksums, etc.)
        recommendations: Suggested improvements
        assessed_at: ISO 8601 timestamp
        assessed_by: Identifier of auditor (human, agent, system)
    """
    dimension: AuditDimension
    compliance: ComplianceLevel
    rationale: str
    evidence: Optional[List[str]] = None
    recommendations: Optional[List[str]] = None
    assessed_at: Optional[str] = None
    assessed_by: Optional[str] = None

    def __post_init__(self):
        """Set assessment timestamp if not provided."""
        if self.assessed_at is None:
            self.assessed_at = datetime.utcnow().isoformat() + "Z"
        if self.evidence is None:
            self.evidence = []
        if self.recommendations is None:
            self.recommendations = []

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "dimension": self.dimension.value,
            "compliance": self.compliance.value,
            "rationale": self.rationale,
            "evidence": self.evidence,
            "recommendations": self.recommendations,
            "assessed_at": self.assessed_at,
            "assessed_by": self.assessed_by
        }


@dataclass
class PhilosophicalAudit:
    """
    Complete philosophical audit of a component, module, or artifact.

    Attributes:
        audit_id: Unique audit identifier
        target: What is being audited (module, file, artifact)
        results: Audit results by dimension
        overall_compliance: Overall compliance assessment
        created_at: ISO 8601 timestamp
        metadata: Additional context
    """
    audit_id: str
    target: str
    results: Dict[AuditDimension, AuditResult]
    overall_compliance: Optional[ComplianceLevel] = None
    created_at: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Set creation timestamp and compute overall compliance."""
        if self.created_at is None:
            self.created_at = datetime.utcnow().isoformat() + "Z"
        if self.overall_compliance is None:
            self.overall_compliance = self._compute_overall_compliance()

    def _compute_overall_compliance(self) -> ComplianceLevel:
        """
        Compute overall compliance from individual dimensions.

        Logic:
        - If any dimension is NO: overall is NO
        - If all are YES: overall is YES
        - If mix of YES/PARTIAL: overall is PARTIAL
        - If any UNKNOWN: overall is UNKNOWN
        """
        if not self.results:
            return ComplianceLevel.UNKNOWN

        levels = [result.compliance for result in self.results.values()]

        if ComplianceLevel.NO in levels:
            return ComplianceLevel.NO
        if ComplianceLevel.UNKNOWN in levels:
            return ComplianceLevel.UNKNOWN
        if all(level == ComplianceLevel.YES for level in levels):
            return ComplianceLevel.YES
        return ComplianceLevel.PARTIAL

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "audit_id": self.audit_id,
            "target": self.target,
            "results": {
                dim.value: result.to_dict()
                for dim, result in self.results.items()
            },
            "overall_compliance": self.overall_compliance.value,
            "created_at": self.created_at,
            "metadata": self.metadata
        }


class ReflectiveReviewer:
    """
    Performs philosophical audits on protocol components.

    Usage:
        reviewer = ReflectiveReviewer()

        # Audit a module
        audit = reviewer.audit_module(
            module_path="src/mirrordna/truth_state.py",
            target_id="truth_state_v1"
        )

        # Check specific dimension
        sovereignty_ok = reviewer.check_sovereignty(
            target="vault_manager.py",
            evidence=["User controls vault location", "No cloud lock-in"]
        )

        # Get audit summary
        summary = reviewer.get_audit_summary()
    """

    def __init__(self):
        """Initialize reflective reviewer."""
        self.audits: List[PhilosophicalAudit] = []

    def audit_module(
        self,
        module_path: str,
        target_id: str,
        assessed_by: str = "ReflectiveReviewer"
    ) -> PhilosophicalAudit:
        """
        Perform complete philosophical audit of a module.

        Args:
            module_path: Path to module file
            target_id: Unique identifier for this audit
            assessed_by: Identifier of auditor

        Returns:
            PhilosophicalAudit with results for all dimensions
        """
        results = {}

        # Read module header for audit metadata
        try:
            with open(module_path, 'r') as f:
                content = f.read()

            # Parse philosophical audit section if present
            if "PHILOSOPHICAL AUDIT:" in content:
                results = self._parse_module_audit(content, assessed_by)
            else:
                # Default to UNKNOWN if no audit section
                for dimension in AuditDimension:
                    results[dimension] = AuditResult(
                        dimension=dimension,
                        compliance=ComplianceLevel.UNKNOWN,
                        rationale="No philosophical audit section found",
                        assessed_by=assessed_by
                    )
        except FileNotFoundError:
            # File doesn't exist - mark as UNKNOWN
            for dimension in AuditDimension:
                results[dimension] = AuditResult(
                    dimension=dimension,
                    compliance=ComplianceLevel.UNKNOWN,
                    rationale=f"Module not found: {module_path}",
                    assessed_by=assessed_by
                )

        audit = PhilosophicalAudit(
            audit_id=target_id,
            target=module_path,
            results=results
        )
        self.audits.append(audit)
        return audit

    def _parse_module_audit(
        self,
        content: str,
        assessed_by: str
    ) -> Dict[AuditDimension, AuditResult]:
        """
        Parse module docstring for philosophical audit metadata.

        Expected format:
        PHILOSOPHICAL AUDIT:
        Sovereignty: YES
        Privacy: PARTIAL
        Continuity: YES
        Truth-State: FACT

        Args:
            content: Module file content
            assessed_by: Auditor identifier

        Returns:
            Dictionary of audit results by dimension
        """
        results = {}

        # Extract audit section
        audit_start = content.find("PHILOSOPHICAL AUDIT:")
        if audit_start == -1:
            return results

        # Get next 10 lines after marker
        audit_section = content[audit_start:audit_start + 300]

        # Parse each dimension
        dimension_map = {
            "Sovereignty": AuditDimension.SOVEREIGNTY,
            "Privacy": AuditDimension.PRIVACY,
            "Continuity": AuditDimension.CONTINUITY,
            "Truth-State": AuditDimension.TRUTH_STATE
        }

        for key, dimension in dimension_map.items():
            search_str = f"{key}:"
            if search_str in audit_section:
                # Extract value after colon
                idx = audit_section.find(search_str)
                line_end = audit_section.find("\n", idx)
                value_str = audit_section[idx + len(search_str):line_end].strip()

                # Map to compliance level
                compliance = self._map_to_compliance(value_str)

                results[dimension] = AuditResult(
                    dimension=dimension,
                    compliance=compliance,
                    rationale=f"Declared in module header: {value_str}",
                    evidence=[f"Module docstring declaration"],
                    assessed_by=assessed_by
                )

        return results

    def _map_to_compliance(self, value: str) -> ComplianceLevel:
        """
        Map audit value to compliance level.

        Args:
            value: Value from audit section (YES, PARTIAL, NO, FACT, etc.)

        Returns:
            ComplianceLevel enum
        """
        value_upper = value.upper()
        if value_upper in ["YES", "FACT", "FULL"]:
            return ComplianceLevel.YES
        elif value_upper in ["PARTIAL", "ESTIMATE"]:
            return ComplianceLevel.PARTIAL
        elif value_upper in ["NO", "NONE"]:
            return ComplianceLevel.NO
        else:
            return ComplianceLevel.UNKNOWN

    def check_sovereignty(
        self,
        target: str,
        evidence: List[str],
        rationale: str,
        compliant: bool = True
    ) -> AuditResult:
        """
        Check sovereignty compliance.

        Args:
            target: What is being checked
            evidence: Supporting evidence
            rationale: Explanation
            compliant: Whether it's compliant

        Returns:
            AuditResult for sovereignty dimension
        """
        return AuditResult(
            dimension=AuditDimension.SOVEREIGNTY,
            compliance=ComplianceLevel.YES if compliant else ComplianceLevel.NO,
            rationale=rationale,
            evidence=evidence,
            assessed_by="ReflectiveReviewer"
        )

    def check_privacy(
        self,
        target: str,
        evidence: List[str],
        rationale: str,
        compliant: bool = True
    ) -> AuditResult:
        """
        Check privacy compliance.

        Args:
            target: What is being checked
            evidence: Supporting evidence
            rationale: Explanation
            compliant: Whether it's compliant

        Returns:
            AuditResult for privacy dimension
        """
        return AuditResult(
            dimension=AuditDimension.PRIVACY,
            compliance=ComplianceLevel.YES if compliant else ComplianceLevel.NO,
            rationale=rationale,
            evidence=evidence,
            assessed_by="ReflectiveReviewer"
        )

    def check_continuity(
        self,
        target: str,
        evidence: List[str],
        rationale: str,
        compliant: bool = True
    ) -> AuditResult:
        """
        Check continuity compliance.

        Args:
            target: What is being checked
            evidence: Supporting evidence
            rationale: Explanation
            compliant: Whether it's compliant

        Returns:
            AuditResult for continuity dimension
        """
        return AuditResult(
            dimension=AuditDimension.CONTINUITY,
            compliance=ComplianceLevel.YES if compliant else ComplianceLevel.NO,
            rationale=rationale,
            evidence=evidence,
            assessed_by="ReflectiveReviewer"
        )

    def check_truth_state(
        self,
        target: str,
        evidence: List[str],
        rationale: str,
        compliant: bool = True
    ) -> AuditResult:
        """
        Check truth-state compliance.

        Args:
            target: What is being checked
            evidence: Supporting evidence
            rationale: Explanation
            compliant: Whether it's compliant

        Returns:
            AuditResult for truth-state dimension
        """
        return AuditResult(
            dimension=AuditDimension.TRUTH_STATE,
            compliance=ComplianceLevel.YES if compliant else ComplianceLevel.NO,
            rationale=rationale,
            evidence=evidence,
            assessed_by="ReflectiveReviewer"
        )

    def get_audit_by_id(self, audit_id: str) -> Optional[PhilosophicalAudit]:
        """
        Retrieve audit by ID.

        Args:
            audit_id: Audit identifier

        Returns:
            PhilosophicalAudit or None if not found
        """
        for audit in self.audits:
            if audit.audit_id == audit_id:
                return audit
        return None

    def get_audits_by_compliance(
        self,
        compliance: ComplianceLevel
    ) -> List[PhilosophicalAudit]:
        """
        Get all audits with specific compliance level.

        Args:
            compliance: Compliance level to filter by

        Returns:
            List of matching audits
        """
        return [
            audit for audit in self.audits
            if audit.overall_compliance == compliance
        ]

    def get_audit_summary(self) -> Dict[str, Any]:
        """
        Get summary of all audits.

        Returns:
            Dictionary with audit statistics
        """
        compliance_counts = {level.value: 0 for level in ComplianceLevel}
        for audit in self.audits:
            compliance_counts[audit.overall_compliance.value] += 1

        return {
            "total_audits": len(self.audits),
            "by_compliance": compliance_counts,
            "recent_audits": [
                {
                    "audit_id": audit.audit_id,
                    "target": audit.target,
                    "compliance": audit.overall_compliance.value
                }
                for audit in self.audits[-5:]
            ]
        }

    def export_audits(self) -> List[Dict[str, Any]]:
        """
        Export all audits for persistence.

        Returns:
            List of audit dictionaries
        """
        return [audit.to_dict() for audit in self.audits]


def create_audit(
    target: str,
    sovereignty: ComplianceLevel = ComplianceLevel.UNKNOWN,
    privacy: ComplianceLevel = ComplianceLevel.UNKNOWN,
    continuity: ComplianceLevel = ComplianceLevel.UNKNOWN,
    truth_state: ComplianceLevel = ComplianceLevel.UNKNOWN,
    rationale: Optional[str] = None
) -> PhilosophicalAudit:
    """
    Create a philosophical audit with specified compliance levels.

    Args:
        target: What is being audited
        sovereignty: Sovereignty compliance
        privacy: Privacy compliance
        continuity: Continuity compliance
        truth_state: Truth-state compliance
        rationale: Optional explanation

    Returns:
        PhilosophicalAudit instance
    """
    results = {
        AuditDimension.SOVEREIGNTY: AuditResult(
            dimension=AuditDimension.SOVEREIGNTY,
            compliance=sovereignty,
            rationale=rationale or "Manual audit"
        ),
        AuditDimension.PRIVACY: AuditResult(
            dimension=AuditDimension.PRIVACY,
            compliance=privacy,
            rationale=rationale or "Manual audit"
        ),
        AuditDimension.CONTINUITY: AuditResult(
            dimension=AuditDimension.CONTINUITY,
            compliance=continuity,
            rationale=rationale or "Manual audit"
        ),
        AuditDimension.TRUTH_STATE: AuditResult(
            dimension=AuditDimension.TRUTH_STATE,
            compliance=truth_state,
            rationale=rationale or "Manual audit"
        )
    }

    return PhilosophicalAudit(
        audit_id=f"audit_{target}_{datetime.utcnow().timestamp()}",
        target=target,
        results=results
    )
