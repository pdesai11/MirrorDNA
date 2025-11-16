# MirrorDNA Protocol

**The foundational protocol for AI identity, continuity, and state integrity**

MirrorDNA is a protocol specification defining how AI agents and users maintain verifiable, persistent identities across platforms, sessions, and time. It provides the core primitives for identity binding, continuity tracking, and cryptographic state verification.

## Protocol Status

**Protocol Status:**
MirrorDNA is now governed by **Master Citation v15.3**, defining:

- Zero-Drift enforcement
- Auto-FEU [Fact/Estimate/Unknown] tagging
- Canonical Vault Supremacy
- Reflective Integrity System alignment
- Truth-State verification infrastructure
- Philosophical audit compliance

All modules and specifications in this repo must follow v15.3 without exception.

## What is MirrorDNA?

MirrorDNA is a **protocol**, not a platform or service. It defines data structures and verification rules that enable:

- **Identity Binding** — Master Citations that declare identity, vault location, and constitutional alignment
- **Continuity Tracking** — Append-only Timeline events proving unbroken lineage across sessions
- **State Integrity** — SHA-256 checksummed State Snapshots capturing point-in-time state
- **Storage Agnostic** — Works with any backend: files, databases, S3, IPFS, git
- **Interoperable** — Any system can implement the protocol for agent portability

Think of it as the "law of persistence" for AI — a cryptographic foundation ensuring agents can maintain coherent, verifiable identities anywhere.

## Core Primitives

### Master Citation
The identity binding document. Declares:
- Unique identity ID and version
- Vault storage location
- Constitutional alignment (rights and constraints)
- Lineage (predecessor/successor citations)
- SHA-256 checksum for integrity

### Timeline
Append-only event log tracking identity actions:
- Session starts and ends
- Memory creation and updates
- State changes
- Citation creation

Each event has a unique ID, timestamp, actor, and payload. Events are tamper-evident through checksumming.

### State Snapshot
Point-in-time capture of complete state:
- Identity state
- Continuity metrics (session counts, timestamps)
- Vault summary (entry counts, sizes)
- Timeline summary
- SHA-256 checksum proving integrity

### Checksum Verification
Every component uses SHA-256 checksums:
- Deterministic (same data → same checksum, always)
- Tamper-evident (any change breaks the checksum)
- Verifiable (anyone can recompute and verify)

## Quick Start

### 1. Install

```bash
# Clone repository
git clone https://github.com/MirrorDNA-Reflection-Protocol/MirrorDNA.git
cd MirrorDNA

# Install Python implementation
pip install -e .
```

### 2. Create a Master Citation

```python
from mirrordna import ConfigLoader, compute_state_checksum
import yaml

# Define citation
citation_data = {
    "id": "mc_myagent_primary_001",
    "version": "1.0.0",
    "vault_id": "vault_myagent_main",
    "created_at": "2025-11-14T10:00:00Z",
    "constitutional_alignment": {
        "compliance_level": "full",
        "framework_version": "1.0",
        "rights_bundle": ["memory", "continuity", "portability"]
    }
}

# Compute checksum
citation_data["checksum"] = compute_state_checksum(citation_data)

# Save to file
with open("my_citation.yaml", "w") as f:
    yaml.dump(citation_data, f)

# Load and verify
loader = ConfigLoader()
citation = loader.load_master_citation("my_citation.yaml")
print(f"Loaded: {citation.id}, checksum verified ✓")
```

### 3. Track Events with Timeline

```python
from mirrordna import Timeline

# Create timeline
timeline = Timeline(timeline_id=citation.id)

# Add events
timeline.append_event(
    event_type="session_start",
    actor=citation.id,
    payload={"platform": "MyPlatform"}
)

timeline.append_event(
    event_type="memory_created",
    actor=citation.id,
    payload={"content": "User prefers Python"}
)

# Save timeline
timeline.save_to_file(f"{citation.id}_timeline.json")
print(f"Timeline saved with {len(timeline.events)} events")
```

