"""
Test: Skeleton Architecture Validation (Milestone 1)
Verifies all skeleton modules import cleanly and all stubbed methods
raise NotImplementedError as expected.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest


class TestEngineSkeletons:
    def test_state_engine_imports(self):
        from backend.engine.state_engine import ProjectStateEngine
        from backend.engine.artifact_registry import ArtifactRegistry
        reg = ArtifactRegistry()
        engine = ProjectStateEngine(artifact_registry=reg)
        state = engine.create_project("Test", "Test project")
        assert state.title == "Test"

    def test_state_engine_get_state(self):
        from backend.engine.state_engine import ProjectStateEngine
        from backend.engine.artifact_registry import ArtifactRegistry
        reg = ArtifactRegistry()
        engine = ProjectStateEngine(artifact_registry=reg)
        engine.create_project("Test", "Test project")
        state = engine.get_state()
        assert state.title == "Test"

    def test_artifact_registry_imports(self):
        from backend.engine.artifact_registry import ArtifactRegistry
        registry = ArtifactRegistry()
        assert registry.count == 0

    def test_dependency_graph_imports(self):
        from backend.engine.dependency_graph import DependencyGraph
        graph = DependencyGraph()
        assert graph.node_count == 0

    def test_dependency_graph_invalidate(self):
        from backend.engine.dependency_graph import DependencyGraph
        graph = DependencyGraph()
        graph.create_node("art-001", "STORY_OUTLINE")
        invalidated = graph.invalidate("art-001", "hairstyle changed")
        assert isinstance(invalidated, set)

    def test_version_graph_imports(self):
        """VersionGraph is fully implemented (Milestone 4) — record_version returns a VersionEntry."""
        from backend.engine.version_graph import VersionGraph
        from backend.contracts.version import VersionEntry
        vg = VersionGraph()
        entry = vg.record_version("art-001", {"title": "Draft"}, {}, created_by="test")
        assert isinstance(entry, VersionEntry)
        assert entry.version_number == 1
        assert entry.artifact_id == "art-001"

    def test_version_graph_rollback_stub(self):
        """VersionGraph rollback is fully implemented — rollback creates a new non-destructive version."""
        from backend.engine.version_graph import VersionGraph
        vg = VersionGraph()
        vg.record_version("art-001", {"title": "V1"}, {})
        vg.record_version("art-001", {"title": "V2"}, {})
        result = vg.rollback("art-001", target_version=1)
        assert result.version_number == 3
        assert result.rollback_of == 1

    def test_event_bus_imports(self):
        """EventBus is fully implemented (Milestone 5) — publish delivers to listeners."""
        from backend.engine.event_bus import EventBus
        from backend.contracts.event import Event, EventType
        bus = EventBus()
        received = []
        bus.subscribe(EventType.GOAL_PUBLISHED, lambda e: received.append(e))
        bus.publish(Event(event_type=EventType.GOAL_PUBLISHED, project_id="p1"))
        assert len(received) == 1
        assert received[0].project_id == "p1"

    def test_context_engine_imports(self):
        """ContextEngine is fully implemented (Milestone 6) — build_context returns an AgentContext."""
        from backend.engine.context_engine import ContextEngine
        from backend.contracts.task import Task
        from backend.contracts.context import AgentContext
        engine = ContextEngine()
        task = Task(goal_id="g1", target_agent_type="STORY", action_type="DRAFT_SCENE")
        ctx = engine.build_context(task)
        assert isinstance(ctx, AgentContext)
        assert ctx.target_agent_type == "STORY"
        assert ctx.action_type == "DRAFT_SCENE"

    def test_scheduler_imports(self):
        """TaskScheduler is fully implemented (Milestone 7) — dispatch_next dispatches ready tasks."""
        from backend.engine.scheduler import TaskScheduler
        from backend.engine.task_registry import TaskRegistry
        from backend.engine.dependency_graph import DependencyGraph
        from backend.contracts.task import Task
        t_reg = TaskRegistry()
        d_graph = DependencyGraph()
        scheduler = TaskScheduler(task_registry=t_reg, dependency_graph=d_graph)
        task = Task(goal_id="g1", target_agent_type="STORY", action_type="DRAFT")
        scheduler.schedule_task(task)
        dispatched = scheduler.dispatch_next()
        assert dispatched is not None
        assert dispatched.task_id == task.task_id


class TestCapabilitySkeletons:
    def test_registry_imports(self):
        """CapabilityRegistry is fully implemented (M8) — resolves MockTextProvider correctly."""
        from backend.capabilities.registry import CapabilityRegistry
        from backend.capabilities.providers.mock_text_provider import MockTextProvider
        from backend.contracts.capability import CapabilityType, ToolRequest

        reg = CapabilityRegistry()
        reg.register_provider(CapabilityType.GENERATE_TEXT, MockTextProvider())

        request = ToolRequest(
            capability_type=CapabilityType.GENERATE_TEXT,
            parameters={"prompt": "test"},
        )
        resolved = reg.resolve(request)
        assert resolved.capability_type == CapabilityType.GENERATE_TEXT
        assert resolved.provider_name == "mock_text_provider"


    def test_base_provider_is_abstract(self):
        from backend.capabilities.providers.base_provider import BaseProvider
        with pytest.raises(TypeError):
            BaseProvider()  # Cannot instantiate abstract class


class TestAgentSkeletons:
    def test_base_agent_is_abstract(self):
        from backend.agents.base_agent import BaseAgent
        with pytest.raises(TypeError):
            BaseAgent()  # Cannot instantiate abstract class

    def test_project_manager_imports(self):
        from backend.agents.project_manager import ProjectManagerAgent
        agent = ProjectManagerAgent()
        assert agent.agent_id == "project_manager_agent"
        assert agent.agent_type == "PROJECT_MANAGER"

    def test_director_agent_imports(self):
        from backend.agents.director_agent import DirectorAgent
        agent = DirectorAgent()
        assert agent.agent_id == "director_agent"
        assert agent.agent_type == "DIRECTOR"

    def test_story_agent_imports(self):
        from backend.agents.story_agent import StoryAgent
        agent = StoryAgent()
        assert agent.agent_id == "story_agent"
        assert agent.agent_type == "STORY"

    def test_character_agent_imports(self):
        from backend.agents.character_agent import CharacterAgent
        agent = CharacterAgent()
        assert agent.agent_id == "character_agent"
        assert agent.agent_type == "CHARACTER"

    def test_image_agent_imports(self):
        from backend.agents.image_agent import ImageAgent
        agent = ImageAgent()
        assert agent.agent_id == "image_agent"
        assert agent.agent_type == "IMAGE"

    def test_creative_safety_agent_imports(self):
        from backend.agents.creative_safety_agent import CreativeSafetyAgent
        agent = CreativeSafetyAgent()
        assert agent.agent_id == "creative_safety_agent"
        assert agent.agent_type == "CREATIVE_SAFETY"

    @pytest.mark.asyncio
    async def test_agent_execute_raises_not_implemented(self):
        from backend.agents.story_agent import StoryAgent
        from backend.contracts.context import AgentContext
        agent = StoryAgent()
        ctx = AgentContext(
            task_id="t-001", project_id="p-001", target_agent_type="STORY"
        )
        with pytest.raises(NotImplementedError):
            await agent.execute(ctx)
