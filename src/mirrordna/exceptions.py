"""
MirrorDNA Protocol - Custom Exception Hierarchy

This module defines domain-specific exceptions for the MirrorDNA protocol,
providing clear error messages and recovery guidance.

All MirrorDNA exceptions inherit from MirrorDNAException to enable
targeted exception handling.
"""

from typing import Optional, Dict, Any


class MirrorDNAException(Exception):
    """
    Base exception for all MirrorDNA protocol errors.

    All custom exceptions inherit from this class to enable:
    - Consistent error handling patterns
    - Easy differentiation from standard Python exceptions
    - Structured error information
    """

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize exception with message and optional details.

        Args:
            message: Human-readable error description
            details: Additional context (e.g., file paths, checksums, IDs)
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        """Format exception with details if available."""
        if self.details:
            detail_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            return f"{self.message} ({detail_str})"
        return self.message


# ============================================================================
# Checksum & Integrity Exceptions
# ============================================================================

class ChecksumError(MirrorDNAException):
    """Base class for checksum-related errors."""
    pass


class ChecksumMismatchError(ChecksumError):
    """
    Raised when computed checksum doesn't match expected value.

    This indicates potential data tampering or corruption.

    Recovery: Verify data source, re-download if applicable, check for
    storage corruption.
    """

    def __init__(self, expected: str, actual: str, context: str = ""):
        details = {"expected": expected, "actual": actual}
        if context:
            details["context"] = context
        message = f"Checksum mismatch: expected {expected}, got {actual}"
        if context:
            message += f" (context: {context})"
        super().__init__(message, details)


class ChecksumComputationError(ChecksumError):
    """
    Raised when checksum computation fails.

    Recovery: Check file permissions, verify file format, ensure readable content.
    """
    pass


# ============================================================================
# Configuration & Loading Exceptions
# ============================================================================

class ConfigurationError(MirrorDNAException):
    """Base class for configuration-related errors."""
    pass


class InvalidMasterCitationError(ConfigurationError):
    """
    Raised when Master Citation is invalid or malformed.

    Recovery: Verify YAML/JSON syntax, check required fields (id, version,
    vault_id), ensure checksum is present and valid.
    """
    pass


class InvalidVaultConfigError(ConfigurationError):
    """
    Raised when Vault configuration is invalid.

    Recovery: Verify vault_id format (^vault_), check storage_type,
    validate file paths.
    """
    pass


class ConfigFileNotFoundError(ConfigurationError):
    """
    Raised when configuration file is missing.

    Recovery: Verify file path, check file permissions, ensure file exists.
    """

    def __init__(self, file_path: str):
        message = f"Configuration file not found: {file_path}"
        super().__init__(message, {"file_path": file_path})


class ConfigLoadError(ConfigurationError):
    """
    Raised when configuration file cannot be loaded.

    Recovery: Check file format (YAML/JSON), verify syntax, ensure encoding is UTF-8.
    """
    pass


# ============================================================================
# Identity & Cryptography Exceptions
# ============================================================================

class IdentityError(MirrorDNAException):
    """Base class for identity-related errors."""
    pass


class InvalidIdentityError(IdentityError):
    """
    Raised when identity data is invalid or malformed.

    Recovery: Verify identity structure matches schema, check ID format,
    ensure required fields are present.
    """
    pass


class IdentityNotFoundError(IdentityError):
    """
    Raised when requested identity does not exist.

    Recovery: Verify identity ID, check storage, ensure identity was created.
    """

    def __init__(self, identity_id: str):
        message = f"Identity not found: {identity_id}"
        super().__init__(message, {"identity_id": identity_id})


class DuplicateIdentityError(IdentityError):
    """
    Raised when attempting to create identity with existing ID.

    Recovery: Use different ID or load existing identity.
    """

    def __init__(self, identity_id: str):
        message = f"Identity already exists: {identity_id}"
        super().__init__(message, {"identity_id": identity_id})


class CryptoError(MirrorDNAException):
    """Base class for cryptographic operation errors."""
    pass


class CryptoOperationError(CryptoError):
    """
    Raised when cryptographic operation fails.

    Recovery: Verify key format, check input data, ensure correct key type
    (public vs private).
    """
    pass


class SignatureVerificationError(CryptoError):
    """
    Raised when signature verification fails.

    Recovery: Verify public key is correct, check signature format, ensure
    message hasn't been altered.
    """

    def __init__(self, message: str = "Signature verification failed"):
        super().__init__(message)


class InvalidKeyError(CryptoError):
    """
    Raised when cryptographic key is invalid.

    Recovery: Verify key format (base64-encoded), check key length,
    ensure correct key type.
    """
    pass


# ============================================================================
# Storage Exceptions
# ============================================================================

class StorageError(MirrorDNAException):
    """Base class for storage-related errors."""
    pass


class StorageConnectionError(StorageError):
    """
    Raised when storage backend is unreachable.

    Recovery: Check storage path, verify permissions, ensure storage service
    is running.
    """
    pass


class StorageWriteError(StorageError):
    """
    Raised when write operation fails.

    Recovery: Check disk space, verify write permissions, ensure directory exists.
    """
    pass


class StorageReadError(StorageError):
    """
    Raised when read operation fails.

    Recovery: Verify file exists, check read permissions, ensure correct format.
    """
    pass


class DuplicateEntryError(StorageError):
    """
    Raised when attempting to create entry with existing ID.

    Recovery: Use different ID or update existing entry.
    """

    def __init__(self, entry_id: str, collection: str = ""):
        details = {"entry_id": entry_id}
        if collection:
            details["collection"] = collection
        message = f"Entry already exists: {entry_id}"
        if collection:
            message += f" in collection '{collection}'"
        super().__init__(message, details)


