"""
MirrorDNA - Identity and Continuity Protocol

The architecture of persistence for AI agents and users.

This package provides the core protocol implementation including:
- Configuration loading and validation
- Checksum computation and verification
- Timeline event management
- State snapshot capture and serialization
- Truth-state enforcement (FEU tagging, drift detection)
- Vault management (VaultID tracking, lineage)
- Reflective review (philosophical audits)
- Meta-cognition (wisdom gates, ethical assessment)

Master Citation Version: v15.3
"""

__version__ = "1.0.0"
__citation_version__ = "15.3"

from .config_loader import ConfigLoader, MasterCitation, VaultConfig
from .checksum import (
    compute_file_checksum,
    compute_state_checksum,
    compute_text_checksum,
    verify_checksum
)
from .timeline import Timeline, TimelineEvent
from .state_snapshot import (
    StateSnapshot,
    capture_snapshot,
    serialize_snapshot,
    save_snapshot,
    load_snapshot,
    compare_snapshots
)

# Protocol Infrastructure (Master Citation v15.3)
from .truth_state import (
    TruthTag,
    TruthAssertion,
    TruthStateEnforcer,
    compute_source_checksum,
    tag_statement
)
from .vault_manager import (
    VaultID,
    LineageChain,
    VaultManager,
    create_vault_id
)
from .reflective_reviewer import (
    AuditDimension,
    ComplianceLevel,
    AuditResult,
    PhilosophicalAudit,
    ReflectiveReviewer,
    create_audit
)
from .meta_cognition import (
    WisdomGateType,
    GateStatus,
    WisdomGateResult,
    CrossDomainInsight,
    EthicalAssessment,
    MetaCognitionEngine
)

__all__ = [
    # Config loading
    "ConfigLoader",
    "MasterCitation",
    "VaultConfig",
    # Checksumming
    "compute_file_checksum",
    "compute_state_checksum",
    "compute_text_checksum",
    "verify_checksum",
    # Timeline
    "Timeline",
    "TimelineEvent",
    # State snapshots
    "StateSnapshot",
    "capture_snapshot",
    "serialize_snapshot",
    "save_snapshot",
    "load_snapshot",
    "compare_snapshots",
    # Truth-state enforcement
    "TruthTag",
    "TruthAssertion",
    "TruthStateEnforcer",
    "compute_source_checksum",
    "tag_statement",
    # Vault management
    "VaultID",
    "LineageChain",
    "VaultManager",
    "create_vault_id",
    # Reflective review
    "AuditDimension",
    "ComplianceLevel",
    "AuditResult",
    "PhilosophicalAudit",
    "ReflectiveReviewer",
    "create_audit",
    # Meta-cognition
    "WisdomGateType",
    "GateStatus",
    "WisdomGateResult",
    "CrossDomainInsight",
    "EthicalAssessment",
    "MetaCognitionEngine",
]
