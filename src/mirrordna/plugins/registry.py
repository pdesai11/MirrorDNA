"""
Plugin registry for managing installed plugins.
"""

from typing import Dict, List, Optional, Type, Any
from pathlib import Path
import json

from .base import Plugin, PluginType, PluginMetadata
from ..exceptions import InvalidDataFormatError


class PluginRegistry:
    """
    Central registry for managing plugins.

    Singleton pattern ensures one global registry.
    """

    _instance: Optional['PluginRegistry'] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._plugins: Dict[str, Plugin] = {}
        self._plugin_classes: Dict[str, Type[Plugin]] = {}
        self._metadata_cache: Dict[str, PluginMetadata] = {}
        self._initialized = True

    def register_plugin_class(self, plugin_class: Type[Plugin], name: Optional[str] = None):
        """
        Register a plugin class.

        Args:
            plugin_class: Plugin class to register
            name: Optional name (defaults to class name)
        """
        if not issubclass(plugin_class, Plugin):
            raise TypeError(f"{plugin_class} is not a Plugin subclass")

        plugin_name = name or plugin_class.__name__
        self._plugin_classes[plugin_name] = plugin_class

    def register_plugin(self, plugin: Plugin, name: Optional[str] = None):
        """
        Register an instantiated plugin.

        Args:
            plugin: Plugin instance to register
            name: Optional name (defaults to metadata name)
        """
        metadata = plugin.get_metadata()
        plugin_name = name or metadata.name

        self._plugins[plugin_name] = plugin
        self._metadata_cache[plugin_name] = metadata

    def unregister_plugin(self, name: str):
        """
        Unregister a plugin.

        Args:
            name: Plugin name to unregister
        """
        if name in self._plugins:
            plugin = self._plugins[name]
            if plugin.is_initialized():
                plugin.cleanup()
            del self._plugins[name]

        if name in self._metadata_cache:
            del self._metadata_cache[name]

        if name in self._plugin_classes:
            del self._plugin_classes[name]

    def get_plugin(self, name: str) -> Optional[Plugin]:
        """
        Get a registered plugin by name.

        Args:
            name: Plugin name

        Returns:
            Plugin instance or None
        """
        return self._plugins.get(name)

    def get_plugin_class(self, name: str) -> Optional[Type[Plugin]]:
        """
        Get a registered plugin class by name.

        Args:
            name: Plugin class name

        Returns:
            Plugin class or None
        """
        return self._plugin_classes.get(name)

    def create_plugin(self, name: str, config: Optional[Dict[str, Any]] = None) -> Plugin:
        """
        Create a plugin instance from registered class.

        Args:
            name: Plugin class name
            config: Plugin configuration

        Returns:
            Instantiated plugin

        Raises:
            ValueError: If plugin class not found
        """
        plugin_class = self.get_plugin_class(name)
        if not plugin_class:
            raise ValueError(f"Plugin class '{name}' not registered")

        plugin = plugin_class(config=config)
        self.register_plugin(plugin, name)
        return plugin

    def list_plugins(self, plugin_type: Optional[PluginType] = None) -> List[str]:
        """
        List registered plugin names.

        Args:
            plugin_type: Optional filter by plugin type

        Returns:
            List of plugin names
        """
        if plugin_type is None:
            return list(self._plugins.keys())

        result = []
        for name, metadata in self._metadata_cache.items():
            if metadata.plugin_type == plugin_type:
                result.append(name)

        return result

    def get_metadata(self, name: str) -> Optional[PluginMetadata]:
        """
        Get plugin metadata.

        Args:
            name: Plugin name

        Returns:
            PluginMetadata or None
        """
        return self._metadata_cache.get(name)

    def initialize_all(self):
        """Initialize all registered plugins."""
        for name, plugin in self._plugins.items():
            if not plugin.is_initialized():
                try:
                    plugin.initialize()
                    plugin._initialized = True
                except Exception as e:
                    print(f"Failed to initialize plugin '{name}': {e}")

    def cleanup_all(self):
        """Cleanup all registered plugins."""
        for plugin in self._plugins.values():
            if plugin.is_initialized():
                try:
                    plugin.cleanup()
                    plugin._initialized = False
                except Exception as e:
                    print(f"Failed to cleanup plugin: {e}")

    def export_metadata(self, filepath: Path):
        """
        Export plugin metadata to JSON file.

        Args:
            filepath: Output file path
        """
        data = {
            "plugins": {
                name: metadata.to_dict()
                for name, metadata in self._metadata_cache.items()
            }
        }

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

    def load_plugin_config(self, filepath: Path) -> Dict[str, Any]:
        """
        Load plugin configuration from file.

        Args:
            filepath: Config file path

        Returns:
            Configuration dictionary
        """
        if not filepath.exists():
            raise FileNotFoundError(f"Config file not found: {filepath}")

        with open(filepath, 'r') as f:
            return json.load(f)


# Global registry accessor
_registry: Optional[PluginRegistry] = None


def get_registry() -> PluginRegistry:
    """Get the global plugin registry."""
    global _registry
    if _registry is None:
        _registry = PluginRegistry()
    return _registry


def reset_registry():
    """Reset the global registry (mainly for testing)."""
    global _registry
    if _registry:
        _registry.cleanup_all()
    _registry = None
