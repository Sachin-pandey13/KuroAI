from typing import Callable, Dict, List, Any
from backend.contracts.event import Event, EventType


# Type alias for event listener callbacks
EventListener = Callable[[Event], None]


class EventBus:
    """
    Abstract in-process event pub/sub mechanism.
    Initially synchronous in-process. Backend can be swapped to
    Redis Streams, RabbitMQ, NATS, or Kafka without changing consumers.
    """

    def __init__(self):
        pass

    def publish(self, event: Event) -> None:
        """Emit an event to all registered listeners for its type."""
        raise NotImplementedError("EventBus.publish stub")

    def subscribe(self, event_type: EventType, listener: EventListener) -> None:
        """Register a listener for a specific event type."""
        raise NotImplementedError("EventBus.subscribe stub")

    def unsubscribe(self, event_type: EventType, listener: EventListener) -> None:
        """Remove a previously registered listener."""
        raise NotImplementedError("EventBus.unsubscribe stub")

    def get_listeners(self, event_type: EventType) -> List[EventListener]:
        """Return all listeners registered for a given event type."""
        raise NotImplementedError("EventBus.get_listeners stub")
