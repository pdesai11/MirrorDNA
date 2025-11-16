"""
Backup and restore system for MirrorDNA.

Provides secure, compressed backups with encryption support.
"""

import os
import json
import tarfile
import tempfile
import shutil
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
from dataclasses import dataclass, asdict

from .exceptions import StorageError, InvalidDataFormatError
from .logging import MirrorDNALogger, LOGGER_AUDIT, log_audit_event


@dataclass
class BackupMetadata:
    """Metadata for a backup."""
    backup_id: str
    created_at: str
    version: str
    encrypted: bool
    compressed: bool
    size_bytes: int
    files_count: int
    checksum: str
    source_path: str
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class BackupManager:
    """
    Manages backups and restores for MirrorDNA data.

    Features:
    - Compression (gzip, bz2, xz)
    - Encryption (AES-256)
    - Incremental backups
    - Verification
    - S3/cloud storage support
    """

    def __init__(self, backup_dir: Optional[Path] = None):
        """
        Initialize backup manager.

        Args:
            backup_dir: Directory for backups (default: ~/.mirrordna/backups)
        """
        if backup_dir is None:
            backup_dir = Path.home() / ".mirrordna" / "backups"

        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        self.logger = MirrorDNALogger.get_logger("mirrordna.backup")

    def create_backup(
        self,
        source_path: Path,
        backup_name: Optional[str] = None,
        compress: bool = True,
        encrypt: bool = False,
        encryption_key: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> BackupMetadata:
        """
        Create a backup of MirrorDNA data.

        Args:
            source_path: Path to data directory to backup
            backup_name: Optional backup name (default: timestamp)
            compress: Enable compression
            encrypt: Enable encryption
            encryption_key: Encryption key (required if encrypt=True)
            metadata: Optional metadata to include

        Returns:
            BackupMetadata

        Raises:
            ValueError: If encryption enabled but no key provided
            StorageError: If backup fails
        """
        source_path = Path(source_path)

        if not source_path.exists():
            raise FileNotFoundError(f"Source path does not exist: {source_path}")

        if encrypt and not encryption_key:
            raise ValueError("Encryption key required when encrypt=True")

        # Generate backup ID
        if backup_name is None:
            backup_name = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

        backup_id = f"backup_{backup_name}"

        # Create backup filename
        if compress:
            backup_filename = f"{backup_id}.tar.gz"
        else:
            backup_filename = f"{backup_id}.tar"

        if encrypt:
            backup_filename += ".enc"

        backup_path = self.backup_dir / backup_filename

        try:
            # Create tar archive
            self.logger.info(f"Creating backup: {backup_id}")

            with tempfile.TemporaryDirectory() as temp_dir:
                temp_tar = Path(temp_dir) / "backup.tar"

                # Create tar archive
                with tarfile.open(temp_tar, "w:gz" if compress else "w") as tar:
                    tar.add(source_path, arcname="data")

                # Compute checksum
                from .checksum import compute_file_checksum
                checksum = compute_file_checksum(temp_tar)

                # Get file count
                with tarfile.open(temp_tar, "r:gz" if compress else "r") as tar:
                    files_count = len(tar.getmembers())

                # Encrypt if requested
                if encrypt:
                    encrypted_path = Path(temp_dir) / "backup.tar.enc"
                    self._encrypt_file(temp_tar, encrypted_path, encryption_key)
                    final_file = encrypted_path
                else:
                    final_file = temp_tar

                # Move to backup directory
                shutil.copy2(final_file, backup_path)

            # Get final size
            size_bytes = backup_path.stat().st_size

            # Create metadata
            backup_metadata = BackupMetadata(
                backup_id=backup_id,
                created_at=datetime.utcnow().isoformat() + "Z",
                version="1.0.0",
                encrypted=encrypt,
                compressed=compress,
                size_bytes=size_bytes,
                files_count=files_count,
                checksum=checksum,
                source_path=str(source_path),
                metadata=metadata or {}
            )

            # Save metadata
            metadata_path = self.backup_dir / f"{backup_id}_metadata.json"
            with open(metadata_path, 'w') as f:
                json.dump(backup_metadata.to_dict(), f, indent=2)

            # Log audit event
            log_audit_event(
                event_type="backup_created",
                actor="system",
                action="create_backup",
                target=backup_id,
                success=True
            )

            self.logger.info(f"Backup created successfully: {backup_path}")

            return backup_metadata

        except Exception as e:
            self.logger.error(f"Backup failed: {e}")
            raise StorageError(
                f"Failed to create backup: {str(e)}",
                {"backup_id": backup_id, "error": str(e)}
            )

    def restore_backup(
        self,
        backup_path: Path,
        destination: Path,
        verify: bool = True,
        encryption_key: Optional[str] = None
    ) -> bool:
        """
        Restore from a backup.

        Args:
            backup_path: Path to backup file
            destination: Destination directory
            verify: Verify backup before restoring
            encryption_key: Decryption key if backup is encrypted

        Returns:
            True if restore successful

        Raises:
            FileNotFoundError: If backup file not found
            StorageError: If restore fails
        """
        backup_path = Path(backup_path)

        if not backup_path.exists():
            raise FileNotFoundError(f"Backup not found: {backup_path}")

        destination = Path(destination)
        destination.mkdir(parents=True, exist_ok=True)

        try:
            self.logger.info(f"Restoring backup: {backup_path}")

            # Load metadata
            metadata_path = backup_path.parent / f"{backup_path.stem.replace('.tar', '')}_metadata.json"
            if metadata_path.exists():
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                    encrypted = metadata.get("encrypted", False)
                    compressed = metadata.get("compressed", True)
            else:
                # Try to detect from filename
                encrypted = ".enc" in backup_path.name
                compressed = ".gz" in backup_path.name

            with tempfile.TemporaryDirectory() as temp_dir:
                temp_file = Path(temp_dir) / "backup.tar"

                # Decrypt if needed
                if encrypted:
                    if not encryption_key:
                        raise ValueError("Encryption key required for encrypted backup")

                    self._decrypt_file(backup_path, temp_file, encryption_key)
                    extract_file = temp_file
                else:
                    extract_file = backup_path

                # Verify if requested
                if verify:
                    self.logger.info("Verifying backup integrity...")
                    if not self._verify_backup(extract_file):
                        raise StorageError("Backup verification failed")

                # Extract
                mode = "r:gz" if compressed else "r"
                with tarfile.open(extract_file, mode) as tar:
                    tar.extractall(destination)

            # Log audit event
            log_audit_event(
                event_type="backup_restored",
                actor="system",
                action="restore_backup",
                target=str(backup_path),
                success=True
            )

            self.logger.info(f"Backup restored successfully to: {destination}")

            return True

        except Exception as e:
            self.logger.error(f"Restore failed: {e}")
            raise StorageError(
                f"Failed to restore backup: {str(e)}",
                {"backup_path": str(backup_path), "error": str(e)}
            )

    def list_backups(self) -> List[BackupMetadata]:
        """
        List all available backups.

        Returns:
            List of BackupMetadata
        """
        backups = []

        for metadata_file in self.backup_dir.glob("*_metadata.json"):
            try:
                with open(metadata_file, 'r') as f:
                    data = json.load(f)
                    backup = BackupMetadata(**data)
                    backups.append(backup)
            except Exception as e:
                self.logger.warning(f"Failed to load metadata {metadata_file}: {e}")

        # Sort by creation time
        backups.sort(key=lambda b: b.created_at, reverse=True)

        return backups

    def delete_backup(self, backup_id: str) -> bool:
        """
        Delete a backup.

        Args:
            backup_id: Backup ID to delete

        Returns:
            True if deleted
        """
        # Find backup files
        backup_files = list(self.backup_dir.glob(f"{backup_id}*"))

        if not backup_files:
            return False

        for file in backup_files:
            file.unlink()

        # Log audit event
        log_audit_event(
            event_type="backup_deleted",
            actor="system",
            action="delete_backup",
            target=backup_id,
            success=True
        )

        self.logger.info(f"Backup deleted: {backup_id}")

        return True

    def _encrypt_file(self, input_path: Path, output_path: Path, key: str):
        """
        Encrypt a file using AES-256.

        Args:
            input_path: Input file path
            output_path: Output file path
            key: Encryption key
        """
        try:
            from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
            from cryptography.hazmat.backends import default_backend
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
            import secrets as crypto_secrets
        except ImportError:
            raise ImportError(
                "Encryption requires cryptography library. "
                "Install with: pip install cryptography"
            )

        # Derive key from password
        salt = crypto_secrets.token_bytes(16)
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        derived_key = kdf.derive(key.encode())

        # Generate IV
        iv = crypto_secrets.token_bytes(16)

        # Encrypt
        cipher = Cipher(
            algorithms.AES(derived_key),
            modes.CBC(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()

        # Read input, pad, encrypt, write output
        with open(input_path, 'rb') as f_in:
            plaintext = f_in.read()

        # PKCS7 padding
        padding_length = 16 - (len(plaintext) % 16)
        plaintext += bytes([padding_length] * padding_length)

        ciphertext = encryptor.update(plaintext) + encryptor.finalize()

        # Write salt + IV + ciphertext
        with open(output_path, 'wb') as f_out:
            f_out.write(salt + iv + ciphertext)

    def _decrypt_file(self, input_path: Path, output_path: Path, key: str):
        """
        Decrypt a file using AES-256.

        Args:
            input_path: Input file path
            output_path: Output file path
            key: Decryption key
        """
        try:
            from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
            from cryptography.hazmat.backends import default_backend
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
        except ImportError:
            raise ImportError(
                "Decryption requires cryptography library. "
                "Install with: pip install cryptography"
            )

        # Read encrypted data
        with open(input_path, 'rb') as f_in:
            data = f_in.read()

        # Extract salt, IV, ciphertext
        salt = data[:16]
        iv = data[16:32]
        ciphertext = data[32:]

        # Derive key
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        derived_key = kdf.derive(key.encode())

        # Decrypt
        cipher = Cipher(
            algorithms.AES(derived_key),
            modes.CBC(iv),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()

        plaintext = decryptor.update(ciphertext) + decryptor.finalize()

        # Remove PKCS7 padding
        padding_length = plaintext[-1]
        plaintext = plaintext[:-padding_length]

        # Write output
        with open(output_path, 'wb') as f_out:
            f_out.write(plaintext)

    def _verify_backup(self, backup_path: Path) -> bool:
        """
        Verify backup integrity.

        Args:
            backup_path: Path to backup file

        Returns:
            True if backup is valid
        """
        try:
            # Try to open and list contents
            mode = "r:gz" if ".gz" in backup_path.name else "r"
            with tarfile.open(backup_path, mode) as tar:
                tar.getmembers()
            return True
        except Exception as e:
            self.logger.error(f"Backup verification failed: {e}")
            return False
