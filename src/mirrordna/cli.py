"""
MirrorDNA Command-Line Interface

Provides command-line access to all core protocol operations including:
- Identity management
- Configuration validation
- Checksum verification
- Timeline query
- State snapshot operations
- Health checks
"""

import argparse
import sys
import json
import yaml
from pathlib import Path
from typing import Optional

from . import __version__
from .identity import IdentityManager
from .config_loader import ConfigLoader
from .checksum import compute_file_checksum, compute_state_checksum, verify_checksum
from .timeline import Timeline
from .state_snapshot import capture_snapshot, save_snapshot, load_snapshot
from .logging import MirrorDNALogger, log_audit_event
from .exceptions import MirrorDNAException


def setup_logging(args):
    """Configure logging based on CLI arguments."""
    level = "DEBUG" if args.verbose else args.log_level
    MirrorDNALogger.initialize(
        level=level,
        enable_console=True,
        enable_file=args.log_file is not None,
        log_file=args.log_file,
        use_structured=args.structured_logs
    )


# ============================================================================
# Identity Commands
# ============================================================================

def cmd_identity_create(args):
    """Create a new identity."""
    try:
        manager = IdentityManager()
        metadata = json.loads(args.metadata) if args.metadata else None

        identity = manager.create_identity(
            identity_type=args.type,
            metadata=metadata
        )

        # Log audit event
        log_audit_event(
            event_type="identity_created",
            actor="cli",
            action="create",
            target=identity["identity_id"],
            success=True
        )

        # Output identity (mask private key unless explicitly requested)
        if args.show_private_key:
            print(json.dumps(identity, indent=2))
        else:
            private_key = identity.pop("_private_key", None)
            print(json.dumps(identity, indent=2))
            if private_key and not args.quiet:
                print(f"\n⚠️  Private key (store securely): {private_key}", file=sys.stderr)

        return 0
    except MirrorDNAException as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_identity_get(args):
    """Retrieve an identity."""
    try:
        manager = IdentityManager()
        identity = manager.get_identity(args.identity_id)

        if identity:
            print(json.dumps(identity, indent=2))
            return 0
        else:
            print(f"Identity not found: {args.identity_id}", file=sys.stderr)
            return 1
    except MirrorDNAException as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


# ============================================================================
# Configuration Commands
# ============================================================================

def cmd_config_validate(args):
    """Validate configuration files."""
    try:
        loader = ConfigLoader()

        if args.master_citation:
            citation = loader.load_master_citation(Path(args.master_citation))
            print(f"✓ Master Citation valid: {citation.id}")
            print(f"  Version: {citation.version}")
            print(f"  Vault ID: {citation.vault_id}")
            print(f"  Checksum: {citation.checksum}")

        if args.vault:
            vault = loader.load_vault_config(Path(args.vault))
            print(f"✓ Vault Config valid: {vault.vault_id}")
            print(f"  Storage: {vault.storage_type}")

        return 0
    except MirrorDNAException as e:
        print(f"✗ Validation failed: {e}", file=sys.stderr)
        return 1


def cmd_config_generate(args):
    """Generate configuration templates."""
    templates = {
        "minimal": {
            "master_citation": {
                "id": "mc_example_001",
                "version": "1.0.0",
                "vault_id": "vault_example_001",
                "created_at": "2025-01-01T00:00:00Z",
                "checksum": "PLACEHOLDER_CHECKSUM",
                "metadata": {}
            },
            "vault": {
                "vault_id": "vault_example_001",
                "storage_type": "json_file",
                "storage_config": {
                    "storage_dir": "~/.mirrordna/data"
                }
            }
        },
        "full": {
            "master_citation": {
                "id": "mc_example_001",
                "version": "1.0.0",
                "vault_id": "vault_example_001",
                "created_at": "2025-01-01T00:00:00Z",
                "checksum": "PLACEHOLDER_CHECKSUM",
                "predecessor": None,
                "successor": None,
                "metadata": {
                    "name": "Example Agent",
                    "description": "Example MirrorDNA configuration"
                }
            },
            "vault": {
                "vault_id": "vault_example_001",
                "storage_type": "json_file",
                "storage_config": {
                    "storage_dir": "~/.mirrordna/data"
                },
                "metadata": {
                    "owner": "example_user",
                    "purpose": "development"
                }
            }
        }
    }

    template = templates.get(args.template, templates["minimal"])

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            if args.format == "json":
                json.dump(template, f, indent=2)
            else:
                yaml.dump(template, f, default_flow_style=False)
        print(f"Generated {args.template} template: {output_path}")
    else:
        if args.format == "json":
            print(json.dumps(template, indent=2))
        else:
            print(yaml.dump(template, default_flow_style=False))

    return 0


