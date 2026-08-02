from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Set
import copy
from backend.contracts.context import (
    AgentContext,
    ContextPolicy,
    ContextSection,
    ContextSectionType,
    ContextSelector,
    BudgetStrategy,
)
from backend.contracts.task import Task
from backend.engine.artifact_registry import ArtifactRegistry
from backend.engine.state_engine import ProjectStateEngine
from backend.engine.dependency_graph import DependencyGraph
from backend.engine.version_graph import VersionGraph


class TokenEstimator:
    """
    Independent helper for heuristic token cost estimation.
    Approximates ~4 characters per token for stringified payloads.
    """

    @staticmethod
    def estimate_token_cost(data: Any) -> int:
        if data is None:
            return 0
        text = str(data)
        return max(1, len(text) // 4)


class ContextCache:
    """
    Request-scoped cache preventing duplicate retrievals during context assembly.
    """

    def __init__(self) -> None:
        self._cache: Dict[str, ContextSection] = {}

    def get(self, key: str) -> Optional[ContextSection]:
        return self._cache.get(key)

    def put(self, key: str, section: ContextSection) -> None:
        self._cache[key] = section

    def clear(self) -> None:
        self._cache.clear()


class BaseRetriever(ABC):
    """
    Abstract Base Class for interface-driven context retrievers.
    New retrieval providers (VectorStore, Memory, ExternalSearch) extend this class.
    """

    @abstractmethod
    def retrieve(
        self,
        task: Task,
        selector: ContextSelector,
        engines: Dict[str, Any],
        cache: ContextCache,
        estimator: TokenEstimator,
    ) -> Optional[ContextSection]:
        pass


class StateRetriever(BaseRetriever):
    """Retrieves project state, style guidelines, and world lore from ProjectStateEngine."""

    def retrieve(
        self,
        task: Task,
        selector: ContextSelector,
        engines: Dict[str, Any],
        cache: ContextCache,
        estimator: TokenEstimator,
    ) -> Optional[ContextSection]:
        state_engine: Optional[ProjectStateEngine] = engines.get("state_engine")
        if not state_engine:
            return None

        project_id = task.payload.get("project_id")
        cache_key = f"state:{selector.value}:{project_id}"
        cached = cache.get(cache_key)
        if cached:
            return cached

        try:
            state = (
                state_engine.get_project(project_id)
                if project_id
                else state_engine.get_state()
            )
        except Exception:
            return None

        section: Optional[ContextSection] = None

        if selector == ContextSelector.PROJECT_STATE:
            goals_payload = [
                g.dict() if hasattr(g, "dict") else str(g)
                for g in state.active_goals
            ]
            content = {
                "title": state.title,
                "description": state.description,
                "active_goals": goals_payload,
                "metadata": state.metadata,
            }
            cost = estimator.estimate_token_cost(content)
            section = ContextSection(
                section_type=ContextSectionType.GOAL,
                title="Project State & Goals",
                content=content,
                priority=1,
                estimated_token_cost=cost,
            )

        elif selector == ContextSelector.PROJECT_STYLE:
            content = dict(state.style_guidelines)
            cost = estimator.estimate_token_cost(content)
            section = ContextSection(
                section_type=ContextSectionType.STYLE_GUIDELINES,
                title="Project Style Guidelines",
                content=content,
                priority=4,
                estimated_token_cost=cost,
            )

        elif selector == ContextSelector.PROJECT_LORE:
            content = dict(state.character_registry)
            cost = estimator.estimate_token_cost(content)
            section = ContextSection(
                section_type=ContextSectionType.WORLD_LORE,
                title="World Lore & Character Registry",
                content=content,
                priority=5,
                estimated_token_cost=cost,
            )

        if section:
            cache.put(cache_key, section)
        return section


class ArtifactRetriever(BaseRetriever):
    """Retrieves direct artifact data and character blueprints from ArtifactRegistry."""

    def retrieve(
        self,
        task: Task,
        selector: ContextSelector,
        engines: Dict[str, Any],
        cache: ContextCache,
        estimator: TokenEstimator,
    ) -> Optional[ContextSection]:
        registry: Optional[ArtifactRegistry] = engines.get("registry")
        if not registry:
            return None

        target_artifact_id = task.payload.get("artifact_id") or task.payload.get("target_artifact_id")

        if selector == ContextSelector.CHARACTER_BLUEPRINT:
            blueprints = {}
            for art in registry.list_all():
                art_type_str = art.artifact_type.value if hasattr(art.artifact_type, "value") else str(art.artifact_type)
                if art_type_str == "CHARACTER_PROFILE":
                    blueprints[art.artifact_id] = art.data

            if not blueprints:
                return None

            cost = estimator.estimate_token_cost(blueprints)
            return ContextSection(
                section_type=ContextSectionType.CHARACTER_BLUEPRINT,
                title="Character Blueprints",
                content=blueprints,
                priority=3,
                estimated_token_cost=cost,
            )

        elif selector in (ContextSelector.ARTIFACT_UPSTREAM, ContextSelector.ARTIFACT_RELATED):
            if not target_artifact_id or not registry.exists(target_artifact_id):
                return None

            art = registry.get(target_artifact_id)
            content = {
                "artifact_id": art.artifact_id,
                "artifact_type": art.artifact_type.value if hasattr(art.artifact_type, "value") else str(art.artifact_type),
                "data": art.data,
                "metadata": art.metadata,
            }
            cost = estimator.estimate_token_cost(content)
            return ContextSection(
                section_type=ContextSectionType.UPSTREAM_ARTIFACT,
                title=f"Artifact Data ({art.artifact_id})",
                content=content,
                priority=2,
                estimated_token_cost=cost,
            )

        return None


class GraphRetriever(BaseRetriever):
    """Traverses DependencyGraph upstream ancestors for direct and transitive dependency context."""

    def retrieve(
        self,
        task: Task,
        selector: ContextSelector,
        engines: Dict[str, Any],
        cache: ContextCache,
        estimator: TokenEstimator,
    ) -> Optional[ContextSection]:
        dep_graph: Optional[DependencyGraph] = engines.get("dep_graph")
        registry: Optional[ArtifactRegistry] = engines.get("registry")

        if not dep_graph or not registry:
            return None

        target_artifact_id = task.payload.get("artifact_id") or task.payload.get("target_artifact_id")
        if not target_artifact_id or not dep_graph.has_node(target_artifact_id):
            return None

        ancestor_ids = dep_graph.ancestors(target_artifact_id)
        ancestor_payloads = {}
        for anc_id in ancestor_ids:
            if registry.exists(anc_id):
                art = registry.get(anc_id)
                ancestor_payloads[anc_id] = {
                    "artifact_type": art.artifact_type.value if hasattr(art.artifact_type, "value") else str(art.artifact_type),
                    "data": art.data,
                }

        if not ancestor_payloads:
            return None

        cost = estimator.estimate_token_cost(ancestor_payloads)
        return ContextSection(
            section_type=ContextSectionType.UPSTREAM_ARTIFACT,
            title=f"Upstream DAG Ancestors ({len(ancestor_payloads)})",
            content=ancestor_payloads,
            priority=2,
            estimated_token_cost=cost,
        )


class HistoryRetriever(BaseRetriever):
    """Retrieves version history snapshots from VersionGraph."""

    def retrieve(
        self,
        task: Task,
        selector: ContextSelector,
        engines: Dict[str, Any],
        cache: ContextCache,
        estimator: TokenEstimator,
    ) -> Optional[ContextSection]:
        version_graph: Optional[VersionGraph] = engines.get("version_graph")
        if not version_graph:
            return None

        target_artifact_id = task.payload.get("artifact_id") or task.payload.get("target_artifact_id")
        if not target_artifact_id or not version_graph.has_history(target_artifact_id):
            return None

        try:
            history = version_graph.get_history(target_artifact_id)
            history_snapshots = [
                {
                    "version_number": v.version_number,
                    "data": v.data_snapshot,
                    "change_summary": v.change_summary,
                }
                for v in history
            ]
            cost = estimator.estimate_token_cost(history_snapshots)
            return ContextSection(
                section_type=ContextSectionType.VERSION_HISTORY,
                title=f"Version History ({target_artifact_id})",
                content={"history": history_snapshots},
                priority=6,
                estimated_token_cost=cost,
            )
        except Exception:
            return None


class ContextEngine:
    """
    Generic Context Engine Infrastructure.

    Features:
    - Interface-driven BaseRetriever hierarchy (State, Artifact, Graph, History).
    - Extensible ContextSelector hierarchies (PROJECT.STATE, ARTIFACT.UPSTREAM, etc.).
    - Section-based AgentContext assembly.
    - TokenEstimator heuristic token costing.
    - Request-scoped ContextCache to eliminate duplicate lookups.
    - Pluggable BudgetStrategy (DROP, TRUNCATE).
    - Generic external policy registration (zero agent-specific hardcoding inside engine).
    """

    def __init__(
        self,
        artifact_registry: Optional[ArtifactRegistry] = None,
        project_state_engine: Optional[ProjectStateEngine] = None,
        dependency_graph: Optional[DependencyGraph] = None,
        version_graph: Optional[VersionGraph] = None,
    ) -> None:
        self._engines: Dict[str, Any] = {
            "registry": artifact_registry,
            "state_engine": project_state_engine,
            "dep_graph": dependency_graph,
            "version_graph": version_graph,
        }
        self._policies: Dict[str, ContextPolicy] = {}
        self._retrievers: Dict[ContextSelector, List[BaseRetriever]] = {}
        self._estimator = TokenEstimator()

        # Register default retriever mappings
        state_ret = StateRetriever()
        art_ret = ArtifactRetriever()
        graph_ret = GraphRetriever()
        hist_ret = HistoryRetriever()

        self.register_retriever(ContextSelector.PROJECT_STATE, state_ret)
        self.register_retriever(ContextSelector.PROJECT_STYLE, state_ret)
        self.register_retriever(ContextSelector.PROJECT_LORE, state_ret)

        self.register_retriever(ContextSelector.ARTIFACT_UPSTREAM, art_ret)
        self.register_retriever(ContextSelector.ARTIFACT_UPSTREAM, graph_ret)
        self.register_retriever(ContextSelector.CHARACTER_BLUEPRINT, art_ret)
        self.register_retriever(ContextSelector.ARTIFACT_RELATED, art_ret)

        self.register_retriever(ContextSelector.ARTIFACT_HISTORY, hist_ret)

    def register_policy(self, policy: ContextPolicy) -> None:
        """Register a ContextPolicy for an agent type."""
        self._policies[policy.agent_type] = policy

    def get_policy(self, agent_type: str) -> ContextPolicy:
        """Retrieve registered policy or return generic fallback policy."""
        if agent_type in self._policies:
            return self._policies[agent_type]

        # Generic fallback policy if agent policy is not pre-registered
        return ContextPolicy(
            agent_type=agent_type,
            selectors=[ContextSelector.PROJECT_STATE, ContextSelector.ARTIFACT_UPSTREAM],
        )

    def register_retriever(self, selector: ContextSelector, retriever: BaseRetriever) -> None:
        """Register a BaseRetriever provider for a ContextSelector."""
        if selector not in self._retrievers:
            self._retrievers[selector] = []
        if retriever not in self._retrievers[selector]:
            self._retrievers[selector].append(retriever)

    def register_section_provider(self, selector: ContextSelector, retriever: BaseRetriever) -> None:
        """Public API Alias for register_retriever."""
        self.register_retriever(selector, retriever)


    def estimate_token_cost(self, data: Any) -> int:
        """Expose token cost estimation API."""
        return self._estimator.estimate_token_cost(data)

    def build_context(
        self, task: Task, cache: Optional[ContextCache] = None
    ) -> AgentContext:
        """
        Build focused AgentContext payload executing 3-stage pipeline:
        1. Retrieval (via BaseRetriever providers + ContextCache)
        2. Assembly (into ContextSection objects with TokenEstimator costs)
        3. Budget Management (applying DROP or TRUNCATE strategy)
        """
        request_cache = cache if cache is not None else ContextCache()
        policy = self.get_policy(task.target_agent_type)

        # Stage 1 & 2: Retrieve and Assemble Sections
        sections: List[ContextSection] = []
        seen_section_types: Set[str] = set()

        for selector in policy.selectors:
            retrievers = self._retrievers.get(selector, [])
            for ret in retrievers:
                sec = ret.retrieve(
                    task=task,
                    selector=selector,
                    engines=self._engines,
                    cache=request_cache,
                    estimator=self._estimator,
                )
                if sec and sec.section_type.value not in seen_section_types:
                    seen_section_types.add(sec.section_type.value)
                    sections.append(sec)

        # Stage 3: Budget Management
        final_sections, total_cost, is_truncated = self._apply_budget(
            sections,
            max_budget=policy.max_token_budget,
            strategy=policy.budget_strategy,
        )

        project_id = (
            task.payload.get("project_id")
            if task.payload
            else "default_project"
        )

        return AgentContext(
            task_id=task.task_id,
            project_id=project_id or "default_project",
            target_agent_type=task.target_agent_type,
            action_type=task.action_type,
            sections=final_sections,
            total_token_cost=total_cost,
            is_truncated=is_truncated,
        )

    def assemble_context(self, task: Task, cache: Optional[ContextCache] = None) -> AgentContext:
        """Public API Alias for build_context."""
        return self.build_context(task, cache=cache)


    def _apply_budget(
        self,
        sections: List[ContextSection],
        max_budget: int,
        strategy: BudgetStrategy = BudgetStrategy.DROP,
    ) -> tuple[List[ContextSection], int, bool]:
        """
        Applies token budgeting.
        If total_cost > max_budget, sheds or truncates sections based on priority (lowest priority dropped/trimmed first).
        """
        total_cost = sum(s.estimated_token_cost for s in sections)
        if total_cost <= max_budget:
            return sections, total_cost, False

        # Budget exceeded — sort by priority (1 is highest priority, 6+ lowest)
        # We process from lowest priority to highest priority for trimming
        sorted_sections = sorted(sections, key=lambda s: s.priority)

        current_cost = total_cost
        is_truncated = False
        kept_sections: List[ContextSection] = list(sorted_sections)

        while current_cost > max_budget and len(kept_sections) > 1:
            is_truncated = True
            lowest_prio_sec = kept_sections[-1]

            if strategy == BudgetStrategy.DROP:
                # Drop section completely
                current_cost -= lowest_prio_sec.estimated_token_cost
                kept_sections.pop()

            elif strategy == BudgetStrategy.TRUNCATE:
                # Truncate content dictionary
                excess = current_cost - max_budget
                item_count = len(lowest_prio_sec.content)
                if item_count > 1:
                    # Drop half of the dictionary items in the section
                    keys_to_keep = list(lowest_prio_sec.content.keys())[: max(1, item_count // 2)]
                    truncated_content = {k: lowest_prio_sec.content[k] for k in keys_to_keep}
                    new_sec_cost = self._estimator.estimate_token_cost(truncated_content)

                    current_cost -= (lowest_prio_sec.estimated_token_cost - new_sec_cost)
                    kept_sections[-1] = ContextSection(
                        section_type=lowest_prio_sec.section_type,
                        title=f"{lowest_prio_sec.title} (Truncated)",
                        content=truncated_content,
                        priority=lowest_prio_sec.priority,
                        estimated_token_cost=new_sec_cost,
                    )
                else:
                    # Cannot truncate single item further, drop it
                    current_cost -= lowest_prio_sec.estimated_token_cost
                    kept_sections.pop()
            else:
                # Fallback drop
                current_cost -= lowest_prio_sec.estimated_token_cost
                kept_sections.pop()

        # Re-sort back into priority order
        final_sections = sorted(kept_sections, key=lambda s: s.priority)
        return final_sections, current_cost, is_truncated

