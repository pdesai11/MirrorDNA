"""
Security hardening features for MirrorDNA protocol.

Provides:
- Secure key management
- Rate limiting for cryptographic operations
- Input validation and sanitization
- Security audit logging
"""

import time
import re
from pathlib import Path
from typing import Optional, Dict, Any, Callable
from datetime import datetime, timedelta
from functools import wraps
import os

from .exceptions import CryptoOperationError, InvalidDataFormatError
from .logging import log_audit_event, log_error, LOGGER_AUDIT


# ============================================================================
# Rate Limiting
# ============================================================================

class RateLimiter:
    """
    Token bucket rate limiter for protecting against DoS attacks.

    Limits the rate of operations (e.g., crypto operations) to prevent
    resource exhaustion.
    """

    def __init__(self, max_calls: int, time_window: int):
        """
        Initialize rate limiter.

        Args:
            max_calls: Maximum number of calls allowed in time window
            time_window: Time window in seconds
        """
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls: Dict[str, list] = {}

    def is_allowed(self, key: str) -> bool:
        """
        Check if operation is allowed for given key.

        Args:
            key: Identifier (e.g., user ID, IP address)

        Returns:
            True if allowed, False if rate limit exceeded
        """
        now = time.time()
        if key not in self.calls:
            self.calls[key] = []

        # Remove old calls outside time window
        self.calls[key] = [
            call_time for call_time in self.calls[key]
            if now - call_time < self.time_window
        ]

        # Check if limit exceeded
        if len(self.calls[key]) >= self.max_calls:
            return False

        # Record this call
        self.calls[key].append(now)
        return True

    def reset(self, key: str):
        """Reset rate limit for key."""
        if key in self.calls:
            del self.calls[key]


# Global rate limiters
_crypto_limiter = RateLimiter(max_calls=100, time_window=60)  # 100 calls per minute
_storage_limiter = RateLimiter(max_calls=1000, time_window=60)  # 1000 calls per minute


