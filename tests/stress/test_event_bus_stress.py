"""
Stress test for EventBus under high-concurrency event publication.
"""

import threading
import pytest
from backend.contracts import EventType, Event
from backend.engine import EventBus


def test_event_bus_high_throughput():
    bus = EventBus()
    received_count = 0
    lock = threading.Lock()

    def handler(payload):
        nonlocal received_count
        with lock:
            received_count += 1

    bus.subscribe(EventType.ARTIFACT_REGISTERED, handler)

    num_threads = 10
    events_per_thread = 1000

    def worker():
        for i in range(events_per_thread):
            bus.publish(Event(event_type=EventType.ARTIFACT_REGISTERED, payload={"seq": i}))

    threads = [threading.Thread(target=worker) for _ in range(num_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert received_count == num_threads * events_per_thread
