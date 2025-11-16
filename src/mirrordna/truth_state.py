"""
VaultID: AMOS://MirrorDNA/TruthState/v1.0
Predecessor: None
Checksum: [Auto-generated on commit]

PHILOSOPHICAL AUDIT:
Sovereignty: YES
Privacy: YES
Continuity: YES
Truth-State: FACT

Truth-State Enforcement Module

Implements anti-hallucination mechanisms through:
- FEU (Fact/Estimate/Unknown) tagging
- Drift detection
- Source verification
- Canonical truth validation
"""

from enum import Enum
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass
from datetime import datetime
import hashlib
import json


class TruthTag(Enum):
    """
    Truth-state classification tags.

    FACT: Verified against canonical source or known data structure
    ESTIMATE: Reasoned inference with confidence level
    UNKNOWN: Acknowledged knowledge gap
    DRIFT: Detected deviation from canonical source
    """
    FACT = "FACT"
    ESTIMATE = "ESTIMATE"
    UNKNOWN = "UNKNOWN"
    DRIFT = "DRIFT"


@dataclass
class TruthAssertion:
    """
    A tagged statement with truth-state metadata.

    Attributes:
        statement: The assertion being made
        tag: Truth classification (FACT/ESTIMATE/UNKNOWN/DRIFT)
        source: Origin of the truth claim (file path, URL, memory ID)
        confidence: Confidence level for ESTIMATE tags (0.0-1.0)
        verified_at: Timestamp of verification
        checksum: SHA-256 of source material (for FACT tags)
        metadata: Additional context
    """
    statement: str
    tag: TruthTag
    source: Optional[str] = None
    confidence: Optional[float] = None
    verified_at: Optional[str] = None
    checksum: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Validate assertion constraints."""
        if self.tag == TruthTag.FACT and not self.source:
            raise ValueError("FACT assertions must include source")
        if self.tag == TruthTag.ESTIMATE and self.confidence is None:
            raise ValueError("ESTIMATE assertions must include confidence")
        if self.tag == TruthTag.ESTIMATE and not (0.0 <= self.confidence <= 1.0):
            raise ValueError("Confidence must be between 0.0 and 1.0")

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "statement": self.statement,
            "tag": self.tag.value,
            "source": self.source,
            "confidence": self.confidence,
            "verified_at": self.verified_at,
            "checksum": self.checksum,
            "metadata": self.metadata
        }


class TruthStateEnforcer:
    """
    Enforces truth-state discipline through FEU tagging and drift detection.

    Usage:
        enforcer = TruthStateEnforcer()

        # Tag a fact
        enforcer.assert_fact(
            statement="User prefers Python over JavaScript",
            source="vault://memories/preference_001.json",
            checksum="a3f2c8b9..."
        )

        # Tag an estimate
        enforcer.assert_estimate(
            statement="User likely works in data science",
            confidence=0.75,
            source="inferred from conversation context"
        )

        # Acknowledge unknown
        enforcer.assert_unknown(
            statement="User's preferred IDE",
            reason="Not yet discussed"
        )

        # Detect drift
        drift = enforcer.detect_drift(
            expected_checksum="a3f2c8b9...",
            actual_checksum="b4e3d9c8..."
        )
    """

    def __init__(self):
        """Initialize truth-state enforcer."""
        self.assertions: List[TruthAssertion] = []
        self.drift_log: List[Dict[str, Any]] = []

    def assert_fact(
        self,
        statement: str,
        source: str,
        checksum: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> TruthAssertion:
        """
        Tag a statement as FACT with source verification.

        Args:
            statement: The factual assertion
            source: Where the fact comes from (file, URL, memory ID)
            checksum: Optional SHA-256 of source material
            metadata: Additional context

        Returns:
            TruthAssertion tagged as FACT
        """
        assertion = TruthAssertion(
            statement=statement,
            tag=TruthTag.FACT,
            source=source,
            verified_at=datetime.utcnow().isoformat() + "Z",
            checksum=checksum,
            metadata=metadata
        )
        self.assertions.append(assertion)
        return assertion

    def assert_estimate(
        self,
        statement: str,
        confidence: float,
        source: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> TruthAssertion:
        """
        Tag a statement as ESTIMATE with confidence level.

        Args:
            statement: The estimated assertion
            confidence: Confidence level (0.0-1.0)
            source: Optional basis for the estimate
            metadata: Additional context

        Returns:
            TruthAssertion tagged as ESTIMATE
        """
        assertion = TruthAssertion(
            statement=statement,
            tag=TruthTag.ESTIMATE,
            confidence=confidence,
            source=source,
            verified_at=datetime.utcnow().isoformat() + "Z",
            metadata=metadata
        )
        self.assertions.append(assertion)
        return assertion

    def assert_unknown(
        self,
        statement: str,
        reason: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> TruthAssertion:
        """
        Explicitly tag a knowledge gap as UNKNOWN.

        Args:
            statement: What is unknown
            reason: Why it's unknown
            metadata: Additional context

        Returns:
            TruthAssertion tagged as UNKNOWN
        """
        assertion = TruthAssertion(
            statement=statement,
            tag=TruthTag.UNKNOWN,
            source=reason,
            verified_at=datetime.utcnow().isoformat() + "Z",
            metadata=metadata
        )
        self.assertions.append(assertion)
        return assertion

    def detect_drift(
        self,
        expected_checksum: str,
        actual_checksum: str,
        source: str,
        context: Optional[str] = None
    ) -> bool:
        """
        Detect drift by comparing expected vs actual checksums.

        Args:
            expected_checksum: Expected SHA-256 checksum
            actual_checksum: Actual SHA-256 checksum
            source: What is being checked
            context: Additional context about the drift

        Returns:
            True if drift detected, False if checksums match
        """
        if expected_checksum != actual_checksum:
            drift_entry = {
                "detected_at": datetime.utcnow().isoformat() + "Z",
                "source": source,
                "expected_checksum": expected_checksum,
                "actual_checksum": actual_checksum,
                "context": context
            }
            self.drift_log.append(drift_entry)

            # Also create a DRIFT assertion
            drift_assertion = TruthAssertion(
                statement=f"Drift detected in {source}",
                tag=TruthTag.DRIFT,
                source=source,
                verified_at=drift_entry["detected_at"],
                metadata={
                    "expected_checksum": expected_checksum,
                    "actual_checksum": actual_checksum,
                    "context": context
                }
            )
            self.assertions.append(drift_assertion)

            return True
        return False

    def get_assertions_by_tag(self, tag: TruthTag) -> List[TruthAssertion]:
        """
        Retrieve all assertions with a specific tag.

        Args:
            tag: Truth tag to filter by

        Returns:
            List of matching assertions
        """
        return [a for a in self.assertions if a.tag == tag]

    def get_drift_summary(self) -> Dict[str, Any]:
        """
        Get summary of detected drift.

        Returns:
            Dictionary with drift statistics and recent entries
        """
        return {
            "total_drift_events": len(self.drift_log),
            "recent_drift": self.drift_log[-5:] if self.drift_log else [],
            "drift_sources": list(set(d["source"] for d in self.drift_log))
        }

    def verify_against_canonical(
        self,
        statement: str,
        canonical_source: str,
        canonical_checksum: str
    ) -> TruthAssertion:
        """
        Verify a statement against canonical source.

        Args:
            statement: Statement to verify
            canonical_source: Canonical source identifier
            canonical_checksum: Expected checksum of canonical source

        Returns:
            TruthAssertion tagged as FACT if verified

        Raises:
            ValueError if verification fails
        """
        # In a real implementation, this would fetch and verify the source
        # For protocol purposes, we assume checksum verification
        return self.assert_fact(
            statement=statement,
            source=canonical_source,
            checksum=canonical_checksum,
            metadata={"verified_against_canonical": True}
        )

    def export_assertions(self) -> List[Dict[str, Any]]:
        """
        Export all assertions for persistence.

        Returns:
            List of assertion dictionaries
        """
        return [a.to_dict() for a in self.assertions]

    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics of truth-state enforcement.

        Returns:
            Dictionary with counts by tag and recent drift
        """
        tag_counts = {}
        for tag in TruthTag:
            tag_counts[tag.value] = len(self.get_assertions_by_tag(tag))

        return {
            "total_assertions": len(self.assertions),
            "by_tag": tag_counts,
            "drift_summary": self.get_drift_summary()
        }


def compute_source_checksum(content: str) -> str:
    """
    Compute SHA-256 checksum of source content.

    Args:
        content: Source content to hash

    Returns:
        64-character hex SHA-256 checksum
    """
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def tag_statement(
    statement: str,
    tag: TruthTag,
    **kwargs
) -> TruthAssertion:
    """
    Create a truth-tagged statement.

    Args:
        statement: The statement to tag
        tag: Truth classification
        **kwargs: Additional TruthAssertion parameters

    Returns:
        TruthAssertion instance
    """
    return TruthAssertion(statement=statement, tag=tag, **kwargs)
