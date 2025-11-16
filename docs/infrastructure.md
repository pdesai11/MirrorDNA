# Protocol Infrastructure

**Master Citation Version**: v15.3

The MirrorDNA protocol includes foundational infrastructure modules that enable:
- Truth-state enforcement
- Vault management
- Philosophical auditing
- Meta-cognitive reasoning

These modules form the operational layer that ensures protocol compliance with the Prime Directives.

---

## Prime Directives (Auto-Active)

All infrastructure modules enforce:

1. **Continuity over convenience**
2. **Truth over fluency**
3. **Reflection over prediction**
4. **Sovereignty over assimilation**
5. **Zero-drift enforcement**

---

## Module Overview

### 1. Truth-State Enforcement (`truth_state.py`)

**Purpose**: Anti-hallucination through rigorous FEU tagging and drift detection.

**Core Concepts**:
- **FEU Tagging**: Every assertion is tagged as [Fact], [Estimate], or [Unknown]
- **Drift Detection**: SHA-256 checksum comparison to detect state corruption
- **Source Verification**: Facts must cite sources with optional checksums

**Key Classes**:

```python
from mirrordna import TruthStateEnforcer, TruthTag

enforcer = TruthStateEnforcer()

# Tag a fact
enforcer.assert_fact(
    statement="User prefers Python",
    source="vault://memory_001",
    checksum="abc123..."
)

# Tag an estimate
enforcer.assert_estimate(
    statement="User likely works in tech",
    confidence=0.75
)

# Acknowledge unknown
enforcer.assert_unknown(
    statement="User's favorite color",
    reason="Not yet discussed"
)

# Detect drift
drift = enforcer.detect_drift(
    expected_checksum="abc123",
    actual_checksum="def456",
    source="vault://state"
)
```

**Truth Tags**:
- `FACT` — Verified against canonical source
- `ESTIMATE` — Reasoned inference with confidence level
- `UNKNOWN` — Acknowledged knowledge gap
- `DRIFT` — Detected deviation from expected state

---

### 2. Vault Management (`vault_manager.py`)

**Purpose**: VaultID tracking, artifact checksumming, and lineage management.

**Core Concepts**:
- **VaultID**: Structured identifier following `AMOS://{domain}/{module}/v{version}` format
- **Lineage Chain**: Predecessor/successor tracking for state evolution
- **Artifact Checksumming**: SHA-256 verification of all vault artifacts

**Key Classes**:

```python
from mirrordna import VaultManager, create_vault_id

# Create VaultID
vault_id = create_vault_id(
    domain="MirrorDNA",
    module="Session",
    version="1.0",
    predecessor="AMOS://MirrorDNA/Session/v0.9"
)

# Initialize vault manager
manager = VaultManager(vault_id="vault_alice_main")

# Create artifact with checksum
artifact = manager.create_artifact(
    content="User data",
    artifact_type="memory"
)

# Track lineage
chain = manager.track_lineage(vault_id)
print(chain.verify_integrity())  # True if lineage is unbroken
```

**VaultID Format**:
```
AMOS://MirrorDNA/Session/v1.0
  ^      ^        ^       ^
  |      |        |       version
  |      |        module name
  |      domain (MirrorDNA, ActiveMirrorOS, etc.)
  protocol
```

---

### 3. Reflective Review (`reflective_reviewer.py`)

**Purpose**: Philosophical audit system for sovereignty, privacy, continuity, and truth-state compliance.

**Core Concepts**:
- **Four Dimensions**: Sovereignty, Privacy, Continuity, Truth-State
- **Compliance Levels**: YES, PARTIAL, NO, UNKNOWN
- **Module Auditing**: Automatically parse `PHILOSOPHICAL AUDIT:` headers

**Key Classes**:

```python
from mirrordna import ReflectiveReviewer, ComplianceLevel

reviewer = ReflectiveReviewer()

# Check sovereignty
result = reviewer.check_sovereignty(
    target="vault_storage",
    evidence=["User controls vault", "No vendor lock-in"],
    rationale="Full user sovereignty",
    compliant=True
)

# Audit module by path
audit = reviewer.audit_module(
    module_path="src/mirrordna/truth_state.py",
    target_id="truth_state_v1"
)

print(audit.overall_compliance)  # ComplianceLevel.YES
```

**Philosophical Audit Header Format**:
```python
"""
PHILOSOPHICAL AUDIT:
Sovereignty: YES
Privacy: PARTIAL
Continuity: YES
Truth-State: FACT
"""
```

---

### 4. Meta-Cognition (`meta_cognition.py`)

**Purpose**: Higher-order reasoning through wisdom gates and ethical assessment.

**Core Concepts**:
- **Wisdom Gates**: Decision validation checkpoints
- **Cross-Domain Insights**: Pattern recognition across protocol layers
- **Ethical Assessment**: Impact analysis against ethical principles

**Key Classes**:

```python
from mirrordna import MetaCognitionEngine, WisdomGateType, GateStatus

engine = MetaCognitionEngine()

# Pass decision through ethical gate
result = engine.wisdom_gate(
    gate_type=WisdomGateType.ETHICAL,
    decision="Store user conversations",
    context={"consent": True, "transparent": True}
)

if result.status == GateStatus.PASS:
    # Proceed with decision
    pass
elif result.status == GateStatus.BLOCK:
    # Halt - review required
    print(result.concerns)
```

