from backend.agents.base_agent import BaseAgent
from backend.contracts.context import AgentContext
from backend.contracts.agent import AgentResult


class DirectorAgent(BaseAgent):
    """
    Maintains creative vision, scene breakdowns, and style consistency.
    Publishes high-level creative goals to the Project State Engine.
    """

    @property
    def agent_id(self) -> str:
        return "director_agent"

    @property
    def agent_type(self) -> str:
        return "DIRECTOR"

    async def execute(self, context: AgentContext) -> AgentResult:
        raise NotImplementedError("DirectorAgent.execute stub")
