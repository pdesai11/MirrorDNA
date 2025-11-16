"""
Health check and diagnostics system for MirrorDNA protocol.

Provides comprehensive health checks for:
- Python version and dependencies
- Storage connectivity
- Configuration validity
- Schema availability
- Cryptographic operations
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class HealthCheckResult:
    """Result of a single health check."""
    name: str
    status: str  # "healthy", "degraded", "unhealthy"
    message: str
    details: Optional[Dict[str, Any]] = None
    duration_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class HealthChecker:
    """
    Centralized health checking system for MirrorDNA.

    Performs various health checks to ensure the system is properly configured
    and operational.
    """

    def __init__(self):
        """Initialize health checker."""
        self.results: List[HealthCheckResult] = []

    def check_python_version(self) -> HealthCheckResult:
        """Check Python version meets requirements."""
        start = datetime.now()

        version_info = sys.version_info
        version_str = f"{version_info.major}.{version_info.minor}.{version_info.micro}"

        if version_info >= (3, 8):
            status = "healthy"
            message = f"Python {version_str} (>= 3.8 required)"
        else:
            status = "unhealthy"
            message = f"Python {version_str} (< 3.8, upgrade required)"

        duration_ms = (datetime.now() - start).total_seconds() * 1000

        return HealthCheckResult(
            name="python_version",
            status=status,
            message=message,
            details={"version": version_str, "required": "3.8+"},
            duration_ms=duration_ms
        )

    def check_dependencies(self) -> HealthCheckResult:
        """Check that all required dependencies are installed."""
        start = datetime.now()

        required_packages = {
            "jsonschema": "4.0.0",
            "cryptography": "40.0.0",
            "yaml": "6.0.0"  # pyyaml
        }

        missing = []
        installed = {}

        for package, min_version in required_packages.items():
            try:
                if package == "yaml":
                    import yaml
                    installed[package] = getattr(yaml, "__version__", "unknown")
                elif package == "jsonschema":
                    import jsonschema
                    installed[package] = jsonschema.__version__
                elif package == "cryptography":
                    import cryptography
                    installed[package] = cryptography.__version__
            except ImportError:
                missing.append(package)

        duration_ms = (datetime.now() - start).total_seconds() * 1000

        if not missing:
            return HealthCheckResult(
                name="dependencies",
                status="healthy",
                message=f"All {len(required_packages)} dependencies installed",
                details={"installed": installed},
                duration_ms=duration_ms
            )
        else:
            return HealthCheckResult(
                name="dependencies",
                status="unhealthy",
                message=f"Missing {len(missing)} dependencies: {', '.join(missing)}",
                details={"missing": missing, "installed": installed},
                duration_ms=duration_ms
            )

    def check_storage(self) -> HealthCheckResult:
        """Check storage connectivity."""
        start = datetime.now()

        try:
            from .storage import JSONFileStorage

            # Create temporary storage instance
            storage = JSONFileStorage()

            # Check directory is writable
            if not storage.storage_dir.exists():
                storage.storage_dir.mkdir(parents=True, exist_ok=True)

            # Try to write test file
            test_file = storage.storage_dir / ".health_check"
            test_file.write_text("health check")
            test_file.unlink()

            duration_ms = (datetime.now() - start).total_seconds() * 1000

            return HealthCheckResult(
                name="storage",
                status="healthy",
                message=f"Storage accessible at {storage.storage_dir}",
                details={"storage_dir": str(storage.storage_dir), "writable": True},
                duration_ms=duration_ms
            )
        except Exception as e:
            duration_ms = (datetime.now() - start).total_seconds() * 1000

            return HealthCheckResult(
                name="storage",
                status="unhealthy",
                message=f"Storage check failed: {str(e)}",
                details={"error": str(e)},
                duration_ms=duration_ms
            )

    def check_schemas(self) -> HealthCheckResult:
        """Check that JSON schemas are available."""
        start = datetime.now()

        try:
            # Find schema directory
            schema_dir = Path(__file__).parent.parent.parent / "schemas"

            if not schema_dir.exists():
                return HealthCheckResult(
                    name="schemas",
                    status="unhealthy",
                    message=f"Schema directory not found: {schema_dir}",
                    details={"schema_dir": str(schema_dir)},
                    duration_ms=(datetime.now() - start).total_seconds() * 1000
                )

            # Count schema files
            protocol_schemas = list((schema_dir / "protocol").glob("*.json")) if (schema_dir / "protocol").exists() else []
            extension_schemas = list((schema_dir / "extensions").glob("*.json")) if (schema_dir / "extensions").exists() else []

            total_schemas = len(protocol_schemas) + len(extension_schemas)

            duration_ms = (datetime.now() - start).total_seconds() * 1000

            if total_schemas > 0:
                return HealthCheckResult(
                    name="schemas",
                    status="healthy",
                    message=f"Found {total_schemas} schemas ({len(protocol_schemas)} protocol, {len(extension_schemas)} extension)",
                    details={
                        "schema_dir": str(schema_dir),
                        "protocol_schemas": len(protocol_schemas),
                        "extension_schemas": len(extension_schemas)
                    },
                    duration_ms=duration_ms
                )
            else:
                return HealthCheckResult(
                    name="schemas",
                    status="unhealthy",
                    message="No schemas found",
                    details={"schema_dir": str(schema_dir)},
                    duration_ms=duration_ms
                )
        except Exception as e:
            duration_ms = (datetime.now() - start).total_seconds() * 1000

            return HealthCheckResult(
                name="schemas",
                status="unhealthy",
                message=f"Schema check failed: {str(e)}",
                details={"error": str(e)},
                duration_ms=duration_ms
            )

    def check_crypto(self) -> HealthCheckResult:
        """Check cryptographic operations."""
        start = datetime.now()

        try:
            from .crypto import CryptoUtils

            crypto = CryptoUtils()

            # Test key generation
            public_key, private_key = crypto.generate_keypair()

            # Test signing
            message = "health check test"
            signature = crypto.sign(message, private_key)

            # Test verification
            verified = crypto.verify(message, signature, public_key)

            duration_ms = (datetime.now() - start).total_seconds() * 1000

            if verified:
                return HealthCheckResult(
                    name="crypto",
                    status="healthy",
                    message="Cryptographic operations functional (Ed25519)",
                    details={"algorithm": "Ed25519", "test_passed": True},
                    duration_ms=duration_ms
                )
            else:
                return HealthCheckResult(
                    name="crypto",
                    status="unhealthy",
                    message="Signature verification failed",
                    details={"test_passed": False},
                    duration_ms=duration_ms
                )
        except Exception as e:
            duration_ms = (datetime.now() - start).total_seconds() * 1000

            return HealthCheckResult(
                name="crypto",
                status="unhealthy",
                message=f"Crypto check failed: {str(e)}",
                details={"error": str(e)},
                duration_ms=duration_ms
            )

    def check_checksum(self) -> HealthCheckResult:
        """Check checksum operations."""
        start = datetime.now()

        try:
            from .checksum import compute_text_checksum, compute_state_checksum

            # Test text checksum
            text = "health check test"
            checksum1 = compute_text_checksum(text)
            checksum2 = compute_text_checksum(text)

            # Verify determinism
            deterministic = checksum1 == checksum2

            # Test state checksum
            state = {"key": "value", "number": 42}
            state_checksum = compute_state_checksum(state)

            duration_ms = (datetime.now() - start).total_seconds() * 1000

            if deterministic and len(checksum1) == 64:  # SHA-256 hex is 64 characters
                return HealthCheckResult(
                    name="checksum",
                    status="healthy",
                    message="Checksum operations functional (SHA-256)",
                    details={"algorithm": "SHA-256", "deterministic": True},
                    duration_ms=duration_ms
                )
            else:
                return HealthCheckResult(
                    name="checksum",
                    status="degraded",
                    message="Checksum operations may have issues",
                    details={"deterministic": deterministic, "checksum_length": len(checksum1)},
                    duration_ms=duration_ms
                )
        except Exception as e:
            duration_ms = (datetime.now() - start).total_seconds() * 1000

            return HealthCheckResult(
                name="checksum",
                status="unhealthy",
                message=f"Checksum check failed: {str(e)}",
                details={"error": str(e)},
                duration_ms=duration_ms
            )

    def run_all_checks(self) -> List[HealthCheckResult]:
        """Run all health checks."""
        self.results = [
            self.check_python_version(),
            self.check_dependencies(),
            self.check_storage(),
            self.check_schemas(),
            self.check_crypto(),
            self.check_checksum(),
        ]
        return self.results

    def get_summary(self) -> Dict[str, Any]:
        """Get health check summary."""
        if not self.results:
            self.run_all_checks()

        total = len(self.results)
        healthy = sum(1 for r in self.results if r.status == "healthy")
        degraded = sum(1 for r in self.results if r.status == "degraded")
        unhealthy = sum(1 for r in self.results if r.status == "unhealthy")

        overall_status = "healthy"
        if unhealthy > 0:
            overall_status = "unhealthy"
        elif degraded > 0:
            overall_status = "degraded"

        total_duration = sum(r.duration_ms for r in self.results)

        return {
            "overall_status": overall_status,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "checks": {
                "total": total,
                "healthy": healthy,
                "degraded": degraded,
                "unhealthy": unhealthy
            },
            "duration_ms": total_duration,
            "results": [r.to_dict() for r in self.results]
        }

    def print_report(self, verbose: bool = False):
        """Print human-readable health report."""
        if not self.results:
            self.run_all_checks()

        summary = self.get_summary()

        # Print header
        print("=" * 60)
        print("MirrorDNA Health Check Report")
        print("=" * 60)
        print(f"Timestamp: {summary['timestamp']}")
        print(f"Overall Status: {summary['overall_status'].upper()}")
        print(f"Duration: {summary['duration_ms']:.2f}ms")
        print()

        # Print results
        status_symbols = {
            "healthy": "✓",
            "degraded": "!",
            "unhealthy": "✗"
        }

        for result in self.results:
            symbol = status_symbols.get(result.status, "?")
            print(f"{symbol} {result.name}: {result.message}")

            if verbose and result.details:
                for key, value in result.details.items():
                    print(f"    {key}: {value}")

        print()
        print("-" * 60)
        print(f"Summary: {summary['checks']['healthy']}/{summary['checks']['total']} healthy, "
              f"{summary['checks']['degraded']} degraded, {summary['checks']['unhealthy']} unhealthy")
        print("=" * 60)


def run_health_check(verbose: bool = False) -> bool:
    """
    Run health check and return success status.

    Args:
        verbose: Print detailed information

    Returns:
        True if all checks pass, False otherwise
    """
    checker = HealthChecker()
    checker.run_all_checks()
    checker.print_report(verbose=verbose)

    summary = checker.get_summary()
    return summary["overall_status"] == "healthy"