def cmd_config_load(args):
    """Load and display configuration."""
    try:
        loader = ConfigLoader()
        citation = loader.load_master_citation(Path(args.file))

        print(json.dumps({
            "id": citation.id,
            "version": citation.version,
            "vault_id": citation.vault_id,
            "created_at": citation.created_at,
            "checksum": citation.checksum,
            "metadata": citation.metadata
        }, indent=2))

        return 0
    except MirrorDNAException as e:
        print(f"Error loading config: {e}", file=sys.stderr)
        return 1


# ============================================================================
# Checksum Commands
# ============================================================================

def cmd_checksum_compute(args):
    """Compute checksum of file or data."""
    try:
        if args.file:
            checksum = compute_file_checksum(args.file)
            print(f"{checksum}  {args.file}")
        elif args.text:
            from .checksum import compute_text_checksum
            checksum = compute_text_checksum(args.text)
            print(checksum)
        return 0
    except MirrorDNAException as e:
        print(f"Error computing checksum: {e}", file=sys.stderr)
        return 1


def cmd_checksum_verify(args):
    """Verify file checksum."""
    try:
        verified = verify_checksum(args.file, args.checksum)
        if verified:
            print(f"✓ Checksum verified: {args.file}")
            return 0
        else:
            print(f"✗ Checksum mismatch: {args.file}", file=sys.stderr)
            return 1
    except MirrorDNAException as e:
        print(f"Error verifying checksum: {e}", file=sys.stderr)
        return 1


# ============================================================================
# Timeline Commands
# ============================================================================

def cmd_timeline_query(args):
    """Query timeline events."""
    try:
        timeline = Timeline()

        # Load events if file specified
        if args.file:
            timeline.load_from_file(Path(args.file))

        # Apply filters
        events = timeline.export_events()

        if args.event_type:
            events = [e for e in events if e.get("event_type") == args.event_type]

        if args.actor:
            events = [e for e in events if e.get("actor") == args.actor]

        # Apply limit
        if args.limit:
            events = events[:args.limit]

        # Output
        if args.format == "json":
            print(json.dumps(events, indent=2))
        else:
            for event in events:
                print(f"{event['timestamp']} | {event['event_type']} | {event['actor']}")
                if args.verbose:
                    print(f"  ID: {event['id']}")
                    if event.get('payload'):
                        print(f"  Payload: {event['payload']}")

        return 0
    except MirrorDNAException as e:
        print(f"Error querying timeline: {e}", file=sys.stderr)
        return 1


# ============================================================================
# Snapshot Commands
# ============================================================================

def cmd_snapshot_create(args):
    """Create state snapshot."""
    try:
        # Create minimal snapshot
        snapshot = capture_snapshot(
            identity_state={},
            continuity_state={},
            vault_state={}
        )

        # Save to file
        output_path = Path(args.output)
        save_snapshot(snapshot, output_path, format=args.format)

        print(f"✓ Snapshot created: {output_path}")
        print(f"  ID: {snapshot.snapshot_id}")
        print(f"  Checksum: {snapshot.checksum}")

        return 0
    except MirrorDNAException as e:
        print(f"Error creating snapshot: {e}", file=sys.stderr)
        return 1


