from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from backend.contracts.event import Event, EventLog, EventType

EventListener = Callable[[Event], None]


class EventDeliveryError(Exception):
    """
    Raised after event delivery completes if one or more listeners raised exceptions.
    Delivery to remaining listeners is NOT interrupted.
    """

    def __init__(self, errors: List[str]):
        self.errors = errors
        super().__init__(
            f"{len(errors)} listener(s) failed during event delivery: {'; '.join(errors)}"
        )


class EventBus:
    """
    In-process event publish/subscribe mechanism with deterministic FIFO ordering,
    error isolation, and auditing history.

    Guarantees:
    - Listeners are invoked in subscription order (FIFO).
    - Errors in one listener do not prevent delivery to other registered listeners.
    - Supports nested publishing (listeners triggering new events during execution).
    """

    def __init__(self) -> None:
        self._listeners: Dict[EventType, List[EventListener]] = {}
        self._history: List[EventLog] = []

    def subscribe(self, event_type: EventType, listener: EventListener) -> None:
        """Register a listener for a specific event type in FIFO order."""
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        if listener not in self._listeners[event_type]:
            self._listeners[event_type].append(listener)

    def unsubscribe(self, event_type: EventType, listener: EventListener) -> None:
        """Remove a previously registered listener."""
        if event_type in self._listeners:
            self._listeners[event_type] = [
                listener_func
                for listener_func in self._listeners[event_type]
                if listener_func != listener
            ]

    def publish(self, event: Any, payload: Optional[Any] = None) -> None:
        """
        Emit an event to all registered listeners in FIFO order.
        Collects errors across all listeners and raises EventDeliveryError at completion if any failed.
        Accepts either an Event instance or (event_type, payload).
        """
        if isinstance(event, Event):
            event_obj = event
        else:
            event_obj = Event(event_type=event, payload=payload or {})

        listeners = list(self._listeners.get(event_obj.event_type, []))
        errors: List[str] = []

        for listener in listeners:
            try:
                listener(event_obj)
            except Exception as e:
                errors.append(str(e))

        log_entry = EventLog(
            event=event,
            delivered_to=len(listeners),
            errors=errors,
            logged_at=datetime.utcnow(),
        )
        self._history.append(log_entry)

        if errors:
            raise EventDeliveryError(errors)

    def get_listeners(self, event_type: EventType) -> List[EventListener]:
        """Return a copy of all listeners registered for a given event type."""
        return list(self._listeners.get(event_type, []))

    def listener_count(self, event_type: EventType) -> int:
        """Return the number of listeners subscribed to a specific event type."""
        return len(self._listeners.get(event_type, []))

    def get_history(self) -> List[EventLog]:
        """Return full ordered delivery history."""
        return list(self._history)

    def get_history_by_type(self, event_type: EventType) -> List[EventLog]:
        """Return delivery history filtered by EventType."""
        return [entry for entry in self._history if entry.event.event_type == event_type]

    def clear_history(self) -> None:
        """Clear event delivery history."""
        self._history.clear()
