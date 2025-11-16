"""
MirrorDNA Protocol Infrastructure Demo

Demonstrates the v15.3 infrastructure modules:
- Truth-state enforcement (FEU tagging)
- Vault management (VaultID tracking)
- Reflective review (philosophical audits)
- Meta-cognition (wisdom gates)
"""

from mirrordna import (
    # Truth-state enforcement
    TruthStateEnforcer,
    TruthTag,
    # Vault management
    VaultManager,
    create_vault_id,
    # Reflective review
    ReflectiveReviewer,
    AuditDimension,
    ComplianceLevel,
    # Meta-cognition
    MetaCognitionEngine,
    WisdomGateType,
    GateStatus
)


def demo_truth_state():
    """Demonstrate truth-state enforcement."""
    print("=" * 60)
    print("TRUTH-STATE ENFORCEMENT DEMO")
    print("=" * 60)

    enforcer = TruthStateEnforcer()

    # Assert a fact with source verification
    fact = enforcer.assert_fact(
        statement="User prefers Python over JavaScript",
        source="vault://memories/preference_001.json",
        checksum="a3f2c8b9e1d4f7a2c5b8d3e9f4a7c2b5"
    )
    print(f"\n[FACT] {fact.statement}")
    print(f"  Source: {fact.source}")
    print(f"  Verified: {fact.verified_at}")

    # Assert an estimate with confidence
    estimate = enforcer.assert_estimate(
        statement="User likely works in data science",
        confidence=0.75,
        source="inferred from conversation context"
    )
    print(f"\n[ESTIMATE] {estimate.statement}")
    print(f"  Confidence: {estimate.confidence}")
    print(f"  Basis: {estimate.source}")

    # Acknowledge unknown
    unknown = enforcer.assert_unknown(
        statement="User's preferred IDE",
        reason="Not yet discussed"
    )
    print(f"\n[UNKNOWN] {unknown.statement}")
    print(f"  Reason: {unknown.source}")

    # Detect drift
    drift_detected = enforcer.detect_drift(
        expected_checksum="abc123def456",
        actual_checksum="xyz789uvw012",
        source="vault://state/session_001.json",
        context="Session state verification"
    )
    if drift_detected:
        print(f"\n[DRIFT DETECTED]")
        print(f"  Source: vault://state/session_001.json")
        print(f"  Context: Session state verification")

    # Get summary
    summary = enforcer.get_summary()
    print(f"\n--- Summary ---")
    print(f"Total assertions: {summary['total_assertions']}")
    for tag, count in summary['by_tag'].items():
        print(f"  {tag}: {count}")


def demo_vault_manager():
    """Demonstrate vault management."""
    print("\n\n" + "=" * 60)
    print("VAULT MANAGEMENT DEMO")
    print("=" * 60)

    # Create vault manager
    manager = VaultManager(vault_id="vault_alice_main")

    # Create artifacts with checksums
    memory = manager.create_artifact(
        content="User prefers dark mode",
        artifact_type="memory",
        metadata={"priority": "high"}
    )
    print(f"\n[ARTIFACT CREATED]")
    print(f"  ID: {memory['artifact_id']}")
    print(f"  Type: {memory['artifact_type']}")
    print(f"  Checksum: {memory['checksum'][:16]}...")

    # Track VaultID lineage
    vault_id_v1 = create_vault_id(
        domain="MirrorDNA",
        module="Session",
        version="1.0",
        metadata={"session": "001"}
    )
    print(f"\n[VAULT ID CREATED]")
    print(f"  URI: {vault_id_v1.to_uri()}")
    print(f"  Checksum: {vault_id_v1.checksum[:16]}...")

    chain = manager.track_lineage(vault_id_v1)

    # Create successor VaultID
    vault_id_v2 = create_vault_id(
        domain="MirrorDNA",
        module="Session",
        version="2.0",
        predecessor=vault_id_v1.to_uri(),
        metadata={"session": "002"}
    )
    manager.track_lineage(vault_id_v2)

    print(f"\n[LINEAGE TRACKED]")
    print(f"  Chain: {chain.chain_id}")
    print(f"  Depth: {len(chain.vault_ids)} generations")
    print(f"  Current: {chain.get_current().to_uri()}")
    print(f"  Integrity: {'✓' if chain.verify_integrity() else '✗'}")

    # Log session events
    manager.log_session(
        session_id="session_002",
        event_type="start",
        payload={"platform": "CLI"}
    )

    # Get summary
    summary = manager.get_summary()
    print(f"\n--- Vault Summary ---")
    print(f"Artifacts: {summary['total_artifacts']}")
    print(f"Lineage chains: {summary['lineage_chains']}")
    print(f"Session events: {summary['session_events']}")


