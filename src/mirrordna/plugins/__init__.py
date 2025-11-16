"""
MirrorDNA Plugin System

Extensible plugin architecture for storage adapters, validators, and event handlers.
"""

from .base import Plugin, PluginType, PluginMetadata
from .registry import PluginRegistry, get_registry
from .storage_plugin import StoragePlugin
from .validator_plugin import ValidatorPlugin
from .event_plugin import EventPlugin

# Global registry instance
registry = get_registry()

__all__ = [
    "Plugin",
    "PluginType",
    "PluginMetadata",
    "PluginRegistry",
    "get_registry",
    "registry",
    "StoragePlugin",
    "ValidatorPlugin",
    "EventPlugin",
]