def cmd_snapshot_load(args):
    """Load and display snapshot."""
    try:
        snapshot = load_snapshot(Path(args.file))

        print(f"Snapshot ID: {snapshot.snapshot_id}")
        print(f"Timestamp: {snapshot.timestamp}")
        print(f"Version: {snapshot.version}")
        print(f"Checksum: {snapshot.checksum}")

        if args.verbose:
            print("\nFull snapshot data:")
            print(json.dumps({
                "snapshot_id": snapshot.snapshot_id,
                "timestamp": snapshot.timestamp,
                "version": snapshot.version,
                "checksum": snapshot.checksum,
                "identity_state": snapshot.identity_state,
                "continuity_state": snapshot.continuity_state,
                "vault_state": snapshot.vault_state
            }, indent=2))

        return 0
    except MirrorDNAException as e:
        print(f"Error loading snapshot: {e}", file=sys.stderr)
        return 1


# ============================================================================
# Version Command
# ============================================================================

def cmd_version(args):
    """Display version information."""
    print(f"MirrorDNA Protocol v{__version__}")
    print("Identity and Continuity Protocol for AI Agents")
    return 0


# ============================================================================
# Benchmark Command
# ============================================================================

def cmd_benchmark(args):
    """Run benchmarks."""
    try:
        from .benchmark import create_default_suite
        from pathlib import Path

        suite = create_default_suite(iterations=args.iterations)
        results = suite.run_all()
        suite.print_results()

        if args.output:
            suite.export_json(Path(args.output))
            print(f"\n✓ Results exported to: {args.output}")

        return 0
    except Exception as e:
        print(f"Benchmark failed: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


# ============================================================================
# Health Check Command
# ============================================================================

def cmd_health_check(args):
    """Run health checks."""
    try:
        from .health import run_health_check
        success = run_health_check(verbose=args.verbose)
        return 0 if success else 1
    except Exception as e:
        print(f"Health check failed: {e}", file=sys.stderr)
        return 1


# ============================================================================
# Main CLI Setup
# ============================================================================

def create_parser():
    """Create argument parser with all subcommands."""
    parser = argparse.ArgumentParser(
        prog="mirrordna",
        description="MirrorDNA Protocol - Command-Line Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                        help="Set logging level")
    parser.add_argument("--log-file", type=str, help="Log to file")
    parser.add_argument("--structured-logs", action="store_true", help="Use structured (JSON) logging")
    parser.add_argument("-q", "--quiet", action="store_true", help="Suppress non-essential output")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Identity commands
    identity_parser = subparsers.add_parser("identity", help="Identity management")
    identity_sub = identity_parser.add_subparsers(dest="identity_command")

    identity_create = identity_sub.add_parser("create", help="Create new identity")
    identity_create.add_argument("--type", required=True, choices=["user", "agent", "system"],
                                  help="Identity type")
    identity_create.add_argument("--metadata", type=str, help="Metadata as JSON string")
    identity_create.add_argument("--show-private-key", action="store_true",
                                  help="Include private key in output")
    identity_create.set_defaults(func=cmd_identity_create)

    identity_get = identity_sub.add_parser("get", help="Get identity by ID")
    identity_get.add_argument("identity_id", help="Identity ID")
    identity_get.set_defaults(func=cmd_identity_get)

    # Config commands
    config_parser = subparsers.add_parser("config", help="Configuration management")
    config_sub = config_parser.add_subparsers(dest="config_command")

    config_validate = config_sub.add_parser("validate", help="Validate configuration files")
    config_validate.add_argument("--master-citation", type=str, help="Master Citation file")
    config_validate.add_argument("--vault", type=str, help="Vault config file")
    config_validate.set_defaults(func=cmd_config_validate)

    config_generate = config_sub.add_parser("generate", help="Generate configuration templates")
    config_generate.add_argument("--template", choices=["minimal", "full"], default="minimal",
                                  help="Template type")
    config_generate.add_argument("--format", choices=["json", "yaml"], default="yaml",
                                  help="Output format")
    config_generate.add_argument("--output", type=str, help="Output file (default: stdout)")
    config_generate.set_defaults(func=cmd_config_generate)

    config_load = config_sub.add_parser("load", help="Load and display configuration")
    config_load.add_argument("file", help="Config file path")
    config_load.set_defaults(func=cmd_config_load)

    # Checksum commands
    checksum_parser = subparsers.add_parser("checksum", help="Checksum operations")
    checksum_sub = checksum_parser.add_subparsers(dest="checksum_command")

    checksum_compute = checksum_sub.add_parser("compute", help="Compute checksum")
    checksum_compute.add_argument("--file", type=str, help="File to checksum")
    checksum_compute.add_argument("--text", type=str, help="Text to checksum")
    checksum_compute.set_defaults(func=cmd_checksum_compute)

    checksum_verify = checksum_sub.add_parser("verify", help="Verify checksum")
    checksum_verify.add_argument("file", help="File to verify")
    checksum_verify.add_argument("checksum", help="Expected checksum")
    checksum_verify.set_defaults(func=cmd_checksum_verify)

    # Timeline commands
    timeline_parser = subparsers.add_parser("timeline", help="Timeline operations")
    timeline_sub = timeline_parser.add_subparsers(dest="timeline_command")

    timeline_query = timeline_sub.add_parser("query", help="Query timeline events")
    timeline_query.add_argument("--file", type=str, help="Timeline file")
    timeline_query.add_argument("--event-type", type=str, help="Filter by event type")
    timeline_query.add_argument("--actor", type=str, help="Filter by actor")
    timeline_query.add_argument("--limit", type=int, help="Limit results")
    timeline_query.add_argument("--format", choices=["json", "text"], default="text",
                                 help="Output format")
    timeline_query.set_defaults(func=cmd_timeline_query)

    # Snapshot commands
    snapshot_parser = subparsers.add_parser("snapshot", help="State snapshot operations")
    snapshot_sub = snapshot_parser.add_subparsers(dest="snapshot_command")

    snapshot_create = snapshot_sub.add_parser("create", help="Create snapshot")
    snapshot_create.add_argument("--output", required=True, help="Output file")
    snapshot_create.add_argument("--format", choices=["json", "yaml"], default="json",
                                  help="Output format")
    snapshot_create.set_defaults(func=cmd_snapshot_create)

    snapshot_load = snapshot_sub.add_parser("load", help="Load snapshot")
    snapshot_load.add_argument("file", help="Snapshot file")
    snapshot_load.set_defaults(func=cmd_snapshot_load)

    # Benchmark command
    benchmark_parser = subparsers.add_parser("benchmark", help="Run performance benchmarks")
    benchmark_parser.add_argument("--suite", choices=["full", "quick"], default="full",
                                   help="Benchmark suite to run")
    benchmark_parser.add_argument("--iterations", type=int, default=100,
                                   help="Number of iterations per benchmark")
    benchmark_parser.add_argument("--output", type=str, help="Export results to JSON file")
    benchmark_parser.set_defaults(func=cmd_benchmark)

    # Health check command
    health_parser = subparsers.add_parser("health", help="System health check")
    health_parser.set_defaults(func=cmd_health_check)

    # Version command
    version_parser = subparsers.add_parser("version", help="Show version information")
    version_parser.set_defaults(func=cmd_version)

    return parser


def main(argv=None):
    """Main entry point for CLI."""
    parser = create_parser()
    args = parser.parse_args(argv)

    # Setup logging
    setup_logging(args)

    # Execute command
    if hasattr(args, "func"):
        try:
            return args.func(args)
        except KeyboardInterrupt:
            print("\nInterrupted", file=sys.stderr)
            return 130
        except Exception as e:
            print(f"Unexpected error: {e}", file=sys.stderr)
            if args.verbose:
                import traceback
                traceback.print_exc()
            return 1
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
