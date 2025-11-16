"""
Production-grade logging system for MirrorDNA protocol.

Provides structured logging with configurable levels, audit trails, and
context-aware logging for all protocol operations.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import json


# Logger names for different components
LOGGER_ROOT = "mirrordna"
LOGGER_CHECKSUM = "mirrordna.checksum"
LOGGER_CRYPTO = "mirrordna.crypto"
LOGGER_IDENTITY = "mirrordna.identity"
LOGGER_STORAGE = "mirrordna.storage"
LOGGER_CONFIG = "mirrordna.config"
LOGGER_TIMELINE = "mirrordna.timeline"
LOGGER_CONTINUITY = "mirrordna.continuity"
LOGGER_MEMORY = "mirrordna.memory"
LOGGER_AUDIT = "mirrordna.audit"


class StructuredFormatter(logging.Formatter):
    """
    Custom formatter that outputs structured log data.

    Includes timestamp, level, logger name, message, and optional context data.
    """

    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record with structured data.

        Args:
            record: Log record to format

        Returns:
            Formatted log string
        """
        # Base log data
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage()
        }

        # Add context if present
        if hasattr(record, "context") and record.context:
            log_data["context"] = record.context

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data, separators=(',', ':'))


class MirrorDNALogger:
    """
    Centralized logging manager for MirrorDNA protocol.

    Provides convenient methods for logging with context and manages
    logger configuration.
    """

    _initialized = False
    _log_level = logging.INFO
    _log_file: Optional[Path] = None
    _enable_console = True
    _enable_file = False
    _use_structured = False

    @classmethod
    def initialize(
        cls,
        level: str = "INFO",
        log_file: Optional[Path] = None,
        enable_console: bool = True,
        enable_file: bool = False,
        use_structured: bool = False
    ):
        """
        Initialize the MirrorDNA logging system.

        Args:
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_file: Optional path to log file
            enable_console: Enable console output
            enable_file: Enable file output
            use_structured: Use structured (JSON) logging format
        """
        cls._log_level = getattr(logging, level.upper(), logging.INFO)
        cls._log_file = Path(log_file) if log_file else None
        cls._enable_console = enable_console
        cls._enable_file = enable_file
        cls._use_structured = use_structured

        # Configure root logger
        root_logger = logging.getLogger(LOGGER_ROOT)
        root_logger.setLevel(cls._log_level)
        root_logger.handlers.clear()

        # Choose formatter
        if use_structured:
            formatter = StructuredFormatter()
        else:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )

        # Add console handler
        if enable_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(cls._log_level)
            console_handler.setFormatter(formatter)
            root_logger.addHandler(console_handler)

        # Add file handler
        if enable_file and log_file:
            log_file_path = Path(log_file)
            log_file_path.parent.mkdir(parents=True, exist_ok=True)

            file_handler = logging.FileHandler(log_file_path)
            file_handler.setLevel(cls._log_level)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)

        cls._initialized = True

    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """
        Get a logger by name.

        Args:
            name: Logger name (use LOGGER_* constants)

        Returns:
            Configured logger instance
        """
        if not cls._initialized:
            cls.initialize()

        return logging.getLogger(name)

    @classmethod
    def log_with_context(
        cls,
        logger_name: str,
        level: str,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Log a message with additional context data.

        Args:
            logger_name: Name of logger to use
            level: Log level (debug, info, warning, error, critical)
            message: Log message
            context: Additional context data
        """
        logger = cls.get_logger(logger_name)
        log_func = getattr(logger, level.lower(), logger.info)

        if cls._use_structured and context:
            # Add context to log record
            extra = {"context": context}
            log_func(message, extra=extra)
        else:
            # Append context to message
            if context:
                context_str = ", ".join(f"{k}={v}" for k, v in context.items())
                message = f"{message} ({context_str})"
            log_func(message)


# Convenience functions for common logging operations

def log_checksum_verification(file_path: str, checksum: str, verified: bool):
    """Log checksum verification operation."""
    MirrorDNALogger.log_with_context(
        LOGGER_CHECKSUM,
        "info",
        f"Checksum verification {'succeeded' if verified else 'failed'}",
        {"file_path": file_path, "checksum": checksum, "verified": verified}
    )


def log_checksum_computation(file_path: str, checksum: str, duration_ms: float):
    """Log checksum computation operation."""
    MirrorDNALogger.log_with_context(
        LOGGER_CHECKSUM,
        "debug",
        f"Computed checksum for {file_path}",
        {"file_path": file_path, "checksum": checksum, "duration_ms": duration_ms}
    )


def log_crypto_operation(operation: str, success: bool, context: Optional[Dict[str, Any]] = None):
    """Log cryptographic operation."""
    level = "info" if success else "error"
    MirrorDNALogger.log_with_context(
        LOGGER_CRYPTO,
        level,
        f"Crypto operation '{operation}' {'succeeded' if success else 'failed'}",
        context or {}
    )


def log_identity_created(identity_id: str, identity_type: str):
    """Log identity creation."""
    MirrorDNALogger.log_with_context(
        LOGGER_IDENTITY,
        "info",
        f"Created identity {identity_id}",
        {"identity_id": identity_id, "identity_type": identity_type}
    )


def log_storage_operation(operation: str, collection: str, record_id: str, success: bool):
    """Log storage operation."""
    level = "debug" if success else "error"
    MirrorDNALogger.log_with_context(
        LOGGER_STORAGE,
        level,
        f"Storage {operation} on {collection}/{record_id} {'succeeded' if success else 'failed'}",
        {"operation": operation, "collection": collection, "record_id": record_id, "success": success}
    )


def log_config_loaded(config_type: str, file_path: str, checksum: Optional[str] = None):
    """Log configuration loading."""
    context = {"config_type": config_type, "file_path": file_path}
    if checksum:
        context["checksum"] = checksum

    MirrorDNALogger.log_with_context(
        LOGGER_CONFIG,
        "info",
        f"Loaded {config_type} from {file_path}",
        context
    )


def log_timeline_event(event_id: str, event_type: str, actor: str):
    """Log timeline event creation."""
    MirrorDNALogger.log_with_context(
        LOGGER_TIMELINE,
        "info",
        f"Timeline event created: {event_id}",
        {"event_id": event_id, "event_type": event_type, "actor": actor}
    )


def log_session_created(session_id: str, parent_session_id: Optional[str] = None):
    """Log session creation."""
    context = {"session_id": session_id}
    if parent_session_id:
        context["parent_session_id"] = parent_session_id

    MirrorDNALogger.log_with_context(
        LOGGER_CONTINUITY,
        "info",
        f"Session created: {session_id}",
        context
    )


def log_memory_operation(operation: str, memory_id: str, tier: str, success: bool):
    """Log memory operation."""
    level = "debug" if success else "error"
    MirrorDNALogger.log_with_context(
        LOGGER_MEMORY,
        level,
        f"Memory {operation} on {memory_id} in tier {tier} {'succeeded' if success else 'failed'}",
        {"operation": operation, "memory_id": memory_id, "tier": tier, "success": success}
    )


def log_audit_event(event_type: str, actor: str, action: str, target: str, success: bool):
    """
    Log security audit event.

    Use this for security-sensitive operations like:
    - Identity creation/deletion
    - Cryptographic operations
    - Configuration changes
    - Access control decisions
    """
    level = "warning" if not success else "info"
    MirrorDNALogger.log_with_context(
        LOGGER_AUDIT,
        level,
        f"Audit: {actor} {action} on {target}",
        {
            "event_type": event_type,
            "actor": actor,
            "action": action,
            "target": target,
            "success": success
        }
    )


def log_error(logger_name: str, error: Exception, context: Optional[Dict[str, Any]] = None):
    """
    Log an exception with full traceback.

    Args:
        logger_name: Logger to use
        error: Exception to log
        context: Additional context data
    """
    logger = MirrorDNALogger.get_logger(logger_name)
    context_dict = context or {}
    context_dict["error_type"] = error.__class__.__name__

    if hasattr(error, "details"):
        context_dict.update(error.details)

    MirrorDNALogger.log_with_context(
        logger_name,
        "error",
        f"Error: {str(error)}",
        context_dict
    )


# Initialize with defaults (can be reconfigured by applications)
MirrorDNALogger.initialize(
    level="INFO",
    enable_console=True,
    enable_file=False,
    use_structured=False
)
