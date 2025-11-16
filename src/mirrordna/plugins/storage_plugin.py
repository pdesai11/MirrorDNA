"""
Storage plugin base class.
"""

from abc import abstractmethod
from typing import Dict, List, Any, Optional

from .base import Plugin, PluginType, PluginMetadata
from ..storage import StorageAdapter


class StoragePlugin(Plugin, StorageAdapter):
    """
    Base class for storage backend plugins.

    Combines Plugin interface with StorageAdapter interface.
    """

    def get_metadata(self) -> PluginMetadata:
        """
        Get plugin metadata.

        Subclasses should override to provide specific metadata.
        """
        return PluginMetadata(
            name=self.__class__.__name__,
            version="1.0.0",
            plugin_type=PluginType.STORAGE,
            description="Storage backend plugin"
        )

    @abstractmethod
    def connect(self) -> bool:
        """
        Connect to storage backend.

        Returns:
            True if connection successful
        """
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect from storage backend."""
        pass

    def initialize(self) -> None:
        """Initialize storage plugin."""
        self.connect()

    def cleanup(self) -> None:
        """Cleanup storage plugin."""
        self.disconnect()

    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on storage backend.

        Returns:
            Health check results
        """
        return {
            "status": "healthy" if self.is_initialized() else "unhealthy",
            "backend": self.get_metadata().name
        }
