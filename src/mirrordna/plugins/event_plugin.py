"""
Event handler plugin base class.
"""

from abc import abstractmethod
from typing import Dict, Any, Callable, List

from .base import Plugin, PluginType, PluginMetadata


class EventPlugin(Plugin):
    """
    Base class for event handler plugins.

    Allows custom handlers to be registered for timeline events,
    identity creation, session start/end, etc.
    """

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize event plugin."""
        super().__init__(config)
        self._handlers: Dict[str, List[Callable]] = {}

    def get_metadata(self) -> PluginMetadata:
        """Get event plugin metadata."""
        return PluginMetadata(
            name=self.__class__.__name__,
            version="1.0.0",
            plugin_type=PluginType.EVENT_HANDLER,
            description="Event handler plugin"
        )

    @abstractmethod
    def get_supported_events(self) -> List[str]:
        """
        Get list of supported event types.

        Returns:
            List of event type names
        """
        pass

    @abstractmethod
    def handle_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """
        Handle an event.

        Args:
            event_type: Type of event
            event_data: Event data payload
        """
        pass

    def register_handler(self, event_type: str, handler: Callable):
        """
        Register a handler for an event type.

        Args:
            event_type: Event type to handle
            handler: Handler function
        """
        if event_type not in self._handlers:
            self._handlers[event_type] = []

        self._handlers[event_type].append(handler)

    def unregister_handler(self, event_type: str, handler: Callable):
        """
        Unregister an event handler.

        Args:
            event_type: Event type
            handler: Handler to remove
        """
        if event_type in self._handlers:
            self._handlers[event_type].remove(handler)

    def emit_event(self, event_type: str, event_data: Dict[str, Any]):
        """
        Emit an event to registered handlers.

        Args:
            event_type: Event type
            event_data: Event data
        """
        if event_type in self._handlers:
            for handler in self._handlers[event_type]:
                try:
                    handler(event_data)
                except Exception as e:
                    print(f"Event handler failed: {e}")

    def initialize(self) -> None:
        """Initialize event plugin."""
        pass

    def cleanup(self) -> None:
        """Cleanup event plugin."""
        self._handlers.clear()