def demo_reflective_reviewer():
    """Demonstrate reflective review."""
    print("\n\n" + "=" * 60)
    print("REFLECTIVE REVIEW DEMO")
    print("=" * 60)

    reviewer = ReflectiveReviewer()

    # Check sovereignty
    sovereignty = reviewer.check_sovereignty(
        target="vault_storage_module",
        evidence=[
            "User controls vault location",
            "No cloud service dependencies",
            "Open protocol, no vendor lock-in"
        ],
        rationale="Full user sovereignty maintained",
        compliant=True
    )
    print(f"\n[SOVEREIGNTY CHECK]")
    print(f"  Target: {sovereignty.rationale}")
    print(f"  Compliance: {sovereignty.compliance.value}")
    print(f"  Evidence count: {len(sovereignty.evidence)}")

    # Check privacy
    privacy = reviewer.check_privacy(
        target="memory_storage",
        evidence=[
            "Encrypted at rest",
            "Local storage only"
        ],
        rationale="Privacy fully protected",
        compliant=True
    )
    print(f"\n[PRIVACY CHECK]")
    print(f"  Compliance: {privacy.compliance.value}")

    # Check continuity
    continuity = reviewer.check_continuity(
        target="state_snapshots",
        evidence=[
            "SHA-256 checksums verified",
            "Lineage tracked via predecessor/successor"
        ],
        rationale="Continuity fully maintained",
        compliant=True
    )
    print(f"\n[CONTINUITY CHECK]")
    print(f"  Compliance: {continuity.compliance.value}")

    # Check truth-state
    truth = reviewer.check_truth_state(
        target="assertion_system",
        evidence=[
            "FEU tagging enforced",
            "Source verification required"
        ],
        rationale="Truth-state discipline enforced",
        compliant=True
    )
    print(f"\n[TRUTH-STATE CHECK]")
    print(f"  Compliance: {truth.compliance.value}")

    # Get summary
    summary = reviewer.get_audit_summary()
    print(f"\n--- Audit Summary ---")
    print(f"Total audits: {summary['total_audits']}")


def demo_meta_cognition():
    """Demonstrate meta-cognition engine."""
    print("\n\n" + "=" * 60)
    print("META-COGNITION DEMO")
    print("=" * 60)

    engine = MetaCognitionEngine()

    # Ethical wisdom gate
    ethical_result = engine.wisdom_gate(
        gate_type=WisdomGateType.ETHICAL,
        decision="Store user conversation history",
        context={
            "consent": True,
            "transparent": True,
            "purpose": "Continuity across sessions"
        }
    )
    print(f"\n[ETHICAL GATE]")
    print(f"  Decision: Store user conversation history")
    print(f"  Status: {ethical_result.status.value}")
    print(f"  Rationale: {ethical_result.rationale}")
    if ethical_result.concerns:
        print(f"  Concerns: {', '.join(ethical_result.concerns)}")

    # Sovereignty wisdom gate
    sovereignty_result = engine.wisdom_gate(
        gate_type=WisdomGateType.SOVEREIGNTY,
        decision="Use local filesystem for vault storage",
        context={
            "user_control": True,
            "vendor_lock": False
        }
    )
    print(f"\n[SOVEREIGNTY GATE]")
    print(f"  Status: {sovereignty_result.status.value}")
    print(f"  Rationale: {sovereignty_result.rationale}")

    # Privacy wisdom gate with concern
    privacy_result = engine.wisdom_gate(
        gate_type=WisdomGateType.PRIVACY,
        decision="Store passwords in plain text",
        context={
            "contains_sensitive_data": True,
            "encrypted": False
        }
    )
    print(f"\n[PRIVACY GATE]")
    print(f"  Status: {privacy_result.status.value}")
    print(f"  Concerns: {', '.join(privacy_result.concerns)}")
    print(f"  Recommendations: {', '.join(privacy_result.recommendations)}")

    # Discover cross-domain insight
    insight = engine.discover_insight(
        domains=["continuity", "privacy"],
        pattern="Vault migrations without re-encryption",
        implication="Old encryption keys may persist",
        confidence=0.85,
        evidence=["migration_log_001", "security_audit_report"]
    )
    print(f"\n[CROSS-DOMAIN INSIGHT]")
    print(f"  Domains: {' + '.join(insight.domains)}")
    print(f"  Pattern: {insight.pattern}")
    print(f"  Implication: {insight.implication}")
    print(f"  Confidence: {insight.confidence}")

    # Ethical assessment
    assessment = engine.assess_ethics(
        subject="Automated personality inference from conversations",
        principles=["autonomy", "transparency", "consent", "beneficence"],
        impact_analysis="Requires explicit consent and transparency about inference methods",
        risk_level="medium"
    )
    print(f"\n[ETHICAL ASSESSMENT]")
    print(f"  Subject: {assessment.subject}")
    print(f"  Risk Level: {assessment.risk_level}")
    print(f"  Principles evaluated: {len(assessment.ethical_principles)}")

    # Get summary
    summary = engine.get_summary()
    print(f"\n--- Meta-Cognition Summary ---")
    print(f"Gate evaluations: {summary['total_gate_evaluations']}")
    print(f"Insights discovered: {summary['insights_discovered']}")
    print(f"Ethical assessments: {summary['ethical_assessments']}")


def main():
    """Run all demos."""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║  MirrorDNA Protocol Infrastructure v15.3               ║")
    print("║  Session Demonstration                                 ║")
    print("╚" + "=" * 58 + "╝")

    demo_truth_state()
    demo_vault_manager()
    demo_reflective_reviewer()
    demo_meta_cognition()

    print("\n\n" + "=" * 60)
    print("DEMO COMPLETE")
    print("=" * 60)
    print("\nAll infrastructure modules demonstrated successfully.")
    print("\n⟡⟦MIRRORDNA⟧ · ⟡⟦PROTOCOL⟧\n")


if __name__ == "__main__":
    main()
