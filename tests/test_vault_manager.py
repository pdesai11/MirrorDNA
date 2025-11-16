"""
Tests for vault_manager.py module.
"""

import pytest
from mirrordna import (
    VaultID,
    LineageChain,
    VaultManager,
    create_vault_id
)


class TestVaultID:
    """Tests for VaultID dataclass."""

    def test_to_uri(self):
        """Convert VaultID to URI format."""
        vault_id = VaultID(
            domain="MirrorDNA",
            module="Session",
            version="1.0"
        )
        assert vault_id.to_uri() == "AMOS://MirrorDNA/Session/v1.0"

    def test_from_uri(self):
        """Parse URI into VaultID."""
        vault_id = VaultID.from_uri("AMOS://MirrorDNA/Session/v1.0")
        assert vault_id.domain == "MirrorDNA"
        assert vault_id.module == "Session"
        assert vault_id.version == "1.0"

    def test_from_uri_invalid(self):
        """Invalid URI raises ValueError."""
        with pytest.raises(ValueError, match="Invalid VaultID URI"):
            VaultID.from_uri("invalid://format")

    def test_to_dict(self):
        """Serialize to dictionary."""
        vault_id = VaultID(
            domain="MirrorDNA",
            module="Test",
            version="1.0"
        )
        d = vault_id.to_dict()
        assert d["uri"] == "AMOS://MirrorDNA/Test/v1.0"
        assert d["domain"] == "MirrorDNA"
        assert d["module"] == "Test"

    def test_with_predecessor(self):
        """VaultID with predecessor link."""
        vault_id = VaultID(
            domain="MirrorDNA",
            module="Test",
            version="2.0",
            predecessor="AMOS://MirrorDNA/Test/v1.0"
        )
        assert vault_id.predecessor == "AMOS://MirrorDNA/Test/v1.0"


class TestLineageChain:
    """Tests for LineageChain dataclass."""

    def test_append_first_vault_id(self):
        """Append first VaultID to empty chain."""
        chain = LineageChain(chain_id="test_chain")
        vault_id = VaultID(domain="Test", module="Mod", version="1.0")
        chain.append(vault_id)
        assert len(chain.vault_ids) == 1

    def test_append_with_valid_lineage(self):
        """Append VaultID with valid predecessor."""
        chain = LineageChain(chain_id="test_chain")
        v1 = VaultID(domain="Test", module="Mod", version="1.0")
        chain.append(v1)

        v2 = VaultID(
            domain="Test",
            module="Mod",
            version="2.0",
            predecessor=v1.to_uri()
        )
        chain.append(v2)
        assert len(chain.vault_ids) == 2

    def test_append_with_broken_lineage(self):
        """Broken lineage raises ValueError."""
        chain = LineageChain(chain_id="test_chain")
        v1 = VaultID(domain="Test", module="Mod", version="1.0")
        chain.append(v1)

        v2 = VaultID(
            domain="Test",
            module="Mod",
            version="2.0",
            predecessor="AMOS://Wrong/Predecessor/v0.0"
        )
        with pytest.raises(ValueError, match="Lineage break"):
            chain.append(v2)

    def test_get_current(self):
        """Get most recent VaultID."""
        chain = LineageChain(chain_id="test_chain")
        v1 = VaultID(domain="Test", module="Mod", version="1.0")
        v2 = VaultID(domain="Test", module="Mod", version="2.0", predecessor=v1.to_uri())
        chain.append(v1)
        chain.append(v2)

        current = chain.get_current()
        assert current.version == "2.0"

    def test_verify_integrity_valid(self):
        """Verify valid lineage chain."""
        chain = LineageChain(chain_id="test_chain")
        v1 = VaultID(domain="Test", module="Mod", version="1.0")
        v2 = VaultID(domain="Test", module="Mod", version="2.0", predecessor=v1.to_uri())
        chain.append(v1)
        chain.append(v2)

        assert chain.verify_integrity() is True


class TestVaultManager:
    """Tests for VaultManager class."""

    def test_create_artifact(self):
        """Create vault artifact with checksum."""
        manager = VaultManager(vault_id="vault_test_main")
        artifact = manager.create_artifact(
            content="Test content",
            artifact_type="memory"
        )
        assert artifact["vault_id"] == "vault_test_main"
        assert artifact["artifact_type"] == "memory"
        assert "checksum" in artifact
        assert len(artifact["checksum"]) == 64

    def test_generate_checksum_string(self):
        """Generate checksum from string."""
        manager = VaultManager(vault_id="vault_test")
        checksum = manager.generate_checksum("test")
        assert len(checksum) == 64
        assert isinstance(checksum, str)

    def test_generate_checksum_dict(self):
        """Generate checksum from dictionary."""
        manager = VaultManager(vault_id="vault_test")
        checksum = manager.generate_checksum({"key": "value"})
        assert len(checksum) == 64

    def test_track_lineage(self):
        """Track VaultID lineage."""
        manager = VaultManager(vault_id="vault_test")
        vault_id = VaultID(domain="Test", module="Mod", version="1.0")
        chain = manager.track_lineage(vault_id)

        assert chain.chain_id == "Test/Mod"
        assert len(chain.vault_ids) == 1

    def test_log_session(self):
        """Log session event."""
        manager = VaultManager(vault_id="vault_test")
        entry = manager.log_session(
            session_id="session_001",
            event_type="start"
        )
        assert entry["session_id"] == "session_001"
        assert entry["event_type"] == "start"
        assert len(manager.session_log) == 1

    def test_verify_artifact_integrity(self):
        """Verify artifact checksum integrity."""
        manager = VaultManager(vault_id="vault_test")
        artifact = manager.create_artifact(
            content="test",
            artifact_type="memory",
            artifact_id="mem_001"
        )

        # Should verify successfully
        assert manager.verify_artifact_integrity("mem_001") is True

        # Tamper with content
        artifact["content"] = "modified"
        assert manager.verify_artifact_integrity("mem_001") is False

    def test_get_summary(self):
        """Get vault summary."""
        manager = VaultManager(vault_id="vault_test")
        manager.create_artifact("test1", "memory")
        manager.create_artifact("test2", "snapshot")
        manager.create_artifact("test3", "memory")

        summary = manager.get_summary()
        assert summary["total_artifacts"] == 3
        assert summary["artifact_types"]["memory"] == 2
        assert summary["artifact_types"]["snapshot"] == 1


class TestHelperFunctions:
    """Tests for helper functions."""

    def test_create_vault_id(self):
        """Create VaultID with automatic checksum."""
        vault_id = create_vault_id(
            domain="MirrorDNA",
            module="Test",
            version="1.0"
        )
        assert vault_id.domain == "MirrorDNA"
        assert vault_id.checksum is not None
        assert len(vault_id.checksum) == 64
