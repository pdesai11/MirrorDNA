"""
Interactive configuration wizard for MirrorDNA.

Provides step-by-step guided setup with validation.
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
import json
import yaml

from .identity import IdentityManager
from .checksum import compute_state_checksum
from .exceptions import InvalidDataFormatError


class ConfigWizard:
    """
    Interactive wizard for creating MirrorDNA configuration.

    Features:
    - Step-by-step prompts
    - Input validation
    - Template generation
    - Storage backend selection
    - Identity creation
    """

    def __init__(self, output_dir: Optional[Path] = None):
        """
        Initialize config wizard.

        Args:
            output_dir: Output directory for generated files
        """
        self.output_dir = Path(output_dir) if output_dir else Path.cwd()
        self.config = {}

    def prompt(self, question: str, default: Optional[str] = None, choices: Optional[List[str]] = None) -> str:
        """
        Prompt user for input.

        Args:
            question: Question to ask
            default: Default value
            choices: List of valid choices

        Returns:
            User input
        """
        if choices:
            choices_str = "/".join(choices)
            if default:
                prompt_text = f"{question} [{choices_str}] (default: {default}): "
            else:
                prompt_text = f"{question} [{choices_str}]: "
        elif default:
            prompt_text = f"{question} (default: {default}): "
        else:
            prompt_text = f"{question}: "

        while True:
            try:
                response = input(prompt_text).strip()

                if not response and default:
                    return default

                if choices and response not in choices:
                    print(f"Invalid choice. Please select from: {choices_str}")
                    continue

                return response

            except (KeyboardInterrupt, EOFError):
                print("\n\nWizard cancelled.")
                sys.exit(1)

    def confirm(self, question: str, default: bool = True) -> bool:
        """
        Ask for yes/no confirmation.

        Args:
            question: Question to ask
            default: Default answer

        Returns:
            True for yes, False for no
        """
        default_str = "Y/n" if default else "y/N"
        response = self.prompt(f"{question} [{default_str}]", default="y" if default else "n")
        return response.lower() in ['y', 'yes']

    def run(self) -> Dict[str, Any]:
        """
        Run the configuration wizard.

        Returns:
            Generated configuration
        """
        print("=" * 60)
        print("MirrorDNA Configuration Wizard")
        print("=" * 60)
        print()

        # Step 1: Basic information
        print("Step 1: Basic Information")
        print("-" * 60)

        agent_name = self.prompt("Agent name")
        agent_description = self.prompt("Agent description (optional)", default="")

        identity_type = self.prompt(
            "Identity type",
            default="agent",
            choices=["user", "agent", "system"]
        )

        print()

        # Step 2: Storage configuration
        print("Step 2: Storage Configuration")
        print("-" * 60)

        storage_type = self.prompt(
            "Storage backend",
            default="json_file",
            choices=["json_file", "postgresql", "mongodb"]
        )

        storage_config = {}

        if storage_type == "json_file":
            storage_dir = self.prompt(
                "Storage directory",
                default="~/.mirrordna/data"
            )
            storage_config = {
                "storage_dir": storage_dir
            }

        elif storage_type == "postgresql":
            db_host = self.prompt("PostgreSQL host", default="localhost")
            db_port = self.prompt("PostgreSQL port", default="5432")
            db_name = self.prompt("Database name", default="mirrordna")
            db_user = self.prompt("Database user", default="mirrordna")
            db_password = self.prompt("Database password")

            storage_config = {
                "url": f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
            }

        elif storage_type == "mongodb":
            mongo_host = self.prompt("MongoDB host", default="localhost")
            mongo_port = self.prompt("MongoDB port", default="27017")
            mongo_db = self.prompt("Database name", default="mirrordna")

            storage_config = {
                "url": f"mongodb://{mongo_host}:{mongo_port}/{mongo_db}"
            }

        print()

        # Step 3: Security settings
        print("Step 3: Security Settings")
        print("-" * 60)

        enable_encryption = self.confirm("Enable backup encryption?", default=True)
        enable_rate_limiting = self.confirm("Enable rate limiting?", default=True)
        enable_audit_logging = self.confirm("Enable audit logging?", default=True)

        print()

        # Step 4: Advanced options
        print("Step 4: Advanced Options")
        print("-" * 60)

        enable_metrics = self.confirm("Enable performance metrics?", default=True)
        log_level = self.prompt(
            "Log level",
            default="INFO",
            choices=["DEBUG", "INFO", "WARNING", "ERROR"]
        )

        print()

        # Build configuration
        print("Generating configuration...")
        print()

        # Create Master Citation
        citation_id = f"mc_{agent_name.lower().replace(' ', '_')}_001"
        vault_id = f"vault_{agent_name.lower().replace(' ', '_')}_001"

        master_citation = {
            "id": citation_id,
            "version": "1.0.0",
            "vault_id": vault_id,
            "created_at": self._get_timestamp(),
            "metadata": {
                "name": agent_name,
                "description": agent_description,
                "identity_type": identity_type
            }
        }

        # Compute checksum (placeholder, will be computed properly later)
        checksum = compute_state_checksum({
            k: v for k, v in master_citation.items() if k != "checksum"
        })
        master_citation["checksum"] = checksum

        # Create Vault Config
        vault_config = {
            "vault_id": vault_id,
            "storage_type": storage_type,
            "storage_config": storage_config,
            "metadata": {
                "name": f"{agent_name} Vault",
                "owner": agent_name
            }
        }

        # Create application config
        app_config = {
            "security": {
                "enable_encryption": enable_encryption,
                "enable_rate_limiting": enable_rate_limiting,
                "enable_audit_logging": enable_audit_logging
            },
            "monitoring": {
                "enable_metrics": enable_metrics,
                "log_level": log_level
            }
        }

        # Store config
        self.config = {
            "master_citation": master_citation,
            "vault_config": vault_config,
            "app_config": app_config
        }

        # Step 5: Create identity
        if self.confirm("Create identity now?", default=True):
            print("\nCreating identity...")

            try:
                identity_manager = IdentityManager()
                identity = identity_manager.create_identity(
                    identity_type=identity_type,
                    metadata={
                        "name": agent_name,
                        "description": agent_description
                    }
                )

                print(f"✓ Identity created: {identity['identity_id']}")

                # Store private key warning
                self.config["identity"] = {
                    "identity_id": identity["identity_id"],
                    "public_key": identity["public_key"],
                    "_private_key_warning": "STORE SECURELY - DO NOT COMMIT TO VERSION CONTROL"
                }

                if self.confirm("Save private key to file? (NOT RECOMMENDED)", default=False):
                    key_file = self.output_dir / f"{identity['identity_id']}_private.key"
                    key_file.write_text(identity["_private_key"])
                    key_file.chmod(0o600)
                    print(f"⚠️  Private key saved to: {key_file}")
                else:
                    print("\n" + "=" * 60)
                    print("IMPORTANT: Store your private key securely!")
                    print("=" * 60)
                    print(f"Private Key: {identity['_private_key']}")
                    print("=" * 60)
                    print()

            except Exception as e:
                print(f"✗ Failed to create identity: {e}")

        print()

        # Step 6: Save configuration files
        print("Saving configuration files...")

        # Save master citation
        citation_file = self.output_dir / "master_citation.yaml"
        with open(citation_file, 'w') as f:
            yaml.dump(master_citation, f, default_flow_style=False)
        print(f"✓ Saved: {citation_file}")

        # Save vault config
        vault_file = self.output_dir / "vault_config.yaml"
        with open(vault_file, 'w') as f:
            yaml.dump(vault_config, f, default_flow_style=False)
        print(f"✓ Saved: {vault_file}")

        # Save app config
        app_config_file = self.output_dir / "app_config.yaml"
        with open(app_config_file, 'w') as f:
            yaml.dump(app_config, f, default_flow_style=False)
        print(f"✓ Saved: {app_config_file}")

        print()
        print("=" * 60)
        print("Configuration complete!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("  1. Review generated configuration files")
        print("  2. Store private key securely")
        print("  3. Run: mirrordna config validate --master-citation master_citation.yaml")
        print("  4. Start using MirrorDNA!")
        print()

        return self.config

    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO 8601 format."""
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"


def run_wizard(output_dir: Optional[Path] = None) -> Dict[str, Any]:
    """
    Run the interactive configuration wizard.

    Args:
        output_dir: Output directory for generated files

    Returns:
        Generated configuration
    """
    wizard = ConfigWizard(output_dir)
    return wizard.run()
