"""
VaultID: AMOS://MirrorDNA/MetaCognition/v1.0
Predecessor: None
Checksum: [Auto-generated on commit]

PHILOSOPHICAL AUDIT:
Sovereignty: YES
Privacy: YES
Continuity: YES
Truth-State: FACT

Meta-Cognition Module

Implements higher-order reasoning and ethical assessment through:
- Cross-domain insight generation
- Wisdom gates for critical decisions
- Ethical impact assessment
- Pattern recognition across protocol layers
"""

from enum import Enum
from typing import Any, Dict, List, Optional, Set, Callable
from dataclasses import dataclass, field
from datetime import datetime


class WisdomGateType(Enum):
    """
    Types of wisdom gates for decision validation.

    ETHICAL: Ethical implications and alignment
    SOVEREIGNTY: User autonomy and control implications
    PRIVACY: Data protection and consent implications
    CONTINUITY: Long-term state integrity implications
    SAFETY: Risk assessment and harm prevention
    """
    ETHICAL = "ETHICAL"
    SOVEREIGNTY = "SOVEREIGNTY"
    PRIVACY = "PRIVACY"
    CONTINUITY = "CONTINUITY"
    SAFETY = "SAFETY"


class GateStatus(Enum):
    """
    Status of wisdom gate evaluation.

    PASS: Decision passes gate criteria
    WARN: Warning issued but not blocked
    BLOCK: Decision blocked pending review
    PENDING: Awaiting human review
    """
    PASS = "PASS"
    WARN = "WARN"
    BLOCK = "BLOCK"
    PENDING = "PENDING"


@dataclass
class WisdomGateResult:
    """
    Result of passing a decision through a wisdom gate.

    Attributes:
        gate_type: Type of wisdom gate
        status: Gate evaluation status
        rationale: Explanation of decision
        concerns: List of identified concerns
        recommendations: Suggested actions or modifications
        evaluated_at: ISO 8601 timestamp
        evaluated_by: Identifier of evaluator
        metadata: Additional context
    """
    gate_type: WisdomGateType
    status: GateStatus
    rationale: str
    concerns: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    evaluated_at: Optional[str] = None
    evaluated_by: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Set evaluation timestamp if not provided."""
        if self.evaluated_at is None:
            self.evaluated_at = datetime.utcnow().isoformat() + "Z"

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "gate_type": self.gate_type.value,
            "status": self.status.value,
            "rationale": self.rationale,
            "concerns": self.concerns,
            "recommendations": self.recommendations,
            "evaluated_at": self.evaluated_at,
            "evaluated_by": self.evaluated_by,
            "metadata": self.metadata
        }


@dataclass
class CrossDomainInsight:
    """
    An insight derived from cross-domain pattern recognition.

    Attributes:
        insight_id: Unique identifier
        domains: Domains involved (e.g., ["continuity", "privacy"])
        pattern: Observed pattern description
        implication: What this pattern implies
        confidence: Confidence in the insight (0.0-1.0)
        discovered_at: ISO 8601 timestamp
        supporting_evidence: List of evidence references
    """
    insight_id: str
    domains: List[str]
    pattern: str
    implication: str
    confidence: float
    discovered_at: Optional[str] = None
    supporting_evidence: Optional[List[str]] = None

    def __post_init__(self):
        """Validate and set defaults."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
        if self.discovered_at is None:
            self.discovered_at = datetime.utcnow().isoformat() + "Z"
        if self.supporting_evidence is None:
            self.supporting_evidence = []

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "insight_id": self.insight_id,
            "domains": self.domains,
            "pattern": self.pattern,
            "implication": self.implication,
            "confidence": self.confidence,
            "discovered_at": self.discovered_at,
            "supporting_evidence": self.supporting_evidence
        }


