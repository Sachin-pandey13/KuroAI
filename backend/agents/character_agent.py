from typing import Optional
from backend.agents.base_agent import BaseAgent
from backend.contracts.context import AgentContext
from backend.contracts.agent import AgentResult
from backend.agents.tool_executor import BaseToolExecutor


class CharacterAgent(BaseAgent):
    """
    Maintains persistent character profiles, visual reference blueprints,
    and consistency sheets (turnarounds, clothing, hairstyle memory).
    """

    @property
    def agent_id(self) -> str:
        return "character_agent"

    @property
    def agent_type(self) -> str:
        return "CHARACTER"

    async def execute(
        self,
        context: AgentContext,
        tool_executor: Optional[BaseToolExecutor] = None,
    ) -> AgentResult:
        raise NotImplementedError("CharacterAgent.execute stub")
