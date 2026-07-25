"""
Test: Agent Runtime & Specialized Agent Subsystem (Milestone 9)
Verifies Stages 1-7:
- AgentRegistry (storage & lookup)
- ToolExecutor injection (agents depend on interface, not CapabilityRegistry)
- RuntimeTransaction (atomic persistence commit & rollback)
- AgentRuntime coordinator (end-to-end task execution, batch execution, error cascade, single publisher rule)
- Specialized Agents (StoryAgent, ImageAgent execution with DecisionTrace & provenance)
"""
import sys
import os
import asyncio
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.contracts.task import Task, TaskPriority, TaskStatus
from backend.contracts.agent import AgentResult, BatchResult
from backend.contracts.event import Event, EventType
from backend.contracts.artifact import Artifact, ArtifactType, ArtifactState
from backend.contracts.capability import CapabilityType, ToolRequest, ToolResponse

from backend.engine.artifact_registry import ArtifactRegistry
from backend.engine.version_graph import VersionGraph
from backend.engine.dependency_graph import DependencyGraph
from backend.engine.event_bus import EventBus
from backend.engine.task_registry import TaskRegistry
from backend.engine.scheduler import TaskScheduler
from backend.capabilities.registry import CapabilityRegistry
from backend.capabilities.providers.mock_text_provider import MockTextProvider
from backend.capabilities.providers.mock_image_provider import MockImageProvider

from backend.agents.agent_registry import AgentRegistry, AgentNotFoundError, AgentAlreadyRegisteredError
from backend.agents.tool_executor import BaseToolExecutor, CapabilityToolExecutor, MockToolExecutor
from backend.agents.runtime_transaction import RuntimeTransaction, TransactionError
from backend.agents.runtime import AgentRuntime
from backend.agents.story_agent import StoryAgent
from backend.agents.image_agent import ImageAgent
from backend.agents.base_agent import BaseAgent


# =====================================================================
# Fixtures
# =====================================================================

@pytest.fixture
def artifact_registry():
    return ArtifactRegistry()


@pytest.fixture
def version_graph():
    return VersionGraph()


@pytest.fixture
def dependency_graph():
    return DependencyGraph()


@pytest.fixture
def event_bus():
    return EventBus()


@pytest.fixture
def task_registry():
    return TaskRegistry()


@pytest.fixture
def scheduler(task_registry, dependency_graph):
    return TaskScheduler(task_registry=task_registry, dependency_graph=dependency_graph)


@pytest.fixture
def capability_registry():
    reg = CapabilityRegistry()
    reg.register_provider(CapabilityType.GENERATE_TEXT, MockTextProvider())
    reg.register_provider(CapabilityType.GENERATE_IMAGE, MockImageProvider())
    return reg


@pytest.fixture
def agent_registry():
    reg = AgentRegistry()
    reg.register_agent(StoryAgent())
    reg.register_agent(ImageAgent())
    return reg


@pytest.fixture
def runtime(agent_registry, capability_registry, artifact_registry, version_graph, scheduler, event_bus):
    return AgentRuntime(
        agent_registry=agent_registry,
        capability_registry=capability_registry,
        artifact_registry=artifact_registry,
        version_graph=version_graph,
        task_scheduler=scheduler,
        event_bus=event_bus,
    )


# =====================================================================
# Unit Tests — AgentRegistry
# =====================================================================

class TestAgentRegistry:
    def test_register_and_lookup(self):
        reg = AgentRegistry()
        story = StoryAgent()
        reg.register_agent(story)
        assert reg.exists("STORY") is True
        assert reg.get_agent("STORY") == story

    def test_list_agents(self):
        reg = AgentRegistry()
        reg.register_agent(StoryAgent())
        reg.register_agent(ImageAgent())
        agents = reg.list_agents()
        assert "STORY" in agents
        assert "IMAGE" in agents

    def test_unregistered_agent_raises_error(self):
        reg = AgentRegistry()
        with pytest.raises(AgentNotFoundError):
            reg.get_agent("NON_EXISTENT")

    def test_duplicate_registration_raises_error(self):
        reg = AgentRegistry()
        reg.register_agent(StoryAgent())
        with pytest.raises(AgentAlreadyRegisteredError):
            reg.register_agent(StoryAgent())

    def test_replace_agent(self):
        reg = AgentRegistry()
        story1 = StoryAgent()
        story2 = StoryAgent()
        reg.register_agent(story1)
        reg.replace_agent(story2)
        assert reg.get_agent("STORY") == story2


# =====================================================================
# Unit Tests — ToolExecutor Injection
# =====================================================================

class TestToolExecutor:
    @pytest.mark.asyncio
    async def test_mock_tool_executor(self):
        executor = MockToolExecutor()
        req = ToolRequest(capability_type=CapabilityType.GENERATE_TEXT)
        resp = await executor.execute(req)
        assert resp.success is True
        assert executor.call_count == 1

    @pytest.mark.asyncio
    async def test_capability_tool_executor(self, capability_registry):
        executor = CapabilityToolExecutor(capability_registry)
        req = ToolRequest(
            capability_type=CapabilityType.GENERATE_TEXT,
            parameters={"prompt": "Write story beat"},
        )
        resp = await executor.execute(req)
        assert resp.success is True
        assert resp.provider_name == "mock_text_provider"


# =====================================================================
# Unit Tests — RuntimeTransaction
# =====================================================================

