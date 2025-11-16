"""
VaultID: AMOS://MirrorDNA/VaultManager/v1.0
Predecessor: None
Checksum: [Auto-generated on commit]

PHILOSOPHICAL AUDIT:
Sovereignty: YES
Privacy: YES
Continuity: YES
Truth-State: FACT

Vault Manager Module

Implements vault management through:
- VaultID tracking and generation
- Checksum generation for artifacts
- Lineage chain management
- Session continuity tracking
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import hashlib
import json
import re


@dataclass
class VaultID:
    """
    Structured VaultID following AMOS:// protocol.

    Format: AMOS://{domain}/{module}/v{version}

    Attributes:
        domain: Top-level domain (e.g., MirrorDNA, ActiveMirrorOS)
        module: Module or component name
        version: Semantic version
        predecessor: Optional predecessor VaultID
        checksum: SHA-256 checksum of this VaultID record
        created_at: ISO 8601 timestamp
        metadata: Additional context
    """
    domain: str
    module: str
    version: str
    predecessor: Optional[str] = None
    checksum: Optional[str] = None
    created_at: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Set creation timestamp if not provided."""
        if self.created_at is None:
            self.created_at = datetime.utcnow().isoformat() + "Z"

    def to_uri(self) -> str:
        """
        Convert to AMOS:// URI format.

        Returns:
            AMOS://{domain}/{module}/v{version}
        """
        return f"AMOS://{self.domain}/{self.module}/v{self.version}"

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "uri": self.to_uri(),
            "domain": self.domain,
            "module": self.module,
            "version": self.version,
            "predecessor": self.predecessor,
            "checksum": self.checksum,
            "created_at": self.created_at,
            "metadata": self.metadata
        }

    @classmethod
    def from_uri(cls, uri: str) -> "VaultID":
        """
        Parse AMOS:// URI into VaultID.

        Args:
            uri: AMOS://{domain}/{module}/v{version}

        Returns:
            VaultID instance

        Raises:
            ValueError if URI format is invalid
        """
        pattern = r"^AMOS://([^/]+)/([^/]+)/v(.+)$"
        match = re.match(pattern, uri)
        if not match:
            raise ValueError(f"Invalid VaultID URI format: {uri}")

        domain, module, version = match.groups()
        return cls(domain=domain, module=module, version=version)


