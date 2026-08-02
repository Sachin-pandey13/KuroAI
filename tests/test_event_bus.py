"""
Test: Event Bus & Reactive Engine (Milestone 5)
Verifies Stages 1-4: Event Contracts, EventBus pub/sub, FIFO ordering, error isolation,
Atomic registration invariants, per-subsystem listener registration/unregistration,
and Integration Scenarios 1-6.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from backend.contracts.artifact import Artifact, ArtifactState, ArtifactType
from backend.contracts.event import Event, EventType
from backend.engine.artifact_registry import ArtifactRegistry
from backend.engine.dependency_graph import DependencyGraph
from backend.engine.event_bus import EventBus, EventDeliveryError
from backend.engine.state_engine import ProjectStateEngine
from backend.engine.version_graph import VersionGraph


@pytest.fixture
def bus() -> EventBus:
    return EventBus()


@pytest.fixture
def registry() -> ArtifactRegistry:
    return ArtifactRegistry()


@pytest.fixture
def version_graph() -> VersionGraph:
    return VersionGraph()


@pytest.fixture
def dep_graph() -> DependencyGraph:
    return DependencyGraph()


@pytest.fixture
def state_engine(registry) -> ProjectStateEngine:
    return ProjectStateEngine(artifact_registry=registry)


# =====================================================================
# Unit Tests — EventBus Core Mechanics
# =====================================================================


class TestEventBusCore:
    def test_subscribe_and_publish(self, bus):
        received = []
        bus.subscribe(EventType.GOAL_PUBLISHED, lambda e: received.append(e))

        event = Event(event_type=EventType.GOAL_PUBLISHED, project_id="p1")
        bus.publish(event)

        assert len(received) == 1
        assert received[0].event_id == event.event_id
        assert received[0].project_id == "p1"

    def test_publish_no_listeners(self, bus):
        event = Event(event_type=EventType.TASK_COMPLETED, project_id="p1")
        bus.publish(event)  # Should not raise
        assert len(bus.get_history()) == 1
        assert bus.get_history()[0].delivered_to == 0

    def test_multiple_listeners_same_type_invoked_in_fifo_order(self, bus):
        order = []
        bus.subscribe(EventType.ARTIFACT_REGISTERED, lambda e: order.append("listener_1"))
        bus.subscribe(EventType.ARTIFACT_REGISTERED, lambda e: order.append("listener_2"))
        bus.subscribe(EventType.ARTIFACT_REGISTERED, lambda e: order.append("listener_3"))

        bus.publish(Event(event_type=EventType.ARTIFACT_REGISTERED, project_id="p1"))

        assert order == ["listener_1", "listener_2", "listener_3"]

    def test_unsubscribe(self, bus):
        received = []

        def callback(e):
            return received.append(e)

        bus.subscribe(EventType.GOAL_UPDATED, callback)
        assert bus.listener_count(EventType.GOAL_UPDATED) == 1

        bus.unsubscribe(EventType.GOAL_UPDATED, callback)
        assert bus.listener_count(EventType.GOAL_UPDATED) == 0

        bus.publish(Event(event_type=EventType.GOAL_UPDATED, project_id="p1"))
        assert len(received) == 0

    def test_publish_wrong_type_not_called(self, bus):
        received = []
        bus.subscribe(EventType.GOAL_PUBLISHED, lambda e: received.append(e))

        bus.publish(Event(event_type=EventType.TASK_SCHEDULED, project_id="p1"))
        assert len(received) == 0

    def test_event_log_recorded(self, bus):
        bus.subscribe(EventType.STATE_DELTA_MUTATED, lambda e: None)
        bus.publish(Event(event_type=EventType.STATE_DELTA_MUTATED, project_id="p1"))

        history = bus.get_history()
        assert len(history) == 1
        assert history[0].event.event_type == EventType.STATE_DELTA_MUTATED
        assert history[0].delivered_to == 1
        assert history[0].errors == []

    def test_get_history_by_type(self, bus):
        bus.publish(Event(event_type=EventType.GOAL_PUBLISHED, project_id="p1"))
        bus.publish(Event(event_type=EventType.GOAL_UPDATED, project_id="p1"))
        bus.publish(Event(event_type=EventType.GOAL_PUBLISHED, project_id="p1"))

        published = bus.get_history_by_type(EventType.GOAL_PUBLISHED)
        updated = bus.get_history_by_type(EventType.GOAL_UPDATED)

        assert len(published) == 2
        assert len(updated) == 1

    def test_clear_history(self, bus):
        bus.publish(Event(event_type=EventType.GOAL_PUBLISHED, project_id="p1"))
        assert len(bus.get_history()) == 1
        bus.clear_history()
        assert len(bus.get_history()) == 0

    def test_listener_error_isolation(self, bus):
        call_tracker = []

        def failing_listener(e):
            call_tracker.append("failing")
            raise RuntimeError("Listener crashed!")

        def succeeding_listener(e):
            call_tracker.append("succeeding")

        bus.subscribe(EventType.ARTIFACT_UPDATED, failing_listener)
        bus.subscribe(EventType.ARTIFACT_UPDATED, succeeding_listener)

        with pytest.raises(EventDeliveryError) as exc_info:
            bus.publish(Event(event_type=EventType.ARTIFACT_UPDATED, project_id="p1"))

        # Crucial guarantee: succeeding listener still ran!
        assert call_tracker == ["failing", "succeeding"]
        assert len(exc_info.value.errors) == 1
        assert "Listener crashed!" in exc_info.value.errors[0]

        # Audit log reflects failure
        history = bus.get_history()
        assert len(history) == 1
        assert history[0].delivered_to == 2
        assert len(history[0].errors) == 1

    def test_listener_count(self, bus):
        assert bus.listener_count(EventType.ARTIFACT_REGISTERED) == 0
        bus.subscribe(EventType.ARTIFACT_REGISTERED, lambda e: None)
        assert bus.listener_count(EventType.ARTIFACT_REGISTERED) == 1


# =====================================================================
# Atomic Invariant Test
# =====================================================================


class TestAtomicInvariants:
    def test_registration_atomic_invariant(self, bus, registry, version_graph):
        """
        Verify invariant: When ARTIFACT_REGISTERED is published,
        Artifact exists in registry AND V1 history exists in VersionGraph.
        """
        event_received_data = {}

        def check_invariant_listener(event):
            art_id = event.target_artifact_id
            # Invariant check inside event handler!
            event_received_data["exists_in_registry"] = registry.exists(art_id)
            event_received_data["has_version_history"] = version_graph.has_history(art_id)
            event_received_data["v1_version_num"] = version_graph.get_latest(art_id).version_number

        bus.subscribe(EventType.ARTIFACT_REGISTERED, check_invariant_listener)

        art = Artifact(
            artifact_id="art-atomic-01",
            project_id="p-01",
            artifact_type=ArtifactType.STORY_OUTLINE,
            owner_agent="story_agent",
            data={"title": "Atomic Outline"},
        )

        # Execute atomic registration
        registry.register(art, version_graph=version_graph, event_bus=bus)

        # Verify invariant was satisfied AT THE MOMENT the event listener executed
        assert event_received_data["exists_in_registry"] is True
        assert event_received_data["has_version_history"] is True
        assert event_received_data["v1_version_num"] == 1


# =====================================================================
# Integration Scenarios 1 to 6
# =====================================================================


class TestIntegrationScenarios:

    def test_scenario_1_registration_cascade(self, bus, registry, dep_graph):
        """
        Scenario 1: Registration cascade.
        Register artifact in registry -> ARTIFACT_REGISTERED event -> DependencyGraph node created automatically.
        """
        dep_graph.register_listeners(bus)

        art = Artifact(
            artifact_id="scene-01",
            project_id="p1",
            artifact_type=ArtifactType.SCENE_SCRIPT,
            owner_agent="story_agent",
        )

        registry.register(art, event_bus=bus)

        # Verify DependencyGraph created node reactively
        assert dep_graph.has_node("scene-01") is True
        assert dep_graph.get_node("scene-01").artifact_type == ArtifactType.SCENE_SCRIPT.value

    def test_scenario_2_invalidation_cascade(self, bus, dep_graph):
        """
        Scenario 2: Invalidation cascade.
        DependencyGraph invalidates Story -> ARTIFACT_INVALIDATED event -> Scene & Prompt marked STALE.
        """
        dep_graph.register_listeners(bus)

        dep_graph.create_node("Story", "STORY_OUTLINE")
        dep_graph.create_node("Scene", "SCENE_SCRIPT")
        dep_graph.create_node("Prompt", "PANEL_PROMPT")

        dep_graph.connect("Story", "Scene")
        dep_graph.connect("Scene", "Prompt")

        # Invalidate Story
        dep_graph.invalidate("Story", reason="Plot revision", event_bus=bus)

        assert dep_graph.get_node("Story").state == ArtifactState.ACTIVE
        assert dep_graph.get_node("Scene").state == ArtifactState.STALE
        assert dep_graph.get_node("Prompt").state == ArtifactState.STALE

        # Check event history
        history = bus.get_history_by_type(EventType.ARTIFACT_INVALIDATED)
        assert len(history) == 1
        assert history[0].event.target_artifact_id == "Story"

    def test_scenario_3_update_cascade(self, bus, registry, version_graph, dep_graph):
        """
        Scenario 3: Update cascade.
        Artifact updated -> ARTIFACT_UPDATED published -> VersionGraph records V2 snapshot + DependencyGraph invalidates downstream.
        """
        registry.register_listeners(bus)
        version_graph.register_listeners(bus)
        dep_graph.register_listeners(bus)

        # Setup initial DAG and artifact
        dep_graph.create_node("Char", "CHARACTER_PROFILE")
        dep_graph.create_node("Prompt", "PANEL_PROMPT")
        dep_graph.connect("Char", "Prompt")

        char_art = Artifact(
            artifact_id="Char",
            project_id="p1",
            artifact_type=ArtifactType.CHARACTER_PROFILE,
            owner_agent="character_agent",
            data={"hair": "black"},
        )
        registry.register(char_art, version_graph=version_graph)

        # Update data via registry (which publishes ARTIFACT_UPDATED)
        reg_with_bus = ArtifactRegistry(event_bus=bus)
        reg_with_bus._store = registry._store
        reg_with_bus.update_data("Char", {"hair": "red"})

        # Verify VersionGraph recorded V2 snapshot reactively
        assert version_graph.get_latest("Char").version_number == 2
        assert version_graph.get_latest("Char").data_snapshot["hair"] == "red"

        # Verify DependencyGraph marked downstream Prompt STALE reactively
        assert dep_graph.get_node("Prompt").state == ArtifactState.STALE

    def test_scenario_4_rollback_cascade(self, bus, registry, version_graph, dep_graph):
        """
        Scenario 4: Rollback cascade.
        VersionGraph performs rollback -> ARTIFACT_ROLLED_BACK published -> Registry payload restored + DependencyGraph invalidates downstream.
        """
        registry.register_listeners(bus)
        dep_graph.register_listeners(bus)

        dep_graph.create_node("Scene", "SCENE_SCRIPT")
        dep_graph.create_node("Image", "GENERATED_IMAGE")
        dep_graph.connect("Scene", "Image")

        scene_art = Artifact(
            artifact_id="Scene",
            project_id="p1",
            artifact_type=ArtifactType.SCENE_SCRIPT,
            owner_agent="story_agent",
            data={"draft": "v1 text"},
        )
        registry.register(scene_art)

        version_graph.record_version("Scene", {"draft": "v1 text"}, {})
        version_graph.record_version("Scene", {"draft": "v2 text"}, {})

        # Perform rollback (which emits ARTIFACT_ROLLED_BACK)
        v3 = version_graph.rollback("Scene", target_version=1, event_bus=bus, project_id="p1")

        assert v3.version_number == 3
        assert v3.rollback_of == 1

        # Verify Registry payload was restored by listener
        assert registry.get("Scene").data["draft"] == "v1 text"
        assert registry.get("Scene").current_version == 3

        # Verify DependencyGraph marked downstream Image STALE by listener
        assert dep_graph.get_node("Image").state == ArtifactState.STALE

    def test_scenario_5_nested_event_chain(self, bus):
        """
        Scenario 5: Multi-tier nested event chain (A -> B -> C).
        Listener for Event A publishes Event B.
        Listener for Event B publishes Event C.
        Verify FIFO ordering, complete history logging, and no recursion errors.
        """
        chain_order = []

        def listener_a(event):
            chain_order.append("A_received")
            bus.publish(Event(event_type=EventType.GOAL_UPDATED, project_id="p1"))

        def listener_b(event):
            chain_order.append("B_received")
            bus.publish(Event(event_type=EventType.TASK_SCHEDULED, project_id="p1"))

        def listener_c(event):
            chain_order.append("C_received")

        bus.subscribe(EventType.GOAL_PUBLISHED, listener_a)
        bus.subscribe(EventType.GOAL_UPDATED, listener_b)
        bus.subscribe(EventType.TASK_SCHEDULED, listener_c)

        bus.publish(Event(event_type=EventType.GOAL_PUBLISHED, project_id="p1"))

        # Verify execution completed in deterministic sequence
        assert chain_order == ["A_received", "B_received", "C_received"]

        # Verify history captured all 3 events (nested publish appends as stack unwinds)
        history = bus.get_history()
        assert len(history) == 3
        history_types = [h.event.event_type for h in history]
        assert EventType.GOAL_PUBLISHED in history_types
        assert EventType.GOAL_UPDATED in history_types
        assert EventType.TASK_SCHEDULED in history_types

    def test_scenario_6_error_isolation_in_reactive_network(self, bus, registry, dep_graph):
        """
        Scenario 6: Error isolation in reactive network.
        One crashing listener does not prevent other listeners or subsystem reactions.
        """
        dep_graph.register_listeners(bus)

        def crashing_listener(event):
            raise ValueError("Crashing analytics listener!")

        bus.subscribe(EventType.ARTIFACT_REGISTERED, crashing_listener)

        art = Artifact(
            artifact_id="art-error-test",
            project_id="p1",
            artifact_type=ArtifactType.WORLD_LORE,
            owner_agent="story_agent",
        )

        with pytest.raises(EventDeliveryError):
            registry.register(art, event_bus=bus)

        # Verify that despite crashing_listener raising ValueError,
        # DependencyGraph's listener still ran and created the node!
        assert dep_graph.has_node("art-error-test") is True