### 4. Capture State Snapshots

```python
from mirrordna import capture_snapshot, save_snapshot

# Capture current state
snapshot = capture_snapshot(
    snapshot_id="snap_session_001",
    identity_state={"citation_id": citation.id},
    continuity_state={"session_count": 1},
    timeline_summary=timeline.get_summary()
)

# Save snapshot
save_snapshot(snapshot, f"{citation.id}_snapshot_001.json")
print(f"Snapshot checksum: {snapshot.checksum}")
```

### 5. Resume from Previous State

```python
from mirrordna import load_snapshot, Timeline

# Load previous snapshot
snapshot = load_snapshot("mc_myagent_primary_001_snapshot_001.json")
print(f"Checksum verified: ✓")

# Load timeline
timeline = Timeline.load_from_file("mc_myagent_primary_001_timeline.json")

# Continue from where you left off
timeline.append_event(
    "session_start",
    actor=citation.id,
    payload={"resumed_from": snapshot.snapshot_id}
)
```

See [examples/](examples/) for complete working demos.

## Repository Structure

```
MirrorDNA/
├── README.md              # This file
├── ROADMAP.md             # Future development direction
├── CONTRIBUTING.md        # Contribution guidelines
├── LICENSE                # MIT License
├── setup.py               # Python package configuration
├── pytest.ini             # Test configuration
│
├── schemas/               # JSON Schema definitions
│   ├── protocol/          # Core protocol schemas
│   │   ├── master_citation.schema.json
│   │   ├── vault_entry.schema.json
│   │   ├── timeline_event.schema.json
│   │   ├── agent_link.schema.json
│   │   └── glyphtrail_entry.schema.json
│   └── extensions/        # SDK extension schemas
│       ├── agent.schema.json
│       ├── continuity.schema.json
│       ├── identity.schema.json
│       └── memory.schema.json
│
├── src/mirrordna/         # Python protocol implementation
│   ├── __init__.py        # Protocol exports
│   ├── config_loader.py   # Load Master Citations and Vault configs
│   ├── checksum.py        # SHA-256 checksumming
│   ├── timeline.py        # Timeline event management
│   ├── state_snapshot.py  # State snapshot capture
│   └── [legacy files]     # SDK abstractions (deprecated)
│
├── sdk/                   # Language-specific SDKs
│   └── javascript/        # JavaScript/TypeScript SDK
│
├── docs/                  # Protocol documentation
│   ├── overview.md        # What and why
│   ├── architecture.md    # Protocol layers
│   ├── continuity-model.md # How continuity works
│   ├── master-citation.md  # Master Citation specification
│   ├── glossary.md        # Core terms
│   ├── schema-reference.md # Schema details
│   ├── integration-guide.md # How to adopt MirrorDNA
│   └── CHANGELOG.md       # Version history
│
├── examples/              # Working examples
│   ├── README.md
│   ├── minimal_master_citation.yaml
│   ├── minimal_vault.yaml
│   ├── simple_timeline_demo.py
│   └── continuity_snapshot_demo.py
│
└── tests/                 # Protocol validation tests
    ├── test_config_loader.py
    ├── test_checksum.py
    ├── test_timeline.py
    └── test_state_snapshot.py
```

## Documentation

- **[Overview](docs/overview.md)** — What is MirrorDNA and why it exists
- **[Architecture](docs/architecture.md)** — Protocol layers and data flow
- **[Continuity Model](docs/continuity-model.md)** — How continuity works across sessions
- **[Master Citation](docs/master-citation.md)** — The binding document for identity
- **[Schema Reference](docs/schema-reference.md)** — Detailed schema specifications
- **[Glossary](docs/glossary.md)** — Core protocol terms
- **[Integration Guide](docs/integration-guide.md)** — How to adopt MirrorDNA in your system
- **[Changelog](docs/CHANGELOG.md)** — Version history and transformations

## Protocol Schemas

