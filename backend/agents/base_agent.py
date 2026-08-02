from abc import ABC, abstractmethod
from typing import Optional

from backend.agents.tool_executor import BaseToolExecutor
from backend.contracts.agent import AgentResult
from backend.contracts.context import AgentContext


class BaseAgent(ABC):
    """
    Unified agent interface (Fifth Law).
    Every agent implements execute(context, tool_executor) -> AgentResult.

    Agents are stateless transformers (Fourth Law):
    - Accept context input and injected tool_executor
    - Perform domain reasoning
    - Return state updates, artifacts, events, and decision trace
    - Never store project data locally
    """

    @property
    @abstractmethod
    def agent_id(self) -> str:
        """Unique agent identifier."""
        ...

    @property
    @abstractmethod
    def agent_type(self) -> str:
        """Agent type string matching ContextPolicy registrations."""
        ...

    @abstractmethod
    async def execute(
        self,
        context: AgentContext,
        tool_executor: Optional[BaseToolExecutor] = None,
    ) -> AgentResult:
        """
        Execute the agent's specialized task given a focused context and tool_executor.

        Returns:
            AgentResult containing state_updates, produced_artifacts,
            emitted_events, and decision_trace.
        """
        ...
