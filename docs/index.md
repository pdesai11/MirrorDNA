# MirrorDNA Documentation Index

Welcome to the MirrorDNA documentation. This index will help you find what you need quickly.

## Getting Started

**New to MirrorDNA?** Start here:

1. **[README](../README.md)** — Quick overview and installation
2. **[Overview](overview.md)** — Core concepts and design philosophy (10 min read)
3. **[Integration Guide](integration-guide.md)** — Step-by-step integration (20 min read)
4. **[Examples](../examples/)** — Working code samples

## Core Documentation

### Conceptual

- **[Overview](overview.md)** — What MirrorDNA is and why it exists
  - Core concepts: Identity, Continuity, Memory, Agent DNA
  - Design philosophy and principles
  - How it fits in the ecosystem

### Technical

- **[Architecture](architecture.md)** — How MirrorDNA works internally
  - Component breakdown
  - Data flow diagrams
  - Storage layer design
  - Security considerations
  - Performance characteristics

- **[Protocol Infrastructure](infrastructure.md)** — Master Citation v15.3 infrastructure modules
  - Truth-state enforcement (FEU tagging)
  - Vault management (VaultID tracking, lineage)
  - Reflective review (philosophical audits)
  - Meta-cognition (wisdom gates, ethical assessment)

- **[Schema Reference](schema-reference.md)** — Detailed schema specifications
  - Identity schema
  - Continuity schema
  - Memory schema
  - Agent DNA schema
  - Validation rules

### Practical

- **[Integration Guide](integration-guide.md)** — How to use MirrorDNA in your application
  - Installation
  - Quick start examples
  - Advanced patterns
  - Custom storage backends
  - Testing

## Quick Reference

### Common Tasks

| Task | Documentation | Example |
|------|---------------|---------|
| Create an identity | [Integration Guide](integration-guide.md#step-1-create-an-identity) | [examples/basic_identity.py](../examples/) |
| Start a session | [Integration Guide](integration-guide.md#step-3-start-a-session) | [examples/basic_continuity.py](../examples/) |
| Save a memory | [Integration Guide](integration-guide.md#step-4-create-memories) | [examples/basic_memory.py](../examples/) |
| Define agent DNA | [Integration Guide](integration-guide.md#agent-dna-definition) | [examples/agent_dna_example.py](../examples/) |
| Validate schemas | [Schema Reference](schema-reference.md#validation) | [examples/validation_example.py](../examples/) |
| Use infrastructure modules | [Protocol Infrastructure](infrastructure.md) | [examples/infrastructure_demo.py](../examples/) |

### Schema Lookups

| Schema | Reference | Location |
|--------|-----------|----------|
| Identity | [Schema Ref](schema-reference.md#identity-schema) | [schemas/identity.schema.json](../schemas/) |
| Continuity | [Schema Ref](schema-reference.md#continuity-schema) | [schemas/continuity.schema.json](../schemas/) |
| Memory | [Schema Ref](schema-reference.md#memory-schema) | [schemas/memory.schema.json](../schemas/) |
| Agent DNA | [Schema Ref](schema-reference.md#agent-dna-schema) | [schemas/agent.schema.json](../schemas/) |

## By Role

### For Developers

**Building an app with MirrorDNA?**

1. Read: [Overview](overview.md) (concepts)
2. Follow: [Integration Guide](integration-guide.md) (implementation)
3. Reference: [Schema Reference](schema-reference.md) (when needed)
4. Copy: [Examples](../examples/) (working code)

### For Architects

**Designing a system using MirrorDNA?**

1. Read: [Overview](overview.md) (design philosophy)
2. Study: [Architecture](architecture.md) (internal design)
3. Review: [Schema Reference](schema-reference.md) (data contracts)
4. Consider: Integration patterns in [Integration Guide](integration-guide.md#integration-patterns)

### For Researchers

**Exploring identity and memory protocols?**

1. Start: [Overview](overview.md) (core concepts)
2. Deep dive: [Architecture](architecture.md) (implementation details)
3. Analyze: [Schema Reference](schema-reference.md) (data structures)
4. Experiment: [Examples](../examples/) (working implementations)

## Related Repositories

MirrorDNA is part of a larger ecosystem:

- **[Active MirrorOS](https://github.com/MirrorDNA-Reflection-Protocol/ActiveMirrorOS)** — Product-facing "intelligence that remembers"
- **[MirrorDNA-Standard](https://github.com/MirrorDNA-Reflection-Protocol/MirrorDNA-Standard)** — Constitutional spec and compliance tooling
- **[LingOS](https://github.com/MirrorDNA-Reflection-Protocol/LingOS)** — Language-native OS for reflective dialogue
- **[AgentDNA](https://github.com/MirrorDNA-Reflection-Protocol/AgentDNA)** — Agent personality and persistence schemas
- **[Glyphtrail](https://github.com/MirrorDNA-Reflection-Protocol/Glyphtrail)** — Interaction lineage and continuity logs
- **[TrustByDesign](https://github.com/MirrorDNA-Reflection-Protocol/TrustByDesign)** — Safety and governance framework
- **[BeaconGlyphs](https://github.com/MirrorDNA-Reflection-Protocol/BeaconGlyphs)** — Visual and symbolic glyph system

## Contributing

This is currently a private repository. If you have access and want to contribute, see the [README](../README.md#contributing) for guidelines.

## Questions?

- Check the documentation sections above
- Review [examples/](../examples/) for working code
- Open an issue on GitHub

---

**MirrorDNA** — The architecture of persistence.
