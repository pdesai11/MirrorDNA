"""
Storage layer interface and implementations for MirrorDNA.
"""

import json
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Any, Optional

from .exceptions import (
    DuplicateEntryError,
    EntryNotFoundError,
    StorageReadError,
    StorageWriteError,
    InvalidDataFormatError
)


class StorageAdapter(ABC):
    """Abstract base class for storage adapters."""

    @abstractmethod
    def create(self, collection: str, record: Dict[str, Any]) -> str:
        """
        Create a new record in a collection.

        Args:
            collection: Collection name
            record: Record data (must contain an 'id' field)

        Returns:
            Record ID
        """
        pass

    @abstractmethod
    def read(self, collection: str, record_id: str) -> Optional[Dict[str, Any]]:
        """
        Read a record by ID.

        Args:
            collection: Collection name
            record_id: Record ID

        Returns:
            Record data or None if not found
        """
        pass

    @abstractmethod
    def update(self, collection: str, record_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update a record.

        Args:
            collection: Collection name
            record_id: Record ID
            updates: Fields to update

        Returns:
            Updated record or None if not found
        """
        pass

    @abstractmethod
    def delete(self, collection: str, record_id: str) -> bool:
        """
        Delete a record.

        Args:
            collection: Collection name
            record_id: Record ID

        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
    def query(self, collection: str, filters: Optional[Dict[str, Any]] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Query records with filters.

        Args:
            collection: Collection name
            filters: Filter criteria (field: value pairs)
            limit: Maximum number of results

        Returns:
            List of matching records
        """
        pass


class JSONFileStorage(StorageAdapter):
    """Simple JSON file-based storage (default implementation)."""

    def __init__(self, storage_dir: Optional[Path] = None):
        """
        Initialize JSON file storage.

        Args:
            storage_dir: Directory for storage files. If None, uses ~/.mirrordna/data
        """
        if storage_dir is None:
            storage_dir = Path.home() / ".mirrordna" / "data"

        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def _get_collection_file(self, collection: str) -> Path:
        """Get the file path for a collection."""
        return self.storage_dir / f"{collection}.json"

    def _load_collection(self, collection: str) -> Dict[str, Dict[str, Any]]:
        """Load a collection from disk."""
        file_path = self._get_collection_file(collection)

        if not file_path.exists():
            return {}

        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise StorageReadError(
                f"Failed to parse JSON in collection '{collection}': {str(e)}",
                {"collection": collection, "file_path": str(file_path), "error": str(e)}
            )
        except Exception as e:
            raise StorageReadError(
                f"Failed to load collection '{collection}': {str(e)}",
                {"collection": collection, "file_path": str(file_path), "error": str(e)}
            )

    def _save_collection(self, collection: str, data: Dict[str, Dict[str, Any]]):
        """Save a collection to disk."""
        file_path = self._get_collection_file(collection)

        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            raise StorageWriteError(
                f"Failed to save collection '{collection}': {str(e)}",
                {"collection": collection, "file_path": str(file_path), "error": str(e)}
            )

    def create(self, collection: str, record: Dict[str, Any]) -> str:
        """Create a new record."""
        # Determine ID field based on collection type
        id_field_map = {
            "identities": "identity_id",
            "sessions": "session_id",
            "memories": "memory_id",
            "agent_dna": "agent_dna_id"
        }

        id_field = id_field_map.get(collection, "id")

        if id_field not in record:
            raise InvalidDataFormatError(
                f"Record must contain '{id_field}' field",
                {"collection": collection, "required_field": id_field}
            )

        record_id = record[id_field]

        # Load collection
        data = self._load_collection(collection)

        # Check for duplicates
        if record_id in data:
            raise DuplicateEntryError(record_id, collection)

        # Store record
        data[record_id] = record

        # Save collection
        self._save_collection(collection, data)

        return record_id

    def read(self, collection: str, record_id: str) -> Optional[Dict[str, Any]]:
        """Read a record by ID."""
        data = self._load_collection(collection)
        return data.get(record_id)

    def update(self, collection: str, record_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a record."""
        data = self._load_collection(collection)

        if record_id not in data:
            return None

        # Update fields
        data[record_id].update(updates)

        # Save collection
        self._save_collection(collection, data)

        return data[record_id]

    def delete(self, collection: str, record_id: str) -> bool:
        """Delete a record."""
        data = self._load_collection(collection)

        if record_id not in data:
            return False

        del data[record_id]

        # Save collection
        self._save_collection(collection, data)

        return True

    def query(self, collection: str, filters: Optional[Dict[str, Any]] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Query records with filters."""
        data = self._load_collection(collection)

        results = list(data.values())

        # Apply filters if provided
        if filters:
            filtered_results = []
            for record in results:
                match = True
                for key, value in filters.items():
                    # Support nested keys like "source.user_id"
                    if '.' in key:
                        parts = key.split('.')
                        record_value = record
                        for part in parts:
                            if isinstance(record_value, dict) and part in record_value:
                                record_value = record_value[part]
                            else:
                                record_value = None
                                break
                    else:
                        record_value = record.get(key)

                    if record_value != value:
                        match = False
                        break

                if match:
                    filtered_results.append(record)

            results = filtered_results

        # Apply limit
        return results[:limit]