@dataclass
class LineageChain:
    """
    Tracks lineage of VaultIDs forming a predecessor/successor chain.

    Attributes:
        chain_id: Unique identifier for this lineage chain
        vault_ids: Ordered list of VaultIDs (oldest to newest)
        created_at: ISO 8601 timestamp
        metadata: Additional context
    """
    chain_id: str
    vault_ids: List[VaultID] = field(default_factory=list)
    created_at: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Set creation timestamp if not provided."""
        if self.created_at is None:
            self.created_at = datetime.utcnow().isoformat() + "Z"

    def append(self, vault_id: VaultID) -> None:
        """
        Add a VaultID to the lineage chain.

        Args:
            vault_id: VaultID to append

        Raises:
            ValueError if lineage is broken
        """
        if self.vault_ids:
            # Verify predecessor link
            last_vault = self.vault_ids[-1]
            if vault_id.predecessor != last_vault.to_uri():
                raise ValueError(
                    f"Lineage break: Expected predecessor {last_vault.to_uri()}, "
                    f"got {vault_id.predecessor}"
                )
        self.vault_ids.append(vault_id)

    def get_current(self) -> Optional[VaultID]:
        """
        Get the most recent VaultID in the chain.

        Returns:
            Latest VaultID or None if chain is empty
        """
        return self.vault_ids[-1] if self.vault_ids else None

    def get_ancestor(self, generations_back: int = 1) -> Optional[VaultID]:
        """
        Get an ancestor VaultID.

        Args:
            generations_back: How many generations to go back

        Returns:
            Ancestor VaultID or None if out of range
        """
        idx = len(self.vault_ids) - 1 - generations_back
        return self.vault_ids[idx] if 0 <= idx < len(self.vault_ids) else None

    def verify_integrity(self) -> bool:
        """
        Verify the lineage chain has no breaks.

        Returns:
            True if chain is valid, False otherwise
        """
        for i in range(1, len(self.vault_ids)):
            current = self.vault_ids[i]
            previous = self.vault_ids[i - 1]
            if current.predecessor != previous.to_uri():
                return False
        return True

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "chain_id": self.chain_id,
            "vault_ids": [v.to_dict() for v in self.vault_ids],
            "created_at": self.created_at,
            "metadata": self.metadata
        }


class VaultManager:
    """
    Manages vault artifacts, VaultIDs, and lineage tracking.

    Usage:
        manager = VaultManager(vault_id="vault_myagent_main")

        # Create artifact with VaultID
        artifact = manager.create_artifact(
            content="User prefers Python",
            artifact_type="memory",
            metadata={"source": "conversation"}
        )

        # Track lineage
        vault_id = VaultID(
            domain="MirrorDNA",
            module="Session",
            version="1.0"
        )
        manager.track_lineage(vault_id)

        # Generate checksum
        checksum = manager.generate_checksum(artifact)
    """

    def __init__(self, vault_id: str):
        """
        Initialize vault manager.

        Args:
            vault_id: Vault identifier (e.g., vault_myagent_main)
        """
        self.vault_id = vault_id
        self.artifacts: List[Dict[str, Any]] = []
        self.lineage_chains: Dict[str, LineageChain] = {}
        self.session_log: List[Dict[str, Any]] = []

    def create_artifact(
        self,
        content: Any,
        artifact_type: str,
        artifact_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a vault artifact with checksum.

        Args:
            content: Artifact content (dict, str, or serializable)
            artifact_type: Type of artifact (memory, snapshot, config, etc.)
            artifact_id: Optional custom artifact ID
            metadata: Additional metadata

        Returns:
            Artifact dictionary with checksum
        """
        if artifact_id is None:
            artifact_id = f"{artifact_type}_{len(self.artifacts):04d}"

        # Serialize content for checksumming
        if isinstance(content, dict):
            content_str = json.dumps(content, sort_keys=True)
        else:
            content_str = str(content)

        checksum = self.generate_checksum(content_str)

        artifact = {
            "artifact_id": artifact_id,
            "vault_id": self.vault_id,
            "artifact_type": artifact_type,
            "content": content,
            "checksum": checksum,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "metadata": metadata or {}
        }

        self.artifacts.append(artifact)
        return artifact

    def generate_checksum(self, content: Any) -> str:
        """
        Generate SHA-256 checksum for content.

        Args:
            content: Content to hash (string or dict)

        Returns:
            64-character hex SHA-256 checksum
        """
        if isinstance(content, dict):
            content_str = json.dumps(content, sort_keys=True)
        else:
            content_str = str(content)

        return hashlib.sha256(content_str.encode("utf-8")).hexdigest()

    def track_lineage(
        self,
        vault_id: VaultID,
        chain_id: Optional[str] = None
    ) -> LineageChain:
        """
        Add VaultID to lineage tracking.

        Args:
            vault_id: VaultID to track
            chain_id: Optional chain ID (defaults to domain/module)

        Returns:
            LineageChain containing the VaultID
        """
        if chain_id is None:
            chain_id = f"{vault_id.domain}/{vault_id.module}"

        if chain_id not in self.lineage_chains:
            self.lineage_chains[chain_id] = LineageChain(chain_id=chain_id)

        chain = self.lineage_chains[chain_id]
        chain.append(vault_id)
        return chain

    def get_lineage_chain(self, chain_id: str) -> Optional[LineageChain]:
        """
        Retrieve a lineage chain.

        Args:
            chain_id: Chain identifier

        Returns:
            LineageChain or None if not found
        """
        return self.lineage_chains.get(chain_id)

    def log_session(
        self,
        session_id: str,
        event_type: str,
        payload: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Log a session event for continuity tracking.

        Args:
            session_id: Session identifier
            event_type: Type of event (start, end, checkpoint)
            payload: Optional event payload

        Returns:
            Session log entry
        """
        entry = {
            "session_id": session_id,
            "vault_id": self.vault_id,
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "payload": payload or {}
        }
        self.session_log.append(entry)
        return entry

    def get_artifact_by_id(self, artifact_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve artifact by ID.

        Args:
            artifact_id: Artifact identifier

        Returns:
            Artifact dictionary or None if not found
        """
        for artifact in self.artifacts:
            if artifact["artifact_id"] == artifact_id:
                return artifact
        return None

    def verify_artifact_integrity(self, artifact_id: str) -> bool:
        """
        Verify artifact checksum integrity.

        Args:
            artifact_id: Artifact identifier

        Returns:
            True if checksum matches, False otherwise
        """
        artifact = self.get_artifact_by_id(artifact_id)
        if not artifact:
            return False

        expected_checksum = artifact["checksum"]
        actual_checksum = self.generate_checksum(artifact["content"])
        return expected_checksum == actual_checksum

    def get_summary(self) -> Dict[str, Any]:
        """
        Get vault summary statistics.

        Returns:
            Dictionary with counts and metadata
        """
        artifact_types = {}
        for artifact in self.artifacts:
            atype = artifact["artifact_type"]
            artifact_types[atype] = artifact_types.get(atype, 0) + 1

        return {
            "vault_id": self.vault_id,
            "total_artifacts": len(self.artifacts),
            "artifact_types": artifact_types,
            "lineage_chains": len(self.lineage_chains),
            "session_events": len(self.session_log)
        }

    def export_state(self) -> Dict[str, Any]:
        """
        Export complete vault state for persistence.

        Returns:
            Dictionary with all vault data
        """
        return {
            "vault_id": self.vault_id,
            "artifacts": self.artifacts,
            "lineage_chains": {
                chain_id: chain.to_dict()
                for chain_id, chain in self.lineage_chains.items()
            },
            "session_log": self.session_log,
            "exported_at": datetime.utcnow().isoformat() + "Z"
        }


def create_vault_id(
    domain: str,
    module: str,
    version: str,
    predecessor: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> VaultID:
    """
    Create a VaultID with automatic checksum.

    Args:
        domain: Top-level domain
        module: Module name
        version: Semantic version
        predecessor: Optional predecessor VaultID URI
        metadata: Additional context

    Returns:
        VaultID with computed checksum
    """
    vault_id = VaultID(
        domain=domain,
        module=module,
        version=version,
        predecessor=predecessor,
        metadata=metadata
    )

    # Compute checksum of VaultID record
    vault_dict = vault_id.to_dict()
    vault_dict.pop("checksum", None)  # Remove checksum field before hashing
    checksum_content = json.dumps(vault_dict, sort_keys=True)
    vault_id.checksum = hashlib.sha256(checksum_content.encode("utf-8")).hexdigest()

    return vault_id