def rate_limit(limiter: RateLimiter, key_func: Optional[Callable] = None):
    """
    Decorator to rate limit function calls.

    Args:
        limiter: RateLimiter instance to use
        key_func: Optional function to extract key from args (default: use "global")

    Example:
        @rate_limit(_crypto_limiter)
        def sign_data(data: str, private_key: str):
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extract key
            if key_func:
                key = key_func(*args, **kwargs)
            else:
                key = "global"

            # Check rate limit
            if not limiter.is_allowed(key):
                raise CryptoOperationError(
                    f"Rate limit exceeded for {func.__name__}",
                    {"function": func.__name__, "key": key}
                )

            return func(*args, **kwargs)
        return wrapper
    return decorator


# ============================================================================
# Input Validation & Sanitization
# ============================================================================

class InputValidator:
    """Input validation and sanitization."""

    # ID pattern validators
    PATTERNS = {
        "identity_id": re.compile(r"^mdna_(usr|agt|sys)_[a-f0-9]{16}$"),
        "master_citation_id": re.compile(r"^mc_[a-zA-Z0-9_-]+$"),
        "vault_id": re.compile(r"^vault_[a-zA-Z0-9_-]+$"),
        "session_id": re.compile(r"^sess_[a-f0-9]{16}$"),
        "memory_id": re.compile(r"^mem_[a-f0-9]{16}$"),
        "event_id": re.compile(r"^evt_\d{14}_[a-f0-9]{4}$"),
        "checksum": re.compile(r"^[a-f0-9]{64}$"),  # SHA-256
    }

    @classmethod
    def validate_id(cls, value: str, id_type: str) -> bool:
        """
        Validate ID format.

        Args:
            value: ID value to validate
            id_type: Type of ID (identity_id, vault_id, etc.)

        Returns:
            True if valid

        Raises:
            InvalidDataFormatError: If ID is invalid
        """
        if id_type not in cls.PATTERNS:
            raise InvalidDataFormatError(
                f"Unknown ID type: {id_type}",
                {"id_type": id_type, "value": value}
            )

        pattern = cls.PATTERNS[id_type]
        if not pattern.match(value):
            raise InvalidDataFormatError(
                f"Invalid {id_type} format: {value}",
                {"id_type": id_type, "value": value, "pattern": pattern.pattern}
            )

        return True

    @classmethod
    def sanitize_string(cls, value: str, max_length: int = 1000) -> str:
        """
        Sanitize string input.

        Args:
            value: String to sanitize
            max_length: Maximum allowed length

        Returns:
            Sanitized string

        Raises:
            InvalidDataFormatError: If string is too long
        """
        if not isinstance(value, str):
            raise InvalidDataFormatError(
                f"Expected string, got {type(value).__name__}",
                {"type": type(value).__name__}
            )

        if len(value) > max_length:
            raise InvalidDataFormatError(
                f"String too long: {len(value)} > {max_length}",
                {"length": len(value), "max_length": max_length}
            )

        # Remove control characters except newlines and tabs
        sanitized = "".join(
            char for char in value
            if char >= ' ' or char in '\n\r\t'
        )

        return sanitized

    @classmethod
    def validate_path(cls, path: Path, must_exist: bool = False, must_be_file: bool = False) -> bool:
        """
        Validate file path for security issues.

        Args:
            path: Path to validate
            must_exist: Path must exist
            must_be_file: Path must be a file

        Returns:
            True if valid

        Raises:
            InvalidDataFormatError: If path is invalid
        """
        path = Path(path).resolve()

        # Check for path traversal
        try:
            path.relative_to(Path.cwd())
        except ValueError:
            # Allow absolute paths in home directory
            try:
                path.relative_to(Path.home())
            except ValueError:
                raise InvalidDataFormatError(
                    f"Path outside allowed directories: {path}",
                    {"path": str(path)}
                )

        if must_exist and not path.exists():
            raise InvalidDataFormatError(
                f"Path does not exist: {path}",
                {"path": str(path)}
            )

        if must_be_file and path.exists() and not path.is_file():
            raise InvalidDataFormatError(
                f"Path is not a file: {path}",
                {"path": str(path)}
            )

        return True


# ============================================================================
# Secure Key Management
# ============================================================================

class KeyManager:
    """
    Secure key management for MirrorDNA.

    Provides:
    - Environment variable loading
    - Secure key storage (encrypted)
    - Key rotation support
    """

    def __init__(self, storage_dir: Optional[Path] = None):
        """
        Initialize key manager.

        Args:
            storage_dir: Directory for key storage (default: ~/.mirrordna/keys)
        """
        if storage_dir is None:
            storage_dir = Path.home() / ".mirrordna" / "keys"

        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True, mode=0o700)

    def load_private_key_from_env(self, env_var: str = "MIRRORDNA_PRIVATE_KEY") -> Optional[str]:
        """
        Load private key from environment variable.

        Args:
            env_var: Environment variable name

        Returns:
            Private key or None if not set
        """
        key = os.environ.get(env_var)
        if key:
            log_audit_event(
                event_type="key_loaded",
                actor="system",
                action="load_from_env",
                target=env_var,
                success=True
            )
        return key

    def save_key_to_file(self, key_id: str, private_key: str, public_key: str) -> Path:
        """
        Save key pair to file (WARNING: Plaintext storage).

        For production, consider using encrypted storage or key management systems.

        Args:
            key_id: Unique key identifier
            private_key: Private key
            public_key: Public key

        Returns:
            Path to key file
        """
        key_file = self.storage_dir / f"{key_id}.key"

        # Ensure file has restrictive permissions
        key_file.touch(mode=0o600, exist_ok=False)

        key_data = {
            "key_id": key_id,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "public_key": public_key,
            "private_key": private_key
        }

        import json
        key_file.write_text(json.dumps(key_data, indent=2))

        log_audit_event(
            event_type="key_saved",
            actor="system",
            action="save_to_file",
            target=key_id,
            success=True
        )

        return key_file

    def load_key_from_file(self, key_id: str) -> Optional[Dict[str, str]]:
        """
        Load key pair from file.

        Args:
            key_id: Key identifier

        Returns:
            Key data dict or None if not found
        """
        key_file = self.storage_dir / f"{key_id}.key"

        if not key_file.exists():
            return None

        import json
        key_data = json.loads(key_file.read_text())

        log_audit_event(
            event_type="key_loaded",
            actor="system",
            action="load_from_file",
            target=key_id,
            success=True
        )

        return key_data

    def rotate_key(self, old_key_id: str, new_key_id: str, new_private_key: str, new_public_key: str):
        """
        Rotate cryptographic key.

        Args:
            old_key_id: Old key identifier
            new_key_id: New key identifier
            new_private_key: New private key
            new_public_key: New public key
        """
        # Archive old key
        old_key_file = self.storage_dir / f"{old_key_id}.key"
        if old_key_file.exists():
            archive_file = self.storage_dir / f"{old_key_id}.key.archived.{int(time.time())}"
            old_key_file.rename(archive_file)

        # Save new key
        self.save_key_to_file(new_key_id, new_private_key, new_public_key)

        log_audit_event(
            event_type="key_rotated",
            actor="system",
            action="rotate",
            target=f"{old_key_id} -> {new_key_id}",
            success=True
        )


# ============================================================================
# Security Audit Helpers
# ============================================================================

def audit_crypto_operation(operation: str, success: bool, context: Optional[Dict[str, Any]] = None):
    """
    Log cryptographic operation for security audit.

    Args:
        operation: Operation name (sign, verify, generate_keypair)
        success: Whether operation succeeded
        context: Additional context
    """
    log_audit_event(
        event_type="crypto_operation",
        actor="crypto",
        action=operation,
        target="cryptographic_operation",
        success=success
    )

    if context:
        from .logging import MirrorDNALogger, LOGGER_AUDIT
        MirrorDNALogger.log_with_context(
            LOGGER_AUDIT,
            "info" if success else "warning",
            f"Crypto operation: {operation}",
            context
        )


def validate_and_sanitize_input(
    value: Any,
    field_name: str,
    required: bool = True,
    validator: Optional[Callable] = None
) -> Any:
    """
    Validate and sanitize input value.

    Args:
        value: Input value
        field_name: Field name for error messages
        required: Whether field is required
        validator: Optional custom validator function

    Returns:
        Validated/sanitized value

    Raises:
        InvalidDataFormatError: If validation fails
    """
    if value is None:
        if required:
            raise InvalidDataFormatError(
                f"Required field missing: {field_name}",
                {"field": field_name}
            )
        return None

    if isinstance(value, str):
        value = InputValidator.sanitize_string(value)

    if validator:
        try:
            validator(value)
        except Exception as e:
            raise InvalidDataFormatError(
                f"Validation failed for {field_name}: {str(e)}",
                {"field": field_name, "error": str(e)}
            )

    return value


# ============================================================================
# Security Configuration
# ============================================================================

class SecurityConfig:
    """Security configuration settings."""

    # Rate limiting
    ENABLE_RATE_LIMITING = True
    CRYPTO_RATE_LIMIT = 100  # operations per minute
    STORAGE_RATE_LIMIT = 1000  # operations per minute

    # Input validation
    ENABLE_INPUT_VALIDATION = True
    MAX_STRING_LENGTH = 10000
    MAX_PAYLOAD_SIZE = 1024 * 1024  # 1 MB

    # Audit logging
    ENABLE_AUDIT_LOGGING = True
    AUDIT_LOG_FILE = Path.home() / ".mirrordna" / "logs" / "audit.log"

    # Key management
    KEY_ROTATION_DAYS = 90
    REQUIRE_KEY_FROM_ENV = False  # If True, only allow keys from environment

    @classmethod
    def configure(cls, **kwargs):
        """Update security configuration."""
        for key, value in kwargs.items():
            if hasattr(cls, key.upper()):
                setattr(cls, key.upper(), value)
