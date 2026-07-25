from backend.agents.base_agent import BaseAgent
from backend.contracts.context import AgentContext
from backend.contracts.agent import AgentResult


class ProjectManagerAgent(BaseAgent):
    """
    Translates human creative intent into structured goals and tasks.
    Monitors project progress, tracks dependencies, and creates task breakdowns.
    """

    @property
    def agent_id(self) -> str:
        return "project_manager_agent"

    @property
    def agent_type(self) -> str:
        return "PROJECT_MANAGER"

    async def execute(self, context: AgentContext) -> AgentResult:
        raise NotImplementedError("ProjectManagerAgent.execute stub")
