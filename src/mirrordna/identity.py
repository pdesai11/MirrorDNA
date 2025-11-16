"""
Identity management for MirrorDNA.
"""

import secrets
from datetime import datetime
from typing import Dict, Any, Optional

from .crypto import CryptoUtils
from .validator import validate_schema
from .storage import StorageAdapter, JSONFileStorage
from .exceptions import InvalidIdentityError, IdentityNotFoundError, SchemaValidationError


class IdentityManager:
    """Manages identity creation and validation."""

    def __init__(self, storage: Optional[StorageAdapter] = None, crypto: Optional[CryptoUtils] = None):
        """
        Initialize identity manager.

        Args:
            storage: Storage adapter (uses JSONFileStorage if None)
            crypto: Crypto utilities (uses CryptoUtils if None)
        """
        self.storage = storage or JSONFileStorage()
        self.crypto = crypto or CryptoUtils()

    def _generate_identity_id(self, identity_type: str) -> str:
        """
        Generate a unique identity ID.

        Args:
            identity_type: Type of identity (user, agent, system)

        Returns:
            Generated identity ID
        """
        type_prefix_map = {
            "user": "usr",
            "agent": "agt",
            "system": "sys"
        }

        prefix = type_prefix_map.get(identity_type, "unk")
        suffix = secrets.token_hex(8)  # 16 characters

        return f"mdna_{prefix}_{suffix}"

    def create_identity(
        self,
        identity_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new identity.

        Args:
            identity_type: Type of identity (user, agent, system)
            metadata: Optional metadata

        Returns:
            Identity record (includes _private_key field)

        Raises:
            InvalidIdentityError: If identity_type is invalid or validation fails
        """
        if identity_type not in ["user", "agent", "system"]:
            raise InvalidIdentityError(
                f"Invalid identity_type: {identity_type}. Must be 'user', 'agent', or 'system'",
                {"identity_type": identity_type, "valid_types": ["user", "agent", "system"]}
            )

        # Generate ID and keypair
        identity_id = self._generate_identity_id(identity_type)
        public_key, private_key = self.crypto.generate_keypair()

        # Create identity record
        identity = {
            "identity_id": identity_id,
            "identity_type": identity_type,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "public_key": public_key
        }

        if metadata:
            identity["metadata"] = metadata

        # Validate against schema
        result = validate_schema(identity, "identity")
        if not result.is_valid:
            raise SchemaValidationError(
                f"Identity validation failed: {', '.join(result.errors)}",
                schema_name="identity",
                validation_errors=result.errors
            )

        # Store identity
        self.storage.create("identities", identity)

        # Return identity with private key (WARNING: Handle with care!)
        identity["_private_key"] = private_key
        return identity

    def get_identity(self, identity_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve an identity by ID.

        Args:
            identity_id: Identity ID

        Returns:
            Identity record or None if not found
        """
        return self.storage.read("identities", identity_id)

    def validate_identity(self, identity: Dict[str, Any]) -> bool:
        """
        Validate an identity record.

        Args:
            identity: Identity record to validate

        Returns:
            True if valid, False otherwise
        """
        result = validate_schema(identity, "identity")
        return result.is_valid

    def sign_claim(self, identity_id: str, claim: str, private_key: str) -> str:
        """
        Sign a claim with an identity's private key.

        Args:
            identity_id: Identity ID
            claim: Claim to sign
            private_key: Private key for signing

        Returns:
            Base64-encoded signature
        """
        message = f"{identity_id}:{claim}"
        return self.crypto.sign(message, private_key)

    def verify_claim(self, identity_id: str, claim: str, signature: str) -> bool:
        """
        Verify a claim signature.

        Args:
            identity_id: Identity ID
            claim: Claim that was signed
            signature: Signature to verify

        Returns:
            True if signature is valid, False otherwise

        Raises:
            IdentityNotFoundError: If identity does not exist
        """
        identity = self.get_identity(identity_id)
        if not identity:
            raise IdentityNotFoundError(identity_id)

        message = f"{identity_id}:{claim}"
        return self.crypto.verify(message, signature, identity["public_key"])