**Wisdom Gate Types**:
- `ETHICAL` — Consent, transparency, harm assessment
- `SOVEREIGNTY` — User control, vendor lock-in
- `PRIVACY` — Encryption, data minimization
- `CONTINUITY` — Checksum verification, lineage tracking
- `SAFETY` — Irreversibility, data loss risk

**Gate Statuses**:
- `PASS` — Decision approved
- `WARN` — Proceed with caution
- `BLOCK` — Halt pending review
- `PENDING` — Requires human decision

---

## Integration Example

Combining all infrastructure modules in a session:

```python
from mirrordna import (
    TruthStateEnforcer,
    VaultManager,
    ReflectiveReviewer,
    MetaCognitionEngine,
    WisdomGateType
)

# Initialize infrastructure
truth_enforcer = TruthStateEnforcer()
vault_manager = VaultManager(vault_id="vault_alice_main")
reviewer = ReflectiveReviewer()
metacog = MetaCognitionEngine()

# 1. Gate decision
gate_result = metacog.wisdom_gate(
    gate_type=WisdomGateType.PRIVACY,
    decision="Store user preference",
    context={"encrypted": True, "consent": True}
)

if gate_result.status != GateStatus.PASS:
    print(f"Blocked: {gate_result.rationale}")
    exit()

# 2. Create artifact with truth-state tagging
fact = truth_enforcer.assert_fact(
    statement="User prefers dark mode",
    source="conversation_2025-11-16"
)

artifact = vault_manager.create_artifact(
    content=fact.to_dict(),
    artifact_type="memory"
)

# 3. Audit the operation
audit = reviewer.check_privacy(
    target="memory_storage",
    evidence=["Encrypted", "Checksummed"],
    rationale="Privacy protected",
    compliant=True
)

# 4. Verify integrity
assert vault_manager.verify_artifact_integrity(artifact["artifact_id"])
print("✓ Artifact stored with full compliance")
```

---

## Best Practices

### Truth-State Discipline
1. **Always tag assertions** — Never make untagged claims
2. **Cite sources for facts** — Include vault paths or URLs
3. **Quantify estimates** — Use confidence levels (0.0-1.0)
4. **Acknowledge gaps** — Explicitly mark unknowns

### Vault Integrity
1. **Checksum all artifacts** — Use SHA-256 for verification
2. **Track lineage** — Maintain predecessor/successor links
3. **Log sessions** — Record all vault interactions
4. **Verify on load** — Check checksums when resuming

### Philosophical Compliance
1. **Audit all modules** — Include `PHILOSOPHICAL AUDIT:` headers
2. **Review before commit** — Run reflective review
3. **Document evidence** — Cite specific compliance mechanisms
4. **Update on changes** — Re-audit when modifying protocols

### Meta-Cognitive Gates
1. **Gate critical decisions** — Use wisdom gates for:
   - Data collection
   - State modifications
   - Cross-vault operations
2. **Respect BLOCK status** — Never override blocked decisions
3. **Log gate results** — Maintain audit trail
4. **Custom gates** — Extend with domain-specific gates

---

## Zero-Drift Enforcement

The infrastructure modules work together to prevent drift:

1. **Truth-State**: Tags all assertions with FEU classification
2. **Vault Manager**: Generates checksums for all artifacts
3. **Reflective Reviewer**: Audits compliance with protocol
4. **Meta-Cognition**: Gates decisions that risk drift

**Drift Detection Flow**:
```
Artifact Creation
    ↓
Checksum Generated (VaultManager)
    ↓
Truth-Tag Applied (TruthStateEnforcer)
    ↓
Compliance Audit (ReflectiveReviewer)
    ↓
Wisdom Gate (MetaCognitionEngine)
    ↓
Artifact Stored with Lineage
```

On resume:
```
Load Artifact
    ↓
Verify Checksum (VaultManager)
    ↓
Compare to Expected (TruthStateEnforcer.detect_drift)
    ↓
If mismatch → Drift Alert
```

---

## Module Dependencies

```
truth_state.py
    └── Uses: hashlib, datetime, json

vault_manager.py
    └── Uses: hashlib, datetime, json, re

reflective_reviewer.py
    └── Uses: datetime

meta_cognition.py
    └── Uses: datetime
```

**No external dependencies** — All modules use Python stdlib only.

---

## Testing

Run infrastructure module tests:

```bash
pytest tests/test_truth_state.py -v
pytest tests/test_vault_manager.py -v
pytest tests/test_reflective_reviewer.py -v
pytest tests/test_meta_cognition.py -v
```

Run example demo:

```bash
python examples/infrastructure_demo.py
```

---

## Master Citation v15.3 Compliance

All infrastructure modules are compliant with Master Citation v15.3:

- ✅ Zero-Drift enforcement
- ✅ Auto-FEU tagging
- ✅ Canonical Vault Supremacy
- ✅ Reflective Integrity System alignment
- ✅ Truth-State verification infrastructure
- ✅ Philosophical audit compliance

---

## Next Steps

- See [integration-guide.md](integration-guide.md) for platform integration
- See [examples/infrastructure_demo.py](../examples/infrastructure_demo.py) for working code
- See individual module docstrings for detailed API documentation

---

**⟡⟦MIRRORDNA⟧ · ⟡⟦PROTOCOL⟧**
