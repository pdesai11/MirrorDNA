"""
Integration tests for complete MirrorDNA lifecycle.

Tests the full workflow: identity creation → session management →
memory operations → state snapshots → verification.
"""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime

from mirrordna import (
    IdentityManager,
    ConfigLoader,
    capture_snapshot,
    save_snapshot,
    load_snapshot
)
from mirrordna.continuity import ContinuityTracker
from mirrordna.memory import MemoryManager
from mirrordna.timeline import Timeline
from mirrordna.storage import JSONFileStorage


class TestFullLifecycle:
    """Test complete protocol lifecycle."""

    @pytest.fixture
    def temp_storage(self):
        """Create temporary storage directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def storage(self, temp_storage):
        """Create storage instance."""
        return JSONFileStorage(temp_storage)

    def test_complete_agent_lifecycle(self, storage, temp_storage):
        """Test complete agent lifecycle from creation to snapshot."""

        # Step 1: Create identity
        identity_manager = IdentityManager(storage=storage)
        identity = identity_manager.create_identity(
            identity_type="agent",
            metadata={"name": "TestAgent", "version": "1.0"}
        )

        assert identity["identity_type"] == "agent"
        assert "identity_id" in identity
        assert "_private_key" in identity

        identity_id = identity["identity_id"]
        private_key = identity["_private_key"]

        # Step 2: Verify identity persisted
        loaded_identity = identity_manager.get_identity(identity_id)
        assert loaded_identity is not None
        assert loaded_identity["identity_id"] == identity_id

        # Step 3: Sign and verify a claim
        claim = "I am TestAgent v1.0"
        signature = identity_manager.sign_claim(
            identity_id=identity_id,
            claim=claim,
            private_key=private_key
        )

        verified = identity_manager.verify_claim(
            identity_id=identity_id,
            claim=claim,
            signature=signature
        )

        assert verified is True

        # Step 4: Create continuity tracker and session
        continuity = ContinuityTracker(storage=storage)
        session1 = continuity.create_session(
            identity_id=identity_id,
            context={"purpose": "test_session"}
        )

        assert session1["session_id"] is not None
        assert session1["identity_id"] == identity_id

        session1_id = session1["session_id"]

        # Step 5: Create child session
        session2 = continuity.create_session(
            identity_id=identity_id,
            parent_session_id=session1_id,
            context={"purpose": "child_session"}
        )

        assert session2["parent_session_id"] == session1_id

        # Step 6: Verify session lineage
        lineage = continuity.get_session_lineage(session2["session_id"])
        assert len(lineage) == 2
        assert lineage[0]["session_id"] == session1_id
        assert lineage[1]["session_id"] == session2["session_id"]

        # Step 7: Create memory manager and add memories
        memory_manager = MemoryManager(storage=storage, identity_id=identity_id)

        memory1 = memory_manager.write_memory(
            tier="short_term",
            content="First interaction with user",
            metadata={"importance": "high"}
        )

        memory2 = memory_manager.write_memory(
            tier="long_term",
            content="User prefers Python over JavaScript",
            metadata={"category": "preferences"}
        )

        # Step 8: Search memories
        results = memory_manager.search_memory("interaction", tier="short_term")
        assert len(results) > 0
        assert results[0]["content"] == "First interaction with user"

        # Step 9: Create timeline
        timeline = Timeline()
        timeline.append_event(
            event_type="identity_created",
            actor=identity_id,
            payload={"identity_type": "agent"}
        )
        timeline.append_event(
            event_type="session_started",
            actor=identity_id,
            payload={"session_id": session1_id}
        )

        events = timeline.export_events()
        assert len(events) == 2

        # Step 10: Create state snapshot
        snapshot = capture_snapshot(
            identity_state={
                "identity_id": identity_id,
                "identity_type": "agent"
            },
            continuity_state={
                "active_sessions": [session1_id, session2["session_id"]],
                "session_count": 2
            },
            vault_state={
                "total_memories": 2,
                "storage_path": str(temp_storage)
            }
        )

        assert snapshot.snapshot_id is not None
        assert snapshot.checksum is not None

        # Step 11: Save and load snapshot
        snapshot_file = temp_storage / "snapshot.json"
        save_snapshot(snapshot, snapshot_file, format="json")

        loaded_snapshot = load_snapshot(snapshot_file)
        assert loaded_snapshot.snapshot_id == snapshot.snapshot_id
        assert loaded_snapshot.checksum == snapshot.checksum

        # Step 12: End sessions
        continuity.end_session(session1_id)
        continuity.end_session(session2["session_id"])

        # Verify final state
        final_identity = identity_manager.get_identity(identity_id)
        assert final_identity is not None

        memories = memory_manager.read_memory(tier="short_term")
        assert len(memories) > 0

    def test_multi_agent_interaction(self, storage):
        """Test interaction between multiple agents."""

        identity_manager = IdentityManager(storage=storage)

        # Create two agents
        agent1 = identity_manager.create_identity(
            identity_type="agent",
            metadata={"name": "Agent1", "role": "assistant"}
        )

        agent2 = identity_manager.create_identity(
            identity_type="agent",
            metadata={"name": "Agent2", "role": "coordinator"}
        )

        # Create sessions for both
        continuity = ContinuityTracker(storage=storage)

        session1 = continuity.create_session(
            identity_id=agent1["identity_id"],
            context={"role": "processing"}
        )

        session2 = continuity.create_session(
            identity_id=agent2["identity_id"],
            context={"role": "coordination"}
        )

        # Create shared timeline
        timeline = Timeline()
        timeline.append_event(
            event_type="agent_interaction",
            actor=agent1["identity_id"],
            payload={
                "action": "send_message",
                "target": agent2["identity_id"],
                "message": "Task complete"
            }
        )

        timeline.append_event(
            event_type="agent_interaction",
            actor=agent2["identity_id"],
            payload={
                "action": "acknowledge",
                "source": agent1["identity_id"]
            }
        )

        # Verify interactions logged
        events = timeline.get_events_by_type("agent_interaction")
        assert len(events) == 2

        # Verify both identities exist
        assert identity_manager.get_identity(agent1["identity_id"]) is not None
        assert identity_manager.get_identity(agent2["identity_id"]) is not None

    def test_memory_tier_progression(self, storage):
        """Test memory progression through tiers."""

        identity_manager = IdentityManager(storage=storage)
        identity = identity_manager.create_identity(
            identity_type="agent",
            metadata={"name": "MemoryTestAgent"}
        )

        memory_manager = MemoryManager(
            storage=storage,
            identity_id=identity["identity_id"]
        )

        # Write to short-term
        memory1 = memory_manager.write_memory(
            tier="short_term",
            content="Recent conversation about weather"
        )

        # Access it multiple times
        for _ in range(5):
            memory_manager.increment_access_count(memory1["memory_id"], "short_term")

        # Write to long-term
        memory2 = memory_manager.write_memory(
            tier="long_term",
            content="User's hometown is San Francisco"
        )

        # Write episodic memory
        memory3 = memory_manager.write_memory(
            tier="episodic",
            content="First meeting with user on 2025-01-01"
        )

        # Verify all tiers have content
        short_term = memory_manager.read_memory(tier="short_term")
        long_term = memory_manager.read_memory(tier="long_term")
        episodic = memory_manager.read_memory(tier="episodic")

        assert len(short_term) > 0
        assert len(long_term) > 0
        assert len(episodic) > 0

        # Archive short-term memory
        memory_manager.archive_memory(memory1["memory_id"], "short_term")

        # Verify archived
        archived = memory_manager.read_memory(tier="short_term", include_archived=True)
        active = memory_manager.read_memory(tier="short_term", include_archived=False)

        assert len(archived) > len(active)

    def test_snapshot_comparison(self, temp_storage):
        """Test snapshot comparison functionality."""

        storage = JSONFileStorage(temp_storage)
        identity_manager = IdentityManager(storage=storage)

        # Create initial state
        identity = identity_manager.create_identity(
            identity_type="agent",
            metadata={"version": "1.0"}
        )

        # Snapshot 1
        snapshot1 = capture_snapshot(
            identity_state={"version": "1.0"},
            continuity_state={"sessions": 0},
            vault_state={"identities": 1}
        )

        # Create another identity (state change)
        identity2 = identity_manager.create_identity(
            identity_type="agent",
            metadata={"version": "1.0"}
        )

        # Snapshot 2
        snapshot2 = capture_snapshot(
            identity_state={"version": "1.0"},
            continuity_state={"sessions": 0},
            vault_state={"identities": 2}
        )

        # Snapshots should have different checksums
        assert snapshot1.checksum != snapshot2.checksum

        # Verify both can be saved and loaded
        save_snapshot(snapshot1, temp_storage / "snap1.json")
        save_snapshot(snapshot2, temp_storage / "snap2.json")

        loaded1 = load_snapshot(temp_storage / "snap1.json")
        loaded2 = load_snapshot(temp_storage / "snap2.json")

        assert loaded1.checksum == snapshot1.checksum
        assert loaded2.checksum == snapshot2.checksum
