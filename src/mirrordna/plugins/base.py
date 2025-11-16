"""
Base plugin classes and interfaces.
"""

from abc import ABC, abstractmethod
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
import importlib
import sys


class PluginType(Enum):
    """Types of plugins supported."""
    STORAGE = "storage"
    VALIDATOR = "validator"
    EVENT_HANDLER = "event_handler"
    CUSTOM = "custom"


@dataclass
class PluginMetadata:
    """Metadata for a plugin."""
    name: str
    version: str
    plugin_type: PluginType
    description: str = ""
    author: str = ""
    requires: List[str] = field(default_factory=list)
    config_schema: Optional[Dict[str, Any]] = None
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "version": self.version,
            "plugin_type": self.plugin_type.value,
            "description": self.description,
            "author": self.author,
            "requires": self.requires,
            "config_schema": self.config_schema,
            "tags": self.tags
        }


class Plugin(ABC):
    """
    Base class for all plugins.

    Plugins must implement:
    - get_metadata(): Return plugin metadata
    - initialize(): Setup plugin
    - cleanup(): Cleanup resources
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize plugin with configuration.

        Args:
            config: Plugin configuration dictionary
        """
        self.config = config or {}
        self._initialized = False

    @abstractmethod
    def get_metadata(self) -> PluginMetadata:
        """
        Get plugin metadata.

        Returns:
            PluginMetadata instance
        """
        pass

    @abstractmethod
    def initialize(self) -> None:
        """
        Initialize the plugin.

        Called when plugin is loaded. Setup connections, validate config, etc.
        """
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """
        Cleanup plugin resources.

        Called when plugin is unloaded. Close connections, release resources, etc.
        """
        pass

    def validate_config(self) -> bool:
        """
        Validate plugin configuration.

        Returns:
            True if config is valid

        Raises:
            ValueError: If configuration is invalid
        """
        metadata = self.get_metadata()

        if metadata.config_schema:
            # Could integrate with jsonschema validator here
            # For now, basic validation
            pass

        return True

    def is_initialized(self) -> bool:
        """Check if plugin is initialized."""
        return self._initialized

    def __enter__(self):
        """Context manager entry."""
        if not self._initialized:
            self.initialize()
            self._initialized = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.cleanup()
        self._initialized = False


def load_plugin_from_module(module_path: str, class_name: str, config: Optional[Dict[str, Any]] = None) -> Plugin:
    """
    Dynamically load a plugin from a module.

    Args:
        module_path: Python module path (e.g., "mirrordna.plugins.postgresql")
        class_name: Name of the plugin class
        config: Optional configuration

    Returns:
        Instantiated plugin

    Raises:
        ImportError: If module cannot be imported
        AttributeError: If class not found in module
        TypeError: If class is not a Plugin subclass
    """
    try:
        module = importlib.import_module(module_path)
    except ImportError as e:
        raise ImportError(f"Failed to import module '{module_path}': {e}")

    try:
        plugin_class = getattr(module, class_name)
    except AttributeError:
        raise AttributeError(f"Class '{class_name}' not found in module '{module_path}'")

    if not issubclass(plugin_class, Plugin):
        raise TypeError(f"Class '{class_name}' is not a Plugin subclass")

    return plugin_class(config=config)


def discover_plugins_in_package(package_name: str) -> List[Plugin]:
    """
    Discover all plugins in a package.

    Args:
        package_name: Package to search (e.g., "mirrordna.plugins")

    Returns:
        List of discovered plugin classes (not instantiated)
    """
    plugins = []

    try:
        package = importlib.import_module(package_name)
    except ImportError:
        return plugins

    # Get all modules in package
    if hasattr(package, '__path__'):
        import pkgutil
        for importer, modname, ispkg in pkgutil.iter_modules(package.__path__):
            if not ispkg:
                try:
                    module = importlib.import_module(f"{package_name}.{modname}")

                    # Find Plugin subclasses
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (isinstance(attr, type) and
                            issubclass(attr, Plugin) and
                            attr is not Plugin):
                            plugins.append(attr)
                except ImportError:
                    continue

    return plugins
