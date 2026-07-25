from typing import Optional
from backend.agents.base_agent import BaseAgent
from backend.contracts.context import AgentContext
from backend.contracts.agent import AgentResult
from backend.agents.tool_executor import BaseToolExecutor


class ProjectManagerAgent(BaseAgent):
    """
    Evaluates top-level project goals, tracks milestone progress,
    identifies missing prerequisites, and generates subtasks for specialized agents.
    """

    @property
    def agent_id(self) -> str:
        return "project_manager_agent"

    @property
    def agent_type(self) -> str:
        return "PROJECT_MANAGER"

    async def execute(
        self,
        context: AgentContext,
        tool_executor: Optional[BaseToolExecutor] = None,
    ) -> AgentResult:
        raise NotImplementedError("ProjectManagerAgent.execute stub")
