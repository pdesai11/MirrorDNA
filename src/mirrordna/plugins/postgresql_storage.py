"""
PostgreSQL storage adapter plugin.

Provides enterprise-grade storage using PostgreSQL database.
"""

from typing import Dict, List, Any, Optional
import json

from ..plugins.storage_plugin import StoragePlugin
from ..plugins.base import PluginMetadata, PluginType
from ..exceptions import StorageError, StorageConnectionError, DuplicateEntryError, EntryNotFoundError


class PostgreSQLStorage(StoragePlugin):
    """
    PostgreSQL storage backend.

    Requires: psycopg2-binary or psycopg2

    Configuration:
        - url: PostgreSQL connection URL
        - schema: Database schema name (default: 'mirrordna')
        - pool_size: Connection pool size (default: 5)
        - pool_max_overflow: Max overflow connections (default: 10)
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize PostgreSQL storage.

        Args:
            config: Configuration dictionary with 'url' required
        """
        super().__init__(config)

        self.url = self.config.get("url")
        if not self.url:
            raise ValueError("PostgreSQL URL is required in config")

        self.schema = self.config.get("schema", "mirrordna")
        self.pool_size = self.config.get("pool_size", 5)
        self.pool_max_overflow = self.config.get("pool_max_overflow", 10)

        self._connection = None
        self._engine = None

    def get_metadata(self) -> PluginMetadata:
        """Get plugin metadata."""
        return PluginMetadata(
            name="PostgreSQLStorage",
            version="1.0.0",
            plugin_type=PluginType.STORAGE,
            description="PostgreSQL database storage backend",
            author="MirrorDNA",
            requires=["psycopg2-binary>=2.9.0", "sqlalchemy>=2.0.0"],
            config_schema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "PostgreSQL connection URL"},
                    "schema": {"type": "string", "default": "mirrordna"},
                    "pool_size": {"type": "integer", "default": 5},
                    "pool_max_overflow": {"type": "integer", "default": 10}
                },
                "required": ["url"]
            },
            tags=["storage", "postgresql", "database", "sql"]
        )

    def connect(self) -> bool:
        """
        Connect to PostgreSQL database.

        Returns:
            True if connection successful

        Raises:
            StorageConnectionError: If connection fails
        """
        try:
            # Try to import required libraries
            try:
                from sqlalchemy import create_engine, MetaData, Table, Column, String, JSON, text
                from sqlalchemy.pool import QueuePool
            except ImportError:
                raise ImportError(
                    "PostgreSQL storage requires SQLAlchemy and psycopg2. "
                    "Install with: pip install sqlalchemy psycopg2-binary"
                )

            # Create engine with connection pooling
            self._engine = create_engine(
                self.url,
                poolclass=QueuePool,
                pool_size=self.pool_size,
                max_overflow=self.pool_max_overflow,
                echo=False
            )

            # Test connection
            with self._engine.connect() as conn:
                # Create schema if it doesn't exist
                conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {self.schema}"))
                conn.commit()

            # Store SQLAlchemy imports for later use
            self._Column = Column
            self._String = String
            self._JSON = JSON
            self._Table = Table
            self._MetaData = MetaData
            self._text = text

            # Initialize metadata
            self._metadata = self._MetaData(schema=self.schema)

            # Create tables for collections as needed
            self._tables = {}

            return True

        except Exception as e:
            raise StorageConnectionError(
                f"Failed to connect to PostgreSQL: {str(e)}",
                {"url": self.url, "error": str(e)}
            )

    def disconnect(self) -> None:
        """Disconnect from PostgreSQL."""
        if self._engine:
            self._engine.dispose()
            self._engine = None
            self._connection = None

    def _get_or_create_table(self, collection: str):
        """Get or create table for collection."""
        if collection in self._tables:
            return self._tables[collection]

        # Create table definition
        table = self._Table(
            collection,
            self._metadata,
            self._Column('id', self._String(255), primary_key=True),
            self._Column('data', self._JSON),
            extend_existing=True
        )

        # Create table if it doesn't exist
        self._metadata.create_all(self._engine, tables=[table], checkfirst=True)

        self._tables[collection] = table
        return table

    def create(self, collection: str, record: Dict[str, Any]) -> str:
        """
        Create a new record.

        Args:
            collection: Collection name
            record: Record data (must contain an ID field)

        Returns:
            Record ID

        Raises:
            DuplicateEntryError: If record already exists
            StorageWriteError: If write fails
        """
        # Determine ID field
        id_field_map = {
            "identities": "identity_id",
            "sessions": "session_id",
            "memories": "memory_id",
            "agent_dna": "agent_dna_id"
        }

        id_field = id_field_map.get(collection, "id")

        if id_field not in record:
            from ..exceptions import InvalidDataFormatError
            raise InvalidDataFormatError(
                f"Record must contain '{id_field}' field",
                {"collection": collection, "required_field": id_field}
            )

        record_id = record[id_field]

        try:
            table = self._get_or_create_table(collection)

            with self._engine.connect() as conn:
                # Check for duplicates
                from sqlalchemy import select
                stmt = select(table).where(table.c.id == record_id)
                result = conn.execute(stmt)

                if result.fetchone():
                    raise DuplicateEntryError(record_id, collection)

                # Insert record
                from sqlalchemy import insert
                stmt = insert(table).values(id=record_id, data=record)
                conn.execute(stmt)
                conn.commit()

            return record_id

        except DuplicateEntryError:
            raise
        except Exception as e:
            from ..exceptions import StorageWriteError
            raise StorageWriteError(
                f"Failed to create record: {str(e)}",
                {"collection": collection, "record_id": record_id, "error": str(e)}
            )

    def read(self, collection: str, record_id: str) -> Optional[Dict[str, Any]]:
        """
        Read a record by ID.

        Args:
            collection: Collection name
            record_id: Record ID

        Returns:
            Record data or None if not found
        """
        try:
            table = self._get_or_create_table(collection)

            with self._engine.connect() as conn:
                from sqlalchemy import select
                stmt = select(table).where(table.c.id == record_id)
                result = conn.execute(stmt)
                row = result.fetchone()

                if row:
                    return row.data

                return None

        except Exception as e:
            raise StorageReadError(
                f"Failed to read record: {str(e)}",
                {"collection": collection, "record_id": record_id, "error": str(e)}
            )

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
        try:
            table = self._get_or_create_table(collection)

            with self._engine.connect() as conn:
                # Get current record
                from sqlalchemy import select
                stmt = select(table).where(table.c.id == record_id)
                result = conn.execute(stmt)
                row = result.fetchone()

                if not row:
                    return None

                # Merge updates
                current_data = row.data
                current_data.update(updates)

                # Update record
                from sqlalchemy import update as sql_update
                stmt = sql_update(table).where(table.c.id == record_id).values(data=current_data)
                conn.execute(stmt)
                conn.commit()

                return current_data

        except Exception as e:
            from ..exceptions import StorageWriteError
            raise StorageWriteError(
                f"Failed to update record: {str(e)}",
                {"collection": collection, "record_id": record_id, "error": str(e)}
            )

    def delete(self, collection: str, record_id: str) -> bool:
        """
        Delete a record.

        Args:
            collection: Collection name
            record_id: Record ID

        Returns:
            True if deleted, False if not found
        """
        try:
            table = self._get_or_create_table(collection)

            with self._engine.connect() as conn:
                from sqlalchemy import delete
                stmt = delete(table).where(table.c.id == record_id)
                result = conn.execute(stmt)
                conn.commit()

                return result.rowcount > 0

        except Exception as e:
            from ..exceptions import StorageWriteError
            raise StorageWriteError(
                f"Failed to delete record: {str(e)}",
                {"collection": collection, "record_id": record_id, "error": str(e)}
            )

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
        try:
            table = self._get_or_create_table(collection)

            with self._engine.connect() as conn:
                from sqlalchemy import select

                # Build query
                stmt = select(table)

                # Apply JSON filters if provided
                if filters:
                    for key, value in filters.items():
                        # Use JSON path queries for filtering
                        if '.' in key:
                            # Nested key support
                            path = key.split('.')
                            json_path = '{' + ','.join(path) + '}'
                            stmt = stmt.where(self._text(f"data#>>'{json_path}' = :val").bindparams(val=str(value)))
                        else:
                            stmt = stmt.where(table.c.data[key].astext == str(value))

                # Apply limit
                stmt = stmt.limit(limit)

                # Execute query
                result = conn.execute(stmt)
                return [row.data for row in result]

        except Exception as e:
            raise StorageReadError(
                f"Failed to query collection: {str(e)}",
                {"collection": collection, "error": str(e)}
            )
