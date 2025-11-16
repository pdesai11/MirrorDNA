# MirrorDNA Developer Guide

**Last Updated**: 2025-11-16
**Version**: 1.0.0 (Beta)

This guide provides comprehensive instructions for developing with and contributing to the MirrorDNA protocol.

---

## Table of Contents

1. [Development Environment Setup](#development-environment-setup)
2. [Project Structure](#project-structure)
3. [Core Concepts](#core-concepts)
4. [Development Workflow](#development-workflow)
5. [Testing](#testing)
6. [CLI Usage](#cli-usage)
7. [API Reference](#api-reference)
8. [Security Best Practices](#security-best-practices)
9. [Performance Optimization](#performance-optimization)
10. [Troubleshooting](#troubleshooting)

---

## Development Environment Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git
- Virtual environment tool (venv)

### Quick Setup

Use the automated setup script:

```bash
./scripts/setup.sh
```

This script will:
1. Check Python version
2. Create virtual environment
3. Install dependencies
4. Run tests to verify installation
5. Set up data directories

### Manual Setup

If you prefer manual setup:

```bash
# Clone repository
git clone https://github.com/MirrorDNA-Reflection-Protocol/MirrorDNA.git
cd MirrorDNA

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Verify installation
mirrordna --version
pytest tests/ -v
```

### Directory Structure

After setup, you'll have:

```
~/.mirrordna/
├── data/           # Storage for identities, sessions, memories
├── logs/           # Application logs
└── keys/           # Cryptographic keys (secure permissions)
```

---

## Project Structure

```
MirrorDNA/
├── src/mirrordna/              # Main package
│   ├── __init__.py             # Package exports
│   ├── checksum.py             # SHA-256 checksumming
│   ├── timeline.py             # Event timeline
│   ├── state_snapshot.py       # State capture
│   ├── config_loader.py        # Configuration loading
│   ├── identity.py             # Identity management
│   ├── crypto.py               # Cryptography (Ed25519)
│   ├── storage.py              # Storage abstraction
│   ├── continuity.py           # Session continuity
│   ├── memory.py               # Memory management
│   ├── validator.py            # Schema validation
│   ├── reflection.py           # Reflection engine
│   ├── agent_dna.py            # Agent DNA
│   ├── exceptions.py           # Custom exceptions
│   ├── logging.py              # Logging system
│   ├── cli.py                  # Command-line interface
│   ├── health.py               # Health checks
│   ├── security.py             # Security hardening
│   └── metrics.py              # Performance metrics
│
├── tests/                      # Test suite
│   ├── conftest.py             # pytest configuration
│   ├── test_checksum.py
│   ├── test_timeline.py
│   └── ...
│
├── schemas/                    # JSON schemas
│   ├── protocol/               # Core protocol schemas
│   └── extensions/             # Extension schemas
│
├── examples/                   # Usage examples
│   ├── basic_identity.py
│   ├── basic_continuity.py
│   └── ...
│
├── docs/                       # Documentation
│   ├── overview.md
│   ├── architecture.md
│   ├── developer-guide.md      # This file
│   └── ...
│
└── scripts/                    # Utility scripts
    ├── setup.sh                # Automated setup
    ├── quickstart.sh           # Demo script
    └── mirrordna               # CLI entry point
```

---

## Core Concepts

### 1. Master Citation

The **Master Citation** is the identity binding document that links an agent to its vault and configuration.

**Key Fields**:
- `id`: Unique identifier (pattern: `^mc_`)
- `version`: Protocol version
- `vault_id`: Associated vault identifier
- `checksum`: SHA-256 integrity checksum
- `created_at`: ISO 8601 timestamp

**Example**:
```yaml
id: mc_agent_001
version: 1.0.0
vault_id: vault_agent_001
created_at: 2025-01-01T00:00:00Z
checksum: abc123...
metadata:
  name: My Agent
```

### 2. Identity Management

Identities are cryptographically-signed entities with Ed25519 keypairs.

**Identity Types**:
- `user`: Human users
- `agent`: AI agents
- `system`: System processes

**Best Practices**:
- Never commit private keys to version control
- Store private keys in environment variables or secure key managers
- Rotate keys regularly (recommended: every 90 days)

### 3. Checksum Verification

All state is checksummed with SHA-256 for integrity verification.

**Deterministic Hashing**:
- Canonical JSON (sorted keys, no whitespace)
- UTF-8 encoding
- Consistent across platforms

### 4. Storage Abstraction

MirrorDNA uses a storage adapter pattern for flexibility.

**Default**: JSONFileStorage
**Future**: Support for databases, S3, IPFS, git

### 5. Timeline Events

Append-only event log for lineage tracking.

**Event Structure**:
- `id`: Unique event ID
- `timestamp`: ISO 8601 timestamp
- `event_type`: Event category
- `actor`: Who triggered the event
- `payload`: Event data

---

## Development Workflow

### 1. Creating a Feature Branch

```bash
git checkout -b feature/my-new-feature
```

### 2. Making Changes

Follow these guidelines:
- Write clear, descriptive commit messages
- Add tests for new functionality
- Update documentation
- Run tests before committing

### 3. Running Tests

```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_checksum.py -v

# With coverage
pytest tests/ --cov=src/mirrordna --cov-report=html

# Specific test function
pytest tests/test_checksum.py::test_compute_file_checksum -v
```

### 4. Code Style

MirrorDNA follows PEP 8 style guidelines:

```bash
# Format code
black src/mirrordna/

# Sort imports
isort src/mirrordna/

# Type checking
mypy src/mirrordna/
```

### 5. Committing Changes

```bash
git add .
git commit -m "feat: Add new feature X"
git push origin feature/my-new-feature
```

**Commit Message Format**:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Test additions/changes
- `refactor:` Code refactoring
- `chore:` Build/tooling changes

---

## Testing

### Test Structure

```
tests/
├── conftest.py              # Shared fixtures
├── test_checksum.py         # Unit tests for checksum module
├── test_identity.py         # Unit tests for identity module
└── integration/             # Integration tests (future)
    └── test_full_lifecycle.py
```

### Writing Tests

Example test:

```python
def test_create_identity():
    """Test identity creation."""
    manager = IdentityManager()

    identity = manager.create_identity(
        identity_type="agent",
        metadata={"name": "Test Agent"}
    )

    # Assertions
    assert identity["identity_type"] == "agent"
    assert "identity_id" in identity
    assert "public_key" in identity
    assert "_private_key" in identity

    # Verify saved to storage
    loaded = manager.get_identity(identity["identity_id"])
    assert loaded is not None
```

### Test Fixtures

```python
# In conftest.py
import pytest
from pathlib import Path
import tempfile

@pytest.fixture
def temp_storage_dir():
    """Create temporary storage directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)
```

### Running Specific Tests

```bash
# By marker (if defined)
pytest -m unit

# By pattern
pytest -k "identity"

# With verbose output
pytest -vv
```

---

## CLI Usage

### Basic Commands

```bash
# Show help
mirrordna --help

# Create an identity
mirrordna identity create --type agent --metadata '{"name":"MyAgent"}'

# Validate configuration
mirrordna config validate --master-citation master_citation.yaml

# Compute checksum
mirrordna checksum compute --file myfile.txt

# Create snapshot
mirrordna snapshot create --output snapshot.json

# Health check
mirrordna health --verbose
```

### Logging Configuration

```bash
# Set log level
mirrordna --log-level DEBUG identity create --type agent

# Log to file
mirrordna --log-file ~/.mirrordna/logs/app.log identity create --type agent

# Structured logging (JSON)
mirrordna --structured-logs identity create --type agent
```

### Example Workflows

#### Workflow 1: Create and Verify Identity

```bash
# Create identity
identity_json=$(mirrordna identity create --type agent --metadata '{"name":"Agent1"}' 2>&1)

# Extract identity ID (requires jq)
identity_id=$(echo "$identity_json" | jq -r '.identity_id')

# Retrieve identity
mirrordna identity get "$identity_id"
```

#### Workflow 2: Configuration Validation

```bash
# Generate template
mirrordna config generate --template minimal --output config.yaml

# Validate
mirrordna config validate --master-citation config.yaml
```

---

## API Reference

### Identity Management

```python
from mirrordna import IdentityManager

manager = IdentityManager()

# Create identity
identity = manager.create_identity(
    identity_type="agent",
    metadata={"name": "MyAgent"}
)

# Retrieve identity
loaded = manager.get_identity(identity["identity_id"])

# Sign claim
signature = manager.sign_claim(
    identity_id=identity["identity_id"],
    claim="I am MyAgent",
    private_key=identity["_private_key"]
)

# Verify claim
verified = manager.verify_claim(
    identity_id=identity["identity_id"],
    claim="I am MyAgent",
    signature=signature
)
```

### Checksumming

```python
from mirrordna import compute_file_checksum, verify_checksum

# Compute checksum
checksum = compute_file_checksum("myfile.txt")

# Verify checksum
is_valid = verify_checksum("myfile.txt", checksum)
```

### Configuration Loading

```python
from mirrordna import ConfigLoader
from pathlib import Path

loader = ConfigLoader()

# Load Master Citation
citation = loader.load_master_citation(Path("master_citation.yaml"))
print(citation.id, citation.vault_id, citation.checksum)

# Load Vault Config
vault = loader.load_vault_config(Path("vault.yaml"))
```

### State Snapshots

```python
from mirrordna import capture_snapshot, save_snapshot

# Capture snapshot
snapshot = capture_snapshot(
    identity_state={"identities": [...]},
    continuity_state={"sessions": [...]},
    vault_state={"vault_id": "..."}
)

# Save snapshot
save_snapshot(snapshot, Path("snapshot.json"), format="json")
```

---

## Security Best Practices

### 1. Key Management

**Never** hardcode private keys:

```python
# ❌ BAD
private_key = "5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY"

# ✅ GOOD
import os
private_key = os.environ.get("MIRRORDNA_PRIVATE_KEY")
```

**Use KeyManager**:

```python
from mirrordna.security import KeyManager

km = KeyManager()

# Load from environment
private_key = km.load_private_key_from_env()

# Save to secure storage
km.save_key_to_file(
    key_id="agent_001",
    private_key=private_key,
    public_key=public_key
)
```

### 2. Input Validation

Always validate user input:

```python
from mirrordna.security import InputValidator

# Validate ID format
InputValidator.validate_id(identity_id, "identity_id")

# Sanitize strings
safe_string = InputValidator.sanitize_string(user_input, max_length=1000)
```

### 3. Rate Limiting

Protect against DoS attacks:

```python
from mirrordna.security import rate_limit, _crypto_limiter

@rate_limit(_crypto_limiter)
def sign_data(data: str, private_key: str):
    # Function will be rate limited
    pass
```

### 4. Audit Logging

Log security-sensitive operations:

```python
from mirrordna.logging import log_audit_event

log_audit_event(
    event_type="identity_created",
    actor="admin",
    action="create",
    target=identity_id,
    success=True
)
```

---

## Performance Optimization

### 1. Metrics Collection

```python
from mirrordna.metrics import timed, counted

@timed()
def expensive_operation():
    # Operation timing will be recorded
    pass

@counted()
def frequent_operation():
    # Call count will be tracked
    pass
```

### 2. Performance Reporting

```python
from mirrordna.metrics import PerformanceStats

# Print performance report
PerformanceStats.print_report()

# Get programmatic stats
stats = PerformanceStats.get_operation_stats()
```

### 3. Optimization Tips

- **Batch Operations**: Group storage operations
- **Caching**: Cache frequently accessed data
- **Lazy Loading**: Load data only when needed
- **Connection Pooling**: Reuse storage connections

---

## Troubleshooting

### Common Issues

#### Issue: Import Error

```
ModuleNotFoundError: No module named 'mirrordna'
```

**Solution**: Install package in editable mode:
```bash
pip install -e .
```

#### Issue: Test Failures

```
FAILED tests/test_identity.py::test_create_identity
```

**Solution**: Check storage directory permissions:
```bash
chmod 700 ~/.mirrordna/data
```

#### Issue: CLI Command Not Found

```
mirrordna: command not found
```

**Solution**: Ensure virtual environment is activated:
```bash
source venv/bin/activate
```

### Debugging

Enable debug logging:

```bash
mirrordna --log-level DEBUG --verbose health
```

Enable Python debugger:

```python
import pdb; pdb.set_trace()
```

### Getting Help

1. Check documentation: `./docs/`
2. Run examples: `./examples/`
3. Open an issue: GitHub Issues
4. Review changelog: `./docs/CHANGELOG.md`

---

## Contributing

See `CONTRIBUTING.md` for detailed contribution guidelines.

**Quick Checklist**:
- [ ] Tests pass locally
- [ ] Code follows PEP 8
- [ ] Documentation updated
- [ ] Commit messages follow format
- [ ] No private keys committed

---

## Resources

- **Main README**: `./README.md`
- **Architecture**: `./docs/architecture.md`
- **API Reference**: `./docs/schema-reference.md`
- **Examples**: `./examples/README.md`
- **Changelog**: `./docs/CHANGELOG.md`

---

**Happy coding with MirrorDNA! 🧬**
