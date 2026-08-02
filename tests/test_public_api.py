"""
API Stability Regression Test Suite for KuroAI v1.0 Release Candidate.

Asserts that all frozen public API methods on core subsystems exist, are callable,
and maintain stable interfaces.
"""

import pytest
from backend.engine.artifact_registry import ArtifactRegistry
from backend.engine.state_engine import ProjectStateEngine
from backend.engine.dependency_graph import DependencyGraph
from backend.engine.version_graph import VersionGraph
from backend.engine.event_bus import EventBus
from backend.engine.context_engine import ContextEngine
from backend.engine.task_registry import TaskRegistry
from backend.engine.scheduler import TaskScheduler
from backend.capabilities.registry import CapabilityRegistry
from backend.agents.runtime import AgentRuntime


class TestPublicAPIContracts:
    """Verifies public method existence on core subsystems."""

    def test_artifact_registry_public_api(self):
        public_methods = ["register", "get", "exists", "update_metadata", "update_data", "update_state", "list_all", "remove"]
        for method in public_methods:
            assert hasattr(ArtifactRegistry, method), f"ArtifactRegistry missing public method '{method}'"
            assert callable(getattr(ArtifactRegistry, method))

    def test_project_state_engine_public_api(self):
        public_methods = ["create_project", "get_project", "get_state", "attach_artifact", "detach_artifact", "mutate_state"]
        for method in public_methods:
            assert hasattr(ProjectStateEngine, method), f"ProjectStateEngine missing public method '{method}'"
            assert callable(getattr(ProjectStateEngine, method))

    def test_dependency_graph_public_api(self):
        public_methods = ["add_node", "add_edge", "get_dependencies", "get_dependents", "detect_cycles"]
        for method in public_methods:
            assert hasattr(DependencyGraph, method), f"DependencyGraph missing public method '{method}'"
            assert callable(getattr(DependencyGraph, method))

    def test_version_graph_public_api(self):
        public_methods = ["record_version", "get_version", "get_history", "get_latest_version", "rollback"]
        for method in public_methods:
            assert hasattr(VersionGraph, method), f"VersionGraph missing public method '{method}'"
            assert callable(getattr(VersionGraph, method))

    def test_event_bus_public_api(self):
        public_methods = ["publish", "subscribe", "unsubscribe", "get_history"]
        for method in public_methods:
            assert hasattr(EventBus, method), f"EventBus missing public method '{method}'"
            assert callable(getattr(EventBus, method))

    def test_context_engine_public_api(self):
        public_methods = ["assemble_context", "register_section_provider"]
        for method in public_methods:
            assert hasattr(ContextEngine, method), f"ContextEngine missing public method '{method}'"
            assert callable(getattr(ContextEngine, method))

    def test_task_registry_public_api(self):
        public_methods = ["register_task", "get_task", "update_status", "list_all"]
        for method in public_methods:
            assert hasattr(TaskRegistry, method), f"TaskRegistry missing public method '{method}'"
            assert callable(getattr(TaskRegistry, method))

    def test_task_scheduler_public_api(self):
        public_methods = ["schedule", "get_plan", "cancel_task"]
        for method in public_methods:
            assert hasattr(TaskScheduler, method), f"TaskScheduler missing public method '{method}'"
            assert callable(getattr(TaskScheduler, method))

    def test_capability_registry_public_api(self):
        public_methods = ["register_provider", "execute_tool", "get_provider"]
        for method in public_methods:
            assert hasattr(CapabilityRegistry, method), f"CapabilityRegistry missing public method '{method}'"
            assert callable(getattr(CapabilityRegistry, method))

    def test_agent_runtime_public_api(self):
        public_methods = ["register_agent", "get_agent", "execute_task"]
        for method in public_methods:
            assert hasattr(AgentRuntime, method), f"AgentRuntime missing public method '{method}'"
            assert callable(getattr(AgentRuntime, method))