class EntryNotFoundError(StorageError):
    """
    Raised when requested entry does not exist.

    Recovery: Verify entry ID, check collection name, ensure entry was created.
    """

    def __init__(self, entry_id: str, collection: str = ""):
        details = {"entry_id": entry_id}
        if collection:
            details["collection"] = collection
        message = f"Entry not found: {entry_id}"
        if collection:
            message += f" in collection '{collection}'"
        super().__init__(message, details)


# ============================================================================
# Validation Exceptions
# ============================================================================

class ValidationError(MirrorDNAException):
    """Base class for validation errors."""
    pass


class SchemaValidationError(ValidationError):
    """
    Raised when data fails JSON schema validation.

    Recovery: Check data structure against schema, verify required fields,
    ensure correct data types.
    """

    def __init__(self, message: str, schema_name: str = "", validation_errors: Optional[list] = None):
        details = {}
        if schema_name:
            details["schema"] = schema_name
        if validation_errors:
            details["errors"] = validation_errors
        super().__init__(message, details)


class InvalidDataFormatError(ValidationError):
    """
    Raised when data format is invalid.

    Recovery: Verify data structure, check field types, ensure required
    fields are present.
    """
    pass


# ============================================================================
# Timeline Exceptions
# ============================================================================

class TimelineError(MirrorDNAException):
    """Base class for timeline-related errors."""
    pass


class InvalidTimelineEventError(TimelineError):
    """
    Raised when timeline event is invalid.

    Recovery: Verify event structure, check required fields (id, timestamp,
    event_type), ensure valid actor.
    """
    pass


class TimelineNotFoundError(TimelineError):
    """
    Raised when timeline file does not exist.

    Recovery: Verify file path, check if timeline was initialized,
    create new timeline if needed.
    """
    pass


# ============================================================================
# Session & Continuity Exceptions
# ============================================================================

class ContinuityError(MirrorDNAException):
    """Base class for session continuity errors."""
    pass


class SessionNotFoundError(ContinuityError):
    """
    Raised when session does not exist.

    Recovery: Verify session ID, check if session was created, ensure
    session hasn't been deleted.
    """

    def __init__(self, session_id: str):
        message = f"Session not found: {session_id}"
        super().__init__(message, {"session_id": session_id})


class InvalidSessionError(ContinuityError):
    """
    Raised when session data is invalid.

    Recovery: Verify session structure, check required fields, ensure
    valid parent references.
    """
    pass


# ============================================================================
# Memory Exceptions
# ============================================================================

class MemoryError(MirrorDNAException):
    """Base class for memory management errors."""
    pass


class InvalidMemoryTierError(MemoryError):
    """
    Raised when memory tier is invalid.

    Recovery: Use valid tier ('short_term', 'long_term', or 'episodic').
    """

    def __init__(self, tier: str):
        message = f"Invalid memory tier: {tier}. Must be 'short_term', 'long_term', or 'episodic'"
        super().__init__(message, {"tier": tier, "valid_tiers": ["short_term", "long_term", "episodic"]})


class MemoryNotFoundError(MemoryError):
    """
    Raised when memory entry does not exist.

    Recovery: Verify memory ID, check tier, ensure memory wasn't archived.
    """

    def __init__(self, memory_id: str, tier: str = ""):
        details = {"memory_id": memory_id}
        if tier:
            details["tier"] = tier
        message = f"Memory not found: {memory_id}"
        if tier:
            message += f" in tier '{tier}'"
        super().__init__(message, details)


# ============================================================================
# Agent DNA Exceptions
# ============================================================================

class AgentDNAError(MirrorDNAException):
    """Base class for AgentDNA-related errors."""
    pass


class InvalidAgentDNAError(AgentDNAError):
    """
    Raised when AgentDNA structure is invalid.

    Recovery: Verify DNA structure, check traits, ensure valid personality
    dimensions.
    """
    pass


# ============================================================================
# Reflection Exceptions
# ============================================================================

class ReflectionError(MirrorDNAException):
    """Base class for reflection-related errors."""
    pass


class InvalidReflectionTypeError(ReflectionError):
    """
    Raised when reflection type is invalid.

    Recovery: Use valid ReflectionType enum value (DECISION, CAPABILITY,
    ALIGNMENT, etc.).
    """

    def __init__(self, reflection_type: str):
        message = f"Invalid reflection type: {reflection_type}"
        super().__init__(message, {"reflection_type": reflection_type})


# ============================================================================
# Utility Functions
# ============================================================================

def wrap_exception(original_exception: Exception, context: str = "") -> MirrorDNAException:
    """
    Wrap standard Python exception in MirrorDNAException.

    Useful for converting low-level exceptions (IOError, JSONDecodeError, etc.)
    into MirrorDNA-specific exceptions with additional context.

    Args:
        original_exception: The original exception to wrap
        context: Additional context about where/why error occurred

    Returns:
        MirrorDNAException with original error details

    Example:
        try:
            data = json.loads(content)
        except json.JSONDecodeError as e:
            raise wrap_exception(e, "Failed to parse master citation")
    """
    message = f"{original_exception.__class__.__name__}: {str(original_exception)}"
    if context:
        message = f"{context}: {message}"

    details = {
        "original_type": original_exception.__class__.__name__,
        "original_message": str(original_exception)
    }

    return MirrorDNAException(message, details)
