"""
Checksum computation for MirrorDNA protocol.

Provides SHA-256 checksumming for files, state data, and canonical representations.
"""

import hashlib
import json
from pathlib import Path
from typing import Dict, Any, Union

from .exceptions import ChecksumComputationError, ConfigFileNotFoundError


def compute_file_checksum(path: Union[str, Path]) -> str:
    """
    Compute SHA-256 checksum of a file.

    Args:
        path: Path to file

    Returns:
        Hexadecimal checksum string

    Raises:
        ConfigFileNotFoundError: If file doesn't exist
        ChecksumComputationError: If checksum computation fails
    """
    path = Path(path)

    if not path.exists():
        raise ConfigFileNotFoundError(str(path))

    try:
        sha256 = hashlib.sha256()

        with open(path, 'rb') as f:
            # Read in chunks for large files
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)

        return sha256.hexdigest()
    except Exception as e:
        raise ChecksumComputationError(
            f"Failed to compute checksum for {path}: {str(e)}",
            {"file_path": str(path), "error": str(e)}
        )


def compute_state_checksum(data: Dict[str, Any]) -> str:
    """
    Compute SHA-256 checksum of state data (dictionary).

    Creates canonical JSON representation with sorted keys to ensure
    deterministic checksums.

    Args:
        data: State data dictionary

    Returns:
        Hexadecimal checksum string
    """
    # Create canonical JSON representation
    canonical_json = json.dumps(data, sort_keys=True, separators=(',', ':'))

    # Compute checksum
    sha256 = hashlib.sha256()
    sha256.update(canonical_json.encode('utf-8'))

    return sha256.hexdigest()


def compute_text_checksum(text: str) -> str:
    """
    Compute SHA-256 checksum of text content.

    Args:
        text: Text content

    Returns:
        Hexadecimal checksum string
    """
    sha256 = hashlib.sha256()
    sha256.update(text.encode('utf-8'))

    return sha256.hexdigest()


def verify_checksum(data: Union[str, Dict[str, Any], Path], expected_checksum: str) -> bool:
    """
    Verify that data matches expected checksum.

    Args:
        data: File path, text string, or dictionary
        expected_checksum: Expected checksum value

    Returns:
        True if checksums match, False otherwise

    Raises:
        ChecksumComputationError: If data type is unsupported
    """
    if isinstance(data, (str, Path)) and Path(data).exists():
        actual = compute_file_checksum(data)
    elif isinstance(data, dict):
        actual = compute_state_checksum(data)
    elif isinstance(data, str):
        actual = compute_text_checksum(data)
    else:
        raise ChecksumComputationError(
            f"Unsupported data type for checksum verification: {type(data).__name__}",
            {"data_type": type(data).__name__}
        )

    return actual.lower() == expected_checksum.lower()