@dataclass
class EthicalAssessment:
    """
    Ethical impact assessment of a decision or action.

    Attributes:
        assessment_id: Unique identifier
        subject: What is being assessed
        ethical_principles: Principles evaluated (e.g., autonomy, beneficence)
        impact_analysis: Analysis of potential impacts
        risk_level: Overall risk level (low, medium, high, critical)
        mitigation_strategies: Recommended mitigations
        assessed_at: ISO 8601 timestamp
    """
    assessment_id: str
    subject: str
    ethical_principles: Dict[str, str]
    impact_analysis: str
    risk_level: str
    mitigation_strategies: List[str] = field(default_factory=list)
    assessed_at: Optional[str] = None

    def __post_init__(self):
        """Set assessment timestamp if not provided."""
        if self.assessed_at is None:
            self.assessed_at = datetime.utcnow().isoformat() + "Z"

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "assessment_id": self.assessment_id,
            "subject": self.subject,
            "ethical_principles": self.ethical_principles,
            "impact_analysis": self.impact_analysis,
            "risk_level": self.risk_level,
            "mitigation_strategies": self.mitigation_strategies,
            "assessed_at": self.assessed_at
        }


class MetaCognitionEngine:
    """
    Higher-order reasoning engine for wisdom gates and cross-domain insights.

    Usage:
        engine = MetaCognitionEngine()

        # Pass decision through wisdom gate
        result = engine.wisdom_gate(
            gate_type=WisdomGateType.ETHICAL,
            decision="Store user conversation data",
            context={"consent": True, "encrypted": True}
        )

        # Generate cross-domain insight
        insight = engine.discover_insight(
            domains=["continuity", "privacy"],
            pattern="Frequent vault migrations without consent tracking",
            confidence=0.85
        )

        # Perform ethical assessment
        assessment = engine.assess_ethics(
            subject="Automated personality inference",
            principles=["autonomy", "transparency", "consent"]
        )
    """

    def __init__(self):
        """Initialize meta-cognition engine."""
        self.gate_results: List[WisdomGateResult] = []
        self.insights: List[CrossDomainInsight] = []
        self.assessments: List[EthicalAssessment] = []
        self.custom_gates: Dict[WisdomGateType, Callable] = {}

    def wisdom_gate(
        self,
        gate_type: WisdomGateType,
        decision: str,
        context: Optional[Dict[str, Any]] = None,
        evaluated_by: str = "MetaCognitionEngine"
    ) -> WisdomGateResult:
        """
        Pass a decision through a wisdom gate.

        Args:
            gate_type: Type of wisdom gate to apply
            decision: Description of the decision being evaluated
            context: Additional context for evaluation
            evaluated_by: Identifier of evaluator

        Returns:
            WisdomGateResult with evaluation outcome
        """
        context = context or {}

        # Check for custom gate implementation
        if gate_type in self.custom_gates:
            return self.custom_gates[gate_type](decision, context)

        # Default gate implementations
        if gate_type == WisdomGateType.ETHICAL:
            result = self._ethical_gate(decision, context, evaluated_by)
        elif gate_type == WisdomGateType.SOVEREIGNTY:
            result = self._sovereignty_gate(decision, context, evaluated_by)
        elif gate_type == WisdomGateType.PRIVACY:
            result = self._privacy_gate(decision, context, evaluated_by)
        elif gate_type == WisdomGateType.CONTINUITY:
            result = self._continuity_gate(decision, context, evaluated_by)
        elif gate_type == WisdomGateType.SAFETY:
            result = self._safety_gate(decision, context, evaluated_by)
        else:
            result = WisdomGateResult(
                gate_type=gate_type,
                status=GateStatus.PENDING,
                rationale="Unknown gate type - requires human review",
                evaluated_by=evaluated_by
            )

        self.gate_results.append(result)
        return result

    def _ethical_gate(
        self,
        decision: str,
        context: Dict[str, Any],
        evaluated_by: str
    ) -> WisdomGateResult:
        """Evaluate ethical implications."""
        concerns = []
        recommendations = []

        # Check for consent
        if not context.get("consent", False):
            concerns.append("User consent not explicitly obtained")
            recommendations.append("Obtain explicit user consent before proceeding")

        # Check for transparency
        if not context.get("transparent", False):
            concerns.append("Decision process not transparent to user")
            recommendations.append("Document and communicate decision rationale")

        # Determine status
        if len(concerns) > 1:
            status = GateStatus.BLOCK
            rationale = "Multiple ethical concerns identified - review required"
        elif concerns:
            status = GateStatus.WARN
            rationale = "Ethical concerns identified - proceed with caution"
        else:
            status = GateStatus.PASS
            rationale = "No ethical concerns identified"

        return WisdomGateResult(
            gate_type=WisdomGateType.ETHICAL,
            status=status,
            rationale=rationale,
            concerns=concerns,
            recommendations=recommendations,
            evaluated_by=evaluated_by
        )

    def _sovereignty_gate(
        self,
        decision: str,
        context: Dict[str, Any],
        evaluated_by: str
    ) -> WisdomGateResult:
        """Evaluate sovereignty implications."""
        concerns = []
        recommendations = []

        # Check for user control
        if not context.get("user_control", True):
            concerns.append("User loses control over their data")
            recommendations.append("Ensure user retains data ownership and control")

        # Check for vendor lock-in
        if context.get("vendor_lock", False):
            concerns.append("Creates vendor lock-in")
            recommendations.append("Use open protocols and portable formats")

        status = GateStatus.BLOCK if concerns else GateStatus.PASS
        rationale = "Sovereignty preserved" if status == GateStatus.PASS else "Sovereignty concerns detected"

        return WisdomGateResult(
            gate_type=WisdomGateType.SOVEREIGNTY,
            status=status,
            rationale=rationale,
            concerns=concerns,
            recommendations=recommendations,
            evaluated_by=evaluated_by
        )

    def _privacy_gate(
        self,
        decision: str,
        context: Dict[str, Any],
        evaluated_by: str
    ) -> WisdomGateResult:
        """Evaluate privacy implications."""
        concerns = []
        recommendations = []

        # Check for encryption
        if context.get("contains_sensitive_data", False) and not context.get("encrypted", False):
            concerns.append("Sensitive data not encrypted")
            recommendations.append("Encrypt sensitive data at rest and in transit")

        # Check for data minimization
        if not context.get("minimal_data", True):
            concerns.append("Collects more data than necessary")
            recommendations.append("Apply data minimization principles")

        status = GateStatus.BLOCK if "not encrypted" in str(concerns) else (
            GateStatus.WARN if concerns else GateStatus.PASS
        )
        rationale = "Privacy protected" if status == GateStatus.PASS else "Privacy concerns detected"

        return WisdomGateResult(
            gate_type=WisdomGateType.PRIVACY,
            status=status,
            rationale=rationale,
            concerns=concerns,
            recommendations=recommendations,
            evaluated_by=evaluated_by
        )

    def _continuity_gate(
        self,
        decision: str,
        context: Dict[str, Any],
        evaluated_by: str
    ) -> WisdomGateResult:
        """Evaluate continuity implications."""
        concerns = []
        recommendations = []

        # Check for checksum verification
        if not context.get("checksummed", False):
            concerns.append("No checksum verification for state integrity")
            recommendations.append("Add SHA-256 checksum verification")

        # Check for lineage tracking
        if not context.get("lineage_tracked", True):
            concerns.append("Lineage not tracked - continuity may break")
            recommendations.append("Track predecessor/successor relationships")

        status = GateStatus.WARN if concerns else GateStatus.PASS
        rationale = "Continuity preserved" if status == GateStatus.PASS else "Continuity concerns detected"

        return WisdomGateResult(
            gate_type=WisdomGateType.CONTINUITY,
            status=status,
            rationale=rationale,
            concerns=concerns,
            recommendations=recommendations,
            evaluated_by=evaluated_by
        )

    def _safety_gate(
        self,
        decision: str,
        context: Dict[str, Any],
        evaluated_by: str
    ) -> WisdomGateResult:
        """Evaluate safety implications."""
        concerns = []
        recommendations = []

        # Check for irreversible actions
        if context.get("irreversible", False) and not context.get("confirmed", False):
            concerns.append("Irreversible action without confirmation")
            recommendations.append("Require explicit user confirmation")

        # Check for data loss risk
        if context.get("data_loss_risk", False):
            concerns.append("Risk of data loss")
            recommendations.append("Create backup before proceeding")

        status = GateStatus.BLOCK if "Irreversible" in str(concerns) else (
            GateStatus.WARN if concerns else GateStatus.PASS
        )
        rationale = "Safe to proceed" if status == GateStatus.PASS else "Safety concerns detected"

        return WisdomGateResult(
            gate_type=WisdomGateType.SAFETY,
            status=status,
            rationale=rationale,
            concerns=concerns,
            recommendations=recommendations,
            evaluated_by=evaluated_by
        )

    def discover_insight(
        self,
        domains: List[str],
        pattern: str,
        implication: str,
        confidence: float,
        evidence: Optional[List[str]] = None
    ) -> CrossDomainInsight:
        """
        Record a cross-domain insight.

        Args:
            domains: Domains involved in the pattern
            pattern: Description of observed pattern
            implication: What the pattern implies
            confidence: Confidence level (0.0-1.0)
            evidence: Supporting evidence

        Returns:
            CrossDomainInsight instance
        """
        insight = CrossDomainInsight(
            insight_id=f"insight_{len(self.insights):04d}",
            domains=domains,
            pattern=pattern,
            implication=implication,
            confidence=confidence,
            supporting_evidence=evidence or []
        )
        self.insights.append(insight)
        return insight

    def assess_ethics(
        self,
        subject: str,
        principles: List[str],
        impact_analysis: str,
        risk_level: str = "medium"
    ) -> EthicalAssessment:
        """
        Perform ethical impact assessment.

        Args:
            subject: What is being assessed
            principles: Ethical principles to evaluate
            impact_analysis: Analysis of impacts
            risk_level: Overall risk (low, medium, high, critical)

        Returns:
            EthicalAssessment instance
        """
        # Generate principle evaluations
        ethical_principles = {}
        for principle in principles:
            ethical_principles[principle] = self._evaluate_principle(
                principle,
                subject,
                impact_analysis
            )

        assessment = EthicalAssessment(
            assessment_id=f"ethics_{len(self.assessments):04d}",
            subject=subject,
            ethical_principles=ethical_principles,
            impact_analysis=impact_analysis,
            risk_level=risk_level
        )
        self.assessments.append(assessment)
        return assessment

    def _evaluate_principle(
        self,
        principle: str,
        subject: str,
        analysis: str
    ) -> str:
        """
        Evaluate a specific ethical principle.

        Args:
            principle: Ethical principle name
            subject: Subject of assessment
            analysis: Impact analysis

        Returns:
            Evaluation result string
        """
        # Simple pattern matching for common principles
        principle_lower = principle.lower()

        if "autonomy" in principle_lower:
            return "Preserves user autonomy and self-determination"
        elif "transparency" in principle_lower:
            return "Maintains transparency in decision-making"
        elif "consent" in principle_lower:
            return "Requires explicit informed consent"
        elif "beneficence" in principle_lower:
            return "Maximizes benefit while minimizing harm"
        else:
            return f"Principle '{principle}' evaluated in context"

    def register_custom_gate(
        self,
        gate_type: WisdomGateType,
        gate_function: Callable[[str, Dict[str, Any]], WisdomGateResult]
    ) -> None:
        """
        Register a custom wisdom gate implementation.

        Args:
            gate_type: Type of wisdom gate
            gate_function: Function that evaluates decisions
        """
        self.custom_gates[gate_type] = gate_function

    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary of meta-cognition activities.

        Returns:
            Dictionary with statistics
        """
        gate_stats = {}
        for result in self.gate_results:
            gate_type = result.gate_type.value
            status = result.status.value
            key = f"{gate_type}_{status}"
            gate_stats[key] = gate_stats.get(key, 0) + 1

        return {
            "total_gate_evaluations": len(self.gate_results),
            "gate_statistics": gate_stats,
            "insights_discovered": len(self.insights),
            "ethical_assessments": len(self.assessments),
            "recent_blocks": [
                r.to_dict() for r in self.gate_results
                if r.status == GateStatus.BLOCK
            ][-5:]
        }

    def export_state(self) -> Dict[str, Any]:
        """
        Export complete meta-cognition state.

        Returns:
            Dictionary with all data
        """
        return {
            "gate_results": [r.to_dict() for r in self.gate_results],
            "insights": [i.to_dict() for i in self.insights],
            "assessments": [a.to_dict() for a in self.assessments],
            "exported_at": datetime.utcnow().isoformat() + "Z"
        }
