from typing import Dict, List, Any, Optional
from backend.contracts.context import AgentContext, ContextPolicy
from backend.contracts.task import Task


class ContextEngine:
    """
    Assembles focused, minimal context payloads for agent tasks
    using configurable per-agent ContextPolicy rules.
    """

    def __init__(self):
        self._policies: Dict[str, ContextPolicy] = {}

    def register_policy(self, policy: ContextPolicy) -> None:
        """Register a context policy for a specific agent type."""
        raise NotImplementedError("ContextEngine.register_policy stub")

    def get_policy(self, agent_type: str) -> Optional[ContextPolicy]:
        """Retrieve the context policy for an agent type."""
        raise NotImplementedError("ContextEngine.get_policy stub")

    def build_context(self, task: Task) -> AgentContext:
        """
        Build a focused AgentContext payload for the given task
        using the registered ContextPolicy for the task's target agent.
        """
        raise NotImplementedError("ContextEngine.build_context stub")