class TestRuntimeTransaction:
    def test_atomic_commit(self, artifact_registry, version_graph, event_bus):
        events_received = []
        event_bus.subscribe(
            EventType.ARTIFACT_CREATED,
            lambda e: events_received.append(e),
        )

        txn = RuntimeTransaction(
            artifact_registry=artifact_registry,
            version_graph=version_graph,
            state_engine=None,
            event_bus=event_bus,
        )

        art = Artifact(
            project_id="p1",
            artifact_type=ArtifactType.STORY_OUTLINE,
            owner_agent="story_agent",
            data={"text": "Scene 1"},
        )

        txn.stage_artifact(art)
        txn.stage_version(art.artifact_id, art.data, art.metadata, art.owner_agent)
        txn.stage_event(Event(project_id="p1", event_type=EventType.ARTIFACT_CREATED, source_agent_id="test", payload={"id": art.artifact_id}))

        txn.commit()

        # Check persisted
        assert artifact_registry.exists(art.artifact_id) is True
        assert version_graph.has_history(art.artifact_id) is True
        assert len(events_received) == 1

    def test_rollback_on_failure(self, artifact_registry, version_graph, event_bus):
        txn = RuntimeTransaction(
            artifact_registry=artifact_registry,
            version_graph=version_graph,
            state_engine=None,
            event_bus=event_bus,
        )

        art = Artifact(
            project_id="p1",
            artifact_type=ArtifactType.STORY_OUTLINE,
            owner_agent="story_agent",
        )

        txn.stage_artifact(art)
        txn._committed_artifact_ids.append(art.artifact_id)

        # Simulate rollback
        txn.rollback()
        assert artifact_registry.exists(art.artifact_id) is False


# =====================================================================
# Integration Tests — AgentRuntime & Specialized Agents
# =====================================================================

class TestAgentRuntimePipeline:
    @pytest.mark.asyncio
    async def test_story_agent_execution_pipeline(self, runtime, task_registry, artifact_registry, version_graph, event_bus):
        events = []
        for evt_type in [EventType.AGENT_STARTED, EventType.AGENT_COMPLETED, EventType.TASK_COMPLETED]:
            event_bus.subscribe(evt_type, lambda e: events.append(e.event_type))

        task = Task(
            goal_id="goal_story_1",
            target_agent_type="STORY",
            payload={"prompt": "Samurai action chapter", "project_id": "proj_manga"},
        )
        task_registry.register_task(task)

        result = await runtime.run_task(task)

        assert result.success is True
        assert result.agent_type == "STORY"
        assert len(result.produced_artifacts) == 1
        assert result.produced_artifacts[0].artifact_type == ArtifactType.STORY_OUTLINE
        assert result.decision_trace is not None

        # Verify artifacts saved to registries
        art_id = result.produced_artifacts[0].artifact_id
        assert artifact_registry.exists(art_id) is True
        assert version_graph.has_history(art_id) is True

        # Verify event sequence
        assert EventType.AGENT_STARTED in events
        assert EventType.AGENT_COMPLETED in events
        assert EventType.TASK_COMPLETED in events

    @pytest.mark.asyncio
    async def test_image_agent_execution_pipeline(self, runtime, task_registry, artifact_registry):
        task = Task(
            goal_id="goal_img_1",
            target_agent_type="IMAGE",
            payload={"prompt": "Cyberpunk cityscape", "width": 1024, "height": 1024},
        )
        task_registry.register_task(task)

        result = await runtime.run_task(task)

        assert result.success is True
        assert result.agent_type == "IMAGE"
        assert len(result.produced_artifacts) == 1
        assert result.produced_artifacts[0].artifact_type == ArtifactType.GENERATED_IMAGE
        assert "image_path" in result.produced_artifacts[0].data
        assert result.decision_trace.provenance.provider_name == "mock_image_provider"

    @pytest.mark.asyncio
    async def test_unregistered_agent_failure(self, runtime, task_registry, event_bus):
        events = []
        for evt_type in [EventType.AGENT_FAILED, EventType.TASK_FAILED]:
            event_bus.subscribe(evt_type, lambda e: events.append(e.event_type))

        task = Task(goal_id="g_unk", target_agent_type="UNKNOWN_AGENT")
        task_registry.register_task(task)

        result = await runtime.run_task(task)

        assert result.success is False
        assert "No agent registered for type 'UNKNOWN_AGENT'" in result.error_message
        assert EventType.AGENT_FAILED in events
        assert EventType.TASK_FAILED in events

    @pytest.mark.asyncio
    async def test_task_timeout_handling(self, runtime, agent_registry, task_registry):
        class SlowAgent(BaseAgent):
            @property
            def agent_id(self):
                return "slow_agent"

            @property
            def agent_type(self):
                return "SLOW"

            async def execute(self, context, tool_executor=None):
                await asyncio.sleep(0.5)
                return AgentResult(task_id=context.goal_id, agent_id=self.agent_id, agent_type=self.agent_type, success=True)

        agent_registry.register_agent(SlowAgent())

        task = Task(
            goal_id="g_timeout",
            target_agent_type="SLOW",
            execution_timeout=0.05,
        )
        task_registry.register_task(task)

        result = await runtime.run_task(task)
        assert result.success is False
        assert "timed out" in result.error_message

    @pytest.mark.asyncio
    async def test_batch_execution(self, runtime, task_registry):
        t1 = Task(goal_id="g_batch_1", target_agent_type="STORY")
        t2 = Task(goal_id="g_batch_2", target_agent_type="IMAGE")
        t3 = Task(goal_id="g_batch_3", target_agent_type="NON_EXISTENT")
        for t in [t1, t2, t3]:
            task_registry.register_task(t)

        batch_result = await runtime.run_batch([t1, t2, t3])

        assert isinstance(batch_result, BatchResult)
        assert batch_result.total_tasks == 3
        assert batch_result.success_count == 2
        assert batch_result.failure_count == 1
        assert batch_result.duration_ms > 0
