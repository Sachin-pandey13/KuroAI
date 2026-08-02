"""
Test: Context Engine & Token Window Budgeting (Milestone 6)
Verifies Stages 1-3: Context Contracts, Selectors, Policy Registration,
Interface-driven Retrievers, TokenEstimator, ContextCache, Budgeting Strategies (DROP & TRUNCATE),
and End-to-End Multi-Engine Pipeline Integration.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from backend.contracts.artifact import Artifact, ArtifactType
from backend.contracts.context import (
    BudgetStrategy,
    ContextPolicy,
    ContextSection,
    ContextSectionType,
    ContextSelector,
)
from backend.contracts.goal import CreativeGoal
from backend.contracts.task import Task
from backend.engine.artifact_registry import ArtifactRegistry
from backend.engine.context_engine import (
    BaseRetriever,
    ContextCache,
    ContextEngine,
    TokenEstimator,
)
from backend.engine.dependency_graph import DependencyGraph
from backend.engine.state_engine import ProjectStateEngine
from backend.engine.version_graph import VersionGraph


@pytest.fixture
def registry() -> ArtifactRegistry:
    return ArtifactRegistry()


@pytest.fixture
def state_engine(registry) -> ProjectStateEngine:
    engine = ProjectStateEngine(artifact_registry=registry)
    engine.create_project("KuroAI Manga", "Action Manga Project")
    return engine


@pytest.fixture
def dep_graph() -> DependencyGraph:
    return DependencyGraph()


@pytest.fixture
def version_graph() -> VersionGraph:
    return VersionGraph()


@pytest.fixture
def context_engine(registry, state_engine, dep_graph, version_graph) -> ContextEngine:
    return ContextEngine(
        artifact_registry=registry,
        project_state_engine=state_engine,
        dependency_graph=dep_graph,
        version_graph=version_graph,
    )


# =====================================================================
# Unit Tests — Policy Management & Policy Lookup
# =====================================================================


class TestPolicyManagement:
    def test_register_and_get_custom_policy(self, context_engine):
        policy = ContextPolicy(
            agent_type="STORY",
            selectors=[ContextSelector.PROJECT_STATE, ContextSelector.PROJECT_STYLE],
            max_token_budget=5000,
        )
        context_engine.register_policy(policy)

        retrieved = context_engine.get_policy("STORY")
        assert retrieved.agent_type == "STORY"
        assert retrieved.max_token_budget == 5000
        assert ContextSelector.PROJECT_STYLE in retrieved.selectors

    def test_fallback_policy_for_unregistered_agent(self, context_engine):
        policy = context_engine.get_policy("UNKNOWN_AGENT")
        assert policy.agent_type == "UNKNOWN_AGENT"
        assert ContextSelector.PROJECT_STATE in policy.selectors
        assert ContextSelector.ARTIFACT_UPSTREAM in policy.selectors


# =====================================================================
# Unit Tests — TokenEstimator & ContextCache
# =====================================================================


class TestEstimatorAndCache:
    def test_token_estimator_calculation(self):
        estimator = TokenEstimator()
        assert estimator.estimate_token_cost(None) == 0
        assert estimator.estimate_token_cost("12345678") == 2
        assert estimator.estimate_token_cost({"key": "value"}) >= 1

    def test_context_cache_get_put_clear(self):
        cache = ContextCache()
        sec = ContextSection(
            section_type=ContextSectionType.GOAL,
            title="Test Section",
            content={"a": 1},
            priority=1,
            estimated_token_cost=5,
        )

        assert cache.get("key1") is None
        cache.put("key1", sec)
        assert cache.get("key1") == sec

        cache.clear()
        assert cache.get("key1") is None


# =====================================================================
# Unit Tests — Custom BaseRetriever Plugin
# =====================================================================


class TestCustomRetrieverPlugin:
    def test_custom_retriever_registration(self, context_engine):
        class CustomLoreRetriever(BaseRetriever):
            def retrieve(self, task, selector, engines, cache, estimator):
                return ContextSection(
                    section_type=ContextSectionType.CUSTOM,
                    title="Custom World Lore",
                    content={"lore": "Ancient Magic Systems"},
                    priority=2,
                    estimated_token_cost=10,
                )

        custom_ret = CustomLoreRetriever()
        context_engine.register_retriever(ContextSelector.CHARACTER_RELATIONSHIPS, custom_ret)

        policy = ContextPolicy(
            agent_type="LORE_AGENT",
            selectors=[ContextSelector.CHARACTER_RELATIONSHIPS],
        )
        context_engine.register_policy(policy)

        task = Task(goal_id="g1", target_agent_type="LORE_AGENT")
        ctx = context_engine.build_context(task)

        sec = ctx.get_section(ContextSectionType.CUSTOM)
        assert sec is not None
        assert sec.title == "Custom World Lore"
        assert sec.content["lore"] == "Ancient Magic Systems"


# =====================================================================
# Unit Tests — Budgeting Strategies (DROP & TRUNCATE)
# =====================================================================


class TestBudgetingStrategies:
    def test_budget_within_limit_no_truncation(self, context_engine, state_engine):
        state_engine.mutate_state({"style_guidelines": {"art_style": "manga_noir"}})

        policy = ContextPolicy(
            agent_type="STORY",
            selectors=[ContextSelector.PROJECT_STYLE],
            max_token_budget=1000,
        )
        context_engine.register_policy(policy)

        task = Task(goal_id="g1", target_agent_type="STORY")
        ctx = context_engine.build_context(task)

        assert ctx.is_truncated is False
        assert ctx.total_token_cost <= 1000

    def test_budget_strategy_drop(self, context_engine, state_engine):
        # Add large payload to style
        large_style = {f"rule_{i}": f"long_value_string_descriptor_{i}" for i in range(100)}
        state_engine.mutate_state({"style_guidelines": large_style})

        # Set tight budget with DROP strategy
        policy = ContextPolicy(
            agent_type="STORY",
            selectors=[ContextSelector.PROJECT_STATE, ContextSelector.PROJECT_STYLE],
            budget_strategy=BudgetStrategy.DROP,
            max_token_budget=20,  # Tight limit forces drop of lower priority section
        )
        context_engine.register_policy(policy)

        task = Task(goal_id="g1", target_agent_type="STORY")
        ctx = context_engine.build_context(task)

        assert ctx.is_truncated is True
        # Style guidelines (priority 4) shed, Goal section (priority 1) preserved
        assert ctx.get_section(ContextSectionType.STYLE_GUIDELINES) is None

    def test_budget_strategy_truncate(self, context_engine, state_engine):
        large_style = {f"rule_{i}": f"long_value_string_descriptor_{i}" for i in range(50)}
        state_engine.mutate_state({"style_guidelines": large_style})

        policy = ContextPolicy(
            agent_type="STORY",
            selectors=[ContextSelector.PROJECT_STATE, ContextSelector.PROJECT_STYLE],
            budget_strategy=BudgetStrategy.TRUNCATE,
            max_token_budget=150,
        )
        context_engine.register_policy(policy)

        task = Task(goal_id="g1", target_agent_type="STORY")
        ctx = context_engine.build_context(task)

        assert ctx.is_truncated is True
        sec = ctx.get_section(ContextSectionType.STYLE_GUIDELINES)
        if sec:
            assert "(Truncated)" in sec.title


# =====================================================================
# Integration Scenarios — End-to-End Context Assembly
# =====================================================================


class TestEndToEndContextAssembly:
    def test_full_pipeline_assembly(
        self, context_engine, registry, state_engine, dep_graph, version_graph
    ):
        """
        Integration Scenario: Build rich AgentContext for an IMAGE task.
        Queries ProjectState, ArtifactRegistry, DependencyGraph, and VersionGraph.
        """
        # 1. State Engine Setup
        state_engine.add_goal(
            CreativeGoal(title="Draw Cyberpunk Scene", description="Neon city theme")
        )
        state_engine.mutate_state(
            {"style_guidelines": {"aspect_ratio": "16:9", "palette": "neon_blue"}}
        )

        # 2. Registry Setup
        char_art = Artifact(
            artifact_id="char-ren",
            project_id="p1",
            artifact_type=ArtifactType.CHARACTER_PROFILE,
            owner_agent="character_agent",
            data={"name": "Ren", "hair": "silver", "eyes": "cyan"},
        )
        registry.register(char_art, version_graph=version_graph)

        prompt_art = Artifact(
            artifact_id="prompt-panel-1",
            project_id="p1",
            artifact_type=ArtifactType.PANEL_PROMPT,
            owner_agent="story_agent",
            data={"prompt": "Ren standing under neon billboard in rain"},
        )
        registry.register(prompt_art, version_graph=version_graph)

        # 3. Dependency Graph Setup
        dep_graph.create_node("char-ren", "CHARACTER_PROFILE")
        dep_graph.create_node("prompt-panel-1", "PANEL_PROMPT")
        dep_graph.connect("char-ren", "prompt-panel-1")

        # 4. Version Graph History
        version_graph.record_version(
            "prompt-panel-1", {"prompt": "Ren standing under neon billboard in rain v2"}, {}
        )

        # 5. Define ContextPolicy for IMAGE Agent
        policy = ContextPolicy(
            agent_type="IMAGE",
            selectors=[
                ContextSelector.PROJECT_STATE,
                ContextSelector.PROJECT_STYLE,
                ContextSelector.CHARACTER_BLUEPRINT,
                ContextSelector.ARTIFACT_UPSTREAM,
                ContextSelector.ARTIFACT_HISTORY,
            ],
            max_token_budget=5000,
        )
        context_engine.register_policy(policy)

        # 6. Build Context for Task targeting prompt-panel-1
        task = Task(
            goal_id="g1",
            target_agent_type="IMAGE",
            action_type="GENERATE_PANEL",
            payload={
                "artifact_id": "prompt-panel-1",
                "project_id": state_engine.get_state().project_id,
            },
        )

        ctx = context_engine.build_context(task)

        # 7. Assertions
        assert ctx.task_id == task.task_id
        assert ctx.target_agent_type == "IMAGE"
        assert ctx.is_truncated is False
        assert len(ctx.sections) > 0

        # Verify Goal Section
        goal_sec = ctx.get_section(ContextSectionType.GOAL)
        assert goal_sec is not None
        assert "Draw Cyberpunk Scene" in str(goal_sec.content)

        # Verify Style Section
        style_sec = ctx.get_section(ContextSectionType.STYLE_GUIDELINES)
        assert style_sec is not None
        assert style_sec.content["palette"] == "neon_blue"

        # Verify Character Blueprint Section
        char_sec = ctx.get_section(ContextSectionType.CHARACTER_BLUEPRINT)
        assert char_sec is not None
        assert "char-ren" in char_sec.content

        # Verify Upstream Artifact Section
        up_sec = ctx.get_section(ContextSectionType.UPSTREAM_ARTIFACT)
        assert up_sec is not None
        assert "prompt-panel-1" in str(up_sec.content)

        # Verify History Section
        hist_sec = ctx.get_section(ContextSectionType.VERSION_HISTORY)
        assert hist_sec is not None
        assert len(hist_sec.content["history"]) >= 1

    def test_request_scoped_cache_reuse(self, context_engine, state_engine):
        state_engine.mutate_state({"style_guidelines": {"theme": "dark_fantasy"}})

        policy = ContextPolicy(
            agent_type="STORY",
            selectors=[ContextSelector.PROJECT_STYLE],
        )
        context_engine.register_policy(policy)

        task1 = Task(
            goal_id="g1",
            target_agent_type="STORY",
            payload={"project_id": state_engine.get_state().project_id},
        )
        task2 = Task(
            goal_id="g2",
            target_agent_type="STORY",
            payload={"project_id": state_engine.get_state().project_id},
        )

        shared_cache = ContextCache()

        ctx1 = context_engine.build_context(task1, cache=shared_cache)
        ctx2 = context_engine.build_context(task2, cache=shared_cache)

        # Both contexts retrieved identical section instance from cache
        assert ctx1.get_section(ContextSectionType.STYLE_GUIDELINES) is ctx2.get_section(
            ContextSectionType.STYLE_GUIDELINES
        )