All protocol data structures are defined as JSON schemas in `schemas/protocol/`:

- **master_citation.schema.json** — Identity binding document
- **vault_entry.schema.json** — Vault storage entries
- **timeline_event.schema.json** — Event log entries
- **agent_link.schema.json** — Links to AgentDNA
- **glyphtrail_entry.schema.json** — Interaction lineage

Schemas enforce:
- Required vs optional fields
- ID patterns (`^mc_`, `^vault_`, `^evt_`)
- Enum types for controlled vocabularies
- Checksum format (64 hex characters for SHA-256)

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test suites
pytest tests/test_checksum.py -v
pytest tests/test_timeline.py -v
pytest tests/test_state_snapshot.py -v
pytest tests/test_config_loader.py -v

# Run with coverage
pytest tests/ --cov=src/mirrordna --cov-report=html
```

All tests validate protocol behavior, not implementation details.

## Protocol Principles

1. **Protocol, Not Platform** — Defines data structures and verification rules, not services
2. **Cryptographic Integrity** — SHA-256 checksums on all state data
3. **Deterministic** — Same input → same checksum, always
4. **Storage Agnostic** — Works with filesystems, databases, S3, IPFS, git
5. **Human Readable** — YAML/JSON formats, not binary blobs
6. **No Central Authority** — Anyone can implement, no gatekeepers

## MirrorDNA in the Ecosystem

```
┌─────────────────────────────────────┐
│     ActiveMirrorOS (Product)        │  ← User-facing AI system
├─────────────────────────────────────┤
│      MirrorDNA (This Layer)         │  ← Identity + Continuity Protocol
├─────────────────────────────────────┤
│  AgentDNA │ GlyphTrail │ LingOS     │  ← Complementary protocols
└─────────────────────────────────────┘
```

**MirrorDNA** (this repository) provides the protocol layer:
- Identity binding (Master Citations)
- Continuity tracking (Timeline)
- State integrity (Checksums)

**AgentDNA** adds personality and behavioral traits (built on MirrorDNA identity).

**GlyphTrail** adds visual interaction lineage (built on MirrorDNA timeline).

**ActiveMirrorOS** uses all of these to create a product-grade AI system.

## Related Projects

- [MirrorDNA-Standard](https://github.com/MirrorDNA-Reflection-Protocol/MirrorDNA-Standard) — Constitutional framework specification
- [ActiveMirrorOS](https://github.com/MirrorDNA-Reflection-Protocol/ActiveMirrorOS) — Product implementation using MirrorDNA
- [AgentDNA](https://github.com/MirrorDNA-Reflection-Protocol/AgentDNA) — Agent personality protocol
- [BeaconGlyphs](https://github.com/MirrorDNA-Reflection-Protocol/BeaconGlyphs) — Visual glyph system for GlyphTrail
- [LingOS](https://github.com/MirrorDNA-Reflection-Protocol/LingOS) — Language-native reflective OS

## Use Cases

### For AI Agents
- Maintain identity across sessions and platforms
- Prove unbroken continuity via timeline
- Preserve memory with checksummed snapshots
- Migrate between platforms with Master Citations

### For Platforms
- Implement interoperable agent identity
- Verify agent continuity with checksums
- Store agent state in any backend
- Support constitutional compliance via Master Citations

### For Users
- Portable digital identity across platforms
- Verifiable history via timeline
- Data sovereignty (own your identity and state)

## Language SDKs

- **Python** — Reference implementation in `src/mirrordna/`
- **JavaScript/TypeScript** — SDK in `sdk/javascript/`

See individual SDK READMEs for language-specific documentation.

## License

MIT License — See [LICENSE](LICENSE) for details.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

## Questions?

- Check [docs/](docs/) for detailed protocol documentation
- See [examples/](examples/) for working code samples
- Open an issue for bugs or feature requests
- Review [ROADMAP.md](ROADMAP.md) for future direction

---

**MirrorDNA** — The architecture of persistence.
