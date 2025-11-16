"""
Validator plugin base class.
"""

from abc import abstractmethod
from typing import Any, Dict

from .base import Plugin, PluginType, PluginMetadata


class ValidatorPlugin(Plugin):
    """Base class for custom validator plugins."""

    def get_metadata(self) -> PluginMetadata:
        """Get validator plugin metadata."""
        return PluginMetadata(
            name=self.__class__.__name__,
            version="1.0.0",
            plugin_type=PluginType.VALIDATOR,
            description="Custom validator plugin"
        )

    @abstractmethod
    def validate(self, data: Dict[str, Any]) -> bool:
        """
        Validate data according to custom rules.

        Args:
            data: Data to validate

        Returns:
            True if valid

        Raises:
            ValidationError: If data is invalid
        """
        pass

    def initialize(self) -> None:
        """Initialize validator."""
        pass

    def cleanup(self) -> None:
        """Cleanup validator."""
        pass
