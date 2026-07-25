from abc import ABC, abstractmethod
from backend.contracts.context import AgentContext
from backend.contracts.agent import AgentResult


class BaseAgent(ABC):
    """
    Unified agent interface (Fifth Law).
    Every agent implements execute(context) -> AgentResult.

    Agents are stateless transformers (Fourth Law):
    - Accept context input
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
    async def execute(self, context: AgentContext) -> AgentResult:
        """
        Execute the agent's specialized task given a focused context.

        Returns:
            AgentResult containing state_updates, produced_artifacts,
            emitted_events, and decision_trace.
        """
        ...
